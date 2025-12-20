# ============================================================================
# Data Transformation & Caching Utilities
# ============================================================================
"""
Data transformation and field formatting utilities.

Focus: Converting raw IBKR data to usable formats and sanitizing for LLM consumption.
Each call fetches fresh data (no caching for real-time MCP server).
"""

import json
import time
from typing import Any, Dict, Optional, List

from ibind import IbkrClient
from ibind.client.ibkr_definitions import snapshot_by_id
from ibind import Result

# from settings import DEFAULT_FIELDS, PREDEFINED_WATCHLIST_SYMBOLS

# Global client instance
_ibind_client: Optional[IbkrClient] = None

def get_conids(symbols: List[str]) -> List[str]:
    """Resolve ticker symbols to IBKR contract IDs (conids).
    
    Args:
        symbols: List of ticker symbols
        
    Returns:
        List of conids (may be shorter than input if some symbols don't resolve)
    """
    client = get_client()
    if client is None:
        return []
    
    symbol_conids: List[str] = []
    for _symbol in symbols:
        try:
            _symbol_result = client.search_contract_by_symbol(_symbol)
            try:
                data = extract_result_data(_symbol_result)
                conid = str(data['conid']).strip()
                symbol_conids.append(conid)
            except (KeyError, IndexError, AttributeError, TypeError) as e:
                print(f"Error extracting conid: {e}")
                continue
        except Exception as e:
            print(e)
            continue
    return symbol_conids

def iterate_to_fetch_market_data(conids: List[str], fields: List[str], max_attempts: int = 10) -> Optional[Dict[str, Any]]:
    """Fetch market data with retries.
    
    Args:
        conids: List of contract IDs
        fields: List of field IDs
        max_attempts: Max retry attempts (default: 10)
        
    Returns:
        Market data dict or None if all attempts fail
    """
    for attempt in range(max_attempts):
        # Convert conids to string for API call
        conid_str = conids[0] if conids else ""
        data_result = fetch_raw_market_data(conid=conid_str, fields=fields)
        if data_result:
            return data_result
        
        if attempt < max_attempts - 1:  # Don't sleep on last iteration
            time.sleep(1)
    
    print(f"⚠️ Failed to retrieve market data after {max_attempts} attempts")
    return None


# ============================================================================
# INTERNAL HELPERS: Data Formatting
# ============================================================================


# def _sanitize_for_json(obj: Any) -> Any:
#     """Recursively sanitize the payload so it's JSON-serializable.

#     - Converts bytes to UTF-8 strings
#     - Converts datetimes/dates/Decimal to strings
#     - Recurses into lists/tuples/sets/dicts
#     - Falls back to str() for unknown types
#     """
#     # Basic primitives are safe
#     if obj is None or isinstance(obj, (str, int, float, bool)):
#         return obj

#     # Bytes -> string
#     if isinstance(obj, (bytes, bytearray)):
#         try:
#             return obj.decode("utf-8")
#         except Exception:
#             return str(obj)

#     # Datetime/Date -> iso format
#     if isinstance(obj, (datetime, date)):
#         try:
#             return obj.isoformat()
#         except Exception:
#             return str(obj)
    
#     # Decimal -> string
#     if isinstance(obj, Decimal):
#         return str(obj)

#     # Dict-like: recurse
#     if isinstance(obj, dict):
#         out: Dict[str, Any] = {}
#         for k, v in obj.items():
#             try:
#                 key = str(k)
#             except Exception:
#                 key = repr(k)
#             out[key] = _sanitize_for_json(v)
#         return out

#     # Iterable: listify and recurse
#     if isinstance(obj, (list, tuple, set)):
#         return [_sanitize_for_json(v) for v in obj]

#     # Last resort: try json.dumps, else str()
#     try:
#         json.dumps(obj)
#         return obj
#     except Exception:
#         return str(obj)


