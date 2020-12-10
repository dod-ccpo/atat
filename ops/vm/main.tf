provider "azurerm" {
  version = "~>2.0"
  features {}
}

resource "azurerm_resource_group" "vm_resource_group" {
  name     = var.resource_group
  location = var.region

}

resource "azurerm_virtual_network" "vm_vnet" {
  name                = var.vnet
  address_space       = ["10.2.0.0/24"]
  location            = var.region
  resource_group_name = azurerm_resource_group.vm_resource_group.name
}

resource "azurerm_subnet" "vm_subnet" {
  name                 = var.subnet
  resource_group_name  = azurerm_resource_group.vm_resource_group.name
  virtual_network_name = azurerm_virtual_network.vm_vnet.name
  address_prefixes     = ["10.2.0.0/24"]
}

resource "azurerm_public_ip" "vm_publicip" {
  name                = "${var.vm_name}-ip"
  location            = var.region
  resource_group_name = azurerm_resource_group.vm_resource_group.name
  allocation_method   = "Static"
}

resource "azurerm_network_security_group" "vm_nsg" {
  name                = "${var.vm_name}-nsg"
  location            = var.region
  resource_group_name = azurerm_resource_group.vm_resource_group.name

  security_rule {
    name                       = "SSH"
    priority                   = 300
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "TCP"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  security_rule {
    name                       = "RDP"
    priority                   = 320
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "TCP"
    source_port_range          = "*"
    destination_port_range     = "3389"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_network_interface" "vm_nic" {
  name                = "${var.vm_name}-nic"
  location            = var.region
  resource_group_name = azurerm_resource_group.vm_resource_group.name

  ip_configuration {
    name                          = "ipconfig1"
    subnet_id                     = azurerm_subnet.vm_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.vm_publicip.id
  }
}

resource "azurerm_network_interface_security_group_association" "nic_nsg_assoc" {
  network_interface_id      = azurerm_network_interface.vm_nic.id
  network_security_group_id = azurerm_network_security_group.vm_nsg.id
}

resource "random_password" "vm_user_password" {
  length           = 16
  min_numeric      = 1
  special          = false
  override_special = "!"
}

data "template_cloudinit_config" "config" {
  gzip          = true
  base64_encode = true
  part {
    content_type = "text/cloud-config"
    content      = templatefile("${path.module}/cloud_config.yml", { username = var.username })

  }
}

resource "azurerm_linux_virtual_machine" "vm" {
  name                  = var.vm_name
  location              = var.region
  resource_group_name   = azurerm_resource_group.vm_resource_group.name
  network_interface_ids = [azurerm_network_interface.vm_nic.id]
  size                  = "Standard_DS1_v2"
  custom_data           = data.template_cloudinit_config.config.rendered

  os_disk {
    name                 = "${var.vm_name}-disk"
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
    disk_size_gb         = 30
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  computer_name                   = var.vm_name
  admin_username                  = var.username
  admin_password                  = random_password.vm_user_password.result
  disable_password_authentication = false

}
