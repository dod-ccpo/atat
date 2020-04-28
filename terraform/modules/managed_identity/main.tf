resource "azurerm_resource_group" "identity" {
  name     = "${var.name}-${var.environment}-${var.identity}"
  location = var.region
}

resource "azurerm_user_assigned_identity" "identity" {
  resource_group_name = azurerm_resource_group.identity.name
  location            = azurerm_resource_group.identity.location

  name = "${var.name}-${var.environment}-${var.identity}"
}

data "azurerm_subscription" "primary" {}

resource "azurerm_role_assignment" "roles" {
  count                = length(var.roles)
  scope                = data.azurerm_subscription.primary.id
  role_definition_name = var.roles[count.index]
  principal_id         = azurerm_user_assigned_identity.identity.principal_id
}
