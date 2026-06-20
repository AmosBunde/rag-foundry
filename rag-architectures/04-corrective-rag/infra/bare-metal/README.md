# Hybrid RAG — Bare-Metal / VM Deployment

This module generates Docker Compose, Nginx, systemd, and deployment scripts for running the Hybrid RAG stack on a single bare-metal or VM host.

## What's included

- `docker-compose.yml` — FastAPI backend + Postgres + Redis + Qdrant + Elasticsearch + optional Ollama
- `nginx.conf` — Reverse proxy to the FastAPI service on port 8001
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
| `app_image` | Backend Docker image | `rag-foundry/hybrid-rag-backend:latest` |
| `ollama_enabled` | Run Ollama container locally | `false` |
| `enable_https` | Enable Let's Encrypt HTTPS | `true` |

## Notes

- Ollama with local LLMs requires a GPU and the NVIDIA Container Toolkit on the host. For CPU-only or cost-sensitive deployments, leave `ollama_enabled=false` and point `OLLAMA_URL` to an external Ollama/OpenAI-compatible endpoint via `extra_env`.
- All persistent data uses named Docker volumes. Back them up with `docker run --rm -v hybrid-rag_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres.tgz -C /data .`.
- The Nginx container uses host networking for simplicity. This is acceptable for a single-host deployment.

## Cost

Infrastructure cost is just the host/volume bill. Estimated monthly (US regions, 2024):

| Host type | vCPU / RAM | ~Monthly |
|-----------|-----------|----------|
| Entry Hetzner / OVH | 4 vCPU / 16 GB | $25–45 |
| AWS EC2 m6i.xlarge | 4 vCPU / 16 GB | $140–160 |
| GCP e2-standard-4 | 4 vCPU / 16 GB | $135–155 |

Add block storage for the databases (~$0.10/GB/month). GPU nodes for Ollama start around $400–700/month.
