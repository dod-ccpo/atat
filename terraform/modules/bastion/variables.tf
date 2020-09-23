variable "mgmt_subnet_rg" {}
variable "mgmt_subnet_cidr" {}
variable "bastion_subnet_rg" {}
variable "bastion_subnet_cidr" {}


variable "mgmt_subnet_vpc_name" {}
variable "bastion_subnet_vpc_name" {}
variable "rg" {}
variable "region" {}
variable "bastion_aks_sp_secret" {}
variable "bastion_aks_sp_id" {}
variable "environment" {}
variable "owner" {}
variable "name" {}

variable "bastion_ssh_pub_key_path" {}
variable "log_analytics_workspace_id" {}


variable "registry_username" {}
variable "registry_password" {}

variable "container_image" {
  default = "bastion:latest"
}

variable container_registry {
  default = "cloudzeroopsregistry.azurecr.io"
}
