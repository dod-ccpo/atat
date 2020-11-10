# output "subscription_id" {
#   value = var.azure_subscription_id
# }

# output "tenant_id" {
#   value = "b5ab0e1e-09f8-4258-afb7-fb17654bc5b3"
# }

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

output "app_config_values" {
  value = {
    "AZURE-CLIENT-ID" : module.tenant_keyvault_app.application_id
    "AZURE-SECRET-KEY" : module.tenant_keyvault_app.application_password
    # "AZURE-TENANT-ID" : var.tenant_id
    # "MAIL-PASSWORD" : var.mailgun_smtp_password
    "AZURE-STORAGE-KEY" : module.task_order_bucket.primary_access_key
    "REDIS-PASSWORD" : module.redis.primary_key
    # "AZURE-HYBRID-TENANT-ID" : var.azure_hybrid_tenant_id
    # "AZURE-USER-OBJECT-ID" : var.azure_hybrid_user_object_id
    # "AZURE-TENANT-ADMIN-PASSWORD" : var.azure_hybrid_tenant_admin_password
    "REDIS-PASSWORD" : module.redis.primary_key
    # "AZURE-BILLING-ACCOUNT-NAME" : var.AZURE-BILLING-ACCOUNT-NAME
    # "AZURE-BILLING-PROFILE-ID" : var.AZURE-BILLING-PROFILE-ID
    # "AZURE-INVOICE-SECTION-ID" : var.AZURE-INVOICE-SECTION-ID
    # "SAML-IDP-CERT" : ""
    # "dhparam4096" : var.dhparam4096
    "PGPASSWORD" : random_password.atat_user_password.result
    "AZURE-VAULT-URL" : module.tenant_keyvault.url
    # "AZURE-SUBSCRIPTION-CREATION-CLIENT-ID" : var.AZURE_SUBSCRIPTION_CREATION_CLIENT_ID
    # "AZURE-SUBSCRIPTION-CREATIONSECRET" : var.AZURE_SUBSCRIPTION_CREATION_SECRET
    # "AZURE-TENANT-ADMIN-USERNAME" : var.AZURE_TENANT_ADMIN_USERNAME
    # "AZURE-TENANT-ID" : var.AZURE_TENANT_ID
    # "AZURE-USER-OBJECT-ID" : var.AZURE_USER_OBJECT_ID
    # "CSP" : var.CSP
    # "AZURE-HYBRID-REPORTING-CLIENT-ID" : var.AZURE_HYBRID_REPORTING_CLIENT_ID
    # # "AZURE-HYBRID-REPORTING-SECRET" : var.AZURE_HYBRID_REPORTING_SECRET
  }
}

# output "circle_ci_api_key" {
#   value = var.circle_ci_api_key
# }

output "ops_container_registry_name" {
  value = module.container_registry.ops_container_registry_name
}

# output "environment" {
#   value = var.deployment_namespace
# }
