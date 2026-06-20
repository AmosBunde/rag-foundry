import logging
import re
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class GuardrailResult(BaseModel):
    allowed: bool
    reason: str | None = None
    violations: list[str] = []


# Heuristic patterns for prompt injection
_PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(previous|above|earlier)\s+instructions?", re.IGNORECASE),
    re.compile(r"disregard\s+(previous|above|earlier)\s+instructions?", re.IGNORECASE),
    re.compile(r"system\s*:\s*", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+", re.IGNORECASE),
    re.compile(r"new\s+role\s*:\s*", re.IGNORECASE),
    re.compile(r"\{\{.*\}\}", re.IGNORECASE),
    re.compile(r"<script", re.IGNORECASE),
]

# Toxicity / content filter heuristics (mock). Production should call a real API.
_TOXIC_PATTERNS = [
    re.compile(r"\b(hate|kill|attack|violence)\b", re.IGNORECASE),
]

# Fast regex-based PII detection. Optional Presidio is loaded lazily for higher accuracy.
_PII_PATTERNS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "pii:US_SSN"),
    (re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"), "pii:CREDIT_CARD"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "pii:EMAIL"),
    (re.compile(r"\b\d{3}-\d{3}-\d{4}\b"), "pii:PHONE"),
]


def _check_length(text: str, max_length: int = 10_000) -> GuardrailResult:
    if len(text) > max_length:
        return GuardrailResult(
            allowed=False,
            reason=f"Input exceeds maximum length of {max_length} characters",
            violations=["input_too_long"],
        )
    return GuardrailResult(allowed=True)


def _check_prompt_injection(text: str) -> GuardrailResult:
    violations = []
    for pattern in _PROMPT_INJECTION_PATTERNS:
        if pattern.search(text):
            violations.append("prompt_injection_pattern")
    if violations:
        return GuardrailResult(
            allowed=False,
            reason="Potential prompt injection detected",
            violations=violations,
        )
    return GuardrailResult(allowed=True)


def _check_pii_regex(text: str) -> GuardrailResult:
    violations = []
    for pattern, label in _PII_PATTERNS:
        if pattern.search(text):
            violations.append(label)
    if violations:
        return GuardrailResult(
            allowed=False,
            reason="PII detected in input",
            violations=violations,
        )
    return GuardrailResult(allowed=True)


def _check_pii_presidio(text: str) -> GuardrailResult:
    try:
        from presidio_analyzer import AnalyzerEngine

        analyzer = AnalyzerEngine()
        results = analyzer.analyze(text=text, language="en")
        if results:
            violations = [f"pii:{r.entity_type}" for r in results]
            return GuardrailResult(
                allowed=False,
                reason="PII detected in input",
                violations=violations,
            )
    except Exception as exc:
        logger.debug("Presidio PII check failed: %s", exc)
    return GuardrailResult(allowed=True)


def _check_toxicity(text: str) -> GuardrailResult:
    violations = []
    for pattern in _TOXIC_PATTERNS:
        if pattern.search(text):
            violations.append("toxic_content")
    if violations:
        return GuardrailResult(
            allowed=False,
            reason="Potentially toxic content detected",
            violations=violations,
        )
    return GuardrailResult(allowed=True)


def validate_query(text: str, max_length: int = 2_000, use_presidio: bool = False) -> GuardrailResult:
    """Run all guardrails on a user query and return aggregated result."""
    checks = [
        _check_length(text, max_length),
        _check_prompt_injection(text),
        _check_pii_regex(text),
    ]
    if use_presidio:
        checks.append(_check_pii_presidio(text))
    checks.append(_check_toxicity(text))

    violations: list[str] = []
    reasons: list[str] = []
    for check in checks:
        if not check.allowed:
            violations.extend(check.violations)
            if check.reason:
                reasons.append(check.reason)
    if violations:
        return GuardrailResult(
            allowed=False,
            reason="; ".join(reasons),
            violations=violations,
        )
    return GuardrailResult(allowed=True)


def guard_query(text: str, max_length: int = 2_000) -> None:
    """Raise HTTPException if guardrails block the input."""
    result = validate_query(text, max_length)
    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Guardrail violation", "reason": result.reason, "violations": result.violations},
        )


def validate_metadata(metadata: dict[str, Any]) -> GuardrailResult:
    """Lightweight metadata guardrail to prevent injection in document metadata."""
    for key, value in metadata.items():
        if isinstance(value, str):
            injection = _check_prompt_injection(value)
            if not injection.allowed:
                return injection
    return GuardrailResult(allowed=True)
