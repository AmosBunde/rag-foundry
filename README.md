# RAG Foundry

[![CI](https://github.com/AmosBunde/rag-foundry/actions/workflows/ci.yml/badge.svg)](https://github.com/AmosBunde/rag-foundry/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready template collection implementing 5 advanced Retrieval-Augmented Generation (RAG) patterns. Each architecture ships with a full-stack backend, Next.js frontend, infrastructure-as-code (Terraform), guardrails, observability, and deployment guides.

## 🏗️ Architectures Included

| # | Architecture | Use Case | Key Tech |
|---|-------------|----------|----------|
| 01 | [Hybrid RAG](01-hybrid-rag/) | Combining dense + sparse retrieval | FastAPI + Qdrant + Elasticsearch + RRF |
| 02 | [Graph RAG](02-graph-rag/) | Knowledge graph enhanced retrieval | FastAPI + Neo4j + NetworkX |
| 03 | [Agentic RAG (Hospital)](03-agentic-rag-hospital/) | Multi-agent medical QA | FastAPI + LangGraph + FHIR |
| 04 | [Corrective RAG](04-corrective-rag/) | Self-correcting retrieval loops | FastAPI + feedback loops + re-ranking |
| 05 | [Multi-Modal RAG](05-multimodal-rag/) | Text + image + audio retrieval | FastAPI + Celery + Qdrant |

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12 (for backend development)
- Node.js 20+ (for frontend development)
- (Optional) Ollama for local embeddings/LLM inference

### Run all shared services locally

```bash
make up
```

This starts Postgres, Redis, Qdrant, Elasticsearch, Neo4j, and Ollama.

### Run a specific architecture

```bash
# Backend (example: Hybrid RAG)
cd 01-hybrid-rag/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest

# Frontend
cd ../frontend
npm install
npm run dev
```

## 🧪 Testing

Run tests for all architectures:

```bash
make test
```

Run tests for a single architecture:

```bash
make test ARCH=01-hybrid-rag
```

Each backend test suite enforces a minimum 80% code coverage gate.

## 📊 Comparison Matrix

| Dimension | Hybrid RAG | Graph RAG | Agentic RAG | Corrective RAG | Multi-Modal RAG |
|-----------|-----------|-----------|-------------|----------------|-----------------|
| Latency | Low | Medium | Medium-High | Medium | Medium-High |
| Cost | Low | Medium | Medium | Low | Medium |
| Complexity | Medium | High | High | Medium | High |
| Best For | General QA | Structured knowledge | Medical/Agent workflows | High-precision QA | Media-rich QA |

## 📁 Repository Structure

```
├── 01-hybrid-rag/
├── 02-graph-rag/
├── 03-agentic-rag-hospital/
├── 04-corrective-rag/
├── 05-multimodal-rag/
├── docs/
│   ├── adr/
│   └── c4/
├── .github/
│   └── workflows/
├── scripts/
├── docker-compose.yml
├── Makefile
├── LICENSE
└── README.md
```

## 🌍 Deployment

Each architecture includes Terraform modules for:

- Bare Metal / VPS
- AWS
- Azure
- GCP

Deploy via GitHub Actions (`deploy-aws.yml`, `deploy-azure.yml`, `deploy-gcp.yml) or manually from the `infra/<cloud>` directory. See each architecture's README for cloud-specific instructions.

## 🔒 Security & Guardrails

Every architecture includes:

- JWT-based authentication
- Redis-backed rate limiting
- Input guardrails (PII, prompt injection, toxicity)
- OpenTelemetry traces and Prometheus metrics
- Structured JSON logging

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/<architecture>-<change>`.
3. Make your changes with tests.
4. Open a PR against `main`.
5. Squash and merge after review.

## 📜 License

MIT — see [LICENSE](LICENSE).
