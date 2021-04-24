import azure.storage.blob
import pytest

from atat.domain.csp.files import AzureFileService


@pytest.fixture
def file_service(app):
    file_service = AzureFileService(config=app.config)
    return file_service


def test_service_name(file_service):
    assert file_service.service_name() == "azure"


def test_get_token(file_service, mocker):
    mocker.patch.object(
        azure.storage.blob, "generate_container_sas", return_value="container_sas_token"
    )
    mocker.patch.object(file_service.blob, "BlobClient")
    file_service.blob.BlobClient.return_value.exists.return_value = False
    token_dict, _ = file_service.get_token()
    assert token_dict["token"] == "container_sas_token"


def test_generate_object_name_no_retries_if_not_exist(file_service, mocker):
    mocker.patch.object(
        azure.storage.blob, "generate_container_sas", return_value="container_sas_token"
    )
    mocker.patch.object(file_service.blob, "BlobClient")
    file_service.blob.BlobClient.return_value.exists.return_value = False
    assert file_service.generate_object_name()
    file_service.blob.BlobClient.return_value.exists.assert_called_once()


def test_generate_object_name_does_retry_if_exists(file_service, mocker):
    mocker.patch.object(
        azure.storage.blob, "generate_container_sas", return_value="container_sas_token"
    )
    mocker.patch.object(file_service.blob, "BlobClient")
    file_service.blob.BlobClient.return_value.exists.side_effect = [
        True,
        True,
        True,
        False,
        True,
    ]
    assert file_service.generate_object_name()
    assert len(file_service.blob.BlobClient.return_value.exists.call_args_list) == 4


def test_generate_download_link(file_service, mocker, app):
    mocker.patch.object(
        azure.storage.blob, "generate_blob_sas", return_value="blob_sas_token"
    )
    object_name = "object_name"
    download_link = file_service.generate_download_link("object_name", "filename")
    assert (
        download_link
        == f"https://{file_service.account_name}.blob.core.windows.net/{file_service.container_name}/{object_name}?blob_sas_token"
    )


def test_client_upload_config(file_service):
    client_config = file_service.client_upload_config()
    assert "azureAccountName" in client_config
    assert "azureContainerName" in client_config
    assert client_config["azureAccountName"] == file_service.account_name
    assert client_config["azureContainerName"] == file_service.container_name


@pytest.fixture
def mock_blob_class():
    class MockBlob:
        name = "object_name"

        def __init__(self, properties):
            self.properties = properties

        def readall(self):
            return b"some_bytes"

    return MockBlob


def test_get_filename_from_blob(file_service, mock_blob_class):

    blob_with_metadata = mock_blob_class({"metadata": {"filename": "filename.pdf"}})
    assert file_service.get_filename_from_blob(blob_with_metadata) == "filename.pdf"

    metadata_missing_filename = mock_blob_class({"metadata": {}})
    assert (
        file_service.get_filename_from_blob(metadata_missing_filename)
        == file_service.DEFAULT_FILENAME
    )

    blob_without_metadata = mock_blob_class({})
    assert (
        file_service.get_filename_from_blob(blob_without_metadata)
        == file_service.DEFAULT_FILENAME
    )


def test_download_task_order(mocker, file_service, mock_blob_class):
    mock_blob = mock_blob_class(properties={"metadata": {"filename": "filename.pdf"}})
    mocker.patch("azure.storage.blob.BlobClient")
    azure.storage.blob.BlobClient.return_value.download_blob.return_value = mock_blob
    task_order_download = file_service.download_task_order("object_name")
    assert task_order_download["name"] == "object_name"
    assert task_order_download["content"] == b"some_bytes"
    assert task_order_download["filename"] == "filename.pdf"
