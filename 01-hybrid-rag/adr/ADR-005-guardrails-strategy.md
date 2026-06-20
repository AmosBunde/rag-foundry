# ADR 005: Guardrails Strategy

## Status

Accepted

## Context

Retrieval-Augmented Generation systems process user-controlled input that is passed to embedding models, search engines, and LLMs. Without guardrails, the system is exposed to prompt injection, PII leakage, toxic content, and abuse. The guardrails must be lightweight enough for local development yet extensible for production.

## Decision

Implement a **layered, defence-in-depth guardrails strategy**:

1. **Input validation** with Pydantic models (`QueryRequest`, `Document`, `IngestRequest`) enforces type, length, and cardinality constraints.
2. **Heuristic checks** in `backend/app/guardrails.py` detect prompt injection patterns, regex-based PII, and toxic keywords.
3. **Optional Presidio** integration provides higher-accuracy NER-based PII detection when enabled via `USE_PRESIDIO=true`.
4. **Rate limiting** via `slowapi` reduces brute-force and abuse risk; Redis-backed storage should be enabled in production.
5. **YAML configuration files** in `guardrails/` document intended rules for prompt injection, PII, content safety, and rate limits, even when the backend currently uses the Python implementations directly.

Guardrails block requests by raising an HTTP 400 with a structured error containing the violations.

## Consequences

- Positive: Multiple independent layers reduce the chance of a single bypass.
- Positive: Regex checks work offline with no external API calls.
- Positive: Presidio can be enabled progressively without code changes.
- Negative: Regex heuristics can produce false positives and must be tuned per domain.
- Negative: Content safety is currently heuristic-only; production deployments should integrate a cloud content moderation API.
- Negative: Rate limits in `guardrails/rate-limit-config.yaml` are not yet automatically wired to `slowapi`; they serve as configuration intent.

## Alternatives Considered

- **LLM-based guardrails only**: more flexible but slower, more expensive, and itself vulnerable to jailbreaks.
- **Dedicated guardrails API** (e.g., NeMo Guardrails, Guardrails AI): richer policy language but adds operational complexity for a template.
- **Cloud provider safety services** (AWS Comprehend, Azure Content Safety): excellent for production but require cloud accounts and keys.

## References

- [OWASP LLM Top 10](https://llmtop10.com/)
- [Microsoft Presidio](https://microsoft.github.io/presidio/)
- [slowapi documentation](https://slowapi.readthedocs.io/en/latest/)
