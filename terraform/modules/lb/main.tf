resource "azurerm_resource_group" "lb" {
  name     = "${var.name}-${var.environment}-lb"
  location = var.region
}

resource "azurerm_public_ip" "lb" {
  name                = "${var.name}-${var.environment}-ip"
  location            = var.region
  resource_group_name = azurerm_resource_group.lb.name
  allocation_method   = "Static"
}

resource "azurerm_lb" "lb" {
  name                = "${var.name}-${var.environment}-lb"
  location            = var.region
  resource_group_name = azurerm_resource_group.lb.name

  frontend_ip_configuration {
    name                 = "${var.name}-${var.environment}-ip"
    public_ip_address_id = azurerm_public_ip.lb.id
  }

  tags = {
    owner       = var.owner
    environment = var.environment
  }
}
