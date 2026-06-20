#!/usr/bin/env bash
set -euo pipefail

# Bootstrap a new architecture directory from the shared template.
# Usage: scripts/bootstrap-app.sh NN-name

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <NN-architecture-name>"
    exit 1
fi

ARCH="$1"
DIR="$ARCH"

if [ -d "$DIR" ]; then
    echo "Directory $DIR already exists. Aborting."
    exit 1
fi

echo "==> Bootstrapping $ARCH"

mkdir -p "$DIR"/{backend,frontend,infra/{bare-metal,aws,azure,gcp},tests,guardrails,adr,c4}

# Placeholder files
cat > "$DIR/README.md" <<EOF
# $ARCH

## Overview

## Architecture Diagram

## Quick Start (Local)

## Deployment Guides

### Bare Metal / VPS

### AWS

### Azure

### GCP

## Testing

## Guardrails

## API Documentation

## Troubleshooting
EOF

cat > "$DIR/backend/.gitkeep" <<EOF
# Backend code goes here
EOF

cat > "$DIR/frontend/.gitkeep" <<EOF
# Frontend code goes here
EOF

echo "==> $ARCH scaffold created at $DIR"
