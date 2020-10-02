resource "azurerm_resource_group" "sql" {
  name     = "${var.name}-postgres-${var.environment}"
  location = var.region
}

resource "azurerm_postgresql_server" "sql" {
  name                = "${var.name}-sql-${var.environment}"
  location            = azurerm_resource_group.sql.location
  resource_group_name = azurerm_resource_group.sql.name

  sku_name = var.sku_name


  storage_mb                   = var.storage_mb
  backup_retention_days        = var.storage_backup_retention_days
  geo_redundant_backup_enabled = var.storage_geo_redundant_backup
  auto_grow_enabled            = var.storage_auto_grow


  administrator_login          = var.administrator_login
  administrator_login_password = var.administrator_login_password
  version                      = var.postgres_version
  ssl_enforcement_enabled      = var.ssl_enforcement

}

resource "azurerm_postgresql_virtual_network_rule" "sql" {
  name                                 = "${var.name}-rule-${var.environment}"
  resource_group_name                  = azurerm_resource_group.sql.name
  server_name                          = azurerm_postgresql_server.sql.name
  subnet_id                            = var.subnet_id
  ignore_missing_vnet_service_endpoint = true
}

resource "azurerm_postgresql_firewall_rule" "operator" {
name                                 = "deployment-subnet-${var.environment}"
resource_group_name                  = azurerm_resource_group.sql.name
server_name                          = azurerm_postgresql_server.sql.name
subnet_id                            = var.deployment_subnet_id
ignore_missing_vnet_service_endpoint = true
}


resource "azurerm_postgresql_firewall_rule" "operator" {
  name                = "office"
  resource_group_name = azurerm_resource_group.sql.name
  server_name         = azurerm_postgresql_server.sql.name
  start_ip_address    = var.operator_ip
  end_ip_address      = var.operator_ip
}





resource "azurerm_postgresql_database" "db" {
  name                = "${var.name}-atat-${var.environment}"
  resource_group_name = azurerm_resource_group.sql.name
  server_name         = azurerm_postgresql_server.sql.name
  charset             = "UTF8"
  collation           = "en-US"
}
