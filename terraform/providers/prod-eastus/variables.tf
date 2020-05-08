variable "environment" {
  default = "jedi"
}

variable "region" {
  default = "eastus"

}

variable "backup_region" {
  default = "westus2"
}


variable "owner" {
  default = "prod"
}

variable "name" {
  default = "cloudzero"
}

variable "virtual_network" {
  type    = string
  default = "164.240.2.0/24"
}


variable "networks" {
  type = map
  default = {
    #format
    #name         = "CIDR, route table, Security Group Name"
    edge  = "164.240.2.0/26,edge"   # LBs
    aks   = "164.240.2.128/25,aks"  # k8s, postgres, keyvault
    redis = "164.240.2.64/26,redis" # Redis
  }
}

variable "service_endpoints" {
  type = map
  default = {
    edge  = "Microsoft.ContainerRegistry" # Not necessary but added to avoid infinite state loop
    aks   = "Microsoft.Storage,Microsoft.KeyVault,Microsoft.ContainerRegistry,Microsoft.Sql"
    redis = "Microsoft.Storage,Microsoft.Sql"
  }
}

variable "route_tables" {
  description = "Route tables and their default routes"
  type        = map
  default = {
    edge  = "Internet"
    aks   = "Internet"
    redis = "VnetLocal"
  }
}

# Custom routes
variable "routes" {
  description = "Routes for next hop types: VirtualNetworkGateway, VnetLocal, Internet or None"
  type        = map
  default = {
    edge  = "edge,to_vnet,164.240.2.0/24,VnetLocal"
    aks   = "aks,to_vnet,164.240.2.0/24,VnetLocal"
    redis = "redis,to_vnet,164.240.2.0/24,VnetLocal"
  }
}

variable "dns_servers" {
  type    = list
  default = []
}

variable "k8s_node_size" {
  type    = string
  default = "Standard_F32s_v2"
}

variable "k8s_dns_prefix" {
  type    = string
  default = "atat"
}

variable "k8s_network_plugin" {
  type    = string
  default = "azure"
}

variable "tenant_id" {
  type    = string
  default = "b05c2da5-f708-47de-9d84-7966e4f4e48b"
}

variable "admin_users" {
  type = map
  default = {
    "Rob Gil"       = "ea13de70-6937-4c64-b15a-4b7e15f2f856"
    "Dan Corrigan"  = "9da9b329-8dd6-4522-be71-cd8908d03a82"
    "James Garrett" = "6e945ba6-d864-45ac-9793-a2ce410c1a06"
  }
}

variable "admin_user_whitelist" {
  type = map
  default = {
    "Rob Gil"           = "66.220.238.184/32"
    "Dan Corrigan Work" = "108.16.207.173/32"
    "Dan Corrigan Home" = "71.162.221.27/32"
  }
}

variable "storage_admin_whitelist" {
  type = map
  default = {
    "Rob Gil"           = "66.220.238.184"
    "Dan Corrigan Work" = "108.16.207.173"
    "Dan Corrigan Home" = "71.162.221.27"
  }
}

variable "vpn_client_cidr" {
  type    = list
  default = ["172.16.255.0/24"]
}
