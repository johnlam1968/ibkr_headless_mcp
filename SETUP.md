# Setup Instructions for llm_public MCP Server

## Quick Start

### Prerequisites
- Python 3.11 or higher
- curl (for uv installation)

### Setup

1. **Run the setup script:**
```bash
cd /workspace/llm_public
./setup.sh
```

2. **Activate the virtual environment:**
```bash
source .venv/bin/activate
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env to point to your secrets files
```

4. **Test HTTP transport:**
```bash
python src/endpoint_server.py
```

## Manual Setup (without setup.sh)

If you prefer to set up manually:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.uv/bin:$PATH"

# Create venv and install dependencies
cd /workspace/llm_public
uv venv .venv --python python3
source .venv/bin/activate
uv pip install -r requirements.txt

# Or using pip
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Dependencies

The following packages are required:

- **mcp** - Model Context Protocol server framework
- **ibind** - IBKR REST client with OAuth support
- **python-dotenv** - Environment variable management
- **uvicorn** - ASGI server for HTTP transport
- **starlette** - Web framework (required by FastMCP HTTP)
- **httpx** - HTTP client library

## Directory Structure

```
llm_public/
├── .venv/                  # Python virtual environment
├── src/
│   ├── endpoint_server.py  # MCP server implementation
│   ├── ibkr_oauth.py       # OAuth 1.0a authentication
│   └── endpoints.md        # IBKR API documentation
├── secrets/                # IBKR credentials (gitignored)
│   ├── consumer_key
│   ├── private_encryption.pem
│   ├── private_signature.pem
│   ├── dh_prime.pem
│   └── access_token
├── .env                   # Environment configuration
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project metadata
└── setup.sh              # Setup script
```

## Environment Variables

Configure the following in `.env`:

```bash
# IBKR OAuth Configuration
IBIND_USE_OAUTH=True
IBIND_OAUTH1A_CONSUMER_KEY_FILE=/path/to/consumer_key
IBIND_OAUTH1A_ENCRYPTION_KEY_FP=/path/to/private_encryption.pem
IBIND_OAUTH1A_SIGNATURE_KEY_FP=/path/to/private_signature.pem
IBIND_OAUTH1A_ACCESS_TOKEN_FILE=/path/to/access_token
IBIND_OAUTH1A_DH_PRIME_FILE=/path/to/dh_prime
```

## Testing

### Quick HTTP Transport Test

```bash
source .venv/bin/activate

# The server uses FastMCP's streamable-http transport by default
# Configure host and port in the code or via environment
python src/endpoint_server.py
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# List allowed endpoints
curl http://localhost:8000/api/endpoints

# Call an endpoint
curl -X POST http://localhost:8000/api/call_endpoint \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "iserver/account", "params": {}}'
```

## Docker Deployment

For containerized deployment:

```bash
# Build the image
docker build -t mcp-server .

# Run with docker-compose
docker-compose up -d
```

See `docker-compose.yml` for configuration options.
