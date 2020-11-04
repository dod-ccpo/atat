data "http" "myip" {
  url = "http://ipinfo.io/ip"
}

data "terraform_remote_state" "bootstrap_new_tenant_state" {
  backend = "local"

  config = {
    path = "../bootstrap_new_tenant/terraform.tfstate"
  }
}

locals {
  ops_sp_url_to_name           = replace(var.OPS_SP_URL, "http://", "")
  environment                  = length(var.environment) > 0 ? var.environment : random_pet.unique_id.id
  private_aks_appliance_routes = var.virtual_appliance_routes["aks-private"]
}

module "tenant_keyvault_app" {
  source = "../../modules/azure_ad"
  name   = "tenant-keyvault"
}

module "aks_sp" {
  source = "../../modules/azure_ad"
  name   = "aks-service-principal"
}

module "bastion_sp" {
  source = "../../modules/azure_ad"
  name   = "bastion-service-principal"
}

module "ops_keyvault_app" {
  source = "../../modules/azure_ad"
  name   = "ops-keyvault-sp"
}

module "bastion" {
  source                     = "../../modules/bastion"
  rg                         = "${var.name}-${random_pet.unique_id.id}-jump"
  region                     = var.region
  mgmt_subnet_rg             = module.vpc.resource_group_name
  mgmt_subnet_vpc_name       = module.vpc.vpc_name
  bastion_subnet_rg          = module.vpc.resource_group_name
  bastion_subnet_vpc_name    = module.vpc.vpc_name
  mgmt_subnet_cidr           = "10.1.250.0/24"
  bastion_subnet_cidr        = "10.1.4.0/24"
  bastion_aks_sp_secret      = module.bastion_sp.application_password
  bastion_aks_sp_id          = module.bastion_sp.application_id
  environment                = local.environment
  owner                      = var.owner
  name                       = var.name
  bastion_ssh_pub_key_path   = var.bastion_ssh_pub_key_path
  log_analytics_workspace_id = module.logs.workspace_id
  registry_password          = var.OPS_SEC
  registry_username          = var.OPS_CID
  depends_on                 = [module.vpc]
  container_registry         = "${var.name}opscontainerregistry${local.environment}.azurecr.io"
}

# Task order bucket is required to be accessible publicly by the users.
# which is why the policy here is "Allow"
module "task_order_bucket" {
  source                 = "../../modules/bucket"
  service_name           = "${local.environment}tasks"
  owner                  = var.owner
  name                   = var.name
  environment            = local.environment
  region                 = var.region
  policy                 = "Allow"
  subnet_ids             = [module.vpc.subnet_list["aks"].id]
  whitelist              = merge(var.storage_admin_whitelist, { "${data.azurerm_client_config.current.client_id}" : chomp(data.http.myip.body) })
  bucket_cors_properties = var.bucket_cors_properties
  storage_container_name = var.task_order_bucket_storage_container_name
  depends_on             = [module.vpc]
}

module "container_registry" {
  source                      = "../../modules/container_registry"
  name                        = var.name
  region                      = var.region
  environment                 = local.environment
  owner                       = var.owner
  backup_region               = var.backup_region
  policy                      = "Allow"
  subnet_ids                  = [module.vpc.subnet_list["aks"].id]
  whitelist                   = var.admin_user_whitelist
  workspace_id                = module.logs.workspace_id
  pet_name                    = random_pet.unique_id.id
  subnet_list                 = module.vpc.subnet_list
  depends_on                  = [module.vpc]
  ops_container_registry_name = "${var.name}opscontainerregistry${local.environment}"
  ops_resource_group_name     = "${var.name}-ops-${local.environment}"
}

module "keyvault_reader_identity" {
  source      = "../../modules/managed_identity"
  name        = var.name
  owner       = var.owner
  environment = local.environment
  region      = var.region
  identity    = "${var.name}-${local.environment}-vault-reader"
  roles       = ["Reader", "Managed Identity Operator"]
}

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
  depends_on               = [module.aks_sp, module.keyvault_reader_identity]
}

