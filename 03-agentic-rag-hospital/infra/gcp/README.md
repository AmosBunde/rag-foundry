# Agentic RAG Hospital — GCP Terraform Module

Production-ready GCP infrastructure for the Agentic RAG Hospital backend using Cloud Run, Cloud SQL Postgres, Memorystore Redis, Cloud Storage, Secret Manager, and Cloud Monitoring.

## Architecture

- **Compute:** Cloud Run
- **Database:** Cloud SQL Postgres
- **Cache:** Memorystore for Redis
- **Object Storage:** Cloud Storage
- **Ingress:** Cloud Load Balancing (optional)
- **Secrets:** Secret Manager

## Prerequisites

- gcloud CLI authenticated
- Terraform >= 1.5
- Container image at `api_image`

## Usage

```bash
cd infra/gcp
terraform init
terraform apply \
  -var="project_id=my-gcp-project" \
  -var="region=us-central1" \
  -var="api_image=gcr.io/my-gcp-project/agentic-rag-hospital-backend:latest" \
  -var="api_secret_key=$(openssl rand -base64 48)" \
  -var="postgres_password=$(openssl rand -base64 32)"
```

## Placeholders

- `QDRANT_URL` and `ELASTICSEARCH_URL` are placeholders. Replace with Vertex AI Vector Search, Elastic Cloud, or self-hosted endpoints.
