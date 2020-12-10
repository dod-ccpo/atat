output "vm_username" {
  value = var.username
}

output "vm_user_password" {
  value = random_password.vm_user_password.result
}

output "public_ip_address" {
  value = azurerm_public_ip.vm_publicip.ip_address
}

output "cloud-init_message" {
  value = "cloud-init script will take a few minutes to finish. Check /var/log/cloud-init-output.log for progress"
}

