data "http" "myip" {
  url = "http://ipinfo.io/ip"
}

resource "azurerm_resource_group" "operations_resource_group" {
  name     = "cloudzero-ops-${var.operations_namespace}"
  location = var.operations_location
}

resource "azurerm_virtual_network" "operations_virtual_network" {
  name                = "cloudzero-ops-network-${var.operations_namespace}"
  location            = var.operations_location
  resource_group_name = azurerm_resource_group.operations_resource_group.name
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "deployment_subnet" {
  name                 = "deployment-subnet-${var.operations_namespace}"
  address_prefixes     = ["10.0.1.0/24"]
  resource_group_name  = azurerm_resource_group.operations_resource_group.name
  virtual_network_name = azurerm_virtual_network.operations_virtual_network.name

  service_endpoints = [
    "Microsoft.ContainerRegistry",
    "Microsoft.KeyVault",
    "Microsoft.Sql",
    "Microsoft.Storage"
  ]
}

resource "azurerm_storage_account" "operations_storage_account" {
  name                     = "czopsstorageaccount${var.operations_namespace}"
  resource_group_name      = azurerm_resource_group.operations_resource_group.name
  location                 = var.operations_location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  network_rules {
    default_action             = "Deny"
    virtual_network_subnet_ids = [azurerm_subnet.deployment_subnet.id]
    ip_rules                   = [chomp(data.http.myip.body)]
  }
}

resource "azurerm_storage_container" "deployment_states" {
  name = "tfstates${var.operations_namespace}"
  storage_account_name = azurerm_storage_account.operations_storage_account.name
  container_access_type = "private"
}

resource "azurerm_container_registry" "operations_container_registry" {
  name                = "cloudzeroopsregistry${var.operations_namespace}"
  resource_group_name = azurerm_resource_group.operations_resource_group.name
  location            = var.operations_location
  sku                 = "Premium"
}
