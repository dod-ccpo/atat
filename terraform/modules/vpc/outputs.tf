output "subnet_list" {
  value = {
    for k, id in azurerm_subnet.subnet : k => id
  }
}

output "subnet_id_list" {
  value = azurerm_subnet.subnet.*
}

output "id" {
  value = azurerm_virtual_network.vpc.id
}

output "vpc_name" {
  value = "${var.name}-network-${var.environment}"
}

output "resource_group_name" {

  value = "${var.name}-vpc-${var.environment}"

}
