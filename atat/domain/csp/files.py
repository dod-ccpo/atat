from uuid import uuid4

import pendulum


class FileService:
    def generate_token(self):
        raise NotImplementedError()

    def generate_download_link(self, object_name, filename) -> (dict, str):
        raise NotImplementedError()

    def generate_object_name(self) -> str:
        return str(uuid4())

    def download_task_order(self, object_name):
        raise NotImplementedError()


class MockFileService(FileService):
    def __init__(self, config):
        self.config = config

    def get_token(self):
        return {}, self.generate_object_name()

    def generate_download_link(self, object_name, filename):
        return ""

    def download_task_order(self, object_name):
        with open("tests/fixtures/sample.pdf", "rb") as some_bytes:
            return {
                "name": object_name,
                "content": some_bytes.read(),
                "filename": "sample.pdf",
            }


class AzureFileService(FileService):
    DEFAULT_FILENAME = "task-order.pdf"

    def __init__(self, config):
        self.account_name = config["AZURE_STORAGE_ACCOUNT_NAME"]
        self.storage_key = config["AZURE_STORAGE_KEY"]
        self.container_name = config["AZURE_TO_BUCKET_NAME"]
        self.timeout = config["PERMANENT_SESSION_LIFETIME"]

        import azure.storage.blob

        self.blob = azure.storage.blob

    def get_token(self):
        """
        Generates an Azure SAS token for pre-authorizing a file upload.

        Returns a tuple in the following format: (token_dict, object_name), where
            - token_dict has a `token` key which contains the SAS token as a string
            - object_name is a string
        """
        # TODO: Handle errors
        sas_token = self.blob.generate_container_sas(
            account_name=self.account_name,
            container_name=self.container_name,
            account_key=self.storage_key,
            permission=self.blob.ContainerSasPermissions(write=True),
            expiry=pendulum.now(tz="UTC").add(self.timeout),
            protocol="https",
        )
        # TODO: remove object name from this tuple -- generate in js
        # We generate a UUID here only for it to be passed through to the frontend where it's used as the name of the
        # blob that's uploaded. We should just generate the object name there.
        return {"token": sas_token}, self.generate_object_name()

    def generate_download_link(self, object_name, filename):
        # TODO: Handle errors
        sas_token = self.blob.generate_blob_sas(
            account_name=self.account_name,
            container_name=self.container_name,
            blob_name=object_name,
            account_key=self.storage_key,
            permission=self.blob.BlobSasPermissions(read=True),
            expiry=pendulum.now(tz="UTC").add(self.timeout),
            content_disposition=f"attachment; filename={filename}",
            protocol="https",
        )
        url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{object_name}"
        return f"{url}?{sas_token}"

    @staticmethod
    def get_filename_from_blob(blob):
        return blob.properties.get("metadata", {}).get(
            "filename", AzureFileService.DEFAULT_FILENAME
        )

    def download_task_order(self, object_name):
        # TODO: Handle errors
        blob_client = self.blob.BlobClient(
            account_url=f"https://{self.account_name}.blob.core.windows.net",
            container_name=self.container_name,
            blob_name=object_name,
            credential=self.storage_key,
        )
        blob = blob_client.download_blob()

        return {
            "name": blob.name,
            "content": blob.readall(),
            "filename": self.get_filename_from_blob(blob),
        }
