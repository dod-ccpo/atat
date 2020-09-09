output "subscription_id" {
  value = "a0f587a4-2876-498d-a3d3-046cd98d5363"
}

output "tenant_id" {
  value = "b5ab0e1e-09f8-4258-afb7-fb17654bc5b3"
}

output "atat_user_password" {
  value = random_password.atat_user_password.result
}

output "atat_user_name" {
  value = module.sql.app_user
}

output "atat_database_instance_name" {
  value = "${var.name}-${var.environment}-sql"
}
output "atat_database_name" {
  value = "${var.name}_${var.environment}_${var.lifecycle_env_name}"
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

output "azure_storage_account_name" {
  value = module.task_order_bucket.storage_account_name
}

output "redis_hostname" {
  value = module.redis.hostname
}

output "redis_ssl_port" {
  value = module.redis.ssl_port
}

output "app_config_values" {

  value = {
    "AZURE-CLIENT-ID" : module.tenant_keyvault_app.application_id
    "AZURE-SECRET-KEY" : module.tenant_keyvault_app.application_password
    "AZURE-TENANT-ID" : var.tenant_id
    "MAIL-PASSWORD" : var.mailgun_api_key
    "AZURE-STORAGE-KEY" : module.task_order_bucket.primary_access_key
    "REDIS-PASSWORD" : module.redis.primary_key
    "AZURE-HYBRID-TENANT-ID" : var.azure_hybrid_tenant_id
    "AZURE-USER-OBJECT-ID" : var.azure_hybrid_user_object_id
    "AZURE-TENANT-ADMIN-PASSWORD" : var.azure_hybrid_tenant_admin_password



  }

}
