# Hybrid RAG — Azure Terraform Module

Production-ready Azure infrastructure for the Hybrid RAG backend using Container Apps, Azure Database for PostgreSQL, Azure Cache for Redis, Blob Storage, Front Door, Key Vault, and Monitor.

## Architecture

- **Compute:** Azure Container Apps
- **Database:** Azure Database for PostgreSQL Flexible Server
- **Cache:** Azure Cache for Redis
- **Object Storage:** Azure Blob Storage
- **Ingress:** Azure Front Door
- **Secrets:** Azure Key Vault
- **Monitoring:** Log Analytics Workspace

## Prerequisites

- Azure CLI authenticated (`az login`)
- Terraform >= 1.5
- A container image pushed to ACR or Docker Hub referenced by `api_image`

## Usage

```bash
cd infra/azure
terraform init
terraform apply \
  -var="location=East US" \
  -var="api_image=hybridrag.azurecr.io/backend:latest" \
  -var="api_secret_key=$(openssl rand -base64 48)" \
  -var="postgres_admin_password=$(openssl rand -base64 32)"
```

## Important placeholders

- `ELASTICSEARCH_URL` and `QDRANT_URL` are set to placeholder values. For production, replace them with Azure AI Search / self-hosted Qdrant endpoints.
- Point a custom domain to the Front Door endpoint and add a Front Door custom domain resource if needed.

## Cost estimate (monthly, East US, 2024)

| Component | Spec | ~Monthly |
|-----------|------|----------|
| Container Apps | 1 vCPU / 2 GB, always-on | $35–55 |
| PostgreSQL | B_Standard_B1ms, 32 GB | $15–25 |
| Redis | Basic C0 | $15–20 |
| Front Door | Standard | $15–35 |
| Blob Storage | < 100 GB | $2–5 |
| Key Vault | few secrets | ~$0.03 |
| Monitor | Log Analytics | $5–20 |

Total: **~$90–165/month** depending on traffic.
