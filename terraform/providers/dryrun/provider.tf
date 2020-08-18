provider "azurerm" {
  version         = "=2.10.0"
  subscription_id = "95934d54-980d-47cc-9bce-3a96bf9a2d1b"
  features {}
}

provider "azuread" {
  # Whilst version is optional, we /strongly recommend/ using it to pin the version of the Provider being used
  version = "=0.7.0"
}

terraform {
  backend "azurerm" {
    resource_group_name  = "cloudzero-dryrun-cloudzeroddryruntfstate"
    storage_account_name = "cloudzeroddryruntfstate"
    container_name       = "tfstate"
    key                  = "dryrun.terraform.tfstate"
  }
}
