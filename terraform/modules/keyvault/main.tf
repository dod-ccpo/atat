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

resource "azurerm_key_vault_access_policy" "keyvault_k8s_policy" {
  count        = length(var.principal_id) > 0 ? 1 : 0
  key_vault_id = azurerm_key_vault.keyvault.id

  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = var.principal_id

  key_permissions = [
    "get",
  ]

  secret_permissions = [
    "get",
  ]
}

# Admin Access
resource "azurerm_key_vault_access_policy" "keyvault_admin_policy" {

  for_each     = var.admin_principals
  key_vault_id = azurerm_key_vault.keyvault.id

  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = each.value

  key_permissions = [
    "get",
    "list",
    "create",
    "update",
    "delete",
  ]

  secret_permissions = [
    "get",
    "list",
    "set",
  ]

  # backup create delete deleteissuers get getissuers import list listissuers managecontacts manageissuers purge recover restore setissuers update
  certificate_permissions = [
    "get",
    "list",
    "create",
    "import",
    "listissuers",
    "manageissuers",
    "deleteissuers",
    "backup",
    "update",
  ]
}

# App Access

resource "azurerm_key_vault_access_policy" "app_policy" {

  for_each     = var.app_principals
  key_vault_id = azurerm_key_vault.keyvault.id

  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = each.value
  application_id = each.value

  key_permissions = [
    "get",
    "list",
    "create",
    "update",
    "delete",
  ]

  secret_permissions = [
    "get",
    "list",
    "set",
  ]

  # backup create delete deleteissuers get getissuers import list listissuers managecontacts manageissuers purge recover restore setissuers update
  certificate_permissions = [
    "get",
    "list",
    "create",
    "import",
    "listissuers",
    "manageissuers",
    "deleteissuers",
    "backup",
    "update",
  ]
}



resource "azurerm_monitor_diagnostic_setting" "keyvault_diagnostic" {
  name                       = "${var.name}-${var.environment}-keyvault-diag"
  target_resource_id         = azurerm_key_vault.keyvault.id
  log_analytics_workspace_id = var.workspace_id

  log {
    category = "AuditEvent"
    enabled  = true

    retention_policy {
      enabled = true
    }
  }
  metric {
    category = "AllMetrics"

    retention_policy {
      enabled = true
    }
  }
}
