terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.5"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"

  postgres_url          = "postgresql+asyncpg://${var.postgres_user}:${var.postgres_password}@/${var.postgres_db}?host=/cloudsql/${google_sql_database_instance.postgres.connection_name}"
  redis_url             = "redis://:${random_password.redis.result}@${google_redis_instance.redis.host}:${google_redis_instance.redis.port}/0"
  celery_broker_url     = local.redis_url
  celery_result_backend = local.redis_url
  qdrant_url            = "https://storage.googleapis.com/${google_storage_bucket.qdrant.name}" # Placeholder
  ollama_url            = "" # Use external LLM endpoint in production

  common_env = {
    APP_NAME              = var.project_name
    ENVIRONMENT           = var.environment
    PORT                  = tostring(var.api_port)
    LOG_LEVEL             = "info"
    SECRET_KEY            = var.api_secret_key
    REDIS_URL             = local.redis_url
    CELERY_BROKER_URL     = local.celery_broker_url
    CELERY_RESULT_BACKEND = local.celery_result_backend
    QDRANT_URL            = local.qdrant_url
    POSTGRES_URL          = local.postgres_url
    OLLAMA_URL            = local.ollama_url
    LLM_MODEL             = "llama3:8b"
    EMBEDDING_MODEL       = "nomic-embed-text"
    MULTIMODAL_COLLECTION = "multimodal_rag"
    VECTOR_SIZE           = "512"
    DEFAULT_TOP_K         = "5"
  }
}

resource "random_password" "redis" {
  length  = 32
  special = false
}

resource "random_id" "suffix" {
  byte_length = 4
}

# ---------------------------------------------------------------------------
# APIs
# ---------------------------------------------------------------------------

resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com",
  ])

  service            = each.value
  disable_on_destroy = false
}

# ---------------------------------------------------------------------------
# VPC
# ---------------------------------------------------------------------------

resource "google_compute_network" "main" {
  name                    = "${local.name_prefix}-vpc"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.apis]
}

resource "google_compute_subnetwork" "main" {
  name          = "${local.name_prefix}-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.main.id
}

resource "google_compute_global_address" "private_ip_alloc" {
  name          = "${local.name_prefix}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]
}

# ---------------------------------------------------------------------------
# Cloud SQL Postgres
# ---------------------------------------------------------------------------

resource "google_sql_database_instance" "postgres" {
  name             = "${local.name_prefix}-psql-${random_id.suffix.hex}"
  database_version = "POSTGRES_16"
  region           = var.region

  settings {
    tier              = var.postgres_tier
    availability_type = "ZONAL"

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.main.id
    }

    backup_configuration {
      enabled = true
    }
  }

  deletion_protection = false
  depends_on          = [google_service_networking_connection.private_vpc_connection]
}

