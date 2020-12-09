resource "azurerm_resource_group" "vpc" {
  name     = "${var.name}-vpc-${var.deployment_namespace}"
  location = var.deployment_location

  tags = {
    environment = var.deployment_namespace
    owner       = var.owner
  }
}

resource "azurerm_network_ddos_protection_plan" "vpc" {
  count               = var.ddos_enabled
  name                = "${var.name}-ddos-${var.deployment_namespace}"
  location            = azurerm_resource_group.vpc.location
  resource_group_name = azurerm_resource_group.vpc.name
}

resource "azurerm_virtual_network" "vpc" {
  name                = "${var.name}-network-${var.deployment_namespace}"
  location            = azurerm_resource_group.vpc.location
  resource_group_name = azurerm_resource_group.vpc.name
  address_space       = [var.virtual_network] # TODO(jesse) Can this be wired up dynamically?
  dns_servers         = []

  tags = {
    environment = var.deployment_namespace
    owner       = var.owner
  }
}
