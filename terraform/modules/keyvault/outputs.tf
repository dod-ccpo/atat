output "id" {
  value = azurerm_key_vault.keyvault.id
}

output "url" {
  value = azurerm_key_vault.keyvault.vault_uri
}

output "keyvault_name" {
  value = "${var.name}-keyvault-${var.environment}"
}
