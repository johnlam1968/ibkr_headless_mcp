"""
Tailored for LLM, this module provides a FastMCP server with documentation to call IBKR (Interactive Brokers) web api endpoints, through ibind rest client (which provides oAuth).
"""
import os
from typing import Any, Dict, Optional, Callable, TypeVar, Awaitable

import json
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from dotenv import load_dotenv


def _load_secrets_from_files():
    """
    Load secrets from files referenced by *_FILE env vars and set them as env vars.
    Files should contain raw values (no quotes).
    This MUST be called BEFORE importing ibind, as ibind reads env vars at import time.
    """
    # Map of env var names to their file-based counterparts
    secret_file_mappings = {
        'IBIND_OAUTH1A_CONSUMER_KEY': 'IBIND_OAUTH1A_CONSUMER_KEY_FILE',
        'IBIND_OAUTH1A_ACCESS_TOKEN': 'IBIND_OAUTH1A_ACCESS_TOKEN_FILE',
        'IBIND_OAUTH1A_ACCESS_TOKEN_SECRET': 'IBIND_OAUTH1A_ACCESS_TOKEN_SECRET_FILE',
        'IBIND_OAUTH1A_DH_PRIME': 'IBIND_OAUTH1A_DH_PRIME_FILE',
    }
    
    for env_var, file_var in secret_file_mappings.items():
        # Only load if not already set
        if not os.environ.get(env_var) and os.environ.get(file_var):
            file_path = os.environ[file_var]
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read().strip()  # Just strip whitespace/newlines
                        os.environ[env_var] = content
                        print(f"✅ Loaded {env_var} from {file_path}")
                except Exception as e:
                    print(f"⚠️ Warning: Failed to read {file_path}: {e}")


# Load .env file first to get environment variables including *_FILE paths
load_dotenv()

# Then load secrets from files referenced by *_FILE env vars
_load_secrets_from_files()

# Set ALLOWED_HOSTS for Starlette's TrustedHostMiddleware
# This must be set BEFORE importing FastMCP
import os
if not os.environ.get('ALLOWED_HOSTS'):
    os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1,mcp-server,mcp-server:8000,172.22.0.0/16,172.18.0.0/16'

# Now import ibind after secrets are loaded
from ibind import IbkrClient, Result # type: ignore

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


# Create FastMCP server with custom transport security for Docker access
server = FastMCP(
    "ibkr-endpoint-server",
    host="0.0.0.0",  # Bind to all interfaces for Docker
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,  # Disable for Docker containers
        allowed_hosts=[
            "localhost:*",
            "127.0.0.1:*",
            "mcp-server:*",           # Container DNS name
            "172.19.0.0/16:*",        # openclaw_default network
            "172.22.0.0/16:*",        # llm_public_default network
            "*"                        # Allow all hosts (for testing)
        ],
        allowed_origins=["*"]          # Allow CORS from anywhere
    )
)


# Type variables for the decorator
F = TypeVar('F', bound=Callable[..., Awaitable[str]])

def mcp_tool(func: F) -> F:
    """Custom decorator for MCP tools that automatically sets structured_output=False"""
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
            print(f"⚠️ IBKR Connection Error: {type(e).__name__}: {str(e)}")
            print("   Contract tools will fail until connection is established")
            return None
    return _ibind_client

