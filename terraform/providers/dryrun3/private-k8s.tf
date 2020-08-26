module "private-k8s" {
  source                     = "../../modules/k8s-private"
  rg                         = module.vpc.resource_group_name
  region                     = var.region
  name                       = var.name
  environment                = var.environment
  owner                      = var.owner
  k8s_dns_prefix             = var.k8s_dns_prefix
  k8s_node_size              = "Standard_D2_v3"
  enable_auto_scaling        = true
  max_count                  = 3
  min_count                  = 3
  private_aks_sp_id          = var.private_aks_sp_id
  private_aks_sp_secret      = var.private_aks_sp_secret
  log_analytics_workspace_id = module.logs.workspace_id
  service_dns                = var.private_aks_service_dns
  docker_bridge_cidr         = var.private_aks_docker_bridge_cidr
  service_cidr               = var.private_aks_service_cidr
  subnet_cidr                = var.private_k8s_subnet_cidr
  vnet_id                    = module.vpc.id
  vpc_name                   = module.vpc.vpc_name
  aks_ssh_pub_key_path       = var.aks_ssh_pub_key_path
  aks_subnet_id              = module.vpc.subnet_list["aks"].id
  vpc_address_space          = "10.1.0.0/16"

  depends_on                 = [module.vpc,module.keyvault_reader_identity]


}
