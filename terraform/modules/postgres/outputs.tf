output "database_name" {

  value = "${var.name}-sql-${var.environment}"
}

output "postgres_resource_group_name" {
  value = "${var.name}-postgres-${var.environment}"
}

output "admin_name" {
  value = var.administrator_login
}

output "pg_admin_user" {
  value = "${var.administrator_login}@${var.name}-sql-${var.environment}"
}

output "pgpassword" {
  value = var.administrator_login_password
}

output "fqdn" {
  value = azurerm_postgresql_server.sql.fqdn
}

output "pgdb_name" {

  value = "${var.name}-staging-${var.environment}"

}

output "app_user" {
  value = "atat@${var.name}-sql-${var.environment}"
}
