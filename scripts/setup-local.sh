#!/usr/bin/env bash
set -euo pipefail

echo "==> Setting up local environment for rag-foundry"

# ---------------------------------------------------------------------------
# OS detection
# ---------------------------------------------------------------------------
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

echo "Detected OS: $OS"

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------
if ! command -v docker &>/dev/null; then
    echo "Installing Docker..."
    if [[ "$OS" == "linux" ]]; then
        curl -fsSL https://get.docker.com | sh
        sudo usermod -aG docker "$(whoami)"
        echo "Docker installed. Please log out and back in for group changes."
    else
        echo "Please install Docker Desktop for macOS manually."
        exit 1
    fi
else
    echo "Docker already installed: $(docker --version)"
fi

if ! command -v docker-compose &>/dev/null && ! docker compose version &>/dev/null; then
    echo "Installing Docker Compose plugin..."
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
else
    echo "Docker Compose already installed"
fi

# ---------------------------------------------------------------------------
# Python 3.11+
# ---------------------------------------------------------------------------
if ! command -v python3.12 &>/dev/null && ! command -v python3.11 &>/dev/null; then
    echo "Installing Python 3.12..."
    if [[ "$OS" == "linux" ]]; then
        sudo apt-get update
        sudo apt-get install -y software-properties-common
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt-get update
        sudo apt-get install -y python3.12 python3.12-venv python3.12-dev
    else
        echo "Please install Python 3.11+ manually on macOS."
        exit 1
    fi
else
    echo "Python already installed: $(python3 --version)"
fi

# ---------------------------------------------------------------------------
# Node.js 20
# ---------------------------------------------------------------------------
if ! command -v node &>/dev/null || [[ "$(node -v | cut -d'v' -f2 | cut -d'.' -f1)" != "20" ]]; then
    echo "Installing Node.js 20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo "Node.js already installed: $(node -v)"
fi

# ---------------------------------------------------------------------------
# Ollama
# ---------------------------------------------------------------------------
if ! command -v ollama &>/dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama already installed: $(ollama --version)"
fi

echo "Pulling default models..."
ollama pull llama3:8b || true
ollama pull nomic-embed-text || true
ollama pull clip || true
ollama pull whisper || true

# ---------------------------------------------------------------------------
# Pre-commit hooks (optional)
# ---------------------------------------------------------------------------
if command -v pipx &>/dev/null; then
    pipx install pre-commit || true
    pre-commit install || true
fi

echo "==> Local setup complete. Run 'make up' to start services."
