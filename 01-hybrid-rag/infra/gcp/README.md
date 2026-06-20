# Hybrid RAG — GCP Terraform Module

Production-ready GCP infrastructure for the Hybrid RAG backend using Cloud Run, Cloud SQL PostgreSQL, Memorystore Redis, Cloud Storage, Cloud CDN, Secret Manager, and Cloud Monitoring.

## Architecture

- **Compute:** Cloud Run
- **Database:** Cloud SQL for PostgreSQL
- **Cache:** Memorystore for Redis
- **Object Storage:** Cloud Storage
- **Ingress:** Cloud Load Balancing + Cloud CDN (optional with custom domain)
- **Secrets:** Secret Manager
- **Monitoring:** Cloud Monitoring dashboard

## Prerequisites

- gcloud CLI authenticated
- Terraform >= 1.5
- A container image pushed to Artifact Registry or Docker Hub referenced by `api_image`

## Usage

```bash
cd infra/gcp
terraform init
terraform apply \
  -var="project_id=my-gcp-project" \
  -var="region=us-central1" \
  -var="api_image=us-central1-docker.pkg.dev/my-gcp-project/hybrid-rag/backend:latest" \
  -var="api_secret_key=$(openssl rand -base64 48)" \
  -var="postgres_password=$(openssl rand -base64 32)" \
  -var="domain_name=rag.example.com"
```

## Important placeholders

- `ELASTICSEARCH_URL` and `QDRANT_URL` are placeholder values. For production, replace them with self-hosted or managed vector/search endpoints.
- The Cloud SQL instance uses private IP via VPC peering. Cloud Run connects through the Cloud SQL Auth Proxy automatically by using the Cloud SQL connection name in the URL.

## Cost estimate (monthly, us-central1, 2024)

| Component | Spec | ~Monthly |
|-----------|------|----------|
| Cloud Run | 1M requests, 1 vCPU / 2 GB | $10–40 |
| Cloud SQL | db-f1-micro, 20 GB | $10–15 |
| Memorystore Redis | Basic 1 GB | $15–20 |
| Cloud Storage | < 100 GB | $2–4 |
| Cloud CDN | < 1 TB | $15–50 |
| Load Balancer | 1 forwarding rule | $20–25 |
| Secret Manager | 1 secret | ~$0.06 |

Total: **~$75–160/month** depending on traffic.
