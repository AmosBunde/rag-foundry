output "project_id" {
  description = "GCP project ID"
  value       = var.project_id
}

output "cloud_run_url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_v2_service.api.uri
}

output "load_balancer_ip" {
  description = "Global load balancer IP address (if custom domain is set)"
  value       = length(google_compute_global_forwarding_rule.https) > 0 ? google_compute_global_forwarding_rule.https[0].ip_address : null
}

output "cloudsql_connection_name" {
  description = "Cloud SQL instance connection name"
  value       = google_sql_database_instance.postgres.connection_name
}

output "cloudsql_public_ip" {
  description = "Cloud SQL instance public IP"
  value       = google_sql_database_instance.postgres.public_ip_address
}

output "redis_host" {
  description = "Memorystore Redis host"
  value       = google_redis_instance.redis.host
}

output "assets_bucket" {
  description = "Cloud Storage assets bucket name"
  value       = google_storage_bucket.assets.name
}

output "secret_manager_secret" {
  description = "Secret Manager secret ID"
  value       = google_secret_manager_secret.api.secret_id
}

output "monitoring_dashboard" {
  description = "Monitoring dashboard ID"
  value       = google_monitoring_dashboard.api.id
}
