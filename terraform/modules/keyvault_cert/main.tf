




resource "azurerm_key_vault_certificate" "example" {

  count = length(var.certificate_path) > 0 ? 1 : 0
  name         = "atatdev"
  key_vault_id = var.keyvault_id

  certificate {
    contents = filebase64("${var.certificate_path}")
    password = ""
  }

  certificate_policy {
    issuer_parameters {
      name = "Self"
    }

    key_properties {
      exportable = true
      key_size   = 2048
      key_type   = "RSA"
      reuse_key  = false
    }

    secret_properties {
      content_type = "application/x-pkcs12"
    }
  }
}
