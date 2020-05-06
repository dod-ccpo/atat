

resource "azuread_application" "app" {

  name                       = var.name
  oauth2_allow_implicit_flow =false


  required_resource_access {
    resource_app_id = "00000003-0000-0000-c000-000000000000"

    resource_access {
      id   = "b24988ac-6180-42a0-ab88-20f7382dd24c"
      type = "Role"
    }

    resource_access {
      id = "e1fe6dd8-ba31-4d61-89e7-88639da4683d"
      type= "Scope"
    }

      }



}


resource "azuread_service_principal" "app_sp" {

  application_id = azuread_application.app.application_id
}
