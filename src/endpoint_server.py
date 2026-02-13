"""
Tailored for LLM, this module provides a FastMCP server with documentation to call IBKR (Interactive Brokers) web api endpoints, through ibind rest client (which provides OAuth).
"""
import os
import logging
from typing import Any, Dict, Optional, Callable, TypeVar, Awaitable

import json
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _load_secrets_from_files() -> None:
    """
    Load secrets from files referenced by *_FILE env vars and set them as env vars.
    Files should contain raw values (no quotes).
    This MUST be called BEFORE importing ibind, as ibind reads env vars at import time.
    """
    # Map of env var names to their file-based counterparts
    secret_file_mappings = {
        "IBIND_OAUTH1A_CONSUMER_KEY": "IBIND_OAUTH1A_CONSUMER_KEY_FILE",
        "IBIND_OAUTH1A_ACCESS_TOKEN": "IBIND_OAUTH1A_ACCESS_TOKEN_FILE",
        "IBIND_OAUTH1A_ACCESS_TOKEN_SECRET": "IBIND_OAUTH1A_ACCESS_TOKEN_SECRET_FILE",
        "IBIND_OAUTH1A_DH_PRIME": "IBIND_OAUTH1A_DH_PRIME_FILE",
    }

    for env_var, file_var in secret_file_mappings.items():
        # Only load if not already set
        if not os.environ.get(env_var) and os.environ.get(file_var):
            file_path = os.environ[file_var]
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        content = f.read().strip()  # Just strip whitespace/newlines
                        os.environ[env_var] = content
                        logger.info("Loaded %s from %s", env_var, file_path)
                except Exception as e:
                    logger.warning("Failed to read %s: %s", file_path, e)


# Load .env file first to get environment variables including *_FILE paths
load_dotenv()

# Then load secrets from files referenced by *_FILE env vars
_load_secrets_from_files()

# Set ALLOWED_HOSTS for Starlette's TrustedHostMiddleware
# This must be set BEFORE importing FastMCP
if not os.environ.get("ALLOWED_HOSTS"):
    os.environ["ALLOWED_HOSTS"] = "localhost,127.0.0.1,mcp-server,mcp-server:8000,172.22.0.0/16,172.18.0.0/16"

# Now import ibind after secrets are loaded
from ibind import IbkrClient

# Global client instance
_ibind_client: Optional[IbkrClient] = None

# Allowed endpoints whitelist
ALLOWED_ENDPOINTS = {
    "iserver/accounts",  # Note: plural "accounts" not "account"
    "iserver/secdef/search",
    "iserver/secdef/info",
    "iserver/contract",
    "iserver/secdef/bond-filters",
    "trsrv/secdef",
    "trsrv/futures",
    "trsrv/stocks",
    "iserver/marketdata/snapshot",
    "iserver/marketdata/history",
}


def _get_transport_security_settings() -> TransportSecuritySettings:
    """Get transport security settings from environment or use defaults."""
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=False,  # Disable for Docker containers
        allowed_hosts=[
            "localhost:*",
            "127.0.0.1:*",
            "mcp-server:*",  # Container DNS name
            "172.19.0.0/16:*",  # openclaw_default network
            "172.22.0.0/16:*",  # llm_public_default network
            "*"  # Allow all hosts (configurable via environment)
        ],
        allowed_origins=["*"],  # Allow CORS from anywhere (configurable)
    )


# Create FastMCP server with custom transport security for Docker access
server = FastMCP(
    "ibkr-endpoint-server",
    host="0.0.0.0",  # Bind to all interfaces for Docker
    transport_security=_get_transport_security_settings(),
)


# Type variables for the decorator
F = TypeVar("F", bound=Callable[..., Awaitable[str]])


def mcp_tool(func: F) -> F:
    """Custom decorator for MCP tools that automatically sets structured_output=False."""

    return server.tool(structured_output=False)(func)  # type: ignore


