resource "azurerm_subnet" "private_aks_subnet" {

   name                 = "${var.name}-private-aks-subnet-${var.environment}"
   resource_group_name  = var.rg
   virtual_network_name = var.vpc_name
   address_prefixes     = ["${var.subnet_cidr}"]


   service_endpoints = ["Microsoft.Sql", "Microsoft.KeyVault","Microsoft.Storage","Microsoft.ContainerRegistry"]
 }

 resource "azurerm_route_table" "route_table" {
   name                = "${var.name}-${var.environment}-private-aks"
   location            = var.region
   resource_group_name = var.rg
 }



 resource "azurerm_subnet_route_table_association" "route_table" {

   subnet_id      = azurerm_subnet.private_aks_subnet.id
   route_table_id = azurerm_route_table.route_table.id
 }



 resource "azurerm_route" "vnet_route" {
    name                = "private-k8s-${var.name}-virtual-network-${var.environment}"
    resource_group_name = var.rg
    route_table_name    = azurerm_route_table.route_table.name
    address_prefix      = var.vpc_address_space
    next_hop_type       = "VnetLocal"
  }

  resource "azurerm_route" "internet" {
     name                = "private-k8s-${var.name}-internet-${var.environment}"
     resource_group_name = var.rg
     route_table_name    = azurerm_route_table.route_table.name
     address_prefix      = "0.0.0.0/0"
     next_hop_type       = "Internet"
   }



#associate this w/ nsg


resource "azurerm_kubernetes_cluster" "k8s_private" {


  name                    = "${var.name}-private-k8s-${var.environment}"
  location                = var.region
  resource_group_name     = var.rg
  dns_prefix              = "atat-aks-private"
  private_cluster_enabled = var.private_cluster_enabled
  node_resource_group     = "${var.rg}-private-aks-node-rgs"

  depends_on = [azurerm_subnet_route_table_association.route_table]


  addon_profile {
    azure_policy {
     enabled =true
    }

    oms_agent {

    enabled = true
    log_analytics_workspace_id = var.log_analytics_workspace_id

    }



  }




  network_profile {

    network_plugin     = "azure"
    dns_service_ip     = var.service_dns
    docker_bridge_cidr = var.docker_bridge_cidr
    outbound_type      = "loadBalancer"
    service_cidr       = var.service_cidr
    load_balancer_sku  = "Standard"


  }


  service_principal {
    client_id     = var.private_aks_sp_id
    client_secret = var.private_aks_sp_secret
  }

  default_node_pool {
    name                  = "default"
    vm_size               = "Standard_B2s"
    os_disk_size_gb       = 30
    vnet_subnet_id        = azurerm_subnet.private_aks_subnet.id
    enable_node_public_ip = false
    enable_auto_scaling   = false
    node_count            = 1
  }

  lifecycle {
    ignore_changes = [
      default_node_pool.0.node_count
    ]
  }

  tags = {
    Name        = "private-aks-atat"
    environment = var.environment
    owner       = var.owner
  }
}
