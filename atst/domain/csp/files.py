from datetime import datetime, timedelta
from uuid import uuid4


class FileService:
    def generate_token(self):
        raise NotImplementedError()

    def generate_download_link(self, object_name, filename) -> (dict, str):
        raise NotImplementedError()

    def object_name(self) -> str:
        return str(uuid4())

    def download_task_order(self, object_name):
        raise NotImplementedError()


class MockFileService(FileService):
    def __init__(self, config):
        self.config = config

    def get_token(self):
        return ({}, self.object_name())

    def generate_download_link(self, object_name, filename):
        return ""

    def download_task_order(self, object_name):
        with open("tests/fixtures/sample.pdf", "rb") as some_bytes:
            return {
                "name": object_name,
                "content": some_bytes,
            }


class AzureFileService(FileService):
    def __init__(self, config):
        self.account_name = config["AZURE_ACCOUNT_NAME"]
        self.storage_key = config["AZURE_STORAGE_KEY"]
        self.container_name = config["AZURE_TO_BUCKET_NAME"]
        self.timeout = timedelta(seconds=config["PERMANENT_SESSION_LIFETIME"])

        from azure.storage.common import CloudStorageAccount
        from azure.storage.blob import BlobSasPermissions
        from azure.storage.blob.models import BlobPermissions
        from azure.storage.blob.blockblobservice import BlockBlobService

        self.CloudStorageAccount = CloudStorageAccount
        self.BlobSasPermissions = BlobSasPermissions
        self.BlobPermissions = BlobPermissions
        self.BlockBlobService = BlockBlobService

    def get_token(self):
        """
        Generates an Azure SAS token for pre-authorizing a file upload.

        Returns a tuple in the following format: (token_dict, object_name), where
            - token_dict has a `token` key which contains the SAS token as a string
            - object_name is a string
        """
        account = self.CloudStorageAccount(
            account_name=self.account_name, account_key=self.storage_key
        )
        bbs = account.create_block_blob_service()
        object_name = self.object_name()
        sas_token = bbs.generate_blob_shared_access_signature(
            self.container_name,
            object_name,
            permission=self.BlobSasPermissions(create=True),
            expiry=datetime.utcnow() + self.timeout,
            protocol="https",
        )
        return ({"token": sas_token}, object_name)

    def generate_download_link(self, object_name, filename):
        block_blob_service = self.BlockBlobService(
            account_name=self.account_name, account_key=self.storage_key
        )
        sas_token = block_blob_service.generate_blob_shared_access_signature(
            container_name=self.container_name,
            blob_name=object_name,
            permission=self.BlobPermissions(read=True),
            expiry=datetime.utcnow() + self.timeout,
            content_disposition=f"attachment; filename={filename}",
            protocol="https",
        )
        return block_blob_service.make_blob_url(
            container_name=self.container_name,
            blob_name=object_name,
            protocol="https",
            sas_token=sas_token,
        )

    def download_task_order(self, object_name):
        block_blob_service = self.BlockBlobService(
            account_name=self.account_name, account_key=self.storage_key
        )
        # TODO: We should downloading errors more gracefully
        # - what happens when we try to request a TO that doesn't exist?
        b = block_blob_service.get_blob_to_bytes(
            container_name=self.container_name, blob_name=object_name,
        )
        return {
            "name": b.name,
            "content": b.content,
        }
