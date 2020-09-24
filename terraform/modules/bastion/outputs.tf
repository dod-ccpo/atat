output "mgmt_subnet_id" {
  value = azurerm_subnet.mgmt_subnet.id
}

output "bastion_image_name" {
 value = var.container_image
}
