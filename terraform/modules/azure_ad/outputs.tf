output "application_id" {

  value = azuread_application.app.application_id
}

output "object_id" {

  value = azuread_application.app.object_id
}

output "oauth2_permissions" {

  value = azuread_application.app.oauth2_permissions
}

output "sp_object_id" {
  value = azuread_service_principal.principal.object_id

}
output "name" {
  value = var.name
}
