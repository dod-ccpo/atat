

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



locals {
  key_path        = "config"
  authorized_keys = fileset(local.key_path, "*.pub")
}



resource "azurerm_kubernetes_cluster" "k8s_bastion" {


  name                    = "${var.name}-${var.environment}-bastion-k8s"
  location                = var.region
  resource_group_name     = var.rg
  dns_prefix              = "atat-aks-bastion"
  private_cluster_enabled = "true"
  node_resource_group = "${var.rg}-aks-node-rg"


  network_profile {

    network_plugin     = "azure"
    dns_service_ip     = "10.1.253.10"
    docker_bridge_cidr = "172.17.0.1/16"
    outbound_type      = "loadBalancer"
    service_cidr       = "10.1.253.0/26"
    load_balancer_sku  = "Standard"


  }




  role_based_access_control {

    enabled = true
  }

  addon_profile {

    oms_agent {

      enabled                    = true
      log_analytics_workspace_id = "/subscriptions/95934d54-980d-47cc-9bce-3a96bf9a2d1b/resourcegroups/cloudzero-pwdev-log-workspace/providers/microsoft.operationalinsights/workspaces/cloudzero-pwdev-log-workspace"

    }

  }

  service_principal {
    client_id     = var.bastion_aks_sp_id
    client_secret = var.bastion_aks_sp_secret
  }

  linux_profile {

    admin_username = "breakglass"
    ssh_key {
      key_data = file("${var.bastion_ssh_pub_key_path}")
    }

  }




  default_node_pool {
    name                  = "default"
    vm_size               = "Standard_B2s"
    os_disk_size_gb       = 30
    vnet_subnet_id        = azurerm_subnet.mgmt_subnet.id
    enable_node_public_ip = false # Nodes need a public IP for external resources. FIXME: Switch to NAT Gateway if its available in our subscription
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






# ansible:
# add ssh key to cluster node
# install azure cli
# configure kubectl to talk to atat
