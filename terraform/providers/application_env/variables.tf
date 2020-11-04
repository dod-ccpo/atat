variable "deployment_location" {
  type        = string
  description = "Azure region in which deployment resources are provisioned."
  default     = "East US"
}

variable "deployment_namespace" {
  type        = string
  description = "Namespace of provisioned deployment resources."
  default     = "dev"
}

variable "lifecycle_env_name" {
  type        = string
  description = "TODO(jesse) I don't think this needs to be used."
  default     = "staging"
}

variable "owner" {
  type        = string
  description = "TODO(jesse) Is this a required property in all those modules?"
  default     = "pw"
}

variable "name" {
  type        = string
  description = "TODO(jesse) Is this a required property in all those modules?"
  default     = "testname"
}

variable "virtual_network" {
  type        = string
  description = ""
  default     = "10.1.0.0/16"
}

variable "networks" {
  type        = map
  description = ""
  default = {}
}

variable "service_endpoints" {
  type        = map
  description = ""
  default = {}
}

variable "route_tables" {
  type        = map
  description = "Route tables and their default routes"
  default = {}
}

variable "routes" {
  type        = map
  description = "Routes for next hop types: VirtualNetworkGateway, VnetLocal, Internet or None"
  default = {}
}

variable "k8s_node_size" {
  type        = string
  description = ""
  default     = "Standard_D2_v2"
}

variable "k8s_dns_prefix" {
  type        = string
  description = ""
  default     = "atat"
}

# variable "tenant_id" {}

# variable "admin_users" {
#   type = map
# }

# variable "admin_user_whitelist" {
#   type = map
# }

# variable "storage_admin_whitelist" {
#   type = map
# }

variable "bucket_cors_properties" {
  type        = list(map(string))
  description = "supports cors"
  default     = []
}

variable "private_k8s_subnet_cidr" {
  type        = string
  default     = "10.1.5.0/24"
  description = ""
}

variable "private_aks_service_dns" {
  default = ""
}

variable "private_aks_service_cidr" {
  default = ""
}

variable "private_aks_docker_bridge_cidr" {
  default = ""
}

variable "private_aks_sp_secret" {
  default = "sdfasdfasf"
}

variable "private_aks_sp_id" {
  default = "asdfasdfasd"
}

variable "aks_max_node_count" {
  type        = number
  description = ""
  default     = 5
}

variable "aks_min_node_count" {
  type        = number
  description = ""
  default     = 3
}

variable "postgres_admin_login" {
  type        = string
  description = ""
  default     = "clouzero_pg_admin"
}

variable "task_order_bucket_storage_container_name" {
  type        = string
  description = ""
  default     = "task-order-pdfs"
}

variable "tf_state_storage_container_name" {
  type        = string
  description = ""
  default     = "tfstate"
}

variable "virtual_appliance_routes" {
  type        = map
  description = ""
  default = {}
}

variable "virtual_appliance_route_tables" {
  type        = map
  description = ""
  default = {
    "aks-private" = "VirtualAppliance"
  }
}

variable "tls_cert_path" {
  type = string
  description = "Path to the TLS cert generated via diffie helman. (?)" 
  default = "/tmp/atatdev.pem"
}

variable "OPS_CID" {
  default = "asfads"
}

variable "OPS_SEC" {
  default = "adsfasd"
}

variable "OPS_OID" {
  default = "adsfadsf"
}

variable "OPS_SP_URL" {
  default = "asdfasd"
}

# variable "mailgun_smtp_password" {}

# variable "azure_subscription_id" {}
# variable "azure_hybrid_tenant_id" {}
# variable "azure_hybrid_user_object_id" {}
# variable "azure_hybrid_tenant_admin_password" {}
# variable "AZURE-BILLING-ACCOUNT-NAME" {}
# variable "AZURE-INVOICE-SECTION-ID" {}
# variable "SAML-IDP-CERT" {}
# variable "AZURE-BILLING-PROFILE-ID" {}
# variable "dhparam4096" {}
# variable "AZURE_SUBSCRIPTION_CREATION_CLIENT_ID" {}
# variable "AZURE_SUBSCRIPTION_CREATION_SECRET" {}
# variable "AZURE_POWERSHELL_CLIENT_ID" {}
# variable "AZURE_ROOT_MGMT_GROUP_ID" {}
# variable "AZURE_TENANT_ADMIN_USERNAME" {}
# variable "AZURE_TENANT_ID" {}
# variable "AZURE_USER_OBJECT_ID" {}
# variable "CSP" {}
# variable "AZURE_HYBRID_REPORTING_CLIENT_ID" {}
# variable "AZURE_HYBRID_REPORTING_SECRET" {}
# variable "circle_ci_api_key" {}
# variable "deployment_subnet_id" {}
