output "hostname" {
  value = azurerm_redis_cache.redis.hostname
}

output "ssl_port" {
  value = azurerm_redis_cache.redis.ssl_port
}

output "primary_key" {
  value = azurerm_redis_cache.redis.primary_access_key
}
