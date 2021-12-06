variable "azure_region" {
  default = "westeurope"
}

variable "location" {
  default = "West Europe"
}

variable "resource_group_name" {
  default = "EPAM_Diploma"
}

variable "DB_PASSWORD" {
  description = "Password for MariaDB admin (get from environment)"
  type        = string
}

variable "ssh_public_key" {
  default = "~/.ssh/azure_key.pub"
}

variable "dns_prefix" {
  default = "aks1"
}

variable "cluster_name" {
  default = "aks1"
}

