provider "azurerm" {
  version = "=2.10.0"
  features {}
}

provider "azuread" {
  # Whilst version is optional, we /strongly recommend/ using it to pin the version of the Provider being used
  version = "=0.7.0"
}
