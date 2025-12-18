# ============================================================================
# Utility Functions
# ============================================================================

import json
from datetime import date, datetime
import time
from decimal import Decimal
from typing import Any, Dict

from settings import FIELDS, WATCHLIST_SYMBOLS
from web_api_client import iterate_to_get_data
from typing import Any, Optional, Dict, List

import time


# Global cache for market data
_data_cache: Optional[Dict[str, Any]] = None
_conids_cache: Optional[List[str]] = None


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


def _get_watchlist_market_data(refresh: bool = False) -> Optional[Dict[str, Any]]:
    """
    Retrieve market data for all configured symbols.

    Args:
        refresh: Force refresh from API (bypass cache)

    Returns:
        Market data dict keyed by conid, or None if fetch fails
    """
    global _data_cache, _conids_cache

    if not refresh and _data_cache is not None:
        return _data_cache

    # Ensure we have conids
    if _conids_cache is None:
        from web_api_client import get_conids
        _conids_cache = get_conids(WATCHLIST_SYMBOLS)

    for attempt in range(3):
        data = iterate_to_get_data(conids=_conids_cache, fields=FIELDS)
        if data and _has_valid_prices(data):
            _data_cache = data
            return _data_cache
        if attempt < 2:
            time.sleep(0.5)

    _data_cache = data
    return _data_cache


def _get_market_json() -> str:
    """Fetch market data, remove metadata, sanitize, and return as JSON string."""
    data = _get_watchlist_market_data()
    if not data:
        return "Market data unavailable."

    filtered = _remove_metadata(data)
    sanitized = _sanitize_for_json(filtered)
    try:
        return json.dumps(sanitized, indent=2, default=str)
    except Exception:
        return json.dumps(sanitized, separators=(",", ":"), default=str)


def get_market_data(refresh: bool = False) -> Optional[Dict[str, Any]]:
    """Public wrapper for retrieving market data."""
    return _get_watchlist_market_data(refresh=refresh)


def get_market_summary() -> str:
    """Public wrapper for getting market summary."""
    return _get_market_json()
