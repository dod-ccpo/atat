
resource "azurerm_resource_group" "ops" {
  name     = "${var.name}-ops-${local.environment}"
  location = var.region
}


resource "azurerm_container_registry" "ops" {
  name                = "${var.name}opscontainerregistry${local.environment}" # Alpha Numeric Only
  resource_group_name = azurerm_resource_group.ops.name
  location            = azurerm_resource_group.ops.location
  sku                 = "Premium"
  admin_enabled       = false
  #georeplication_locations = [azurerm_resource_group.ops.location, var.backup_region]



  network_rule_set {
    default_action = "Allow"

    ip_rule = [
      for cidr_name, cidr_val in values(var.container_network_whitelist) : {
        action   = "Allow"
        ip_range = cidr_val
      }
    ]





  }

}
