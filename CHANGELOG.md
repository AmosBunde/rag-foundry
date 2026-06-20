# Changelog

All notable changes to the RAG Foundry project will be documented in this file.

## [0.1.0] - 2026-06-20

### Added
- Initial release of the RAG Foundry template collection.
- Five production-ready RAG architecture templates:
  - **01-hybrid-rag**: Dense + sparse retrieval with Reciprocal Rank Fusion.
  - **02-graph-rag**: Knowledge graph enhanced retrieval with Neo4j.
  - **03-agentic-rag-hospital**: Multi-agent medical QA with FHIR mock data.
  - **04-corrective-rag**: Self-correcting retrieval loops with confidence scoring.
  - **05-multimodal-rag**: Text + image + audio retrieval.
- Shared local orchestration via `docker-compose.yml` and `Makefile`.
- GitHub Actions CI workflow for backend tests, frontend tests, and Terraform validation.
- Per-architecture Terraform modules for bare-metal/VPS, AWS, Azure, and GCP.
- Per-architecture ADRs and C4 diagrams.
- MIT LICENSE.
