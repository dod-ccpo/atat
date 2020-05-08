module "cdn" {
  source           = "../../modules/cdn"
  origin_host_name = "staging.atat.code.mil"
  owner            = var.owner
  environment      = var.environment
  name             = var.name
  region           = var.region
  workspace_id     = module.logs.workspace_id
}
