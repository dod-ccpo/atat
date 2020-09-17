module "redis" {
  source       = "../../modules/redis"
  owner        = var.owner
  environment  = local.environment
  region       = var.region
  name         = var.name
  subnet_id    = module.vpc.subnet_list["redis"].id
  sku_name     = "Premium"
  family       = "P"
  workspace_id = module.logs.workspace_id
  pet_name     = random_pet.unique_id.id
}
