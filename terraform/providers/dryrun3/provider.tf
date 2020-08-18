provider "azurerm" {
  version         = "=2.19.0"
  subscription_id = "a0f587a4-2876-498d-a3d3-046cd98d5363"
  features {}

}

provider "azuread" {
  # Whilst version is optional, we /strongly recommend/ using it to pin the version of the Provider being used
  version = "=0.11.0"
}

terraform {
  backend "azurerm" {}
}

resource "random_pet" "unique_id" {

  length    = 2
  separator = ""

}
