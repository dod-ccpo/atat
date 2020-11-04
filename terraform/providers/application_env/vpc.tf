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


# edge subnet
resource "azurerm_subnet" "edge" {
  name = "${var.name}-edge-${var.deployment_namespace}"
  resource_group_name = azurerm_resource_group.vpc.name
  virtual_network_name = azurerm_virtual_network.vpc.name
  address_prefixes = ["10.1.1.0/24"]
  service_endpoints = ["Microsoft.ContainerRegistry"]
}

resource "azurerm_route_table" "edge" {
  name = "${var.name}-edge-${var.deployment_namespace}"
  location = azurerm_resource_group.vpc.location
  resource_group_name = azurerm_resource_group.vpc.name
}
resource "azurerm_subnet_route_table_association" "edge" {
  subnet_id = azurerm_subnet.edge.id
  route_table_id = azurerm_route_table.edge.id
}
resource "azurerm_route" "edge_to_internet" {
  name                = "${var.name}-default-${var.deployment_namespace}"
  resource_group_name = azurerm_resource_group.vpc.name
  route_table_name    = azurerm_route_table.edge.name
  address_prefix      = "0.0.0.0/0"
  next_hop_type       = "Internet"
}
resource "azurerm_route" "edge_to_vnet" {
  name = "${var.name}-vnet-${var.deployment_namespace}"
  resource_group_name = azurerm_resource_group.vpc.name
  route_table_name = azurerm_route_table.edge.name
  address_prefix = "10.1.0.0/16"
  next_hop_type = "VnetLocal"
}


# appgateway
resource "azurerm_subnet" "appgateway" {
  name = "${var.name}-appgateway-${var.deployment_namespace}"
  resource_group_name = azurerm_resource_group.vpc.name
  virtual_network_name = azurerm_virtual_network.vpc.name
  address_prefixes = ["10.1.6.0/24"]
  service_endpoints = []
}

resource "azurerm_route_table" "appgateway" {
  name = "${var.name}-appgateway-${var.deployment_namespace}"
  location = azurerm_resource_group.vpc.location
  resource_group_name = azurerm_resource_group.vpc.name
}
resource "azurerm_subnet_route_table_association" "appgateway" {
  subnet_id = azurerm_subnet.appgateway.id
  route_table_id = azurerm_route_table.appgateway.id
}
resource "azurerm_route" "appgateway_to_internet" {
  name                = "${var.name}-default-${var.deployment_namespace}"
  resource_group_name = azurerm_resource_group.vpc.name
  route_table_name    = azurerm_route_table.appgateway.name
  address_prefix      = "0.0.0.0/0"
  next_hop_type       = "Internet"
}
resource "azurerm_route" "appgateway_to_vnet" {
  name = "${var.name}-vnet-${var.deployment_namespace}"
  resource_group_name = azurerm_resource_group.vpc.name
  route_table_name = azurerm_route_table.appgateway.name
  address_prefix = "10.1.0.0/16"
  next_hop_type = "VnetLocal"
}
