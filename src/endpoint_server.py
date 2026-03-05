"""
Tailored for LLM, this module provides a FastMCP server with documentation to call IBKR (Interactive Brokers) web api endpoints, through ibind rest client (which provides OAuth).
"""
import os
import sys
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


def get_client(fail_on_auth_error: bool = True) -> Optional[IbkrClient]:
    """
    Get or initialize the ibind client (lazy-loaded on first use).

    Args:
        fail_on_auth_error: If True, exit the server process when authentication fails.
                            If False, return None and allow server to continue (for testing).

    Returns None if connection fails (when fail_on_auth_error=False).
    Exits the process if authentication fails (when fail_on_auth_error=True).
    Subsequent calls reuse the same authenticated connection.
    """

    global _ibind_client
    if _ibind_client is None:
        try:
            _ibind_client = IbkrClient()
        except Exception as e:
            error_str = str(e)
            logger.error("IBKR Connection Error: %s: %s", type(e).__name__, error_str)
            
            # Check if it's an authentication error
            if "invalid consumer" in error_str.lower() or "401" in error_str:
                logger.error("FATAL: IBKR authentication failed! Check your OAuth credentials.")
                if fail_on_auth_error:
                    logger.error("Exiting server...")
                    sys.exit(1)
            else:
                logger.warning("Contract tools will fail until connection is established")
            return None
    return _ibind_client


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
        error_str = str(e)
        # Check if it's an authentication error (401 Unauthorized)
        if "401" in error_str or "Unauthorized" in error_str or "not authenticated" in error_str:
            logger.warning("IBKR session expired, attempting re-authentication...")
            try:
                # This will regenerate the LST and restart the Tickler
                # handle_auth_status() returns True if successful, False otherwise
                if client.handle_auth_status(raise_exceptions=True):
                    # Retry the original request after successful re-authentication
                    result = client.get(path=path, params=params)
                    return {"data": result.data}
                else:
                    return {"error": "Session expired and re-authentication returned False"}
            except Exception as reauth_error:
                logger.error("Re-authentication failed: %s", reauth_error)
                return {"error": f"Session expired and re-authentication failed: {type(reauth_error).__name__}: {str(reauth_error)}"}
        return {"error": f"API request failed: {type(e).__name__}: {str(e)}"}


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


@mcp_tool
async def get_accounts() -> str:
    """
    Get IBKR account information.

    This is a mandatory first step before making further requests.
    Returns account IDs and their associated information.

    Returns:
        JSON string with account data or error dict.

    Examples:
        get_accounts()
    """
    _result = _call_endpoint("iserver/accounts", {})
    return json.dumps(_result)


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


# Default market data fields for snapshot
SNAPSHOT_FIELDS = "31,55,70,71,82,83,84,86,87,6008,6070,6457,7051,7084,7085,7086,7087,7088,7089,7282,7283,7285,7289,7290,7291,7293,7294,7295,7296,7607,7633,7638,7644,7655,7674,7675,7676,7677,7682,7683,7684,7685,7686,7687,7688,7689,7690,7718,7741,7762"


def _get_snapshot(conids: str, delay: int = 50, requested_symbols: Optional[str] = None) -> Dict[str, Any]:
    """
    Helper function to fetch market snapshot for one or more conids.

    Makes two API calls with a delay in between to ensure market data is populated.
    Supports up to 100 conids per request (comma-separated).
    
    Args:
        conids: Comma-separated IBKR contract IDs (e.g., "265598" for AAPL, or "265598,123456" for multiple)
        delay: Delay in seconds between API calls (default: 50). Minimum recommended is 50.
        requested_symbols: Optional comma-separated symbols to include in the response (e.g., "AAPL,MSFT")

    Returns:
        Dict with market snapshot data or error.
    """
    import time

    logger.info(f"Fetching market snapshot for conids {conids} (delay={delay}s)...")

    # First call - initiates data fetch
    snapshot_result_1 = _call_endpoint(
        "iserver/marketdata/snapshot",
        {"conids": conids, "fields": SNAPSHOT_FIELDS}
    )

    # Wait for data to populate
    time.sleep(delay)

    # Second call - retrieves populated data
    snapshot_result_2 = _call_endpoint(
        "iserver/marketdata/snapshot",
        {"conids": conids, "fields": SNAPSHOT_FIELDS}
    )

    if "error" in snapshot_result_2:
        return {"error": f"Failed to get snapshot: {snapshot_result_2.get('error')}"}

    # Add requested_symbols to the response if provided
    snapshot_data = snapshot_result_2.get("data", {})
    if requested_symbols and snapshot_data.get("data"):
        symbol_list = [s.strip().upper() for s in requested_symbols.split(",")]
        for i, item in enumerate(snapshot_data["data"]):
            if i < len(symbol_list):
                item["requested_symbol"] = symbol_list[i]

    return snapshot_data


