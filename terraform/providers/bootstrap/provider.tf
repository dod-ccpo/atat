provider "azurerm" {
  version         = "=2.0.0"
  subscription_id = "95934d54-980d-47cc-9bce-3a96bf9a2d1b"
  features {}
}

provider "azuread" {
  # Whilst version is optional, we /strongly recommend/ using it to pin the version of the Provider being used
  version = "=0.7.0"
}

terraform {
  backend "azurerm" {
    resource_group_name  = "cloudzero-pwdev-cloudzerodevtfstate"
    storage_account_name = "cloudzerodevtfstate"
    container_name       = "tfstate"
    key                  = "pwdev.terraform.tfstate"
  }
}
