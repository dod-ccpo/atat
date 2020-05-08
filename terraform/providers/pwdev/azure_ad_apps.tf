

# register the app with the executor owner.
# assign a role to it on either subscription, resource group or resource to assign something to its service principle. without this, the app is on-behalf of user
# give it a secret
# configure access policies on target resources
module "tenant_keyvault_app" {

  source = "../../modules/azure_ad"
  name   = "tenant-keyvault"


}
