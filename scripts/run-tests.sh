#!/usr/bin/env bash
set -euo pipefail

ARCH="${1:-all}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PYTHON_CMD="${PYTHON_CMD:-python3}"

cd "$ROOT_DIR"

run_backend_tests() {
    local dir="$1"
    if [ -f "$dir/backend/requirements-dev.txt" ]; then
        echo "==> Running backend tests for $dir"
        (
            cd "$dir/backend"
            if [ ! -d ".venv" ]; then
                echo "    Creating virtual environment..."
                "$PYTHON_CMD" -m venv .venv
            fi
            source .venv/bin/activate
            echo "    Installing dependencies..."
            pip install -q -r requirements.txt -r requirements-dev.txt
            echo "    Running pytest..."
            pytest -q --cov=app --cov-report=term-missing --cov-fail-under=80
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
            if [ ! -d "node_modules" ]; then
                echo "    Installing npm dependencies..."
                npm install
            fi
            echo "    Running build and tests..."
            npm run build
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
