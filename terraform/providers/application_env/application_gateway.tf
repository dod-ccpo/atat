resource "azurerm_resource_group" "gateway_rg" {
  name     = "cloudzero-${var.environment}-gateway-rg"
  location = "East US"
}

locals {
  backend_address_pool_name      = "${azurerm_virtual_network.vpc.name}-beap"
  frontend_port_name             = "${azurerm_virtual_network.vpc.name}-feport"
  frontend_ip_configuration_name = "${azurerm_virtual_network.vpc.name}-feip"
  http_setting_name              = "${azurerm_virtual_network.vpc.name}-be-htst"
  listener_name                  = "${azurerm_virtual_network.vpc.name}-httplstn"
  request_routing_rule_name      = "${azurerm_virtual_network.vpc.name}-rqrt"
  redirect_configuration_name    = "${azurerm_virtual_network.vpc.name}-rdrcfg"
}

resource "azurerm_application_gateway" "network" {
  name                = "cloudzero-${var.environment}-gateway"
  resource_group_name = azurerm_resource_group.gateway_rg.name
  location            = azurerm_resource_group.gateway_rg.location

  sku {
    name     = "Standard_Small"
    tier     = "Standard"
    capacity = 2
  }

  gateway_ip_configuration {
    name      = "my-gateway-ip-configuration"
    subnet_id = azurerm_subnet.subnet.id
  }

  frontend_port {
    name = local.frontend_port_name
    port = 80
  }

  frontend_ip_configuration {
    name                 = local.frontend_ip_configuration_name
    public_ip_address_id = azurerm_public_ip.az_fw_ip.id
  }

  backend_address_pool {
    name = local.backend_address_pool_name
  }

  backend_http_settings {
    name                  = local.http_setting_name
    cookie_based_affinity = "Disabled"
    path                  = "/path1/"
    port                  = 80
    protocol              = "Http"
    request_timeout       = 60
  }

  http_listener {
    name                           = local.listener_name
    frontend_ip_configuration_name = local.frontend_ip_configuration_name
    frontend_port_name             = local.frontend_port_name
    protocol                       = "Http"

    custom_error_configuration {
        status_code = "HttpStatus502"
        custom_error_page_url = "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502"
    }
  }

  request_routing_rule {
    name                       = local.request_routing_rule_name
    rule_type                  = "Basic"
    http_listener_name         = local.listener_name
    backend_address_pool_name  = local.backend_address_pool_name
    backend_http_settings_name = local.http_setting_name
  }
}
