# ADR 001: Choice of Multi-Agent Framework for Medical QA

## Status

Accepted

## Context

The Agentic RAG Hospital architecture must answer medical questions by decomposing a user query into discrete, observable steps. We need a framework that:

1. Supports stateful, multi-step workflows.
2. Allows each step (planning, retrieval, verification, response) to be independently tested and observed.
3. Integrates with LangChain/LangChain-compatible LLM clients.
4. Runs locally without cloud dependencies.

## Decision

Use **LangGraph** on top of **LangChain** to model the medical QA workflow as a directed graph of agent nodes.

- **LangGraph** manages the shared `AgentState` and orchestrates transitions between planner, retriever, verifier, and responder nodes.
- **LangChain** provides the base abstractions; our `LLMClient` wraps Ollama for local inference.
- Each node is async, making it compatible with FastAPI's async request handlers.

## Consequences

- Positive: Observable reasoning steps are first-class citizens in the graph state.
- Positive: Nodes can be mocked independently for unit and integration tests.
- Positive: The graph can be extended with additional safety or specialty nodes.
- Negative: LangGraph is an additional dependency with its own release cadence.
- Negative: Graph debugging requires understanding of state transitions.

## Alternatives Considered

- **Plain Python functions**: simpler but loses explicit state management and observability.
- **CrewAI / AutoGen**: powerful agent frameworks but heavier than needed for a deterministic medical QA pipeline.

## References

- [LangGraph documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain documentation](https://python.langchain.com/)
