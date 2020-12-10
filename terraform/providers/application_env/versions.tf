terraform {
  required_version = ">= 0.13"

  backend "azurerm" {
    resource_group_name  = var.resource_group_name
    storage_account_name = var.storage_account_name
    container_name       = var.container_name
    key                  = var.key
  }

  required_providers {
    azuread = {
      source  = "hashicorp/azuread"
      version = "= 1.0.0"
    }

    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 2.37.0"
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
  subscription_id = var.operator_subscription_id
  client_id       = var.operator_client_id
  client_secret   = var.operator_client_secret
  tenant_id       = var.operator_tenant_id

  features {}
}

data "terraform_remote_state" "previous_stage" {
  backend = "azurerm"

  config = {
    resource_group_name  = var.ops_resource_group  #"${azurerm_resource_group.operations_resource_group.name}"
    storage_account_name = var.ops_storage_account #"${azurerm_storage_account.operations_storage_account.name}"
    container_name       = var.tf_bootstrap_container
    key                  = "terraform.tfstate"
  }
}
