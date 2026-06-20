# Agentic RAG Hospital — Azure Terraform Module

Production-ready Azure infrastructure for the Agentic RAG Hospital backend using Container Apps, PostgreSQL Flexible Server, Azure Cache for Redis, Storage Accounts, Key Vault, and Front Door.

## Architecture

- **Compute:** Azure Container Apps
- **Database:** Azure Database for PostgreSQL Flexible Server
- **Cache:** Azure Cache for Redis
- **Object Storage:** Azure Storage Account
- **Ingress:** Azure Front Door
- **Secrets:** Azure Key Vault

## Prerequisites

- Azure CLI authenticated
- Terraform >= 1.5
- Container image available at `api_image`

## Usage

```bash
cd infra/azure
terraform init
terraform apply \
  -var="location=East US" \
  -var="api_image=<acr>.azurecr.io/agentic-rag-hospital-backend:latest" \
  -var="api_secret_key=$(openssl rand -base64 48)" \
  -var="postgres_admin_password=$(openssl rand -base64 32)"
```

## Placeholders

- `QDRANT_URL` and `ELASTICSEARCH_URL` are placeholders. Replace with Azure AI Search or self-hosted endpoints before production use.
