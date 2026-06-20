output "container_app_fqdn" {
  description = "FQDN of the Graph RAG Container App"
  value       = azurerm_container_app.api.ingress[0].fqdn
}

output "postgres_fqdn" {
  description = "Azure PostgreSQL flexible server FQDN"
  value       = azurerm_postgresql_flexible_server.postgres.fqdn
}

output "redis_hostname" {
  description = "Azure Cache for Redis hostname"
  value       = azurerm_redis_cache.redis.hostname
}
