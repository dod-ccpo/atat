output "container_registry_name" {
  value = azurerm_container_registry.acr.name
}

output "ops_container_registry_name" {
  value = azurerm_container_registry.ops.name
}
