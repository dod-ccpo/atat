


resource "azuread_application" "app" {

  name = var.name

}


resource "azuread_service_principal" "principal" {
  application_id               = "${azuread_application.app.application_id}"
  app_role_assignment_required = false


}
