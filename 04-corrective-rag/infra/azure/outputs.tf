output "resource_group_name" {
  description = "Azure resource group name"
  value       = azurerm_resource_group.main.name
}

output "container_app_fqdn" {
  description = "Container App default FQDN"
  value       = azurerm_container_app.api.ingress[0].fqdn
}

output "frontdoor_endpoint" {
  description = "Front Door endpoint hostname"
  value       = azurerm_cdn_frontdoor_endpoint.main.host_name
}

output "postgresql_fqdn" {
  description = "PostgreSQL flexible server FQDN"
  value       = azurerm_postgresql_flexible_server.postgres.fqdn
}

output "redis_hostname" {
  description = "Azure Cache for Redis hostname"
  value       = azurerm_redis_cache.redis.hostname
}

output "storage_account_name" {
  description = "Primary storage account name"
  value       = azurerm_storage_account.assets.name
}

output "key_vault_name" {
  description = "Key Vault name"
  value       = azurerm_key_vault.main.name
}