resource "google_sql_database" "rag" {
  name     = var.postgres_db
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "rag" {
  name     = var.postgres_user
  instance = google_sql_database_instance.postgres.name
  password = var.postgres_password
}

# ---------------------------------------------------------------------------
# Memorystore Redis
# ---------------------------------------------------------------------------

resource "google_redis_instance" "redis" {
  name               = "${local.name_prefix}-redis"
  tier               = var.redis_tier
  memory_size_gb     = var.redis_memory_gb
  region             = var.region
  authorized_network = google_compute_network.main.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"
  redis_version      = "REDIS_7_0"

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

# ---------------------------------------------------------------------------
# Cloud Storage
# ---------------------------------------------------------------------------

resource "google_storage_bucket" "assets" {
  name          = "${local.name_prefix}-assets-${random_id.suffix.hex}"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = false
  }
}

resource "google_storage_bucket" "qdrant" {
  name          = "${local.name_prefix}-qdrant-${random_id.suffix.hex}"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true
}

# ---------------------------------------------------------------------------
# Secret Manager
# ---------------------------------------------------------------------------

resource "google_secret_manager_secret" "api" {
  secret_id = "${local.name_prefix}-api-secrets"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "api" {
  secret = google_secret_manager_secret.api.id

  secret_data = jsonencode({
    secret_key        = var.api_secret_key
    postgres_password = var.postgres_password
    redis_password    = random_password.redis.result
    postgres_url      = local.postgres_url
    redis_url         = local.redis_url
  })
}

# ---------------------------------------------------------------------------
# Cloud Run
# ---------------------------------------------------------------------------

resource "google_cloud_run_v2_service" "api" {
  name     = "${local.name_prefix}-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.api.email

    scaling {
      min_instance_count = var.api_min_instances
      max_instance_count = var.api_max_instances
    }

    containers {
      image = var.api_image

      ports {
        container_port = var.api_port
      }

      resources {
        limits = {
          cpu    = var.api_cpu
          memory = var.api_memory
        }
        cpu_idle = var.api_min_instances == 0
      }

      dynamic "env" {
        for_each = merge(local.common_env, var.extra_env)
        content {
          name  = env.key
          value = env.value
        }
      }

      startup_probe {
        initial_delay_seconds = 10
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 6
        http_get {
          path = "/health"
          port = var.api_port
        }
      }

      liveness_probe {
        timeout_seconds   = 5
        period_seconds    = 30
        failure_threshold = 3
        http_get {
          path = "/health"
          port = var.api_port
        }
      }
    }
  }

  depends_on = [google_project_service.apis]
}

resource "google_cloud_run_service_iam_member" "public" {
  location = google_cloud_run_v2_service.api.location
  service  = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_service_account" "api" {
  account_id   = "${local.name_prefix}-api"
  display_name = "Multi-Modal RAG API service account"
}

resource "google_project_iam_member" "api_storage" {
  project = var.project_id
  role    = "roles/storage.objectUser"
  member  = "serviceAccount:${google_service_account.api.email}"
}

resource "google_project_iam_member" "api_secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.api.email}"
}

resource "google_project_iam_member" "api_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.api.email}"
}

# ---------------------------------------------------------------------------
# Cloud CDN + Load Balancer (optional, for custom domain + CDN)
# ---------------------------------------------------------------------------

resource "google_compute_backend_bucket" "assets" {
  name        = "${local.name_prefix}-assets-backend"
  bucket_name = google_storage_bucket.assets.name
  enable_cdn  = true
}

resource "google_compute_region_network_endpoint_group" "api" {
  name                  = "${local.name_prefix}-api-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = google_cloud_run_v2_service.api.name
  }
}

resource "google_compute_backend_service" "api" {
  name        = "${local.name_prefix}-api-backend"
  description = "Backend service for Multi-Modal RAG API"

  backend {
    group = google_compute_region_network_endpoint_group.api.id
  }
}

resource "google_compute_url_map" "main" {
  count           = var.domain_name != "" ? 1 : 0
  name            = "${local.name_prefix}-urlmap"
  default_service = google_compute_backend_service.api.id
}

resource "google_compute_managed_ssl_certificate" "main" {
  count = var.domain_name != "" ? 1 : 0
  name  = "${local.name_prefix}-cert"

  managed {
    domains = [var.domain_name]
  }
}

resource "google_compute_target_https_proxy" "main" {
  count            = var.domain_name != "" ? 1 : 0
  name             = "${local.name_prefix}-https-proxy"
  url_map          = google_compute_url_map.main[0].id
  ssl_certificates = [google_compute_managed_ssl_certificate.main[0].id]
}

resource "google_compute_global_forwarding_rule" "https" {
  count                 = var.domain_name != "" ? 1 : 0
  name                  = "${local.name_prefix}-https-rule"
  target                = google_compute_target_https_proxy.main[0].id
  port_range            = "443"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
}

# ---------------------------------------------------------------------------
# Monitoring
# ---------------------------------------------------------------------------

resource "google_monitoring_dashboard" "api" {
  dashboard_json = jsonencode({
    displayName = "${local.name_prefix} API"
    gridLayout = {
      columns = "2"
      widgets = [
        {
          title = "Request Count"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
                  aggregation = {
                    alignmentPeriod    = "60s"
                    per_series_aligner = "ALIGN_RATE"
                  }
                }
              }
            }]
          }
        },
        {
          title = "Request Latency"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\""
                  aggregation = {
                    alignmentPeriod    = "60s"
                    per_series_aligner = "ALIGN_PERCENTILE_99"
                  }
                }
              }
            }]
          }
        }
      ]
    }
  })
}
