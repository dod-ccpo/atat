output "rg_id" { value = azurerm_resource_group.bucket.id }
output "storage_account_id" { value = azurerm_storage_account.bucket.id }
output "container_id" { value = azurerm_storage_container.bucket.id }
output "storage_account_name" { value = azurerm_storage_account.bucket.name }
output "primary_access_key" { value = azurerm_storage_account.bucket.primary_access_key}
