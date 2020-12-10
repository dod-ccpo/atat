variable "vm_name" {
  description = "The base name of virtual machine"
  default     = "dry-run-ops-vm"
  type        = string
}

variable "region" {
  description = "Azure region"
  default     = "eastus"
  type        = string
}

variable "username" {
  description = "username to be created on the vm"
  default     = "atat"
  type        = string
}

variable "vnet" {
  description = "vnet vm will use"
  default     = "dry-run-ops-vm-vnet"
  type        = string
}

variable "subnet" {
  description = "subnet vm will use"
  default     = "dry-run-ops-vm-subnet"
  type        = string
}

variable "resource_group" {
  description = "resource_group vm will use"
  default     = "dry-run-ops-vm-resource-group"
  type        = string
}
