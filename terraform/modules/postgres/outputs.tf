output "database_name" {

 value = "${var.name}-${var.environment}-sql"
}

output "postgres_resource_group_name" {
value= "${var.name}-${var.environment}-postgres"
}

output "admin_name" {
value = var.administrator_login
}

output "pg_user" {
value = "${var.administrator_login}@${var.name}-${var.environment}-sql"
}

output "pgpassword" {
value = var.administrator_login_password
}

output "fqdn" {
value = azurerm_postgresql_server.sql.fqdn
}

output "pgdb_name" {

value = "${var.name}-${var.environment}-staging"

}

output "app_user" {
value = "atat@${var.name}-${var.environment}-sql"
}
