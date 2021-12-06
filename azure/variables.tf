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

variable "log_analytics_workspace_name" {
  default = "DefaultLogAnalyticsWorkspaceName"
}

# refer https://azure.microsoft.com/global-infrastructure/services/?products=monitor for log analytics available regions
variable "log_analytics_workspace_location" {
  default = "westeurope"
}

# refer https://azure.microsoft.com/pricing/details/monitor/ for log analytics pricing
variable "log_analytics_workspace_sku" {
  default = "PerGB2018"
}
