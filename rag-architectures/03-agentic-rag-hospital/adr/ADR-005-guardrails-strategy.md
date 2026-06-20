# ADR 005: Guardrails Strategy

## Status

Accepted

## Context

A hospital-facing RAG system processes sensitive medical queries. Guardrails must prevent prompt injection, PII leakage, toxic content, and unsafe medical advice.

## Decision

Implement a **layered, defence-in-depth guardrails strategy**:

1. **Input validation** with Pydantic models enforces type, length, and cardinality constraints.
2. **Heuristic checks** detect prompt injection patterns, regex-based PII, toxic keywords, and medical-advice patterns.
3. **Optional Presidio** integration provides higher-accuracy NER-based PII detection when enabled.
4. **Verifier agent** uses an LLM to assess whether the query can be answered safely from retrieved sources.
5. **Responder agent** refuses unsafe queries and appends a medical disclaimer to educational answers.
6. **Rate limiting** via `slowapi` reduces brute-force and abuse risk.

## Consequences

- Positive: Multiple independent layers reduce the chance of a single bypass.
- Positive: Regex checks work offline.
- Positive: Medical disclaimer and refusal logic are explicit in the agent graph.
- Negative: Regex heuristics can produce false positives.
- Negative: Content safety is currently heuristic-only; production should integrate a cloud moderation API.

## Alternatives Considered

- **LLM-based guardrails only**: slower, more expensive, and itself vulnerable to jailbreaks.
- **Dedicated guardrails API**: richer policy language but adds operational complexity.

## References

- [OWASP LLM Top 10](https://llmtop10.com/)
- [Microsoft Presidio](https://microsoft.github.io/presidio/)
