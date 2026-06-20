# AWS Multi-Modal RAG Infrastructure

Terraform module for deploying the Multi-Modal RAG backend on AWS.

## Resources

- VPC with public/private subnets and NAT gateways
- ECS Fargate service for the FastAPI backend
- RDS Postgres for metadata and session storage
- ElastiCache Redis for rate limiting and Celery broker
- S3 bucket for media asset storage
- Application Load Balancer with optional CloudFront CDN
- Secrets Manager for credentials

## Usage

```bash
cd infra/aws
terraform init
terraform apply \
  -var="api_image=your-ecr-repo/multimodal-rag-backend:latest" \
  -var="api_secret_key=$(openssl rand -hex 32)" \
  -var="postgres_password=$(openssl rand -hex 16)"
```

## Notes

- Replace `qdrant_url` placeholder with a managed vector DB or self-hosted Qdrant endpoint.
- For production, enable Redis transit encryption and configure TLS for Postgres.
