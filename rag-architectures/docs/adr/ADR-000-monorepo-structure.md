# ADR 000: Monorepo Structure for RAG Architecture Templates

## Status
Accepted

## Context
We need a single repository that hosts multiple independent, production-ready RAG architecture templates. Each template must be deployable on its own while sharing common conventions, CI/CD, and documentation patterns.

## Decision
Adopt a monorepo with a top-level `rag-architectures/` directory. Each architecture is a self-contained folder with backend, frontend, infra, tests, guardrails, ADRs, and C4 diagrams. Shared automation lives at the root (`Makefile`, `docker-compose.yml`, `scripts/`, `.github/`).

## Consequences
- Positive: Easier cross-architecture comparison, shared CI/CD, consistent conventions.
- Negative: Larger repository, potential dependency version drift between architectures.
- Risks: Engineers may accidentally couple architectures; mitigated by clear boundaries and independent Dockerfiles.

## Alternatives Considered
- Separate repositories per architecture: better isolation but harder to maintain consistency.
- Single shared backend/frontend with feature flags: too complex and reduces clarity of each pattern.

## References
- [C4 System Landscape](../c4/system-landscape.md)
