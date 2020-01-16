data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "keyvault" {
  name     = "${var.name}-${var.environment}-keyvault"
  location = var.region
}

resource "azurerm_key_vault" "keyvault" {
  name                = "${var.name}-${var.environment}-keyvault"
  location            = azurerm_resource_group.keyvault.location
  resource_group_name = azurerm_resource_group.keyvault.name
  tenant_id           = data.azurerm_client_config.current.tenant_id

  sku_name = "premium"

  tags = {
    environment = var.environment
    owner       = var.owner
  }
}

resource "azurerm_key_vault_access_policy" "keyvault" {
  key_vault_id = azurerm_key_vault.keyvault.id

  tenant_id = "b5ab0e1e-09f8-4258-afb7-fb17654bc5b3"
  object_id = "ca8cfc48-9995-4973-a8cc-6c7f755e84de"

  key_permissions = [
    "get",
    "list",
    "create",
  ]

  secret_permissions = [
    "get",
    "list",
    "set",
  ]
}

