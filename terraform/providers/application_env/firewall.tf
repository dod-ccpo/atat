# azure_firewall_subnet
resource "azurerm_subnet" "azure_firewall" {
  name = "AzureFirewallSubnet"
  resource_group_name = azurerm_resource_group.vpc.name
  virtual_network_name = azurerm_virtual_network.vpc.name
  address_prefixes = ["10.1.4.0/24"]
  service_endpoints = []
}

resource "azurerm_route_table" "azure_firewall" {
  name = "${var.name}-fw-${var.deployment_namespace}"
  location = azurerm_resource_group.vpc.location
  resource_group_name = azurerm_resource_group.vpc.name
}

resource "azurerm_subnet_route_table_association" "azure_firewall" {
  subnet_id = azurerm_subnet.azure_firewall.id
  route_table_id = azurerm_route_table.azure_firewall.id
}

resource "azurerm_route" "firewall_to_internet" {
  name = "default"
  resource_group_name = azurerm_resource_group.vpc.name
  route_table_name = azurerm_route_table.azure_firewall.name
  address_prefix = "0.0.0.0/0"
  next_hop_type = "Internet"
}

resource "azurerm_route" "fw_route_egress" {
   name                   = "vnetlocal"
   resource_group_name    = azurerm_resource_group.vpc.name
   route_table_name       = azurerm_route_table.azure_firewall.name
   address_prefix         = "10.1.0.0/16"
   next_hop_type          = "VnetLocal"
 }

resource "azurerm_public_ip" "firewall_ip" {
  name                = "az-firewall-${var.deployment_namespace}"
  location            = var.deployment_location
  resource_group_name = azurerm_resource_group.vpc.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_firewall" "fw" {
  name                = "az-firewall-${var.deployment_namespace}"
  location            = var.deployment_location
  resource_group_name = azurerm_resource_group.vpc.name
  ip_configuration {
    name                 = "configuration"
    subnet_id            = azurerm_subnet.azure_firewall.id
    public_ip_address_id = azurerm_public_ip.firewall_ip.id
  }
}

resource "azurerm_firewall_policy" "enable_dns_proxy" {
  name = "fw-policy-${var.deployment_namespace}"
  resource_group_name = azurerm_resource_group.vpc.name
  location            = var.deployment_location
  dns {
    proxy_enabled = true
  }
}

resource "azurerm_firewall_nat_rule_collection" "dnat_tolb" {
  name                = "to_aks"
  azure_firewall_name = azurerm_firewall.fw.name
  resource_group_name = azurerm_resource_group.vpc.name
  priority            = 100
  action              = "Dnat"

  rule {
    name = "tok8slb"
    source_addresses = [
      "*",
    ]
    destination_ports = [
      "443",
    ]
    destination_addresses = [
      azurerm_public_ip.firewall_ip.ip_address
    ]
    translated_port    = 443
    translated_address = var.aks_internal_lb_ip
    protocols = [
      "TCP"
    ]
  }
  timeouts {
    create = "30h"
    update = "30h"
    read   = "30h"
    delete = "30h"
  }
}

resource "azurerm_firewall_nat_rule_collection" "dnat_to_maint_page" {
  name                = "to_maint_page"
  azure_firewall_name = azurerm_firewall.fw.name
  resource_group_name = azurerm_resource_group.vpc.name
  priority            = 110
  action              = "Dnat"

  rule {
    name = "maintenancepage"
    source_addresses = [
      "*",
    ]
    destination_ports = [
      "443",
    ]
    destination_addresses = [
      azurerm_public_ip.firewall_ip.ip_address
    ]
    translated_port    = 443
    translated_address = var.maintenance_page_ip
    protocols = [
      "TCP"
    ]
  }
}

resource "azurerm_firewall_network_rule_collection" "natsourcedest" {
  name                = "vnetall"
  azure_firewall_name = azurerm_firewall.fw.name
  resource_group_name = azurerm_resource_group.vpc.name
  priority            = 102
  action              = "Allow"
  rule {
    name             = "vnetall"
    protocols = [ "Any" ]
    source_addresses = ["*"]
    destination_addresses = ["*"]
    destination_ports = [ "*" ]
  }
}

resource "azurerm_firewall_network_rule_collection" "api" {
 name = "api"
 azure_firewall_name = azurerm_firewall.fw.name
 resource_group_name = azurerm_resource_group.vpc.name
 priority = 100
 action   = "Allow"
  rule {
      name = "apiudp"
      source_addresses = ["*"]
      destination_addresses = ["AzureCloud.${var.region}"]
      destination_ports = [1194]
      protocols = ["UDP"]
  }
  rule {
      name = "apitcp"
      source_addresses = ["*"]
      destination_addresses = ["AzureCloud.${var.region}"]
      destination_ports = [9000]
      protocols = ["TCP"]
  }
}



resource "azurerm_firewall_application_rule_collection" "azure" {
  name                = "aksbasics"
  azure_firewall_name = azurerm_firewall.fw.name
  resource_group_name = azurerm_resource_group.vpc.name
  priority            = 100
  action              = "Allow"
  rule {
    name             = "allow azure"
    source_addresses = ["*"]
    target_fqdns = [
      "*.cdn.mscr.io",
      "mcr.microsoft.com",
      "*.data.mcr.microsoft.com",
      "management.azure.com",
      "login.microsoftonline.com",
      "acs-mirror.azureedge.net",
      "dc.services.visualstudio.com",
      "*.opinsights.azure.com",
      "*.oms.opinsights.azure.com",
      "*.microsoftonline.com",
      "*.monitoring.azure.com",
    ]
    protocol {
      port = "80"
      type = "Http"
    }
    protocol {
      port = "443"
      type = "Https"
    }
  }
}


resource "azurerm_firewall_application_rule_collection" "fqdns" {
  name                = "aksfqdns"
  azure_firewall_name = azurerm_firewall.fw.name
  resource_group_name = azurerm_resource_group.vpc.name
  priority            = 101
  action              = "Allow"
  rule {
    name             = "allowk8s"
    source_addresses = ["*"]
    fqdn_tags= ["AzureKubernetesService"]
  }
}

