data "azurerm_client_config" "current" {}

data "http" "myip" {
  url = "http://ipinfo.io/ip"
}
