# Agentic RAG Hospital — Bare-Metal / VM Deployment

This module generates Docker Compose, Nginx, systemd, and deployment scripts for running the Agentic RAG Hospital stack on a single bare-metal or VM host.

## What's included

- `docker-compose.yml` — FastAPI backend + Postgres + Redis + Qdrant + Elasticsearch + optional Ollama
- `nginx.conf` — Reverse proxy to the FastAPI service on port 8003
- systemd service units for Docker Compose and Nginx
- `deploy.sh` — SCP/SSH helper to push artifacts to the host
- Certbot/Let's Encrypt integration for HTTPS

## Usage

```bash
cd infra/bare-metal
terraform init
terraform apply -var="domain=rag.example.com" \
                -var="admin_email=admin@example.com" \
                -var="host_ip=203.0.113.10" \
                -var="postgres_password=$(openssl rand -base64 32)" \
                -var="redis_password=$(openssl rand -base64 32)" \
                -var="api_secret_key=$(openssl rand -base64 48)"
```

After apply, the rendered files are in `out/`. To deploy to the remote host:

```bash
bash out/deploy.sh
```

## Variables

| Name | Description | Default |
|------|-------------|---------|
| `domain` | Public domain for the API | required |
| `admin_email` | Let's Encrypt email | required |
| `host_ip` | Host IP or DNS | required |
| `host_user` | SSH user | `ubuntu` |
| `app_image` | Backend Docker image | `rag-foundry/agentic-rag-hospital-backend:latest` |
| `ollama_enabled` | Run Ollama container locally | `false` |
| `enable_https` | Enable Let's Encrypt HTTPS | `true` |

## Notes

- Ollama with local LLMs requires a GPU and the NVIDIA Container Toolkit on the host.
- All persistent data uses named Docker volumes.
- The Nginx container uses host networking for simplicity.
