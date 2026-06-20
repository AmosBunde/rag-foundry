#!/usr/bin/env bash
set -euo pipefail

ARCH="${1:-all}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

run_backend_tests() {
    local dir="$1"
    if [ -f "$dir/backend/requirements-dev.txt" ]; then
        echo "==> Running backend tests for $dir"
        (
            cd "$dir/backend"
            python -m pytest --cov=app --cov-report=term-missing
        )
    else
        echo "==> Skipping backend tests for $dir (no requirements-dev.txt)"
    fi
}

run_frontend_tests() {
    local dir="$1"
    if [ -f "$dir/frontend/package.json" ]; then
        echo "==> Running frontend tests for $dir"
        (
            cd "$dir/frontend"
            npm run test:ci
        )
    else
        echo "==> Skipping frontend tests for $dir (no package.json)"
    fi
}

if [ "$ARCH" == "all" ]; then
    for dir in 0*-*/; do
        run_backend_tests "$dir"
        run_frontend_tests "$dir"
    done
else
    dir="$ARCH"
    if [ ! -d "$dir" ]; then
        echo "Architecture $ARCH not found"
        exit 1
    fi
    run_backend_tests "$dir"
    run_frontend_tests "$dir"
fi

echo "==> All requested tests completed"
