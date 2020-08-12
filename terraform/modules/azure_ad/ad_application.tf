data "azurerm_subscription" "main" {}


resource "random_password" "password" {
  length = 32
  special = true
  override_special = ""
}



resource "azuread_application" "app" {

  name = var.name

}


resource "azuread_service_principal" "principal" {

  application_id               = azuread_application.app.application_id
  app_role_assignment_required = false

}


resource "azuread_service_principal_password" "sp_password" {

  service_principal_id =  azuread_service_principal.principal.id
  value                = random_password.password.result
  end_date             = "2099-01-01T01:02:03Z"

}

resource "azuread_application_password" "app_password" {
  # application_id is really object_id. Terraform docs has object_id instead...
  application_object_id     = azuread_application.app.object_id
  value              = random_password.password.result
  end_date  = "2099-01-01T01:02:03Z"
}

resource "azurerm_role_assignment" "main" {
  scope                = data.azurerm_subscription.main.id
  role_definition_name = "Contributor"
  principal_id         = azuread_service_principal.principal.id
}
