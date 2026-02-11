#!/bin/bash
# Setup script for llm_public MCP server
# This script installs uv and creates a Python virtual environment

set -e

echo "=== llm_public MCP Server Setup ==="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Please install Python 3.11+ before running this script."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Minimum Python 3.11 required
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo "ERROR: Python 3.11+ is required. Found: $PYTHON_VERSION"
    exit 1
fi

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv (UVX)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.uv/bin:$PATH"
    echo "UV installed successfully"
else
    echo "UV is already installed: $(uv --version)"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
uv venv .venv --python python3

# Activate and install dependencies
echo ""
echo "Installing dependencies..."
source .venv/bin/activate

# Install from requirements.txt (simpler approach)
uv pip install -r requirements.txt

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To activate the environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To run the server:"
echo "  source .venv/bin/activate"
echo "  python src/endpoint_server.py"
echo ""
echo "=== Docker Deployment ==="
echo ""
echo "To deploy via Docker:"
echo ""
echo "1. Build the Docker image:"
echo "  docker build -t mcp-server ."
echo ""
echo "2. Run with Docker Compose:"
echo "  docker-compose up -d"
echo ""
echo "3. Or run directly:"
echo "  docker run -d -p 8000:8000 --name mcp-server mcp-server"
echo ""
echo "Quick Docker setup:"
echo "  ./setup.sh && docker build -t mcp-server . && docker-compose up -d"
