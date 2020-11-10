terraform {
  required_version = ">= 0.13"

  backend "azurerm" {
    resource_group_name  = "cloudzero-ops-dev"
    storage_account_name = "czopsstorageaccountdev"
    container_name       = "tfstatesdev"
    key                  = "dev.application.tfstate"
  }

  required_providers {
    azuread = {
      source  = "hashicorp/azuread"
      version = "= 1.0.0"
    }

    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 2.35.0"
    }

    http = {
      source  = "hashicorp/http"
      version = "~> 2.0.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.0.0"
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

data "terraform_remote_state" "previous_stage" {
  backend = "azurerm"

  config = {
    resource_group_name  = "cloudzero-ops-dev"
    storage_account_name = "czopsstorageaccountdev"
    container_name       = "tfstatesdev"
    key                  = "dev.bootstrap.tfstate"
  }
}
