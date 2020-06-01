resource "azurerm_resource_group" "k8s" {
  name     = "${var.name}-${var.environment}-vpc"
  location = var.region
  tags = {
    environment = var.environment
    owner       = var.owner
  }
}

resource "azurerm_kubernetes_cluster" "k8s" {
  name                    = "${var.name}-${var.environment}-k8s"
  location                = azurerm_resource_group.k8s.location
  resource_group_name     = azurerm_resource_group.k8s.name
  dns_prefix              = var.k8s_dns_prefix
  private_cluster_enabled = var.private_cluster_enabled

  service_principal {
    client_id     = var.client_id
    client_secret = var.client_secret
  }

  default_node_pool {
    name                  = "default"
    vm_size               = var.k8s_node_size
    os_disk_size_gb       = 30
    vnet_subnet_id        = var.vnet_subnet_id
    enable_node_public_ip = true # Nodes need a public IP for external resources. FIXME: Switch to NAT Gateway if its available in our subscription
    enable_auto_scaling   = var.enable_auto_scaling
    max_count             = var.max_count # FIXME: if auto_scaling disabled, set to 0
    min_count             = var.min_count # FIXME: if auto_scaling disabled, set to 0
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

resource "azurerm_monitor_diagnostic_setting" "k8s_diagnostic-1" {
  name                       = "${var.name}-${var.environment}-k8s-diag"
  target_resource_id         = azurerm_kubernetes_cluster.k8s.id
  log_analytics_workspace_id = var.workspace_id
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
