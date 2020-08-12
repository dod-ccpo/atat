resource "azurerm_resource_group" "vpc" {
  name     = "${var.name}-${var.environment}-vpc"
  location = var.region

  tags = {
    environment = var.environment
    owner       = var.owner
  }
}

resource "azurerm_network_ddos_protection_plan" "vpc" {
  count               = var.ddos_enabled
  name                = "${var.name}-${var.environment}-ddos"
  location            = azurerm_resource_group.vpc.location
  resource_group_name = azurerm_resource_group.vpc.name
}

resource "azurerm_virtual_network" "vpc" {
  name                = "${var.name}-${var.environment}-network"
  location            = azurerm_resource_group.vpc.location
  resource_group_name = azurerm_resource_group.vpc.name
  address_space       = ["${var.virtual_network}"]
  dns_servers         = var.dns_servers

  tags = {
    environment = var.environment
    owner       = var.owner
  }
}

resource "azurerm_subnet" "subnet" {
  for_each             = var.networks
  name                 = "${var.name}-${var.environment}-${each.key}"
  resource_group_name  = azurerm_resource_group.vpc.name
  virtual_network_name = azurerm_virtual_network.vpc.name
  address_prefixes     = [element(split(",", each.value), 0)]
  service_endpoints    = split(",", var.service_endpoints[each.key])
}

resource "azurerm_route_table" "route_table" {
  for_each            = var.route_tables
  name                = "${var.name}-${var.environment}-${each.key}"
  location            = azurerm_resource_group.vpc.location
  resource_group_name = azurerm_resource_group.vpc.name
}

resource "azurerm_subnet_route_table_association" "route_table" {
  for_each       = var.route_tables
  subnet_id      = azurerm_subnet.subnet[each.key].id
  route_table_id = azurerm_route_table.route_table[each.key].id
}

# Default Routes
resource "azurerm_route" "route" {
  for_each            = var.route_tables
  name                = "${var.name}-${var.environment}-default"
  resource_group_name = azurerm_resource_group.vpc.name
  route_table_name    = azurerm_route_table.route_table[each.key].name
  address_prefix      = "0.0.0.0/0"
  next_hop_type       = each.value
}

# Custom Routes
resource "azurerm_route" "custom_routes" {
  for_each            = var.custom_routes
  name                = "${var.name}-${var.environment}-${element(split(",", each.value), 1)}"
  resource_group_name = azurerm_resource_group.vpc.name
  #route_table_name    = "${var.name}-${var.environment}-${element(split(",", each.value), 0)}"
  route_table_name = azurerm_route_table.route_table[each.key].name
  address_prefix   = element(split(",", each.value), 2)
  next_hop_type    = element(split(",", each.value), 3)
}
