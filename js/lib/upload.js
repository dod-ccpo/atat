import { BlobServiceClient } from '@azure/storage-blob'
import 'whatwg-fetch'

class AzureUploader {
  constructor(accountName, containerName, sasToken, objectName) {
    this.accountName = accountName
    this.containerName = containerName
    this.sasToken = sasToken.token
    this.objectName = objectName
  }

  async upload(file) {
    const blobServiceClient = new BlobServiceClient(
      `https://${this.accountName}.blob.core.windows.net?${this.sasToken}`
    )
    const containerClient = blobServiceClient.getContainerClient(
      this.containerName
    )
    const blobClient = containerClient.getBlockBlobClient(this.objectName)
    const options = {
      blobHTTPHeaders: {
        blobContentType: 'application/pdf',
      },
      metadata: {
        filename: file.name,
      },
    }
    return blobClient.uploadBrowserData(file, options)
  }
}

export class MockUploader {
  constructor(token, objectName) {
    this.token = token
    this.objectName = objectName
  }

  async upload(file, objectName) {
    // mock BlobUploadCommonResponse structure: https://docs.microsoft.com/en-us/javascript/api/@azure/storage-blob/blobuploadcommonresponse?view=azure-node-latest
    return Promise.resolve({ _response: { status: 201 } })
  }
}

export const buildUploader = (token, objectName) => {
  const cloudProvider = process.env.CLOUD_PROVIDER || 'mock'
  if (cloudProvider === 'azure') {
    return new AzureUploader(
      process.env.AZURE_ACCOUNT_NAME,
      process.env.AZURE_CONTAINER_NAME,
      token,
      objectName
    )
  } else {
    return new MockUploader(token, objectName)
  }
}
