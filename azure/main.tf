# Configure the Azure provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.65"
    }
  }

  required_version = ">= 0.14.9"

  backend "azurerm" {
    resource_group_name  = "tfstate"
    storage_account_name = "tfstate5870"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }

}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.azure_region

  tags = {
    Owner = "mskawslearn1@gmail.com"
  }
}

resource "azurerm_kubernetes_cluster" "k8s" {
  name                = var.cluster_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = var.dns_prefix

  linux_profile {
    admin_username = "ubuntu"

    ssh_key {
      key_data = file(var.ssh_public_key)
    }
  }

  default_node_pool {
    name      = "default"
    min_count = 1
    max_count = 2
    vm_size   = "Standard_B2s"
    #vm_size             = "Standard_DS2_v2"
    enable_auto_scaling = true
  }

  auto_scaler_profile {
    scale_down_delay_after_add = "2m"
    scale_down_unneeded        = "2m"
  }

  identity {
    type = "SystemAssigned"
  }

}

resource "azurerm_container_registry" "acr" {
  name                = "mskepamdiplomaacr"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
}

# Allow AKS to pull images from ACR
resource "azurerm_role_assignment" "aks_to_acr_role" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.k8s.kubelet_identity[0].object_id
}

resource "azurerm_mariadb_server" "dbsrv" {
  name                = "mskepamdiplomadb"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  sku_name = "B_Gen5_1"

  storage_mb                   = 5120
  backup_retention_days        = 7
  geo_redundant_backup_enabled = false

  administrator_login          = "nhltop"
  administrator_login_password = var.DB_PASSWORD
  version                      = "10.3"
  ssl_enforcement_enabled      = false
}

resource "azurerm_mariadb_database" "dbprod" {
  name                = "nhltop"
  resource_group_name = azurerm_resource_group.rg.name
  server_name         = azurerm_mariadb_server.dbsrv.name
  charset             = "utf8"
  collation           = "utf8_general_ci"
}

resource "azurerm_mariadb_database" "dbtest" {
  name                = "test"
  resource_group_name = azurerm_resource_group.rg.name
  server_name         = azurerm_mariadb_server.dbsrv.name
  charset             = "utf8"
  collation           = "utf8_general_ci"
}

resource "azurerm_mariadb_firewall_rule" "db_firewall_rule" {
  name                = "permit-azure"
  resource_group_name = azurerm_resource_group.rg.name
  server_name         = azurerm_mariadb_server.dbsrv.name
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "0.0.0.0"
}
