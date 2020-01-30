resource "azurerm_resource_group" "bucket" {
  name     = "${var.name}-${var.environment}-${var.service_name}"
  location = var.region
}

resource "azurerm_storage_account" "bucket" {
  name                     = var.service_name
  resource_group_name      = azurerm_resource_group.bucket.name
  location                 = azurerm_resource_group.bucket.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_account_network_rules" "acls" {
  resource_group_name  = azurerm_resource_group.bucket.name
  storage_account_name = azurerm_storage_account.bucket.name

  default_action = var.policy

  # Azure Storage CIDR ACLs do not accept /32 CIDR ranges.
  ip_rules = [
    for cidr in values(var.whitelist) : cidr
  ]
  virtual_network_subnet_ids = var.subnet_ids
  bypass                     = ["AzureServices"]
}

resource "azurerm_storage_container" "bucket" {
  name                  = "content"
  storage_account_name  = azurerm_storage_account.bucket.name
  container_access_type = var.container_access_type
}

# Added until requisite TF bugs are fixed. Typically this would be configured in the 
# storage_account resource
resource "null_resource" "retention" {
  provisioner "local-exec" {
    command = "az storage logging update --account-name ${azurerm_storage_account.bucket.name} --log rwd --services bqt --retention 90"
  }
}

##alert rule tag on the the storage module 
resource "azurerm_metric_alertrule" "storage" {
  name                = "${var.service_name}-storage"
  resource_group_name = "${azurerm_resource_group.bucket.name}"
  location            = "${azurerm_resource_group.bucket.location}"

  description = "An alert rule to watch the metric Storage"

  enabled = true

  resource_id = "$(azurerm_storage_bucket.bucket.id}"
  metric_name = "storage"
  operator    = "GreaterThan"
  threshold   = 1649267441664
  aggregation = "Maximum"
  period      = "PT10M"

  email_action {
    send_to_service_owners = false

    custom_emails = [
      "${var.custom_emails}", # add email 
    ]
  }
