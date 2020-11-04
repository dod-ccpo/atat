output "deployment_container_registry_name" {
  value       = azurerm_container_registry.ops.name
  description = "Stores images built for this deployment through CI/CD."
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
