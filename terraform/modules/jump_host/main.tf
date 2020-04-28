resource "azurerm_resource_group" "jump" {
  name     = "${var.name}-${var.environment}-jump"
  location = var.region
}

resource "azurerm_public_ip" "jump" {
  name                = "${var.name}-${var.environment}-jump"
  location            = var.region
  resource_group_name = azurerm_resource_group.jump.name
  allocation_method   = "Static"

  tags = {
    environment = var.environment
    owner       = var.owner
  }
}

resource "azurerm_network_interface" "jump" {
  name                = "${var.name}-${var.environment}-jump"
  location            = azurerm_resource_group.jump.location
  resource_group_name = azurerm_resource_group.jump.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = var.subnet_id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.jump.id
  }
}

resource "azurerm_virtual_machine" "jump" {
  name                = "${var.name}-${var.environment}-jump"
  resource_group_name = azurerm_resource_group.jump.name
  location            = azurerm_resource_group.jump.location
  vm_size             = "Standard_F2"
  network_interface_ids = [
    azurerm_network_interface.jump.id,
  ]
  os_profile {
    computer_name  = "jumphost"
    admin_username = "rootuser"
  }
  os_profile_linux_config {
    disable_password_authentication = true
    ssh_keys {
      key_data = file("~/.ssh/pwdev.pub")
      path     = "/home/rootuser/.ssh/authorized_keys"
    }
  }

  storage_os_disk {
    name              = "os"
    caching           = "ReadWrite"
    managed_disk_type = "Standard_LRS"
    create_option     = "FromImage"
  }

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }
  tags = {
    owner       = var.owner
    environment = var.environment
  }
}
