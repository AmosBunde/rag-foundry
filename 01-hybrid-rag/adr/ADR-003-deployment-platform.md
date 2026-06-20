# ADR 003: Deployment Platform and Tooling

## Status

Accepted

## Context

The template must support multiple deployment targets so teams can choose the environment that matches their operational maturity and cloud strategy. The deployment artefacts should be version-controlled, reproducible, and shareable across the monorepo.

## Decision

Adopt a **multi-platform deployment strategy** with two layers:

1. **Local development**: Docker Compose defined at the repository root (`docker-compose.yml`) provisions shared data stores and optional application profiles.
2. **Cloud / remote**: Terraform module scaffolds under `infra/{bare-metal,aws,azure,gcp}/` provide per-platform infrastructure-as-code starting points.

Each module is intentionally a scaffold. Teams are expected to extend modules with their own networking, secrets management, TLS, and backup policies.

## Consequences

- Positive: A single `docker compose up` gives developers a working stack without cloud accounts.
- Positive: Terraform modules can be evolved independently for each cloud provider.
- Positive: The backend ships with a Dockerfile, making container-based deployment the default path everywhere.
- Negative: The Terraform modules are not production-complete out of the box; they require customisation.
- Negative: Keeping four cloud modules up to date adds maintenance overhead.

## Alternatives Considered

- **Single-platform focus (e.g., only AWS)**: reduces maintenance but limits audience.
- **Kubernetes-first with Helm**: powerful but raises the barrier for simple VPS deployments.
- **Pulumi instead of Terraform**: equally valid, but Terraform is more widely adopted and easier to review in pull requests.

## References

- [Terraform best practices](https://developer.hashicorp.com/terraform/cloud-docs/recommended-practices)
- [Docker Compose profiles](https://docs.docker.com/compose/profiles/)
- [RAG Foundry docker-compose.yml](../docker-compose.yml)