@mcp_tool
async def call_endpoint(path: str, params: Optional[Dict[str, Any]]) -> str:
    """
    Call a specific endpoint with given parameters.
    This utilize ibind's rest_client method to make API calls to IBKR end points.
    
    Args:
        path: The API endpoint path, e.g.:
            "iserver/accounts"
            "iserver/secdef/search"
            "iserver/secdef/info"
            "iserver/contract"
            "iserver/secdef/bond-filters"
            "trsrv/secdef"
            "trsrv/futures"
            "trsrv/stocks"
            "iserver/marketdata/snapshot"
            "iserver/marketdata/history"
            "iserver/account/{{ accountId }}/alerts"
        params: Dictionary of parameters to be passed to the endpoint.

    Returns:
        JSON with the result of the endpoint call or error dict.
    Examples:
        call_endpoint(path='iserver/accounts')
        upstream docs: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#get-accounts
        from the response, parse for accountId and use in subsequent calls.

        call_endpoint(path='iserver/secdef/search', params={"symbol":"US-T", "sectype":"BOND"})
        Valid Values: "STK", "IND", "BOND"
        "STK" for Stocks, "IND" for Indices, "BOND" for Bonds.
        call_endpoint('iserver/secdef/search', params={"symbol":"SPY", "sectype":"STK")
        call_endpoint('iserver/secdef/search', params={"symbol":"SPX", "sectype":"IND")
        call_endpoint(path='iserver/secdef/search', params={"symbol":"Apple", "name":"true"})
        upstream docs: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#search-symbol-contract

        call_endpoint(path='iserver/secdef/info', params={"conid":"265598"})
        upstream docs: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#secdef-info-contract
        
        call_endpoint(path=f'iserver/contract/265598/info')
        upstream docs: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#info-conid-contract

        call_endpoint(path=f'iserver/account/{{ accountId }}/alerts')
        accountId has Value Format: "DU1234567"
        call_endpoint(path=f'iserver/account/{{ "DU1234567" }}/alerts')

        upstream docs: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#get-alert-list

        Workflow to get market snapshot data:

            (1) The endpoint /iserver/accounts must be called prior to /iserver/marketdata/snapshot:

            (2) Obtain conid from /iserver/secdef/search:

            (3) Then use conid in the /iserver/marketdata/snapshot endpoint.
                100 conids can be requested at once
                10 requests per second

            (3.1) First call to onboard:
                call_endpoint(path='iserver/marketdata/snapshot', params={"conids":"265598", "fields":"31,84,86"})

            (3.2) Must call twice to get actual data, first call only returns empty data. Make a second call to get actual data:
                call_endpoint(path='iserver/marketdata/snapshot', params={"conids":"265598", "fields":"31,84,86"})

            upstream docs: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#md-snapshot

    """
    if params:
        _result = _call_endpoint(path, params)
    else:
        _result = _call_endpoint(path, {})

    if isinstance(_result, str):
        return json.dumps({"error": "ibind client not initialized"})

    return json.dumps(_result.data)  # type: ignore


def _call_endpoint(path: str, params: Dict[str, Any]) -> Result | str:
    # Validate path against allowlist
    if path not in ALLOWED_ENDPOINTS:
        return json.dumps({
            "error": f"Endpoint '{path}' is not allowed. Allowed endpoints: {', '.join(sorted(ALLOWED_ENDPOINTS))}",
        })

    client = get_client()
    if client is None:
        return json.dumps({"error": "IBKR client not initialized"})

    result = client.get(path=path, params=params)  # type: ignore
    
    # Add reminder for secdef/search and marketdata endpoints
    if isinstance(result, Result) and result.data is not None:
        if path.startswith("iserver/marketdata"):
            reminder = (
                "NOTE: If data is empty or rejected, call 'call_endpoint' with "
                "path='iserver/accounts' first to authenticate/onboard with IBKR. "
                "The /iserver/accounts endpoint must be called before market data endpoints."
            )
            result.data = f"{reminder}\n\n{json.dumps(result.data)}"
    
    return result

@mcp_tool
async def endpoint_instructions() -> str:
    """
    Details of how to call IBKR endpoints.

    Returns:
        Markdown formatted documentation of all tools, parameters, and examples.
    """
    import os
    # Read the documentation from the external file
    file_path = os.path.join(os.path.dirname(__file__), "endpoints.md")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: Documentation file not found at {file_path}"
    except Exception as e:
        return f"Error reading documentation: {str(e)}"


if __name__ == "__main__":
    import uvicorn
    
    print("Starting MCP server with HTTP transport...")
    print("Press Ctrl+C to stop")
    print("")
    print("Endpoints:")
    print("  - MCP:    http://localhost:8000/mcp")
    print("  - Health: http://localhost:8000/health")
    print("")
    
    # Run with uvicorn using the streamable_http_app
    # Disable host validation to allow access from Docker containers
    uvicorn.run(
        "src.endpoint_server:server.streamable_http_app",
        host="0.0.0.0",
        port=8000,
        lifespan="on",
        log_level="info",
        forwarded_allow_ips="*"  # Allow all forwarded headers
    )