module "keyvault" {
  source             = "../../modules/keyvault"
  name               = "cz"
  region             = var.region
  owner              = var.owner
  environment        = local.environment
  tenant_id          = var.tenant_id
  principal_id_count = 1
  principal_id       = module.keyvault_reader_identity.principal_id
  admin_principals   = merge(var.admin_users, { "${local.ops_sp_url_to_name}" : var.OPS_OID })
  tenant_principals  = {}
  policy             = "Deny"
  subnet_ids         = [module.vpc.subnet_list["aks"].id, module.bastion.mgmt_subnet_id, var.deployment_subnet_id]
  whitelist          = var.admin_user_whitelist
  workspace_id       = module.logs.workspace_id
  tls_cert_path      = var.tls_cert_path
}

module "tenant_keyvault" {
  source            = "../../modules/keyvault"
  name              = "tenants"
  region            = var.region
  owner             = var.owner
  environment       = local.environment
  tenant_id         = var.tenant_id
  principal_id      = ""
  tenant_principals = { "${module.tenant_keyvault_app.name}" = "${module.tenant_keyvault_app.sp_object_id}" }
  admin_principals  = {}
  policy            = "Deny"
  subnet_ids        = [module.vpc.subnet_list["aks"].id]
  whitelist         = var.admin_user_whitelist
  workspace_id      = module.logs.workspace_id
}

module "logs" {
  source            = "../../modules/log_analytics"
  owner             = var.owner
  environment       = local.environment
  region            = var.region
  name              = var.name
  retention_in_days = 365
}

resource "random_password" "pg_root_password" {
  length           = 15
  min_numeric      = 0
  special          = false
  override_special = "!"
}

resource "random_password" "atat_user_password" {
  length           = 15
  min_numeric      = 0
  special          = false
  override_special = "!"
}

module "sql" {
  source                       = "../../modules/postgres"
  name                         = var.name
  owner                        = var.owner
  environment                  = local.environment
  region                       = var.region
  subnet_id                    = module.vpc.subnet_list["aks"].id
  administrator_login          = var.postgres_admin_login
  administrator_login_password = random_password.pg_root_password.result
  workspace_id                 = module.logs.workspace_id
  operator_ip                  = chomp(data.http.myip.body)
  deployment_subnet_id         = var.deployment_subnet_id
}

module "private-k8s" {
  source                     = "../../modules/k8s-private"
  rg                         = module.vpc.resource_group_name
  region                     = var.region
  name                       = var.name
  environment                = local.environment
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
  aks_subnet_id              = module.vpc.subnet_list["aks-private"].id
  vpc_address_space          = "10.1.0.0/16"

  depends_on = [module.vpc, module.keyvault_reader_identity]
}

module "private-aks-firewall" {

  source              = "../../modules/azure_firewall"
  resource_group_name = module.vpc.resource_group_name
  location            = var.region
  name                = var.name
  environment         = local.environment
  subnet_id           = module.vpc.subnet_list["AzureFirewallSubnet"].id
  az_fw_ip            = module.vpc.fw_ip_address_id
}

module "redis" {
  source       = "../../modules/redis"
  owner        = var.owner
  environment  = local.environment
  region       = var.region
  name         = var.name
  subnet_id    = module.vpc.subnet_list["redis"].id
  sku_name     = "Premium"
  family       = "P"
  workspace_id = module.logs.workspace_id
  pet_name     = random_pet.unique_id.id
}

module "operator_keyvault" {
  source            = "../../modules/keyvault"
  name              = "ops"
  region            = var.region
  owner             = var.owner
  environment       = local.environment
  tenant_id         = var.tenant_id
  principal_id      = ""
  admin_principals  = merge(var.admin_users, { "TerraformOperator" = "${var.OPS_OID}" })
  tenant_principals = { "${module.ops_keyvault_app.name}" = "${module.ops_keyvault_app.sp_object_id}" }
  policy            = "Deny"
  subnet_ids        = [module.vpc.subnet_list["aks"].id, module.bastion.mgmt_subnet_id, var.deployment_subnet_id]
  whitelist         = var.admin_user_whitelist
  workspace_id      = module.logs.workspace_id
}

module "vpc" {
  source                         = "../../modules/vpc/"
  environment                    = local.environment
  region                         = var.region
  virtual_network                = var.virtual_network
  networks                       = var.networks
  route_tables                   = var.route_tables
  owner                          = var.owner
  name                           = var.name
  dns_servers                    = var.dns_servers
  service_endpoints              = var.service_endpoints
  custom_routes                  = var.routes
  virtual_appliance_routes       = "${var.virtual_appliance_routes["aks-private"]},${module.private-aks-firewall.ip_config[0].private_ip_address}"
  virtual_appliance_route_tables = var.virtual_appliance_route_tables
}
