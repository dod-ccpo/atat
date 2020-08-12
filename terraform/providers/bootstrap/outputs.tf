output "storage_account_name" { value = "${var.name}${var.environment}tfstate" }
output "resource_group_name" { value = "${var.name}-${var.environment}-${var.name}${var.environment}tfstate" }
output "container_name" {value= "tfstate" }
output "key" { value="${var.environment}.tfstate"}
