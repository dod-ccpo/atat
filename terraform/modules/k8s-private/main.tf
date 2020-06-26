resource "azurerm_subnet" "private_aks_subnet" {

  name                 = "private-aks-subnet"
  resource_group_name  = var.rg
  virtual_network_name = var.vpc_name
  address_prefixes     = ["${var.subnet_cidr}"]

  enforce_private_link_endpoint_network_policies = true


  service_endpoints = ["Microsoft.Sql", "Microsoft.KeyVault"]


}


resource "azurerm_public_ip" "aks_gateway_ip" {
  name                = "private-aks-nat-gateway-publicIP"
  location            = var.region
  resource_group_name = var.rg
  allocation_method   = "Static"
  sku                 = "Standard"
  zones               = ["1"]
}

resource "azurerm_public_ip_prefix" "aks_gateway_ip_range" {
  name                = "nat-gateway-publicIPPrefix"
  location            = var.region
  resource_group_name = var.rg
  prefix_length       = 29
  zones               = ["1"]
}


resource "azurerm_nat_gateway" "aks_gateway" {
  name                    = "aks-private-gateway"
  location                = var.region
  resource_group_name     = var.rg
  public_ip_address_ids   = [azurerm_public_ip.aks_gateway_ip.id]
  public_ip_prefix_ids    = [azurerm_public_ip_prefix.aks_gateway_ip_range.id]
  sku_name                = "Standard"
  idle_timeout_in_minutes = 10
  zones                   = ["1"]
}


resource "azurerm_subnet_nat_gateway_association" "aks_gateway_aks_subnet" {
  subnet_id      = azurerm_subnet.private_aks_subnet.id
  nat_gateway_id = azurerm_nat_gateway.aks_gateway.id
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

# Default Routes
resource "azurerm_route" "local_route" {
  name                = "${var.name}-${var.environment}-default"
  resource_group_name = var.rg
  route_table_name    = azurerm_route_table.route_table.name
  address_prefix      = var.subnet_cidr
  next_hop_type       = "VnetLocal"
}

resource "azurerm_route" "internet_route" {
  name                = "${var.name}-${var.environment}-internet"
  resource_group_name = var.rg
  route_table_name    = azurerm_route_table.route_table.name
  address_prefix      = "0.0.0.0/0"
  next_hop_type       = "Internet"
}


resource "azurerm_route" "vnet_route" {
  name                = "${var.name}-${var.environment}-virtual-network"
  resource_group_name = var.rg
  route_table_name    = azurerm_route_table.route_table.name
  address_prefix      = var.vpc_address_space
  next_hop_type       = "VnetLocal"
}





#associate this w/ nsg


resource "azurerm_kubernetes_cluster" "k8s_private" {


  name                    = "${var.name}-${var.environment}-private-k8s"
  location                = var.region
  resource_group_name     = var.rg
  dns_prefix              = "atat-aks-private"
  private_cluster_enabled = true
  node_resource_group     = "${var.rg}-private-aks-node-rg"


  linux_profile {
    admin_username = "mike_papetti"
    ssh_key {

      key_data = file("${var.aks_ssh_pub_key_path}")
    }
  }

  network_profile {

    network_plugin     = "azure"
    dns_service_ip     = var.service_dns
    docker_bridge_cidr = var.docker_bridge_cidr
    outbound_type      = "userDefinedRouting"
    service_cidr       = var.service_cidr
    load_balancer_sku  = "Standard"



  }




  service_principal {
    client_id     = var.private_aks_sp_id
    client_secret = var.private_aks_sp_secret
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
    vnet_subnet_id        = azurerm_subnet.private_aks_subnet.id
    enable_node_public_ip = false
    enable_auto_scaling   = false
    node_count            = 3
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









resource "azurerm_monitor_diagnostic_setting" "k8s_private-diagnostic" {
  name                       = "${var.name}-${var.environment}-private-k8s-diag"
  target_resource_id         = azurerm_kubernetes_cluster.k8s_private.id
  log_analytics_workspace_id = var.log_analytics_workspace_id
  log {
    category = "kube-apiserver"
    retention_policy {
      enabled = true
    }
  }
  log {
    category = "kube-controller-manager"
    retention_policy {
      enabled = true
    }
  }
  log {
    category = "kube-scheduler"
    retention_policy {
      enabled = true
    }
  }
  log {
    category = "kube-audit"
    retention_policy {
      enabled = true
    }
  }
  log {
    category = "cluster-autoscaler"
    retention_policy {
      enabled = true
    }
  }
  metric {
    category = "AllMetrics"
    retention_policy {
      enabled = true
    }
  }
}
