terraform {
  backend "azurerm" {
    resource_group_name  = "cloudzero-ops-dev"
    storage_account_name = "czopsstorageaccountdev"
    container_name       = "tfstatesdev"
    key                  = "dev.bootstrap.tfstate"
  }

  required_providers {
    azuread = {
      source  = "hashicorp/azuread"
      version = "= 1.0.0"
    }

    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 2.34.0"
    }

    http = {
      source = "hashicorp/http"
    }

    random = {
      source = "hashicorp/random"
    }
  }
}

# Specifying a `provider` this way is deprecated. It is necessary in this 
# situation due to an issue with the `azurerm` provider. 
#
# https://www.terraform.io/docs/configuration/providers.html#version-an-older-way-to-manage-provider-versions
# https://github.com/terraform-providers/terraform-provider-azurerm/issues/7359
provider "azurerm" {
  features {}
}
