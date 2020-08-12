
resource "azurerm_kubernetes_cluster" "k8s" {
  name                    = "${var.name}-${var.environment}-k8s"
  location                = var.region
  resource_group_name     = var.vnet_resource_group_name
  dns_prefix              = var.k8s_dns_prefix
  private_cluster_enabled = var.private_cluster_enabled
  node_resource_group     = var.node_resource_group
  #enable_pod_security_policy = true


  role_based_access_control {
    enabled = true
  }

  service_principal {
    client_id     = var.client_id
    client_secret = var.client_secret
  }



  default_node_pool {
    name            = "default"
    vm_size         = var.k8s_node_size
    os_disk_size_gb = 30
    vnet_subnet_id  = var.vnet_subnet_id
    #enable_node_public_ip = true # Nodes need a public IP for external resources. FIXME: Switch to NAT Gateway if its available in our subscription
    enable_auto_scaling = var.enable_auto_scaling
    max_count           = var.max_count # FIXME: if auto_scaling disabled, set to 0
    min_count           = var.min_count # FIXME: if auto_scaling disabled, set to 0
  }

  lifecycle {
    ignore_changes = [
      default_node_pool.0.node_count
    ]
  }

  tags = {
    environment = var.environment
    owner       = var.owner
  }
}
