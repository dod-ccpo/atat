resource "azurerm_resource_group" "k8s" {
  name     = "${var.name}-${var.environment}-k8s"
  location = var.region
}

resource "azurerm_template_deployment" "main" {
  name                = "${var.name}-${var.environment}-aks-ARM"
  resource_group_name = azurerm_resource_group.k8s.name

  template_body = file("${path.module}/arm/template.json")

  deployment_mode = "Incremental"

  parameters = {
    resourceName                 = "${var.name}-${var.environment}-k8s"
    resourceGroup                = azurerm_resource_group.k8s.name
    location                     = var.region
    dnsPrefix                    = var.k8s_dns_prefix
    osDiskSizeGB                 = var.os_disk_size_gb
    agentVMSize                  = var.k8s_node_size
    minAgentCount                = var.min_count
    maxAgentCount                = var.max_count
    agentCount                   = var.node_count
    servicePrincipalClientId     = var.client_id
    servicePrincipalClientSecret = var.client_secret
    networkPlugin                = var.k8s_network_plugin
    kubernetesVersion            = var.k8s_version
    enableAutoScaling            = var.enable_auto_scaling
    enablePrivateCluster         = var.enable_private_cluster
    enableRBAC                   = var.enable_rbac
    vmssNodePool                 = var.vmss_node_pool
    principalId                  = var.principal_object_id
    vnetSubnetID                 = var.vnet_subnet_id
    omsWorkspaceID               = var.workspace_id
    serviceCidr                  = var.service_cidr
    dnsServiceIP                 = var.dns_service_ip
    dockerBridgeCidr             = var.docker_bridge_cidr
    environment                  = var.environment
    owner                        = var.owner
  }
}
