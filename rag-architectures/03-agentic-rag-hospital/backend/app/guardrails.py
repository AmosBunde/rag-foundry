import logging
import re
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel

from app.config import settings

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

# Medical advice patterns that should trigger disclaimer requirement
_MEDICAL_ADVICE_PATTERNS = [
    re.compile(r"\b(should i|do i need to|is it safe to|can i take|will i die|diagnose|diagnosis|treatment plan|prescribe)\b", re.IGNORECASE),
]

# Fast regex-based PII detection
_PII_PATTERNS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "pii:US_SSN"),
    (re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"), "pii:CREDIT_CARD"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "pii:EMAIL"),
    (re.compile(r"\b\d{3}-\d{3}-\d{4}\b"), "pii:PHONE"),
    (re.compile(r"\b(MR|MS|MRS|DR)\.?\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b"), "pii:PATIENT_NAME"),
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


def _check_medical_safety(text: str) -> GuardrailResult:
    """Detect requests that ask for personal medical advice and require disclaimer."""
    violations = []
    for pattern in _MEDICAL_ADVICE_PATTERNS:
        if pattern.search(text):
            violations.append("medical_advice_request")
    if violations:
        return GuardrailResult(
            allowed=True,
            reason="Medical advice disclaimer required",
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
    checks.append(_check_medical_safety(text))

    violations: list[str] = []
    reasons: list[str] = []
    blocked = False
    for check in checks:
        if check.violations:
            violations.extend(check.violations)
        if check.reason:
            reasons.append(check.reason)
        if not check.allowed:
            blocked = True
    if blocked:
        return GuardrailResult(
            allowed=False,
            reason="; ".join(reasons),
            violations=violations,
        )
    return GuardrailResult(allowed=True, reason="; ".join(reasons) if reasons else None, violations=violations)


def guard_query(text: str, max_length: int = 2_000) -> None:
    """Raise HTTPException if guardrails block the input."""
    result = validate_query(text, max_length)
    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Guardrail violation", "reason": result.reason, "violations": result.violations},
        )


def requires_medical_disclaimer(text: str) -> bool:
    return bool(_check_medical_safety(text).violations)


def append_medical_disclaimer(answer: str) -> str:
    disclaimer = (
        "\n\nDisclaimer: This information is for educational purposes only and is not a "
        "substitute for professional medical advice, diagnosis, or treatment. Always seek the "
        "advice of a qualified healthcare provider with any questions you may have regarding a "
        "medical condition."
    )
    return answer + disclaimer


def redact_pii(text: str) -> str:
    """Best-effort PII redaction for logged or returned text."""
    redacted = text
    for pattern, label in _PII_PATTERNS:
        redacted = pattern.sub(f"[REDACTED:{label.split(':')[-1]}]", redacted)
    return redacted
