resource "azurerm_subnet" "redis" {
  name = "${var.name}-redis-${var.deployment_namespace}"
  resource_group_name = azurerm_resource_group.vpc.name
  virtual_network_name = azurerm_virtual_network.vpc.name
  address_prefixes = ["10.1.3.0/24"]
  service_endpoints = [
    "Microsoft.Storage",
    "Microsoft.Sql"
  ]
}

resource "azurerm_route_table" "redis" {
  name = "${var.name}-redis-${var.deployment_namespace}"
  location = azurerm_resource_group.vpc.location
  resource_group_name = azurerm_resource_group.vpc.name
}
resource "azurerm_subnet_route_table_association" "redis" {
  subnet_id = azurerm_subnet.redis.id
  route_table_id = azurerm_route_table.redis.id
}
resource "azurerm_route" "redis_to_internet" {
  name                = "${var.name}-default-${var.deployment_namespace}"
  resource_group_name = azurerm_resource_group.vpc.name
  route_table_name    = azurerm_route_table.redis.name
  address_prefix      = "0.0.0.0/0"
  next_hop_type       = "Internet"
}
resource "azurerm_route" "redis_to_vnet" {
  name = "${var.name}-vnet-${var.deployment_namespace}"
  resource_group_name = azurerm_resource_group.vpc.name
  route_table_name = azurerm_route_table.redis.name
  address_prefix = "10.1.0.0/16"
  next_hop_type = "VnetLocal"
}

resource "azurerm_resource_group" "redis" {
  name     = "${var.name}-redis-${var.deployment_namespace}"
  location = var.deployment_location
}

# NOTE: the Name used for Redis needs to be globally unique
resource "azurerm_redis_cache" "redis" {
  name                = "${var.name}-redis-${var.deployment_namespace}"
  location            = azurerm_resource_group.redis.location
  resource_group_name = azurerm_resource_group.redis.name
  capacity            = 1
  family              = "P"
  sku_name            = "Premium"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
  subnet_id           = azurerm_subnet.redis.id

  redis_configuration {
    enable_authentication = true
  }
  tags = {
    environment = var.deployment_namespace
    owner       = var.owner
  }
}
