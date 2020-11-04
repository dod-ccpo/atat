# Postgres
resource "azurerm_resource_group" "sql" {
  name     = "${var.deployment_namespace}-postgres"
  location = var.deployment_location
}

resource "random_password" "pg_root_password" {
  length           = 16
  min_numeric      = 1
  special          = true
  override_special = "!"
}

resource "azurerm_postgresql_server" "sql" {
  name                = "${var.deployment_namespace}-sql"
  location            = azurerm_resource_group.sql.location
  resource_group_name = azurerm_resource_group.sql.name
  sku_name            = "GP_Gen5_2"

  storage_mb                   = "5120"
  backup_retention_days        = "7"
  geo_redundant_backup_enabled = false
  auto_grow_enabled            = true

  administrator_login          = "clouzero_pg_admin"
  administrator_login_password = random_password.pg_root_password.result
  version                      = "10"
  ssl_enforcement_enabled      = true

}

resource "azurerm_postgresql_virtual_network_rule" "allow_aks_subnet" {
  name                                 = "allow-aks-subnet-rule"
  resource_group_name                  = azurerm_resource_group.sql.name
  server_name                          = azurerm_postgresql_server.sql.name
  subnet_id                            = azurerm_subnet.aks.id
  ignore_missing_vnet_service_endpoint = true
}

resource "azurerm_postgresql_virtual_network_rule" "allow_deployment_subnet" {
  name                                 = "allow-deployment-subnet-rule"
  resource_group_name                  = azurerm_resource_group.sql.name
  server_name                          = azurerm_postgresql_server.sql.name
  subnet_id                            = local.deployment_subnet_id
  ignore_missing_vnet_service_endpoint = true
}

resource "azurerm_postgresql_virtual_network_rule" "allow_management_subnet" {
  name                                 = "allow-management-subnet-rule"
  resource_group_name                  = azurerm_resource_group.sql.name
  server_name                          = azurerm_postgresql_server.sql.name
  subnet_id                            = azurerm_subnet.mgmt_subnet.id
  ignore_missing_vnet_service_endpoint = true
}

resource "azurerm_postgresql_firewall_rule" "operator" {
  name                = "operator"
  resource_group_name = azurerm_resource_group.sql.name
  server_name         = azurerm_postgresql_server.sql.name
  start_ip_address    = chomp(data.http.myip.body)
  end_ip_address      = chomp(data.http.myip.body)
}

resource "azurerm_postgresql_database" "db" {
  name                = "${var.deployment_namespace}-atat"
  resource_group_name = azurerm_resource_group.sql.name
  server_name         = azurerm_postgresql_server.sql.name
  charset             = "UTF8"
  collation           = "en-US"
}
