output "storage_account_name" { value = "${var.name}${local.environment}tfstate" }
output "resource_group_name" { value = "${var.name}-${var.name}${local.environment}tfstate-${local.environment}" }
output "container_name" { value = "tfstate" }
output "key" { value = "${local.environment}.tfstate" }
output "environment" { value = local.environment }
