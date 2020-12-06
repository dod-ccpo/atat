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




resource "azurerm_public_ip" "az_fw_ip" {
  name                = "az-firewall-${var.environment}"
  location            = var.region
  resource_group_name = azurerm_resource_group.vpc.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

# security groups w/ default rules:

resource "azurerm_network_security_group" "example" {
  for_each            = var.networks
  name                = "${var.name}-${each.key}-${var.environment}-nsg"
  location            = var.region
  resource_group_name = azurerm_resource_group.vpc.name

  security_rule {
    name                       = "allowATAT"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    environment = var.environment
    owner       = var.owner
  }
}
