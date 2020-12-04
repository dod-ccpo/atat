# output "subnet_list" {
#   value = {
#     for k, id in azurerm_subnet.subnet : k => id
#   }
# }

output "subnet_id_list" {
  value = azurerm_subnet.subnet.*
}

output "id" {
  value = azurerm_virtual_network.vpc.id
}

output "vpc_name" {
  value = azurerm_virtual_network.vpc.name
}

output "resource_group_name" {
  value = azurerm_resource_group.vpc.name
}

output "fw_ip_address_id" {
  value = azurerm_public_ip.az_fw_ip.id
}
