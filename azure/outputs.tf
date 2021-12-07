#output "client_certificate" {
#  value = azurerm_kubernetes_cluster.k8s.kube_config.0.client_certificate
#}

output "db_fqdn" {
  value = azurerm_mariadb_server.dbsrv.fqdn
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.k8s.kube_config_raw
  sensitive = true
}

output "acr_username" {
  value     = azurerm_container_registry.acr.admin_username
  sensitive = true
}

output "acr_password" {
  value     = azurerm_container_registry.acr.admin_password
  sensitive = true
}
