variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "graph-rag"
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
  default     = 8002
}

variable "api_image" {
  description = "Backend container image"
  type        = string
}

variable "api_cpu" {
  description = "Cloud Run CPU limit"
  type        = string
  default     = "1"
}

variable "api_memory" {
  description = "Cloud Run memory limit"
  type        = string
  default     = "2Gi"
}

variable "api_min_instances" {
  description = "Minimum Cloud Run instances"
  type        = number
  default     = 0
}

variable "api_max_instances" {
  description = "Maximum Cloud Run instances"
  type        = number
  default     = 5
}

variable "api_secret_key" {
  description = "FastAPI secret key"
  type        = string
  sensitive   = true
}

variable "postgres_user" {
  description = "Cloud SQL Postgres username"
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
  description = "Cloud SQL Postgres tier"
  type        = string
  default     = "db-f1-micro"
}

variable "redis_tier" {
  description = "Memorystore Redis tier"
  type        = string
  default     = "BASIC"
}

variable "redis_memory_gb" {
  description = "Memorystore Redis memory size (GiB)"
  type        = number
  default     = 1
}

variable "qdrant_endpoint" {
  description = "Qdrant vector store URL placeholder"
  type        = string
  default     = "https://qdrant.internal:6333"
}

variable "neo4j_endpoint" {
  description = "Neo4j Bolt URI placeholder"
  type        = string
  default     = "bolt://neo4j.internal:7687"
}

variable "ollama_endpoint" {
  description = "Ollama or OpenAI-compatible endpoint"
  type        = string
  default     = ""
}

variable "domain_name" {
  description = "Custom domain for the global load balancer"
  type        = string
  default     = ""
}

variable "extra_env" {
  description = "Additional environment variables for the API container"
  type        = map(string)
  default     = {}
}
