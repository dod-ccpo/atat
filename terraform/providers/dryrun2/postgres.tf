



resource "random_password" "pg_root_password" {
  length = 16
  special = true
  override_special = "%@#="
}


resource "random_password" "atat_user_password" {
  length = 16
  special = true
  override_special = "%@#="
}



module "sql" {
  source                       = "../../modules/postgres"
  name                         = var.name
  owner                        = var.owner
  environment                  = var.environment
  region                       = var.region
  subnet_id                    = module.vpc.subnet_list["aks"].id
  administrator_login          = var.postgres_admin_login
  administrator_login_password = random_password.pg_root_password.result
  workspace_id                 = module.logs.workspace_id
  pet_name     = random_pet.unique_id.id
}
