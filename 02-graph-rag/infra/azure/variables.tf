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

variable "location" {
  description = "Azure region"
  type        = string
  default     = "westeurope"
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
  description = "Container App CPU cores"
  type        = number
  default     = 1
}

variable "api_memory" {
  description = "Container App memory (GiB)"
  type        = string
  default     = "2Gi"
}

variable "api_min_replicas" {
  description = "Minimum Container App replicas"
  type        = number
  default     = 1
}

variable "api_max_replicas" {
  description = "Maximum Container App replicas"
  type        = number
  default     = 3
}

variable "api_secret_key" {
  description = "FastAPI secret key"
  type        = string
  sensitive   = true
}

variable "postgres_admin_username" {
  description = "Azure PostgreSQL admin username"
  type        = string
  default     = "rag"
}

variable "postgres_admin_password" {
  description = "Azure PostgreSQL admin password"
  type        = string
  sensitive   = true
}

variable "postgres_db" {
  description = "PostgreSQL database name"
  type        = string
  default     = "rag"
}

variable "postgres_sku" {
  description = "PostgreSQL flexible server SKU"
  type        = string
  default     = "B_Standard_B2s"
}

variable "redis_sku" {
  description = "Azure Cache for Redis SKU"
  type        = string
  default     = "Basic"
}

variable "redis_family" {
  description = "Redis family"
  type        = string
  default     = "C"
}

variable "redis_capacity" {
  description = "Redis capacity"
  type        = number
  default     = 0
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

variable "extra_env" {
  description = "Additional environment variables for the API container"
  type        = map(string)
  default     = {}
}
