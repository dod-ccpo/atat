variable "environment" {
  default = "jedidev"
}

variable "region" {
  default = "eastus"

}

variable "backup_region" {
  default = "westus2"
}


variable "owner" {
  default = "dev"
}

variable "name" {
  default = "cloudzero"
}

variable "virtual_network" {
  type    = string
  default = "10.1.0.0/16"
}


variable "networks" {
  type = map
  default = {
    #format
    #name         = "CIDR, route table, Security Group Name"
    public  = "10.1.1.0/24,public"  # LBs
    private = "10.1.2.0/24,private" # k8s, postgres, keyvault
    redis   = "10.1.3.0/24,private" # Redis
  }
}

variable "service_endpoints" {
  type = map
  default = {
    public  = "Microsoft.ContainerRegistry" # Not necessary but added to avoid infinite state loop
    private = "Microsoft.Storage,Microsoft.KeyVault,Microsoft.ContainerRegistry,Microsoft.Sql"
    redis   = "Microsoft.Storage,Microsoft.Sql" # FIXME: There is no Microsoft.Redis
  }
}

variable "gateway_subnet" {
  type    = string
  default = "10.1.20.0/24"
}


variable "route_tables" {
  description = "Route tables and their default routes"
  type        = map
  default = {
    public  = "Internet"
    private = "Internet"
    redis   = "VnetLocal"
    #private = "VnetLocal"
  }
}

variable "dns_servers" {
  type    = list
  default = []
}

variable "k8s_node_size" {
  type    = string
  default = "Standard_A1_v2"
}

variable "k8s_dns_prefix" {
  type    = string
  default = "atat"
}

variable "tenant_id" {
  type    = string
  default = "47f616e9-6ff5-4736-9b9e-b3f62c93a915"
}

variable "admin_users" {
  type = map
  default = {
    "Rob Gil"      = "cef37d01-1acf-4085-96c8-da9d34d0237e"
    "Dan Corrigan" = "7e852ceb-eb0d-49b1-b71e-e9dcd1082ffc"
  }
}

variable "admin_user_whitelist" {
  type = map
  default = {
    "Rob Gil"           = "66.220.238.246/32"
    "Dan Corrigan Work" = "108.16.207.173/32"
    "Dan Corrigan Home" = "71.162.221.27/32"
  }
}

variable "storage_admin_whitelist" {
  type = map
  default = {
    "Rob Gil"           = "66.220.238.246"
    "Dan Corrigan Work" = "108.16.207.173"
    "Dan Corrigan Home" = "71.162.221.27"
  }
}

variable "vpn_client_cidr" {
  type    = list
  default = ["172.16.255.0/24"]
}

variable "custom_emails" {
  type        = map
    default = {
    "Sec-Ops"           = "ccpotech@cloud.mil"
  }
}
}
