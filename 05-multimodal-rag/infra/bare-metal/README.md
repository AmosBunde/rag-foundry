# Bare-Metal / VPS Multi-Modal RAG Infrastructure

Terraform module for rendering Docker Compose, nginx, systemd, and deploy scripts for a self-hosted deployment.

## Rendered artifacts

- `out/docker-compose.yml` — full stack including API, Celery worker, Postgres, Redis, Qdrant, and optional Ollama
- `out/nginx.conf` — reverse proxy with optional Let's Encrypt TLS
- `out/multimodal-rag-api.service` — systemd unit for the API stack
- `out/multimodal-rag-nginx.service` — systemd unit for nginx
- `out/deploy.sh` — remote deployment script
- `out/.env` — environment file

## Usage

```bash
cd infra/bare-metal
terraform init
terraform apply \
  -var="host_ip=203.0.113.10" \
  -var="domain=rag.example.com" \
  -var="api_secret_key=$(openssl rand -hex 32)" \
  -var="postgres_password=$(openssl rand -hex 16)" \
  -var="redis_password=$(openssl rand -hex 16)"
```

To deploy remotely, set `null_resource.deploy` count to `1` after configuring SSH access.
