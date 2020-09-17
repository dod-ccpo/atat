



resource "random_password" "pg_root_password" {
  length           = 16
  special          = false
  override_special = "!"
}


resource "random_password" "atat_user_password" {
  length           = 16
  special          = false
  override_special = "!"
}



module "sql" {
  source                       = "../../modules/postgres"
  name                         = var.name
  owner                        = var.owner
  environment                  = local.environment
  region                       = var.region
  subnet_id                    = module.vpc.subnet_list["aks"].id
  administrator_login          = var.postgres_admin_login
  administrator_login_password = random_password.pg_root_password.result
  workspace_id                 = module.logs.workspace_id
  operator_ip                  = chomp(data.http.myip.body)
}
