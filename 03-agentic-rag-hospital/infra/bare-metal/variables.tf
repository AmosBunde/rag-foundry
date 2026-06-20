variable "project_name" {
  description = "Project name used for resource naming and labels"
  type        = string
  default     = "agentic-rag-hospital"
}

variable "environment" {
  description = "Deployment environment (e.g. staging, production)"
  type        = string
  default     = "production"
}

variable "domain" {
  description = "Public domain name for the Agentic RAG Hospital API"
  type        = string
}

variable "admin_email" {
  description = "Email address used for Let's Encrypt certificate registration"
  type        = string
}

variable "host_ip" {
  description = "Public IP or DNS name of the bare-metal host"
  type        = string
}

variable "host_user" {
  description = "SSH user for the bare-metal host"
  type        = string
  default     = "ubuntu"
}

variable "ssh_private_key_path" {
  description = "Path to the SSH private key used to connect to the host"
  type        = string
  default     = "~/.ssh/id_rsa"
}

variable "api_port" {
  description = "Port exposed by the FastAPI backend container"
  type        = number
  default     = 8003
}

variable "postgres_user" {
  description = "Postgres username"
  type        = string
  default     = "rag"
}

variable "postgres_password" {
  description = "Postgres password"
  type        = string
  sensitive   = true
}

variable "postgres_db" {
  description = "Postgres database name"
  type        = string
  default     = "rag"
}

variable "redis_password" {
  description = "Redis password"
  type        = string
  sensitive   = true
}

variable "api_secret_key" {
  description = "FastAPI secret key for JWT signing"
  type        = string
  sensitive   = true
}

variable "ollama_enabled" {
  description = "Enable the Ollama container on the host"
  type        = bool
  default     = false
}

variable "ollama_image" {
  description = "Ollama Docker image"
  type        = string
  default     = "ollama/ollama:latest"
}

variable "ollama_models" {
  description = "List of Ollama models to pull on startup"
  type        = list(string)
  default     = ["llama3:8b", "nomic-embed-text"]
}

variable "app_image" {
  description = "Docker image for the Agentic RAG Hospital FastAPI backend"
  type        = string
  default     = "rag-foundry/agentic-rag-hospital-backend:latest"
}

variable "docker_network" {
  description = "Docker bridge network name"
  type        = string
  default     = "agentic-rag-hospital"
}

variable "deploy_path" {
  description = "Remote path where deployment files are uploaded"
  type        = string
  default     = "/opt/agentic-rag-hospital"
}

variable "enable_https" {
  description = "Enable HTTPS via Let's Encrypt; set false for local/lab deployments"
  type        = bool
  default     = true
}

variable "extra_env" {
  description = "Additional environment variables injected into the API container"
  type        = map(string)
  default     = {}
}
