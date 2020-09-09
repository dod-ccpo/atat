resource "azurerm_resource_group" "jump" {
  name     = "${var.bastion_subnet_rg}-bastion"
  location = var.region
}


# add mgmgt subnet

resource "azurerm_subnet" "mgmt_subnet" {

  name                 = "mgr-subnet"
  resource_group_name  = var.mgmt_subnet_rg
  virtual_network_name = var.mgmt_subnet_vpc_name
  address_prefixes     = ["${var.mgmt_subnet_cidr}"]

  enforce_private_link_endpoint_network_policies = true

  service_endpoints = ["Microsoft.KeyVault", "Microsoft.ContainerRegistry", "Microsoft.Sql"]

  delegation {
    name = "delegation"

    service_delegation {
      name    = "Microsoft.ContainerInstance/containerGroups"
      actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
    }
  }

}


resource "azurerm_network_profile" "bastion" {
  name                = "examplenetprofile"
  location            = azurerm_resource_group.jump.location
  resource_group_name = azurerm_resource_group.jump.name

  container_network_interface {
    name = "bastionnic"

    ip_configuration {
      name      = "bastionipconfig"
      subnet_id = azurerm_subnet.mgmt_subnet.id
    }
  }
}


resource "azurerm_container_group" "bastion" {
  name                = "bastion"
  location            = azurerm_resource_group.jump.location
  resource_group_name = azurerm_resource_group.jump.name
  ip_address_type     = "private"
  network_profile_id  = azurerm_network_profile.bastion.id
  os_type             = "Linux"

  container {
    name   = "hello-world"
    image  = "microsoft/aci-helloworld:latest"
    cpu    = "0.5"
    memory = "1.5"

    ports {
      port     = 443
      protocol = "TCP"
    }
  }

  container {
    name   = "sidecar"
    image  = "microsoft/aci-tutorial-sidecar"
    cpu    = "0.5"
    memory = "1.5"
  }

  tags = {
    environment = "testing"
  }
}




# add azure AzureBastion







# add aks cluster 1 node, 2vcpu 4 gb ram
