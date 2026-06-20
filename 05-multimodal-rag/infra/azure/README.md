# Azure Multi-Modal RAG Infrastructure

Terraform module for deploying the Multi-Modal RAG backend on Azure.

## Resources

- Resource group and virtual network
- Azure Container Apps for the FastAPI backend
- Azure Database for PostgreSQL flexible server
- Azure Cache for Redis (Celery broker + rate limiting)
- Storage accounts for media assets
- Key Vault for secrets
- Azure Front Door for CDN/load balancing

## Usage

```bash
cd infra/azure
terraform init
terraform apply \
  -var="api_image=your-acr.azurecr.io/multimodal-rag-backend:latest" \
  -var="api_secret_key=$(openssl rand -hex 32)" \
  -var="postgres_admin_password=$(openssl rand -hex 16)"
```

## Notes

- Replace `qdrant_url` placeholder with Azure AI Search, a self-hosted Qdrant endpoint, or another vector store.
