locals {
  ops_sp_url_to_name           = replace(var.OPS_SP_URL, "http://", "")
  environment                  = length(var.environment) > 0 ? var.environment : random_pet.unique_id.id
  private_aks_appliance_routes = var.virtual_appliance_routes["aks-private"]
}
