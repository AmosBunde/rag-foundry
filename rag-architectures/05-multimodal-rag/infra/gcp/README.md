# GCP Multi-Modal RAG Infrastructure

Terraform module for deploying the Multi-Modal RAG backend on Google Cloud.

## Resources

- VPC and subnets
- Cloud Run service for the FastAPI backend
- Cloud SQL Postgres
- Memorystore Redis (Celery broker + rate limiting)
- Cloud Storage buckets for media assets
- Secret Manager for credentials
- Optional Cloud CDN + Load Balancer for custom domains

## Usage

```bash
cd infra/gcp
terraform init
terraform apply \
  -var="project_id=my-gcp-project" \
  -var="api_image=gcr.io/my-gcp-project/multimodal-rag-backend:latest" \
  -var="api_secret_key=$(openssl rand -hex 32)" \
  -var="postgres_password=$(openssl rand -hex 16)"
```

## Notes

- Replace `qdrant_url` placeholder with Vertex AI Vector Search, a self-hosted Qdrant endpoint, or another vector store.
