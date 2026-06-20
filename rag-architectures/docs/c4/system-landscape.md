# C4 System Landscape

## RAG Foundry Ecosystem

```mermaid
graph TB
    User[Developer / Evaluator]
    subgraph rag-foundry [RAG Foundry Repository]
        HR[01 Hybrid RAG]
        GR[02 Graph RAG]
        AR[03 Agentic RAG Hospital]
        CR[04 Corrective RAG]
        MR[05 Multi-Modal RAG]
        Shared[Shared Infra & CI/CD]
    end
    User --> HR
    User --> GR
    User --> AR
    User --> CR
    User --> MR
    Shared --> HR
    Shared --> GR
    Shared --> AR
    Shared --> CR
    Shared --> MR
```

## Purpose
This landscape shows the five RAG architecture templates coexisting in a single repository, each independent but sharing common tooling and deployment patterns.
