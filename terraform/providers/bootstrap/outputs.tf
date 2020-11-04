output "operations_container_registry_name" {
  value       = local.operations_container_registry_name
  description = "The name of the container registry which holds long-lived base images at the tenant level."
}

output "operations_container_registry_login_server" {
  value       = local.operations_container_registry_login_server
  description = "The URL that can be used to log into the container registry which holds long-lived base images at the tenant level."
}

output "operations_resource_group_name" {
  value       = local.operations_resource_group_name
  description = "Resource group containing all operations resources."
}

output "deployment_storage_account_name" {
  value       = module.tf_state.storage_account_name
  description = "Holds the terraform state for this deployment."
}

output "deployment_storage_account_container_key" {
  value       = "tfstate"
  description = "TODO(jesse) This is a hardcoded value, review this."
}

output "deployment_storage_account_container_name" {
  value       = local.operations_storage_account_name
  description = "The name of the state container within the deployment storage account."
}

output "deployment_resource_group_name" {
  value       = azurerm_resource_group.ops.name
  description = "Resource group for managing operations resources for this deployment."
}

output "operations_deployment_subnet_id" {
  value = local.operations_deployment_subnet_id
  description = "ID of the subnet all subsequent resources are deployed into."
}
