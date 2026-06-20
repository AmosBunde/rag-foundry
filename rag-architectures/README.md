# RAG Architecture Templates

A production-ready template collection implementing 5 advanced RAG patterns, each with full-stack backend, frontend, infrastructure-as-code, and deployment guides.

## 🏗️ Architectures Included

| # | Architecture | Use Case | Key Tech |
|---|-------------|----------|----------|
| 01 | [Hybrid RAG](01-hybrid-rag/) | Combining dense + sparse retrieval | FastAPI + Qdrant + Elasticsearch + RRF |
| 02 | [Graph RAG](02-graph-rag/) | Knowledge graph enhanced retrieval | FastAPI + Neo4j + NetworkX |
| 03 | [Agentic RAG (Hospital)](03-agentic-rag-hospital/) | Multi-agent medical QA | FastAPI + LangGraph + FHIR |
| 04 | [Corrective RAG](04-corrective-rag/) | Self-correcting retrieval loops | FastAPI + feedback loops + re-ranking |
| 05 | [Multi-Modal RAG](05-multimodal-rag/) | Text + image + audio retrieval | FastAPI + CLIP/Whisper + Qdrant |

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for backend development)
- Node.js 20+ (for frontend development)
- (Optional) Ollama for local embeddings/LLM inference

### Run all shared services locally

```bash
cd rag-architectures
make up
```

This starts Postgres, Redis, Qdrant, Elasticsearch, Neo4j, and Ollama.

### Run a specific architecture

```bash
# Backend (example: Hybrid RAG)
cd 01-hybrid-rag/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest

# Frontend
cd ../frontend
npm install
npm run dev
```

## 📊 Comparison Matrix

| Dimension | Hybrid RAG | Graph RAG | Agentic RAG | Corrective RAG | Multi-Modal RAG |
|-----------|-----------|-----------|-------------|----------------|-----------------|
| Latency | Low | Medium | Medium-High | Medium | Medium-High |
| Cost | Low | Medium | Medium | Low | Medium |
| Complexity | Medium | High | High | Medium | High |
| Best For | General QA | Structured knowledge | Medical/Agent workflows | High-precision QA | Media-rich QA |

## 📁 Repository Structure

```
rag-architectures/
├── 01-hybrid-rag/
├── 02-graph-rag/
├── 03-agentic-rag-hospital/
├── 04-corrective-rag/
├── 05-multimodal-rag/
├── docs/
│   ├── adr/
│   └── c4/
├── .github/
├── scripts/
├── docker-compose.yml
├── Makefile
├── LICENSE
└── README.md
```

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/M2-hybrid-rag-backend`.
3. Make your changes with tests.
4. Open a PR using the provided template.
5. Squash and merge after review.

## 📜 License

MIT — see [LICENSE](LICENSE).
