resource "azurerm_resource_group" "redis" {
  name     = "${var.name}-${var.environment}-redis"
  location = var.region
}

# NOTE: the Name used for Redis needs to be globally unique
resource "azurerm_redis_cache" "redis" {
  name                = "${var.name}-${var.environment}-redis"
  location            = azurerm_resource_group.redis.location
  resource_group_name = azurerm_resource_group.redis.name
  capacity            = var.capacity
  family              = var.family
  sku_name            = var.sku_name
  enable_non_ssl_port = var.enable_non_ssl_port
  minimum_tls_version = var.minimum_tls_version
  subnet_id           = var.subnet_id

  redis_configuration {
    enable_authentication = var.enable_authentication
  }
  tags = {
    environment = var.environment
    owner       = var.owner
  }
}

resource "azurerm_monitor_diagnostic_setting" "redis_diagnostic" {
  name                       = "${var.name}-${var.environment}-redis-diag"
  target_resource_id         = azurerm_redis_cache.redis.id
  log_analytics_workspace_id = var.workspace_id
  metric {
    category = "AllMetrics"

    retention_policy {
      enabled = true
    }
  }
}
