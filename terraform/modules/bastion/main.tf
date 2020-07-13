

# add AzureBastionSubnet

resource "azurerm_subnet" "azure_bastion_subnet" {



  name                                           = "AzureBastionSubnet"
  resource_group_name                            = var.bastion_subnet_rg
  virtual_network_name                           = var.bastion_subnet_vpc_name
  address_prefixes                               = ["${var.bastion_subnet_cidr}"]
  enforce_private_link_endpoint_network_policies = true




}

# add mgmgt subnet

resource "azurerm_subnet" "mgmt_subnet" {

  name                 = "mgmt-subnet"
  resource_group_name  = var.mgmt_subnet_rg
  virtual_network_name = var.mgmt_subnet_vpc_name
  address_prefixes     = ["${var.mgmt_subnet_cidr}"]

  enforce_private_link_endpoint_network_policies = true

  service_endpoints = ["Microsoft.Sql", "Microsoft.KeyVault"]


}





# add azure AzureBastion

resource "azurerm_public_ip" "bastion_ip" {
  name                = "bastion-ip"
  location            = var.region
  resource_group_name = var.rg
  allocation_method   = "Static"
  sku                 = "Standard"
}


resource "azurerm_bastion_host" "host" {
  name                = "jit-bastion"
  location            = var.region
  resource_group_name = var.rg

  ip_configuration {
    name                 = "configuration"
    subnet_id            = azurerm_subnet.azure_bastion_subnet.id
    public_ip_address_id = azurerm_public_ip.bastion_ip.id
  }
}



# add aks cluster 1 node, 2vcpu 4 gb ram


resource "azurerm_kubernetes_cluster" "k8s_bastion" {


  name                    = "${var.name}-${var.environment}-bastion-k8s"
  location                = var.region
  resource_group_name     = var.rg
  dns_prefix              = "atat-aks-bastion"
  private_cluster_enabled = "true"
  node_resource_group     = "${var.rg}-aks-node-rg"


  linux_profile {
    admin_username = "bastion"
    ssh_key {

      key_data = file("${var.bastion_ssh_pub_key_path}")
    }
  }

  network_profile {

    network_plugin     = "azure"
    dns_service_ip     = "10.254.253.10"
    docker_bridge_cidr = "172.17.0.1/16"
    outbound_type      = "loadBalancer"
    service_cidr       = "10.254.253.0/26"
    load_balancer_sku  = "Standard"


  }


  service_principal {
    client_id     = var.bastion_aks_sp_id
    client_secret = var.bastion_aks_sp_secret
  }

  addon_profile {

    oms_agent {

      enabled = true

      log_analytics_workspace_id = var.log_analytics_workspace_id

    }

  }


  default_node_pool {
    name                  = "default"
    vm_size               = "Standard_B2s"
    os_disk_size_gb       = 30
    vnet_subnet_id        = azurerm_subnet.mgmt_subnet.id
    enable_node_public_ip = false
    type                  = "AvailabilitySet"
    enable_auto_scaling   = false
    node_count            = 1
  }

  lifecycle {
    ignore_changes = [
      default_node_pool.0.node_count
    ]
  }

  tags = {
    Name        = "bastion-aks"
    environment = var.environment
    owner       = var.owner
  }
}
