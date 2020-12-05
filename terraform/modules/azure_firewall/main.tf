




resource "azurerm_route_table" "firewall_route_table" {
  for_each            = var.virtual_appliance_route_tables
  name                = "${var.name}-${each.key}-${var.environment}-fw"
  location            = var.location
  resource_group_name = var.resource_group_name
}





resource "azurerm_route" "firewall_routes_internet" {

  for_each               = var.virtual_appliance_routes
  name                   = "${var.name}-${element(split(",", each.value), 0)}-${var.environment}-public"
  resource_group_name    = var.resource_group_name
  route_table_name       = azurerm_route_table.firewall_route_table[each.key].name
  address_prefix         = "${var.az_fw_ip}/32"
  next_hop_type          = "Internet"

}

# Default Routes
resource "azurerm_route" "fw_route_egress" {
  for_each               = var.virtual_appliance_route_tables
  name                   = "${var.name}-default-${var.environment}"
  resource_group_name    = var.resource_group_name
  route_table_name       = azurerm_route_table.firewall_route_table[each.key].name
  address_prefix         = "0.0.0.0/0"
  next_hop_type          = each.value
  next_hop_in_ip_address = azurerm_firewall.fw.ip_configuration[0].private_ip_address
}



resource "azurerm_subnet_route_table_association" "firewall_route_table" {
  for_each       = var.virtual_appliance_route_tables
  subnet_id      = var.subnets[each.key].id
  route_table_id = azurerm_route_table.firewall_route_table[each.key].id
}





resource "azurerm_firewall" "fw" {
  name                = "az-firewall-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name

  ip_configuration {
    name                 = "configuration"
    subnet_id            = var.subnet_id
    public_ip_address_id = var.az_fw_ip_id
  }

  #firewall_policy_id = azurerm_firewall_policy.enable_dns_proxy.id

}


resource "azurerm_firewall_policy" "enable_dns_proxy" {
  name                = "az-firewall-${var.environment}-policy"
  resource_group_name = var.resource_group_name
  location            = var.location

  dns {
   proxy_enabled= true
  }
}


resource "azurerm_firewall_application_rule_collection" "fw_rule_collection" {
  name                = "aksbasics"
  azure_firewall_name = azurerm_firewall.fw.name
  resource_group_name = var.resource_group_name
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






  depends_on = [azurerm_firewall.fw]

}


resource "azurerm_firewall_application_rule_collection" "fw_rule_collection_fqdns" {
  name                = "aksfqdns"
  azure_firewall_name = azurerm_firewall.fw.name
  resource_group_name = var.resource_group_name
  priority            = 101
  action              = "Allow"


  rule {
    name             = "allowk8s"
    source_addresses = ["*"]

    fqdn_tags= ["AzureKubernetesService"]




  }

  depends_on = [azurerm_firewall.fw]
  }


resource "azurerm_firewall_network_rule_collection" "api" {

 azure_firewall_name = azurerm_firewall.fw.name
 name = "${var.name}-network-rules-${var.environment}"
 resource_group_name = var.resource_group_name
 priority = 100
 action   = "Allow"

rule {
    name = "apiudp"
    source_addresses = ["*"]
    destination_addresses = ["AzureCloud.${var.location}"]

    destination_ports = [1194]
    protocols = ["UDP"]

}

rule {
    name = "apitcp"
    source_addresses = ["*"]
    destination_addresses = ["AzureCloud.${var.location}"]

    destination_ports = [9000]
    protocols = ["TCP"]


}




  depends_on = [azurerm_firewall.fw]
}


resource "azurerm_firewall_nat_rule_collection" "tolb" {
  name                = "tolb"
  azure_firewall_name = azurerm_firewall.fw.name
  resource_group_name = var.resource_group_name
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
      var.az_fw_ip
    ]

    translated_port = 443

    translated_address = "${var.nat_rules_translated_ips}"

    protocols = [
      "TCP"

    ]



  }


  rule {
    name = "maintenancepage"

    source_addresses = [
      "*",
    ]

    destination_ports = [
      "443",
    ]

    destination_addresses = [
      var.az_fw_ip
    ]

    translated_port = 443

    translated_address = "${var.maintenance_page_ip}"

    protocols = [
      "TCP"

    ]



  }


  timeouts {

    create = "30h"
    update = "30h"
    read = "30h"
    delete = "30h"
  }


  depends_on = [azurerm_firewall.fw]

}
