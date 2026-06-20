# ADR 001: Shared CI/CD and Monorepo Automation

## Status
Accepted

## Context
The repository contains five independent but related RAG architecture templates. Each has its own backend, frontend, infrastructure, tests, and documentation. We need a consistent, maintainable way to build, test, and lint all of them without duplicating CI logic in every folder.

## Decision
Use a shared GitHub Actions workflow (`.github/workflows/ci.yml`) triggered on pushes and pull requests to `main`. The workflow:

- Uses `dorny/paths-filter` to detect which architectures changed.
- Runs backend tests (pytest with coverage), frontend lint/tests, and Terraform validation for changed architectures.
- Uses Python 3.12 and Node 20 across all jobs.
- Leaves deployment workflows (`deploy-aws.yml`, `deploy-azure.yml`, `deploy-gcp.yml`) as template workflows that are invoked manually or extended per project.

Common commands are exposed via the root `Makefile` and `scripts/run-tests.sh`.

## Consequences
- Positive: One place to update CI logic; consistent quality gates for all architectures.
- Positive: Faster builds because only changed architectures are tested.
- Negative: The shared workflow must handle five different dependency sets; matrix failures can be noisy.
- Risk: If an architecture deviates from the expected folder layout, the workflow breaks. Mitigated by the `bootstrap-app.sh` scaffold script.

## Alternatives Considered
- Per-architecture workflow files: simpler per-project customization but high duplication.
- A single mega-job: slower and harder to debug.

## References
- `.github/workflows/ci.yml`
- `Makefile`
- `scripts/run-tests.sh`
