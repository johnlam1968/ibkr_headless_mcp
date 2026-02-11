#!/bin/bash
# Start script for llm_public MCP server in Docker
# This script builds and runs the Docker container

set -e

echo "=== llm_public MCP Server - Docker Start ==="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running or not installed."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "WARNING: .env file not found. Creating from example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Created .env from .env.example"
    else
        echo "ERROR: No .env or .env.example found. Please create .env file first."
        exit 1
    fi
fi

# Stop and remove existing container if it exists
if [ "$(docker ps -aq -f name=mcp-server)" ]; then
    echo "Stopping existing container..."
    docker stop mcp-server > /dev/null 2>&1 || true
    docker rm mcp-server > /dev/null 2>&1 || true
fi

# Build Docker image
echo ""
echo "Building Docker image..."
docker build -t mcp-server .

# Create llm_public_default network if it doesn't exist
if ! docker network inspect llm_public_default > /dev/null 2>&1; then
    echo "Creating llm_public_default network..."
    docker network create llm_public_default > /dev/null 2>&1
    echo "✓ Network created"
fi

# Parse .env file to get secrets directory
# Extract directory path from any *_FILE variable in .env
SECRETS_DIR_FROM_ENV=$(grep "_FILE=" .env 2>/dev/null | head -1 | cut -d'=' -f2 | xargs dirname 2>/dev/null || echo "")

if [ -n "$SECRETS_DIR" ]; then
    SECRETS_MOUNT="$SECRETS_DIR"
    echo "INFO: Using secrets directory from SECRETS_DIR: $SECRETS_MOUNT"
elif [ -n "$SECRETS_DIR_FROM_ENV" ]; then
    SECRETS_MOUNT="$SECRETS_DIR_FROM_ENV"
    echo "INFO: Using secrets directory from .env: $SECRETS_MOUNT"
elif [ -d "$PWD/secrets" ]; then
    SECRETS_MOUNT="$PWD/secrets"
    echo "INFO: Using local secrets directory: $SECRETS_MOUNT"
else
    echo "ERROR: Could not determine secrets directory. Set SECRETS_DIR environment variable or ensure .env has *_FILE paths configured."
    exit 1
fi

# Run container
echo ""
echo "Starting container..."
docker run -d \
    --name mcp-server \
    --hostname mcp-server \
    -p 8000:8000 \
    -v "$SECRETS_MOUNT:$SECRETS_MOUNT:ro" \
    --env-file .env \
    -e IBIND_USE_OAUTH=True \
    -e ALLOWED_HOSTS=localhost,127.0.0.1,172.22.0.0/16,172.18.0.0/16,mcp-server,mcp-server:8000 \
    --restart unless-stopped \
    --network llm_public_default \
    mcp-server

# Connect to openclaw_default network if it exists (for openclaw gateway access)
echo ""
if docker network inspect openclaw_default > /dev/null 2>&1; then
    echo "Connecting mcp-server to openclaw_default network..."
    docker network connect openclaw_default mcp-server
    echo "✓ Connected to openclaw_default network"
else
    echo "openclaw_default network not found (optional, for openclaw gateway access)"
fi

# Wait for server to be ready
echo ""
echo "Waiting for server to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/mcp > /dev/null 2>&1; then
        echo "✓ Server is ready!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Check container status
echo ""
echo "Container status:"
docker ps --filter name=mcp-server

echo ""
echo "=== Server Started Successfully ==="
echo ""
echo "Server URL: http://localhost:8000/mcp"
echo ""
echo "To view logs:"
echo "  docker logs mcp-server"
echo ""
echo "To stop server:"
echo "  docker stop mcp-server"
echo ""
echo "To restart server:"
echo "  docker restart mcp-server"
echo ""
echo "To remove container:"
echo "  docker stop mcp-server && docker rm mcp-server"
echo ""
echo "Test server:"
echo "  ./tests/run_all_tests.sh                           # Run all tests (recommended)"
echo "  ./tests/run_all_tests.sh --help                     # Show all options"
echo "  ./tests/run_all_tests.sh --localhost                # Test only localhost"
echo "  ./tests/run_all_tests.sh --container               # Test only Docker container"
echo "  ./tests/run_all_tests.sh --symbol AAPL              # Test with specific symbol"
echo ""
