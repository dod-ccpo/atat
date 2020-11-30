data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "keyvault" {
  name     = "${var.name}-keyvault-${var.environment}"
  location = var.region
}

resource "azurerm_key_vault" "keyvault" {
  name                = "${var.name}-kv-${var.environment}"
  location            = azurerm_resource_group.keyvault.location
  resource_group_name = azurerm_resource_group.keyvault.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  soft_delete_enabled = true

  sku_name = "premium"

  network_acls {
    default_action             = var.policy
    bypass                     = "AzureServices"
    virtual_network_subnet_ids = var.subnet_ids
    ip_rules                   = values(var.whitelist)
  }

  tags = {
    environment = var.environment
    owner       = var.owner
  }
}

resource "time_sleep" "wait_30_seconds" {
  depends_on = [
      azurerm_key_vault.keyvault,
      azurerm_key_vault_access_policy.keyvault_tenant_policy,
      azurerm_key_vault_access_policy.keyvault_admin_policy,
    ]

  create_duration = "30s"
}

resource "azurerm_key_vault_access_policy" "keyvault_k8s_policy" {
  count        = var.principal_id_count
  key_vault_id = azurerm_key_vault.keyvault.id

  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = var.principal_id

  key_permissions = [
    "get",
  ]

  secret_permissions = [
    "get",
  ]

  certificate_permissions = [
    "get"
  ]

}


resource "azurerm_key_vault_access_policy" "keyvault_tenant_policy" {
  for_each     = var.tenant_principals
  key_vault_id = azurerm_key_vault.keyvault.id

  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = each.value

  key_permissions = []

  secret_permissions = [
    "get",
    "list",
    "set",
    "delete"
  ]

  certificate_permissions = [
    "get"
  ]
}

# Admin Access
resource "azurerm_key_vault_access_policy" "keyvault_admin_policy" {
  for_each     = var.admin_principals
  key_vault_id = azurerm_key_vault.keyvault.id

  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = each.value

  key_permissions = [
    "create",
    "delete",
    "get",
    "list",
    "recover",
    "update",
    "restore",
  ]

  secret_permissions = [
    "get",
    "list",
    "set",
    "delete",
    "recover",
    "restore",
  ]

  # backup create delete deleteissuers get getissuers import list listissuers managecontacts manageissuers purge recover restore setissuers update
  certificate_permissions = [
    "backup",
    "create",
    "delete",
    "deleteissuers",
    "get",
    "import",
    "list",
    "listissuers",
    "manageissuers",
    "update",
    "recover",
    "restore",
  ]
}


resource "azurerm_key_vault_key" "generated" {
  count        = var.name == "cz" ? 1 : 0
  name         = "SECRET-KEY"
  key_vault_id = azurerm_key_vault.keyvault.id
  key_type     = "RSA"
  key_size     = 2048

  key_opts = [
    "decrypt",
    "encrypt",
    "sign",
    "unwrapKey",
    "verify",
    "wrapKey",
  ]

  depends_on = [time_sleep.wait_30_seconds]
}
