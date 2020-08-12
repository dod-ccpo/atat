module "logs" {
  source            = "../../modules/log_analytics"
  owner             = var.owner
  environment       = var.environment
  region            = var.region
  name              = var.name
  retention_in_days = 365
}

