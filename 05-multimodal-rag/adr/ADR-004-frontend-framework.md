# ADR 004: Frontend Framework

## Status

Accepted

## Context

The frontend must support JWT auth, multimodal uploads, a chat/query UI, and a result gallery. It should align with the rest of the RAG Foundry templates.

## Decision

Use **Next.js 14 App Router** with **Tailwind CSS**, **shadcn/ui**, and **TanStack Query**.

- App Router enables server/client composition and route-level code splitting.
- Tailwind + shadcn/ui provide accessible, themeable components.
- TanStack Query manages server state for ingestion, uploads, and queries.
- The UI exposes tabs for text/image/audio ingestion and a gallery with modality filters.

## Consequences

- Positive: Consistent with the Hybrid RAG reference pattern.
- Positive: Strong type safety and developer experience.
- Negative: Requires careful handling of client-only APIs (localStorage, fetch).
