.PHONY: up down build test lint fmt clean help

# Default architecture to run tests against
ARCH ?= 01-hybrid-rag

help: ## Show this help
	@echo "RAG Architecture Templates — Common Commands"
	@echo ""
	@echo "  make up              Start all shared services and placeholder apps"
	@echo "  make down            Stop all services"
	@echo "  make build           Build all Docker images"
	@echo "  make test            Run all tests across all architectures"
	@echo "  make test ARCH=...   Run tests for a single architecture"
	@echo "  make lint            Run linters on backend and frontend code"
	@echo "  make fmt             Format all code"
	@echo "  make clean           Remove containers, volumes, and build artifacts"
	@echo ""

up: ## Start the full local stack
	docker compose up -d

down: ## Stop the full local stack
	docker compose down

build: ## Build all Docker images
	docker compose build

test: ## Run tests for all architectures or a single one
	@bash scripts/run-tests.sh $(ARCH)

lint: ## Run linters
	@echo "Linting backend code..."
	@find . -path '*/backend/*' -name 'requirements*.txt' -exec dirname {} \; | sort -u | while read dir; do \
		if [ -f "$$dir/pyproject.toml" ] || [ -f "$$dir/setup.cfg" ] || [ -f "$$dir/.flake8" ]; then \
			cd "$$dir" && ruff check . && cd - > /dev/null; \
		fi; \
	done
	@echo "Linting frontend code..."
	@find . -path '*/frontend/*' -name 'package.json' -not -path '*/node_modules/*' -exec dirname {} \; | sort -u | while read dir; do \
		cd "$$dir" && npm run lint && cd - > /dev/null; \
	done

fmt: ## Format all code
	@find . -path '*/backend/*' -name 'pyproject.toml' -exec dirname {} \; | sort -u | while read dir; do \
		cd "$$dir" && ruff format . && cd - > /dev/null; \
	done
	@find . -path '*/frontend/*' -name 'package.json' -not -path '*/node_modules/*' -exec dirname {} \; | sort -u | while read dir; do \
		cd "$$dir" && npm run format && cd - > /dev/null; \
	done

clean: ## Remove containers, volumes, and build artifacts
	docker compose down -v --remove-orphans
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
