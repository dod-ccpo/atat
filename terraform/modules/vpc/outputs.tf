output "subnet_list" {
  value = {
    for k, id in azurerm_subnet.subnet : k => id
  }
}

output "id" {
  value = azurerm_virtual_network.vpc.id
}
