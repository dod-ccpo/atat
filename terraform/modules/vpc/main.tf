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
  address_prefix       = element(split(",", each.value), 0)

  # See https://github.com/terraform-providers/terraform-provider-azurerm/issues/3471
  lifecycle {
    ignore_changes = [route_table_id]
  }
  #delegation {
  #  name = "acctestdelegation"
  #
  #  service_delegation {
  #    name    = "Microsoft.ContainerInstance/containerGroups"
  #    actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
  #  }
  #}
}

resource "azurerm_route_table" "route_table" {
  for_each            = var.route_tables
  name                = "${var.name}-${var.environment}-${each.key}"
  location            = azurerm_resource_group.vpc.location
  resource_group_name = azurerm_resource_group.vpc.name
}

resource "azurerm_subnet_route_table_association" "route_table" {
  for_each       = var.networks
  subnet_id      = azurerm_subnet.subnet[each.key].id
  route_table_id = azurerm_route_table.route_table[each.key].id
}

resource "azurerm_route" "route" {
  for_each            = var.route_tables
  name                = "${var.name}-${var.environment}-default"
  resource_group_name = azurerm_resource_group.vpc.name
  route_table_name    = azurerm_route_table.route_table[each.key].name
  address_prefix      = "0.0.0.0/0"
  next_hop_type       = each.value
}

# Required for the gateway
resource "azurerm_subnet" "gateway" {
  name                 = "GatewaySubnet"
  resource_group_name  = azurerm_resource_group.vpc.name
  virtual_network_name = azurerm_virtual_network.vpc.name
  address_prefix       = var.gateway_subnet
}


resource "azurerm_public_ip" "vpn_ip" {
  name                = "${var.name}-${var.environment}-vpn-ip"
  location            = azurerm_resource_group.vpc.location
  resource_group_name = azurerm_resource_group.vpc.name

  allocation_method = "Dynamic"
}

resource "azurerm_virtual_network_gateway" "vnet_gateway" {
  name                = "${var.name}-${var.environment}-gateway"
  location            = azurerm_resource_group.vpc.location
  resource_group_name = azurerm_resource_group.vpc.name

  type     = "Vpn"
  vpn_type = "RouteBased"

  active_active = false
  enable_bgp    = false
  sku           = "Standard"

  ip_configuration {
    name                          = "vnetGatewayConfig"
    public_ip_address_id          = azurerm_public_ip.vpn_ip.id
    private_ip_address_allocation = "Dynamic"
    subnet_id                     = azurerm_subnet.gateway.id
  }

  vpn_client_configuration {
    address_space        = ["172.16.1.0/24"]
    vpn_client_protocols = ["OpenVPN"]
  }
}