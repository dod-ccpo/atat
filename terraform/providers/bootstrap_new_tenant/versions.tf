terraform {
  required_version = ">= 0.13"

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

    local = {
      source  = "hashicorp/local"
      version = "~> 2.0.0"
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
