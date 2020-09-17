

module "k8s" {
  source                   = "../../modules/k8s"
  region                   = var.region
  name                     = var.name
  environment              = local.environment
  owner                    = var.owner
  k8s_dns_prefix           = var.k8s_dns_prefix
  k8s_node_size            = "Standard_D2_v3"
  vnet_subnet_id           = module.vpc.subnet_list["aks"].id
  enable_auto_scaling      = true
  max_count                = var.aks_max_node_count
  min_count                = var.aks_min_node_count
  client_id                = module.aks_sp.application_id
  client_secret            = module.aks_sp.application_password
  client_object_id         = module.aks_sp.object_id
  workspace_id             = module.logs.workspace_id
  vnet_id                  = module.vpc.id
  node_resource_group      = "${var.name}-node-rg-${local.environment}"
  virtual_network          = var.virtual_network
  vnet_resource_group_name = module.vpc.resource_group_name
  aks_subnet_id            = module.vpc.subnet_list["aks"].id
  aks_route_table          = "${var.name}-aks-${local.environment}"
  depends_on               = [module.aks_sp,module.keyvault_reader_identity]


}
