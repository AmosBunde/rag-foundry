# ADR 004: Choice of Frontend Framework

## Status

Accepted

## Context

The frontend must demonstrate how a user interface consumes the Agentic RAG Hospital backend, display agent reasoning, and support patient lookup.

## Decision

Use **Next.js** (App Router) with **Tailwind CSS** and **shadcn/ui** components.

- The `frontend/` directory is bootstrapped as a Next.js application.
- TanStack Query handles server state for chat, ingestion, and patient requests.
- An accordion component exposes agent reasoning steps and sources to the user.

## Consequences

- Positive: Next.js is widely adopted and deployable to many platforms.
- Positive: shadcn/ui gives accessible, composable components without a heavy runtime.
- Positive: The reasoning accordion makes the multi-agent system transparent to users.
- Negative: Next.js adds Node.js build complexity compared to a static demo.

## Alternatives Considered

- **Plain React + Vite**: simpler build but loses SSR and file-based routing.
- **Streamlit**: rapid for demos but too opinionated for production UIs.

## References

- [Next.js documentation](https://nextjs.org/docs)
- [shadcn/ui documentation](https://ui.shadcn.com/)
