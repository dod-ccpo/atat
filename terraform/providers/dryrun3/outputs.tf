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
  value = "${var.name}_${var.environment}_${var.dev_env_name}"
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

output "subnets" {
  value = module.vpc.subnet_list
}
