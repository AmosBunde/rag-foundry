# ADR 002: Security Baseline for RAG Templates

## Status
Accepted

## Context
RAG systems process untrusted user queries and often handle sensitive documents. The templates must demonstrate production-ready security controls without requiring external cloud accounts or paid APIs.

## Decision
Every architecture implements the following baseline:

1. **Authentication**: JWT Bearer tokens (mock provider) for all state-changing and retrieval endpoints.
2. **Authorization**: Per-endpoint dependency injection of the current user; disabled users are rejected.
3. **Input validation**: Strict Pydantic models with length limits and field constraints.
4. **Guardrails**: Regex + optional Presidio for PII, heuristic prompt-injection detection, and mock toxicity filtering.
5. **Rate limiting**: Redis-backed sliding-window rate limits via `slowapi`.
6. **Transport**: TLS terminated at the reverse proxy (Nginx/ALB/CloudFront/Front Door/CDN).
7. **Secrets**: Externalized via environment variables; cloud modules use native secret managers (Secrets Manager, Key Vault, Secret Manager).
8. **Observability**: Structured JSON logs, Prometheus metrics, and OpenTelemetry traces.

Cloud-specific security services (AWS Comprehend, Azure Content Safety, GCP DLP) are documented but mocked locally.

## Consequences
- Positive: Templates are secure-by-default and easy to audit.
- Positive: No hardcoded secrets or paid API dependencies for local development.
- Negative: Some guardrails are heuristic-only; production deployments should integrate real content-safety APIs.

## Alternatives Considered
- OAuth2/OIDC provider integration: more realistic but adds setup complexity; mock JWT keeps templates self-contained.
- No guardrails: unacceptable for production templates.

## References
- `01-hybrid-rag/backend/app/guardrails.py`
- `01-hybrid-rag/guardrails/`
