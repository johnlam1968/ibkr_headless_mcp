"""
Tailored for LLM, this module provides a FastMCP server with documentation to call IBKR (Interactive Brokers) web api endpoints, through ibind rest client (which provides oAuth).
"""
from typing import Any, Dict, Optional, Callable, TypeVar, Awaitable

import json
from mcp.server.fastmcp import FastMCP

from dotenv import load_dotenv
from ibind import IbkrClient, Result # type: ignore

load_dotenv()

# Global client instance
_ibind_client: Optional[IbkrClient] = None


server = FastMCP("ibkr-endpoint-server")


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
            "iserver/account"
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
        call_endpoint(path='iserver/secdef/search', params={"symbol":"US-T", "sectype":"BOND"})
        Valid Values: “STK”, “IND”, “BOND”
        "STK" for Stocks, "IND" for Indices, "BOND" for Bonds.
        call_endpoint('iserver/secdef/search', params={"symbol":"SPY", "sectype":"STK")
        call_endpoint('iserver/secdef/search', params={"symbol":"SPX", "sectype":"IND")
        upstream docs: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#search-symbol-contract

        call_endpoint(path='iserver/secdef/info', params={"conid":"265598"})
        upstream docs: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#secdef-info-contract
        
        call_endpoint(path=f'iserver/contract/265598/info')
        upstream docs: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#info-conid-contract

        call_endpoint(path='iserver/accounts')
        upstream docs: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#get-accounts
        from the response, parse for accountId and use in subsequent calls.

        call_endpoint(path=f'iserver/account/{{ accountId }}/alerts')
        accountId has Value Format: “DU1234567”
        call_endpoint(path=f'iserver/account/{{ “DU1234567” }}/alerts')

        upstream docs: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#get-alert-list
        
        Market Data:
        The best approach is to obtain conid from /iserver/secdef/search. Then use conid in the /iserver/marketdata/snapshot endpoint.
        The endpoint /iserver/accounts must be called prior to /iserver/marketdata/snapshot.
        First call to onboard:
        call_endpoint(path='iserver/marketdata/snapshot', params={"conids":"265598", "fields":"31,84,86"})
        Must call twice to get actual data, first call returns empty data. 
        So, Second call to get actual data:
        call_endpoint(path='iserver/marketdata/snapshot', params={"conids":"265598", "fields":"31,84,86"})

    """
    if params:
        _result = _call_endpoint(path, params)
    else:
        _result = _call_endpoint(path, {})

    if isinstance(_result, str):
                return json.dumps({
            "error": "ibind client not initialized",
        })

    return json.dumps(_result.data) # type: ignore


def _call_endpoint(path: str, params: Dict[str, Any]) -> Result | str:

    client = get_client()
    if client is None:
        return json.dumps({
            "error": "IBKR client not initialized",
        })

    return client.get(path=path, params=params) # type: ignore

@mcp_tool
async def endpont_instructions() -> str:
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
    server.run()
