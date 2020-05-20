

# add AzureBastionSubnet


resource "azurerm_subnet" "bastion_subnet" {



  name                 = "AzureBastionSubnet"
  resource_group_name  = var.bastion_subnet_rg
  virtual_network_name = var.bastion_subnet_vpc_name
  address_prefix       = var.bastion_subnet_cidr


}


# add mgmgt subnet

resource "azurerm_subnet" "mgmt_subnet" {



  name                 = "management-subnet"
  resource_group_name  = var.mgmt_subnet_rg
  virtual_network_name = var.mgmt_subnet_vpc_name
  address_prefix       = var.mgmt_subnet_cidr


}

# add bastion public ip

resource "azurerm_public_ip" "bastion_pub_ip" {
  name                = "cloudzero-pwdev-network-bastion-ip"
  location            = var.region
  resource_group_name = var.rg
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = {
    Name        = "aks-bastion"
    environment = "Bastion"
  }
}



# add azure AzureBastion

resource "azurerm_bastion_host" "aks_bastion" {
  name                = "azure-aks-bastion"
  location            = var.region
  resource_group_name = var.rg

  ip_configuration {
    name                 = "IpConf"
    subnet_id            = azurerm_subnet.bastion_subnet.id
    public_ip_address_id = azurerm_public_ip.bastion_pub_ip.id
  }

  tags = {

    Name = "aks-bastion"

  }
}


# add aks cluster 1 node, 2vcpu 4 gb ram


# ansible:
# add ssh key to cluster node
# install azure cli
# configure kubectl to talk to atat