@mcp_tool
async def search_conids(symbols: str) -> str:
    """
    Find conids for given ticker symbols.

    This resolves comma-separated ticker symbols (e.g., "AAPL,QQQ,MSFT") to their IBKR contract IDs (conids).

    Args:
        symbols: Comma-separated ticker symbols (e.g., "AAPL,QQQ,MSFT")

    Returns:
        JSON string with a list of conids and their symbol mappings, or error dict.

    Examples:
        search_conids(symbols="AAPL")
        search_conids(symbols="AAPL,QQQ,MSFT")
    """
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    results = []
    
    for symbol in symbol_list:
        search_result = _call_endpoint(
            "iserver/secdef/search",
            {"symbol": symbol, "sectype": "STK"}
        )

        if "error" in search_result:
            results.append({"requested_symbol": symbol, "error": search_result.get("error")})
            continue

        data = search_result.get("data", {})
        conid = None
        matched_symbol = None
        
        if data.get("data"):
            # Try to find exact symbol match first
            for item in data["data"]:
                if item.get("symbol", "").upper() == symbol:
                    conid = item.get("conid")
                    matched_symbol = item.get("symbol")
                    break
            # If exact match not found, use first result
            if not conid and data["data"]:
                conid = data["data"][0].get("conid")
                matched_symbol = data["data"][0].get("symbol")

        if not conid:
            results.append({"requested_symbol": symbol, "error": f"Could not find conid for symbol {symbol}"})
        else:
            results.append({
                "conid": conid,
                "symbol": matched_symbol,
                "requested_symbol": symbol
            })

    return json.dumps({"results": results})


@mcp_tool
async def get_snapshot_by_conids(conids: str, delay: int = 50) -> str:
    """
    Get market snapshot for given conids.

    This is a convenience endpoint that first calls get_accounts() to prepare the session,
    then fetches market snapshots for the given conids.
    Supports up to 100 conids per request (comma-separated).

    Path (1): get_accounts() -> get_snapshot()

    Args:
        conids: Comma-separated IBKR contract IDs (e.g., "265598" or "265598,123456")
        delay: Delay in seconds between API calls (default: 50). Minimum recommended is 50.

    Returns:
        JSON string with market snapshot data including price, volume, and other fields.

    Examples:
        get_snapshot_by_conids(conids="265598")
        get_snapshot_by_conids(conids="265598,123456,789012")
        get_snapshot_by_conids(conids="265598", delay=60)
    """
    # First call get_accounts to prepare session
    accounts_result = _call_endpoint("iserver/accounts", {})
    if "error" in accounts_result:
        return json.dumps({"error": f"Failed to get accounts: {accounts_result.get('error')}"})

    # Then get snapshot
    result = _get_snapshot(conids, delay)
    return json.dumps(result)


@mcp_tool
async def get_snapshot_by_symbols(symbols: str, delay: int = 50) -> str:
    """
    Get market snapshot for given ticker symbols.

    This is a convenience endpoint that first calls get_accounts() to prepare the session,
    then resolves the symbols to conids, then fetches market snapshots.
    Supports up to 100 symbols per request (comma-separated).

    Path (2): get_accounts() -> search_conids() -> get_snapshot()

    Args:
        symbols: Comma-separated ticker symbols (e.g., "AAPL" or "AAPL,QQQ,MSFT")
        delay: Delay in seconds between API calls (default: 50). Minimum recommended is 50.

    Returns:
        JSON string with market snapshot data including price, volume, and other fields.

    Examples:
        get_snapshot_by_symbols(symbols="AAPL")
        get_snapshot_by_symbols(symbols="AAPL,QQQ,MSFT")
        get_snapshot_by_symbols(symbols="AAPL,QQQ", delay=60)
    """
    # First call get_accounts to prepare session
    accounts_result = _call_endpoint("iserver/accounts", {})
    if "error" in accounts_result:
        return json.dumps({"error": f"Failed to get accounts: {accounts_result.get('error')}"})

    # Then search for conids
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    conid_list = []
    matched_symbols = []
    
    for symbol in symbol_list:
        search_result = _call_endpoint(
            "iserver/secdef/search",
            {"symbol": symbol, "sectype": "STK"}
        )

        if "error" in search_result:
            return json.dumps({"error": f"Failed to search for {symbol}: {search_result.get('error')}"})

        data = search_result.get("data", {})
        conid = None
        matched_symbol = None
        
        if data.get("data"):
            # Try to find exact symbol match first
            for item in data["data"]:
                if item.get("symbol", "").upper() == symbol:
                    conid = item.get("conid")
                    matched_symbol = item.get("symbol")
                    break
            # If exact match not found, use first result
            if not conid and data["data"]:
                conid = data["data"][0].get("conid")
                matched_symbol = data["data"][0].get("symbol")

        if not conid:
            return json.dumps({"error": f"Could not find conid for symbol {symbol}"})

        conid_list.append(str(conid))
        matched_symbols.append(matched_symbol)

    # Build conids string and requested_symbols
    conids = ",".join(conid_list)
    requested_symbols = ",".join(matched_symbols)

    # Then get snapshot
    result = _get_snapshot(conids, delay, requested_symbols)
    return json.dumps(result)


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
