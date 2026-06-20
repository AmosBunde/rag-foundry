# Graph RAG — AWS Deployment

This Terraform module provisions a VPC, ECS Fargate service, RDS Postgres, ElastiCache Redis, S3 assets bucket, and an application load balancer for the Graph RAG backend.

## Data stores

- **Qdrant** and **Neo4j** are referenced via endpoint variables. Use self-managed instances, Neo4j Aura, or a managed vector store such as Amazon OpenSearch Serverless with vector engine.
- **RDS Postgres** is used for operational metadata.
- **ElastiCache Redis** backs rate limiting.

## Usage

```bash
cd infra/aws
terraform init
terraform apply \
  -var="api_image=<account>.dkr.ecr.us-east-1.amazonaws.com/graph-rag-backend:latest" \
  -var="postgres_password=$(openssl rand -base64 32)" \
  -var="api_secret_key=$(openssl rand -base64 48)" \
  -var="neo4j_endpoint=bolt://..."
```

## Variables

| Name | Description | Default |
|------|-------------|---------|
| `api_image` | Backend container image | required |
| `api_port` | Container port | `8002` |
| `neo4j_endpoint` | Neo4j Bolt URI | `bolt://neo4j.internal:7687` |
| `qdrant_endpoint` | Qdrant URL | `http://qdrant.internal:6333` |
| `postgres_password` | RDS password | required |
| `api_secret_key` | JWT secret | required |