# def _remove_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
#     """Remove IBKR metadata fields not relevant for LLM analysis."""
#     metadata_keys = {"_updated", "server_id", "conidEx", "market_data_marker", "market_data_availability", "service_params"}
#     return {
#         conid: {k: v for k, v in fields_dict.items() if k not in metadata_keys}
#         if isinstance(fields_dict, dict) else fields_dict
#         for conid, fields_dict in data.items()
#     }


# def _has_valid_prices(data: Dict[str, Any]) -> bool:
#     """Check if data contains at least one instrument with a valid price."""
#     if not data:
#         return False
#     price_keys = ("last_price", "Last", "mark_price")
#     for fields_dict in data.values():
#         if isinstance(fields_dict, dict):
#             for key in price_keys:
#                 if fields_dict.get(key) not in (None, "N/A"):
#                     return True
#     return False


# def get_market_data_of_watchlist(conids: List[str], fields: List[str]=DEFAULT_FIELDS) -> Optional[Dict[str, Any]]:
#     """
#     Fetch real-time market data for predefined watchlist symbols.
    
#     Each call fetches fresh data from IBKR (no caching for MCP server).
#     Validates that data contains valid prices before returning.
    
#     Returns:
#         Market data dict keyed by conid, or None if fetch fails
#     """
    
#     for attempt in range(3):
#         data = iterate_to_fetch_market_data(conids=conids, fields=fields)
#         if data and _has_valid_prices(data):
#             return data
#         if attempt < 2:
#             time.sleep(0.5)
    
#     return None


def get_client() -> Optional[IbkrClient]:
    """
    Get or initialize the IBKR client (lazy-loaded on first use).

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


def to_json(data: Any) -> str:
    """Safely convert any object to JSON string with fallback to str()"""
    try:
        return json.dumps(data, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": "JSON serialization failed", "details": str(e)})


def extract_result_data(result: Result) -> Any:
    """Extract .data attribute from IbkrClient Result object"""
    # This helper is to make PyLance happy
    # if result.data is not None:
    return result.data

def fetch_raw_market_data(conid: str, fields: list[str]) -> Optional[Dict[str, Any]]:
    """Fetch raw market data snapshot from IBKR API.s

    Internal helper. Applies field ID mapping but minimal processing.

    Args:
        conid: Contract ID
        fields: List of field IDs to retrieve

    Returns:
        Dict mapping conid to raw field data, or None if no data
    """
    client = get_client()
    if client is None:
        return None

    response = client.live_marketdata_snapshot(conids=conid, fields=fields)
    entries = extract_result_data(response)

    if not entries:
        return None

    _dict: Dict[str, Any] = {}
    for entry in entries:
        try:
            _entry_dict: Dict[str, Any] = {}
            # Use direct iteration with type ignore for Pylance
            for key, value in entry.items():  # type: ignore
                if key not in snapshot_by_id:
                    _entry_dict[key] = value
                    continue
                _entry_dict[snapshot_by_id[key]] = value
            _dict[entry['conid']] = _entry_dict  # type: ignore
        except (KeyError, IndexError, AttributeError) as e:
            print(f'⚠️ Error processing entry: {str(e)}')

    if entries and '31' in entries[0]:
        return _dict
    return None


def fetch_market_data_snapshot_by_queries(queries: StockQueries, field_list: list[str]) -> Optional[Any]:
    """Fetch market data snapshot by symbol with field validation.

    Returns data only if field '31' (Last Price) is present.

    Args:
        symbol: Ticker symbol
        field_list: List of field IDs to retrieve

    Returns:
        Validated market data or None if validation fails
    """
    client = get_client()
    if client is None:
        return None

    result = client.live_marketdata_snapshot_by_symbol(queries, fields=field_list)  # type: ignore[arg-type]
    data = result  # type: ignore[assignment] - This method returns dict directly, not Result

    if not data:
        return None

    if isinstance(data, dict) and '31' in data:  # type: ignore[unreachable]
        return data  # type: ignore[return-value]

    return None
