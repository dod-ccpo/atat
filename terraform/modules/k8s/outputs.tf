output "principal_id" {
  value = azurerm_kubernetes_cluster.k8s.identity[0].principal_id
}
