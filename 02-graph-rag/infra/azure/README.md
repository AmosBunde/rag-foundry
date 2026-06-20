# Graph RAG — Azure Deployment

This module deploys the Graph RAG backend to Azure Container Apps with Azure Database for PostgreSQL, Azure Cache for Redis, Azure Key Vault, and Azure Front Door.

## Data stores

- **Neo4j** and **Qdrant** are configured via endpoint variables. Use Neo4j Aura, a self-managed Neo4j cluster, Azure Managed Instance for Apache Cassandra with graph extensions, or a self-hosted Qdrant deployment.
- **Azure Database for PostgreSQL** holds operational metadata.
- **Azure Cache for Redis** backs rate limiting.

## Usage

```bash
cd infra/azure
terraform init
terraform apply \
  -var="api_image=<registry>.azurecr.io/graph-rag-backend:latest" \
  -var="location=westeurope" \
  -var="postgres_admin_password=$(openssl rand -base64 32)" \
  -var="api_secret_key=$(openssl rand -base64 48)" \
  -var="neo4j_endpoint=bolt://..."
```

## Variables

| Name | Description | Default |
|------|-------------|---------|
| `api_image` | Backend container image | required |
| `api_port` | Container port | `8002` |
| `neo4j_endpoint` | Neo4j Bolt URI | `bolt://neo4j.internal:7687` |
| `qdrant_endpoint` | Qdrant URL | `https://qdrant.internal:6333` |
| `postgres_admin_password` | PostgreSQL password | required |
| `api_secret_key` | JWT secret | required |
