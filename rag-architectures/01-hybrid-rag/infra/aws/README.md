# Hybrid RAG — AWS Terraform Module

Production-ready AWS infrastructure for the Hybrid RAG backend using ECS Fargate, RDS Postgres, ElastiCache Redis, S3, ALB, CloudFront, Secrets Manager, and CloudWatch.

## Architecture

- **Compute:** ECS Fargate (serverless containers) with CloudWatch Logs
- **Database:** RDS Postgres (multi-AZ ready)
- **Cache:** ElastiCache for Redis
- **Object Storage:** S3
- **Ingress:** ALB + optional CloudFront
- **Secrets:** AWS Secrets Manager
- **DNS:** Route53 (optional)

## Prerequisites

- AWS CLI configured
- Terraform >= 1.5
- A container image pushed to ECR or Docker Hub referenced by `api_image`
- (Optional) Route53 hosted zone for TLS + custom domain

## Usage

```bash
cd infra/aws
terraform init
terraform apply \
  -var="aws_region=us-east-1" \
  -var="api_image=123456789012.dkr.ecr.us-east-1.amazonaws.com/hybrid-rag-backend:latest" \
  -var="api_secret_key=$(openssl rand -base64 48)" \
  -var="postgres_password=$(openssl rand -base64 32)" \
  -var="domain_name=rag.example.com" \
  -var="route53_zone_id=ZXXXXXXXXXXXXX" \
  -var="enable_cdn=true"
```

## Important placeholders

- `QDRANT_URL` and `ELASTICSEARCH_URL` are set to placeholder internal hostnames. Replace them with managed service endpoints (e.g., Amazon OpenSearch for Elasticsearch) before production deployment.
- For local embeddings/LLM, keep `ollama_url` empty and inject an external provider via `extra_env`.

## Cost estimate (monthly, us-east-1, 2024)

| Component | Spec | ~Monthly |
|-----------|------|----------|
| ECS Fargate | 2 tasks × 1 vCPU / 2 GB | $70–90 |
| RDS Postgres | db.t4g.micro, 20 GB | $15–20 |
| ElastiCache Redis | cache.t4g.micro | $15–20 |
| ALB | 1 ALB | $20–25 |
| S3 | < 100 GB | $2–5 |
| CloudFront | < 1 TB transfer | $10–50 |
| Secrets Manager | 1 secret | ~$0.40 |

Total: **~$140–220/month** depending on traffic and data volume.
