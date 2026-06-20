# ADR 005: Guardrails for Media

## Status

Accepted

## Context

In addition to text guardrails, media uploads introduce new risks: oversized files, unsafe filenames, unsupported formats, and potentially harmful imagery/audio.

## Decision

Layer media-specific guardrails on top of existing text checks.

- Filename validation rejects path traversal and unsafe characters.
- File size limits are enforced per modality (10 MB images, 50 MB audio).
- MIME type allowlists restrict uploads to supported formats.
- Text extracted from audio transcriptions and image captions runs through the same text guardrails.
- A new `media-safety.yaml` config file documents cloud moderation API placeholders.

## Consequences

- Positive: Reduces abuse surface for upload endpoints.
- Positive: Configuration-driven limits are easy to tune per environment.
- Negative: Regex/MIME checks are not a substitute for deep content moderation.
