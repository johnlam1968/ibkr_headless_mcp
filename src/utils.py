# ============================================================================
# Data Transformation & Caching Utilities
# ============================================================================
"""
Data transformation and field formatting utilities.

Focus: Converting raw IBKR data to usable formats and sanitizing for LLM consumption.
Each call fetches fresh data (no caching for real-time MCP server).
"""

import json
from datetime import date, datetime
import time
from decimal import Decimal
from typing import Any, Dict, Optional, List

from settings import DEFAULT_FIELDS, PREDEFINED_WATCHLIST_SYMBOLS
from ibind_web_client import iterate_to_fetch_market_data, get_conids


# ============================================================================
# INTERNAL HELPERS: Data Formatting
# ============================================================================


def _sanitize_for_json(obj: Any) -> Any:
    """Recursively sanitize the payload so it's JSON-serializable.

    - Converts bytes to UTF-8 strings
    - Converts datetimes/dates/Decimal to strings
    - Recurses into lists/tuples/sets/dicts
    - Falls back to str() for unknown types
    """
    # Basic primitives are safe
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # Bytes -> string
    if isinstance(obj, (bytes, bytearray)):
        try:
            return obj.decode("utf-8")
        except Exception:
            return str(obj)

    # Datetime/Date/Decimal -> iso / string
    if isinstance(obj, (datetime, date, Decimal)):
        try:
            return obj.isoformat()
        except Exception:
            return str(obj)

    # Dict-like: recurse
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for k, v in obj.items():
            try:
                key = str(k)
            except Exception:
                key = repr(k)
            out[key] = _sanitize_for_json(v)
        return out

    # Iterable: listify and recurse
    if isinstance(obj, (list, tuple, set)):
        return [_sanitize_for_json(v) for v in obj]

    # Last resort: try json.dumps, else str()
    try:
        json.dumps(obj)
        return obj
    except Exception:
        return str(obj)


def _remove_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove IBKR metadata fields not relevant for LLM analysis."""
    metadata_keys = {"_updated", "server_id", "conidEx", "market_data_marker", "market_data_availability", "service_params"}
    return {
        conid: {k: v for k, v in fields_dict.items() if k not in metadata_keys}
        if isinstance(fields_dict, dict) else fields_dict
        for conid, fields_dict in data.items()
    }


def _has_valid_prices(data: Dict[str, Any]) -> bool:
    """Check if data contains at least one instrument with a valid price."""
    if not data:
        return False
    price_keys = ("last_price", "Last", "mark_price")
    for fields_dict in data.values():
        if isinstance(fields_dict, dict):
            for key in price_keys:
                if fields_dict.get(key) not in (None, "N/A"):
                    return True
    return False


def get_market_data_of_watchlist(conids: List[int], fields: List[str]=DEFAULT_FIELDS) -> Optional[Dict[str, Any]]:
    """
    Fetch real-time market data for predefined watchlist symbols.
    
    Each call fetches fresh data from IBKR (no caching for MCP server).
    Validates that data contains valid prices before returning.
    
    Returns:
        Market data dict keyed by conid, or None if fetch fails
    """
    
    for attempt in range(3):
        data = iterate_to_fetch_market_data(conids=conids, fields=fields)
        if data and _has_valid_prices(data):
            return data
        if attempt < 2:
            time.sleep(0.5)
    
    return None

def get_market_data_of_predefined_watchlist() -> str:
    try:
        conids = get_conids(PREDEFINED_WATCHLIST_SYMBOLS)
        if not conids:
            return "Watchlist symbols not found."
    except Exception as e:
        return f"Error resolving watchlist symbols: {e}"
    return get_market_data(conids)


def get_market_data(conids: List[int], fields: List[str]=DEFAULT_FIELDS) -> str:
    """
    Fetch real-time market data for predefined watchlist, remove metadata, sanitize, and return as JSON string.
    
    Returns:
        JSON string with cleaned market data, or error message if unavailable
    """
    data = get_market_data_of_watchlist(conids=conids, fields=fields)
    if not data:
        return "Market data unavailable."
    
    filtered = _remove_metadata(data)
    sanitized = _sanitize_for_json(filtered)
    try:
        return json.dumps(sanitized, indent=2, default=str)
    except Exception:
        return json.dumps(sanitized, separators=(",", ":"), default=str)

