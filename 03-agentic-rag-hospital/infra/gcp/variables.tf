variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "project_name" {
  description = "Project name used for resource naming and labels"
  type        = string
  default     = "agentic-rag-hospital"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "api_port" {
  description = "FastAPI container port"
  type        = number
  default     = 8003
}

variable "api_image" {
  description = "Backend container image URL"
  type        = string
}

variable "api_cpu" {
  description = "Cloud Run CPU allocation (1, 2, 4)"
  type        = string
  default     = "1"
}

variable "api_memory" {
  description = "Cloud Run memory allocation"
  type        = string
  default     = "2Gi"
}

variable "api_min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 0
}

variable "api_max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

variable "api_secret_key" {
  description = "FastAPI secret key"
  type        = string
  sensitive   = true
}

variable "postgres_user" {
  description = "Cloud SQL Postgres user"
  type        = string
  default     = "rag"
}

variable "postgres_password" {
  description = "Cloud SQL Postgres password"
  type        = string
  sensitive   = true
}

variable "postgres_db" {
  description = "Cloud SQL Postgres database name"
  type        = string
  default     = "rag"
}

variable "postgres_tier" {
  description = "Cloud SQL Postgres machine tier"
  type        = string
  default     = "db-f1-micro"
}

variable "redis_tier" {
  description = "Memorystore Redis tier"
  type        = string
  default     = "BASIC"
}

variable "redis_memory_gb" {
  description = "Memorystore Redis memory size in GiB"
  type        = number
  default     = 1
}

variable "domain_name" {
  description = "Custom domain name for Cloud CDN / Load Balancer"
  type        = string
  default     = ""
}

variable "extra_env" {
  description = "Additional environment variables for the API container"
  type        = map(string)
  default     = {}
}