def get_client() -> Optional[IbkrClient]:
    """
    Get or initialize the ibind client (lazy-loaded on first use).

    Returns None if connection fails, allowing imports to succeed.
    Subsequent calls reuse the same authenticated connection.
    """

    global _ibind_client
    if _ibind_client is None:
        try:
            _ibind_client = IbkrClient()
        except Exception as e:
            logger.warning("IBKR Connection Error: %s: %s", type(e).__name__, str(e))
            logger.warning("Contract tools will fail until connection is established")
            return None
    return _ibind_client


@mcp_tool
async def call_endpoint(path: str, params: Optional[Dict[str, Any]] = None) -> str:
    """
    Call a specific IBKR endpoint with given parameters.

    Args:
        path: The API endpoint path (e.g., 'iserver/accounts', 'iserver/secdef/search').
        params: Optional dictionary of parameters to pass to the endpoint.

    Returns:
        JSON string with the result of the endpoint call or error dict.

    Examples:
        call_endpoint(path='iserver/accounts')
        call_endpoint(path='iserver/secdef/search', params={"symbol": "AAPL", "sectype": "STK"})
        call_endpoint(path='iserver/secdef/info', params={"conid": "265598"})
        call_endpoint(path='iserver/marketdata/snapshot', params={"conids": "265598", "fields": "31,84,86"})

    For full documentation, use the endpoint_instructions() tool.
    """
    _result = _call_endpoint(path, params or {})

    return json.dumps(_result)


def _call_endpoint(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call an IBKR endpoint and return a consistent dict result.

    Args:
        path: The API endpoint path.
        params: Dictionary of parameters.

    Returns:
        Dict with 'data' key on success, or 'error' key on failure.
    """
    # Validate path against allowlist
    if path not in ALLOWED_ENDPOINTS:
        return {
            "error": f"Endpoint '{path}' is not allowed.",
            "allowed_endpoints": sorted(ALLOWED_ENDPOINTS),
        }

    client = get_client()
    if client is None:
        return {"error": "IBKR client not initialized"}

    try:
        result = client.get(path=path, params=params)  # type: ignore
        return {"data": result.data}
    except Exception as e:
        return {"error": f"API request failed: {type(e).__name__}: {str(e)}"}


@mcp_tool
async def endpoint_instructions() -> str:
    """
    Get detailed documentation for calling IBKR endpoints.

    Returns:
        Markdown formatted documentation of all tools, parameters, and examples.
    """
    # Read the documentation from the external file
    file_path = os.path.join(os.path.dirname(__file__), "endpoints.md")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: Documentation file not found at {file_path}"
    except Exception as e:
        return f"Error reading documentation: {str(e)}"


@mcp_tool
async def market_data_fields() -> str:
    """
    Get organized market data fields documentation.

    Returns:
        Markdown formatted documentation of all market data fields organized by category.
        Includes Price Data, Volume, Position/PnL, Options Greeks, Fundamentals, etc.
    """
    # Read the market data fields documentation from the external file
    file_path = os.path.join(os.path.dirname(__file__), "market_data_fields.md")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: Market data fields documentation not found at {file_path}"
    except Exception as e:
        return f"Error reading documentation: {str(e)}"


@mcp_tool
async def market_data_fields_original() -> str:
    """
    Get original market data fields reference (sorted by Field ID).

    Returns:
        Markdown formatted documentation with all fields sorted by Field ID.
        Use this for quick field ID lookups.
    """
    # Read the original market data fields documentation from the external file
    file_path = os.path.join(os.path.dirname(__file__), "market_data_fields_original.md")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: Original market data fields documentation not found at {file_path}"
    except Exception as e:
        return f"Error reading documentation: {str(e)}"


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting MCP server with HTTP transport...")
    logger.info("Press Ctrl+C to stop")
    logger.info("")
    logger.info("Endpoints:")
    logger.info("  - MCP:    http://localhost:8000/mcp")
    logger.info("  - Health: http://localhost:8000/health")
    logger.info("")

    # Run with uvicorn using the streamable_http_app
    # Disable host validation to allow access from Docker containers
    uvicorn.run(
        "src.endpoint_server:server.streamable_http_app",
        host="0.0.0.0",
        port=8000,
        lifespan="on",
        log_level="info",
        forwarded_allow_ips="*",  # Allow all forwarded headers
    )
