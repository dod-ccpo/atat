output "subscription_id" {
  value = data.azurerm_client_config.azure_client.subscription_id
}

output "tenant_id" {
  value = data.azurerm_client_config.azure_client.tenant_id
}

output "atat_user_password" {
  value = random_password.atat_user_password.result
}

output "atat_user_name" {
  value = module.sql.app_user
}

output "atat_database_instance_name" {
  value = "${var.name}-sql-${var.deployment_namespace}"
}

output "atat_database_name" {
  value = "${var.name}_${var.deployment_namespace}_${var.lifecycle_env_name}"
}

output "postgres_resource_group_name" {
  value = module.sql.postgres_resource_group_name
}

output "postgres_root_password" {
  value = random_password.pg_root_password.result
}

output "postgres_root_user_name" {
  value = module.sql.pg_admin_user
}

output pg_host {
  value = module.sql.fqdn
}

output pg_server_name {
  value = module.sql.database_name
}

output aks_sp_id {
  value = module.aks_sp.application_id
}

output aks_sp_oid {
  value = module.aks_sp.object_id
}

output aks_sp_secret {
  value = module.aks_sp.application_password
}

output "operator_keyvault_url" {
  value = module.operator_keyvault.url
}

output "ops_keyvault_sp_client_id" {
  value = module.ops_keyvault_app.application_id
}

output "ops_keyvault_sp_object_id" {
  value = module.ops_keyvault_app.sp_object_id
}

output "ops_keyvault_sp_secret" {
  value = module.ops_keyvault_app.service_principal_password
}

output "application_keyvault_name" {
  value = module.keyvault.keyvault_name
}

output "application_keyvault_url" {
  value = module.keyvault.url
}

output "operator_keyvault_name" {
  value = module.operator_keyvault.keyvault_name
}

output "subnets" {
  value = module.vpc.subnet_list
}

output "container_registry_name" {
  value = module.container_registry.container_registry_name
}

output "keyvault_reader_client_id" {
  value = module.keyvault_reader_identity.client_id
}

output "keyvault_reader_id" {
  value = module.keyvault_reader_identity.id
}

output "azure_storage_account_name" {
  value = module.task_order_bucket.storage_account_name
}

output "redis_hostname" {
  value = module.redis.hostname
}

output "redis_ssl_port" {
  value = module.redis.ssl_port
}

output "vnet_id" {
  value = module.vpc.id
}

output "ops_container_registry_name" {
  value = module.container_registry.ops_container_registry_name
}

output "environment" {
  value = var.deployment_namespace
}
