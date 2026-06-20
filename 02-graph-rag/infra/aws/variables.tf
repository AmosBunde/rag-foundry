variable "project_name" {
  description = "Project name used for tagging and resource naming"
  type        = string
  default     = "graph-rag"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "az_count" {
  description = "Number of availability zones to use"
  type        = number
  default     = 2
}

variable "api_port" {
  description = "FastAPI container port"
  type        = number
  default     = 8002
}

variable "api_image" {
  description = "Backend container image (ECR or Docker Hub)"
  type        = string
}

variable "api_cpu" {
  description = "Fargate task CPU units"
  type        = number
  default     = 1024
}

variable "api_memory" {
  description = "Fargate task memory (MiB)"
  type        = number
  default     = 2048
}

variable "api_desired_count" {
  description = "Desired number of API tasks"
  type        = number
  default     = 2
}

variable "api_secret_key" {
  description = "FastAPI secret key"
  type        = string
  sensitive   = true
}

variable "postgres_username" {
  description = "RDS Postgres master username"
  type        = string
  default     = "rag"
}

variable "postgres_password" {
  description = "RDS Postgres master password"
  type        = string
  sensitive   = true
}

variable "postgres_db" {
  description = "RDS Postgres database name"
  type        = string
  default     = "rag"
}

variable "postgres_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t4g.micro"
}

variable "qdrant_endpoint" {
  description = "Qdrant vector store URL (self-managed or managed endpoint)"
  type        = string
  default     = "http://qdrant.internal:6333"
}

variable "neo4j_endpoint" {
  description = "Neo4j Bolt URI (self-managed or Neo4j Aura)"
  type        = string
  default     = "bolt://neo4j.internal:7687"
}

variable "ollama_endpoint" {
  description = "Ollama or OpenAI-compatible embeddings/LLM endpoint"
  type        = string
  default     = ""
}

variable "domain_name" {
  description = "Primary domain name for CloudFront / ALB"
  type        = string
  default     = ""
}

variable "route53_zone_id" {
  description = "Route53 hosted zone ID for the domain"
  type        = string
  default     = ""
}

variable "enable_cdn" {
  description = "Enable CloudFront distribution in front of the ALB"
  type        = bool
  default     = false
}

variable "allowed_cidr" {
  description = "CIDR allowed to access the ALB (empty = open)"
  type        = string
  default     = "0.0.0.0/0"
}

variable "extra_env" {
  description = "Additional environment variables for the API container"
  type        = map(string)
  default     = {}
}
