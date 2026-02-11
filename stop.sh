#!/bin/bash
# Stop script for llm_public MCP server in Docker
# This script stops and removes the container and network

set -e

echo "=== llm_public MCP Server - Docker Stop ==="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running or not installed."
    exit 1
fi

# Stop and remove mcp-server container
if [ "$(docker ps -aq -f name=mcp-server)" ]; then
    echo "Stopping mcp-server container..."
    docker stop mcp-server 2>/dev/null || true
    echo "✓ Container stopped"
    
    echo ""
    echo "Removing mcp-server container..."
    docker rm mcp-server 2>/dev/null || true
    echo "✓ Container removed"
else
    echo "mcp-server container not found (already stopped/removed)"
fi

# Remove llm_public_default network
if docker network inspect llm_public_default > /dev/null 2>&1; then
    echo ""
    echo "Removing llm_public_default network..."
    docker network rm llm_public_default 2>/dev/null || true
    echo "✓ Network removed"
else
    echo ""
    echo "llm_public_default network not found (already removed or never created)"
fi

# Note: We don't remove openclaw_default network as it may be used by other containers
echo ""
echo "=== Cleanup Complete ==="
echo ""
echo "Note: openclaw_default network (if it exists) was preserved as it may be used by other services."
echo ""
echo "To start the server again:"
echo "  ./start.sh"
echo ""