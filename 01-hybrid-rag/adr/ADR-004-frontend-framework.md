# ADR 004: Choice of Frontend Framework

## Status

Accepted

## Context

Each architecture template needs a frontend scaffold that demonstrates how a user interface consumes the backend API. The scaffold should be familiar to most web developers, support TypeScript, server-side rendering, and straightforward deployment alongside the backend.

## Decision

Use **Next.js** (App Router) as the frontend framework.

- The `frontend/` directory is bootstrapped as a Next.js application with `src/`, `public/`, `tests/`, and `e2e/` folders.
- The frontend communicates with the FastAPI backend over REST.
- Authentication uses JWT bearer tokens stored securely (e.g., HTTP-only cookies in production).

At the time of writing, the frontend is an empty scaffold; implementers should add pages for ingestion, query, and result inspection.

## Consequences

- Positive: Next.js is widely adopted, well-documented, and deployable to Vercel, Netlify, AWS Amplify, Azure Static Web Apps, or self-hosted Docker containers.
- Positive: React-based UI patterns match the skill sets of most frontend engineers.
- Positive: API routes and server components can proxy requests to the backend, hiding secrets from the browser.
- Negative: Next.js adds Node.js build complexity compared to a static HTML demo.
- Negative: An empty scaffold does not provide a runnable UI until pages are implemented.

## Alternatives Considered

- **Plain React + Vite**: simpler build pipeline but loses SSR and file-based routing.
- **SvelteKit**: smaller bundle sizes but less ecosystem familiarity.
- **Streamlit**: rapid for demos but too opinionated and hard to style for production UIs.

## References

- [Next.js documentation](https://nextjs.org/docs)
- [FastAPI CORS configuration](../backend/app/main.py)
