data "azurerm_resource_group" "ops" {
  name = var.ops_resource_group_name
}

data "azurerm_container_registry" "ops" {
  name                = var.ops_container_registry_name
  resource_group_name = azurerm_resource_group.ops.name
}

resource "azurerm_resource_group" "acr" {
  name     = "${var.name}-${var.environment}-acr"
  location = var.region
}

resource "azurerm_container_registry" "acr" {
  name                = "${var.name}${var.environment}${var.pet_name}registry" # Alpha Numeric Only
  resource_group_name = azurerm_resource_group.acr.name
  location            = azurerm_resource_group.acr.location
  sku                 = var.sku
  admin_enabled       = var.admin_enabled
  #georeplication_locations = [azurerm_resource_group.acr.location, var.backup_region]



  network_rule_set {
    default_action = var.policy

    ip_rule = [
      for cidr in values(var.whitelist) : {
        action   = "Allow"
        ip_range = cidr
      }
    ]
    # Dynamic rule should work, but doesn't - See https://github.com/hashicorp/terraform/issues/22340#issuecomment-518779733
    #dynamic "ip_rule" {
    #  for_each = values(var.whitelist)
    #  content {
    #    action   = "Allow"
    #    ip_range = ip_rule.value
    #  }
    #}

    virtual_network = [
      for sub_name, sub_map in var.subnet_list : {

        action    = "Allow"
        subnet_id = sub_map.id

      }
      if sub_name == "aks"

    ]

  }

}

resource "azurerm_monitor_diagnostic_setting" "acr_diagnostic" {
  name                       = "${var.name}-${var.environment}-acr-diag"
  target_resource_id         = azurerm_container_registry.acr.id
  log_analytics_workspace_id = var.workspace_id
  log {
    category = "ContainerRegistryRepositoryEvents"
    retention_policy {
      enabled = true
    }
  }
  log {
    category = "ContainerRegistryLoginEvents"
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
