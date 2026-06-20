terraform {
  required_version = ">= 1.5.0"
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = ">= 2.4"
    }
    null = {
      source  = "hashicorp/null"
      version = ">= 3.2"
    }
  }
}

locals {
  api_env = merge({
    APP_NAME    = var.project_name
    ENVIRONMENT = var.environment
    PORT        = var.api_port
    LOG_LEVEL   = "info"

    SECRET_KEY = var.api_secret_key

    REDIS_URL             = "redis://:${var.redis_password}@redis:6379/0"
    CELERY_BROKER_URL     = "redis://:${var.redis_password}@redis:6379/0"
    CELERY_RESULT_BACKEND = "redis://:${var.redis_password}@redis:6379/0"
    QDRANT_URL            = "http://qdrant:6333"
    POSTGRES_URL          = "postgresql+asyncpg://${var.postgres_user}:${var.postgres_password}@postgres:5432/${var.postgres_db}"
    OLLAMA_URL            = var.ollama_enabled ? "http://ollama:11434" : ""

    LLM_MODEL             = "llama3:8b"
    EMBEDDING_MODEL       = "nomic-embed-text"
    MULTIMODAL_COLLECTION = "multimodal_rag"
    VECTOR_SIZE           = "512"
    DEFAULT_TOP_K         = "5"
    MOCK_EMBEDDINGS       = var.ollama_enabled ? "false" : "true"
  }, var.extra_env)
}

# ---------------------------------------------------------------------------
# Rendered deployment artifacts
# ---------------------------------------------------------------------------

resource "local_file" "docker_compose" {
  filename        = "${path.module}/out/docker-compose.yml"
  file_permission = "0644"
  content = templatefile("${path.module}/templates/docker-compose.yml.tpl", {
    project_name = var.project_name
    environment  = var.environment
    app_image    = var.app_image
    api_port     = var.api_port
    api_env      = local.api_env

    postgres_user     = var.postgres_user
    postgres_password = var.postgres_password
    postgres_db       = var.postgres_db

    redis_password = var.redis_password

    ollama_enabled = var.ollama_enabled
    ollama_image   = var.ollama_image
    ollama_models  = var.ollama_models

    docker_network = var.docker_network
  })
}

resource "local_file" "nginx_conf" {
  filename        = "${path.module}/out/nginx.conf"
  file_permission = "0644"
  content = templatefile("${path.module}/templates/nginx.conf.tpl", {
    domain     = var.domain
    api_port   = var.api_port
    enable_https = var.enable_https
  })
}

resource "local_file" "api_systemd" {
  filename        = "${path.module}/out/multimodal-rag-api.service"
  file_permission = "0644"
  content = templatefile("${path.module}/templates/systemd-api.service.tpl", {
    project_name = var.project_name
    deploy_path  = var.deploy_path
  })
}

resource "local_file" "nginx_systemd" {
  filename        = "${path.module}/out/multimodal-rag-nginx.service"
  file_permission = "0644"
  content = templatefile("${path.module}/templates/systemd-nginx.service.tpl", {
    deploy_path = var.deploy_path
  })
}

resource "local_file" "deploy_script" {
  filename        = "${path.module}/out/deploy.sh"
  file_permission = "0755"
  content = templatefile("${path.module}/templates/deploy.sh.tpl", {
    host_ip              = var.host_ip
    host_user            = var.host_user
    ssh_private_key_path = var.ssh_private_key_path
    deploy_path          = var.deploy_path
    enable_https         = var.enable_https
    admin_email          = var.admin_email
    domain               = var.domain
  })
}

resource "local_file" "env_file" {
  filename        = "${path.module}/out/.env"
  file_permission = "0600"
  content = join("\n", [
    for k, v in local.api_env : "${k}=${v}"
  ])
}

# ---------------------------------------------------------------------------
# Optional remote deployment trigger
# ---------------------------------------------------------------------------

resource "null_resource" "deploy" {
  count = 0 # Disabled by default; set to 1 to run the deploy script after apply

  triggers = {
    compose_hash = local_file.docker_compose.content_sha256
    nginx_hash   = local_file.nginx_conf.content_sha256
  }

  provisioner "local-exec" {
    command = "bash ${local_file.deploy_script.filename}"
  }
}
