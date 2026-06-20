variable "project_name" {
  description = "Project name used for tagging and resource naming"
  type        = string
  default     = "multimodal-rag"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "api_port" {
  description = "FastAPI container port"
  type        = number
  default     = 8005
}

variable "api_image" {
  description = "Backend container image"
  type        = string
}

variable "api_cpu" {
  description = "Container App CPU cores (e.g. 0.5, 1.0)"
  type        = number
  default     = 1.0
}

variable "api_memory" {
  description = "Container App memory in GiB"
  type        = string
  default     = "2Gi"
}

variable "api_min_replicas" {
  description = "Minimum number of API replicas"
  type        = number
  default     = 1
}

variable "api_max_replicas" {
  description = "Maximum number of API replicas"
  type        = number
  default     = 3
}

variable "api_secret_key" {
  description = "FastAPI secret key"
  type        = string
  sensitive   = true
}

variable "postgres_admin_username" {
  description = "PostgreSQL admin username"
  type        = string
  default     = "ragadmin"
}

variable "postgres_admin_password" {
  description = "PostgreSQL admin password"
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
  default     = "B_Standard_B1ms"
}

variable "redis_sku" {
  description = "Azure Cache for Redis SKU"
  type        = string
  default     = "Basic"
}

variable "redis_family" {
  description = "Azure Cache for Redis family"
  type        = string
  default     = "C"
}

variable "redis_capacity" {
  description = "Azure Cache for Redis capacity"
  type        = number
  default     = 0
}

variable "domain_name" {
  description = "Custom domain name for Front Door"
  type        = string
  default     = ""
}

variable "extra_env" {
  description = "Additional environment variables for the API container"
  type        = map(string)
  default     = {}
}
