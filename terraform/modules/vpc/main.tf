resource "azurerm_resource_group" "vpc" {
  name     = "${var.name}-vpc-${var.environment}"
  location = var.region

  tags = {
    environment = var.environment
    owner       = var.owner
  }
}

resource "azurerm_network_ddos_protection_plan" "vpc" {
  count               = var.ddos_enabled
  name                = "${var.name}-ddos-${var.environment}"
  location            = azurerm_resource_group.vpc.location
  resource_group_name = azurerm_resource_group.vpc.name
}

resource "azurerm_virtual_network" "vpc" {
  name                = "${var.name}-network-${var.environment}"
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
  name                 = "${each.key == "AzureFirewallSubnet" ? "AzureFirewallSubnet" : "${var.name}-${each.key}-${var.environment}"}"
  resource_group_name  = azurerm_resource_group.vpc.name
  virtual_network_name = azurerm_virtual_network.vpc.name
  address_prefixes     = [element(split(",", each.value), 0)]
  service_endpoints    = split(",", var.service_endpoints[each.key])
}

resource "azurerm_route_table" "route_table" {
  for_each            = var.route_tables
  name                = "${var.name}-${each.key}-${var.environment}"
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
  name                = "${var.name}-default-${var.environment}"
  resource_group_name = azurerm_resource_group.vpc.name
  route_table_name    = azurerm_route_table.route_table[each.key].name
  address_prefix      = "0.0.0.0/0"
  next_hop_type       = each.value
}

# Custom Routes
resource "azurerm_route" "custom_routes" {
  for_each            = var.custom_routes
  name                = "${var.name}-${element(split(",", each.value), 1)}-${var.environment}"
  resource_group_name = azurerm_resource_group.vpc.name
  route_table_name    = azurerm_route_table.route_table[each.key].name
  address_prefix      = element(split(",", each.value), 2)
  next_hop_type       = element(split(",", each.value), 3)
}

resource "azurerm_route_table" "firewall_route_table" {
  for_each            = var.virtual_appliance_route_tables
  name                = "${var.name}-${each.key}-${var.environment}"
  location            = azurerm_resource_group.vpc.location
  resource_group_name = azurerm_resource_group.vpc.name
}



resource "azurerm_route" "firewall_routes" {

  name                   = "${var.name}-${element(split(",", var.virtual_appliance_routes), 0)}-${var.environment}"
  resource_group_name    = azurerm_resource_group.vpc.name
  route_table_name       = azurerm_route_table.firewall_route_table[element(split(",", var.virtual_appliance_routes), 0)].name
  address_prefix         = chomp(element(split(",", var.virtual_appliance_routes), 2))
  next_hop_type          = chomp(element(split(",", var.virtual_appliance_routes), 3))
  next_hop_in_ip_address = chomp(element(split(",", var.virtual_appliance_routes), 4))
}

resource "azurerm_subnet_route_table_association" "firewall_route_table" {
  for_each       = var.virtual_appliance_route_tables
  subnet_id      = azurerm_subnet.subnet[each.key].id
  route_table_id = azurerm_route_table.firewall_route_table[each.key].id
}

# Default Routes
resource "azurerm_route" "fw_route" {
  for_each               = var.virtual_appliance_route_tables
  name                   = "${var.name}-default-${var.environment}"
  resource_group_name    = azurerm_resource_group.vpc.name
  route_table_name       = azurerm_route_table.firewall_route_table[each.key].name
  address_prefix         = "0.0.0.0/0"
  next_hop_type          = each.value
  next_hop_in_ip_address = chomp(element(split(",", var.virtual_appliance_routes), 4))
}
