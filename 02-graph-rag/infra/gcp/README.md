# Graph RAG — GCP Deployment

This module deploys the Graph RAG backend to Cloud Run with Cloud SQL Postgres, Memorystore Redis, Cloud Storage, Secret Manager, and an optional global HTTPS load balancer.

## Data stores

- **Neo4j** and **Qdrant** are configured via endpoint variables. Use Neo4j Aura, self-managed GCE instances, Vertex AI Vector Search, or a managed vector store.
- **Cloud SQL Postgres** holds operational metadata.
- **Memorystore Redis** backs rate limiting.

## Usage

```bash
cd infra/gcp
terraform init
terraform apply \
  -var="project_id=my-gcp-project" \
  -var="api_image=gcr.io/<project>/graph-rag-backend:latest" \
  -var="postgres_password=$(openssl rand -base64 32)" \
  -var="api_secret_key=$(openssl rand -base64 48)" \
  -var="neo4j_endpoint=bolt://..."
```

## Variables

| Name | Description | Default |
|------|-------------|---------|
| `project_id` | GCP project ID | required |
| `api_image` | Backend container image | required |
| `api_port` | Container port | `8002` |
| `neo4j_endpoint` | Neo4j Bolt URI | `bolt://neo4j.internal:7687` |
| `qdrant_endpoint` | Qdrant URL | `https://qdrant.internal:6333` |
| `postgres_password` | Cloud SQL password | required |
| `api_secret_key` | JWT secret | required |
