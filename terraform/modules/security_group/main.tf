resource "azurerm_network_security_group" "security_group" {
  name                = "${var.name}-sg-${var.environment}"
  location            = var.region
  resource_group_name = var.resource_group_name

  tags = {
    environment = var.environment
    owner       = var.owner
  }
}

resource "azurerm_network_security_rule" "rules" {
  name                        = "test123"
  priority                    = 100
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "*"
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  resource_group_name         = "${azurerm_resource_group.example.name}"
  network_security_group_name = "${azurerm_network_security_group.example.name}"
}
