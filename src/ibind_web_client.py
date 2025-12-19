"""
Low-level IBKR API wrapper and data fetching.

Focus: Client initialization, symbol/conid resolution, raw market data retrieval,
and low-level data orchestration helpers.
"""
from dotenv import load_dotenv
from ibind import IbkrClient
from ibind.client.ibkr_definitions import snapshot_by_id
import time
from typing import Optional, List, Tuple, Dict, Any

load_dotenv()


def get_client() -> Optional[IbkrClient]:
    """Initialize and return an IBKR API client instance.
    
    Returns:
        IbkrClient instance or None if initialization fails
    """
    try:
        client = IbkrClient()
        return client
    except Exception as e:
        print(f"Error initializing IBKR client: {e}")
        return None

def get_conids(symbols: list[str]) -> list[str]:
    """Resolve ticker symbols to IBKR contract IDs (conids).
    
    Args:
        symbols: List of ticker symbols
        
    Returns:
        List of conids (may be shorter than input if some symbols don't resolve)
    """
    client = get_client()
    if client is None:
        return []
    
    symbol_conids = []
    for _symbol in symbols:
        try:
            _symbol_result = client.search_contract_by_symbol(_symbol)
            try:
                conid = str(_symbol_result.data[0]['conid']).strip()
            except (KeyError, IndexError, AttributeError, TypeError) as e:
                print(f"Error extracting conid: {e}")
                conid = None
            symbol_conids.append(conid)
        except Exception as e:
            print(e)
            continue
    return symbol_conids



# def _fetch_raw_market_data(conids: list[str], fields: list[str]) -> Optional[Dict[int, Dict[str, Any]]]:
#     """Fetch raw market data snapshot from IBKR API.
    
#     Internal helper. Applies field ID mapping but minimal processing.
    
#     Args:
#         conids: List of contract IDs
#         fields: List of field IDs to retrieve
        
#     Returns:
#         Dict mapping conid to raw field data, or None if no data
#     """
#     client = get_client()
#     if client is None:
#         return None
    
#     response = client.live_marketdata_snapshot(conids=conids, fields=fields)
#     entries = response.data
    
#     if not entries:
#         return None
    
#     results = {}
#     for entry in entries:
#         try:
#             result = {}
#             for key, value in entry.items():
#                 if key not in snapshot_by_id:
#                     result[key] = value
#                     continue
#                 result[snapshot_by_id[key]] = value
#             results[entry['conid']] = result
#         except (KeyError, IndexError, AttributeError) as e:
#             print(f'⚠️ Error processing entry: {str(e)}')
    
#     if entries and '31' in entries[0]:
#         return results
#     return None


def iterate_to_fetch_market_data(conids: list[str], fields: list[str], max_attempts: int = 10):
    """Fetch market data with retries.
    
    Args:
        conids: List of contract IDs
        fields: List of field IDs
        max_attempts: Max retry attempts (default: 10)
        
    Returns:
        Market data dict or None if all attempts fail
    """
    for attempt in range(max_attempts):
        data_result = _fetch_raw_market_data(conids=conids, fields=fields)
        if data_result:
            return data_result
        
        if attempt < max_attempts - 1:  # Don't sleep on last iteration
            time.sleep(1)
    
    print(f"⚠️ Failed to retrieve market data after {max_attempts} attempts")
    return None


# ============================================================================
# HISTORICAL DATA HELPERS
# ============================================================================

async def get_historical_data_by_conid(conid: str, bar: str, period: Optional[str], 
                                       exchange: Optional[str], outside_rth: bool) -> Tuple[Any, Optional[Dict[str, Any]]]:
    """
    Low-level helper to fetch historical data by conid.
    
    Returns: (result_object, error_dict_or_None)
    """
    try:
        client = get_client()
        if client is None:
            return None, {"error": "IBKR client not initialized"}
        
        result = client.marketdata_history_by_conid(
            conid=conid,
            bar=bar,
            period=period,
            exchange=exchange,
            outside_rth=outside_rth
        )
        
        if not result or not result.data:
            return None, {"error": f"No historical data found for conid: {conid}"}
        
        return result, None
    except Exception as e:
        return None, {"error": f"Historical data retrieval failed: {str(e)}"}

async def get_historical_data_by_symbol(symbol: str, bar: str, period: Optional[str], 
                                       exchange: Optional[str], outside_rth: bool) -> Tuple[Any, Optional[Dict[str, Any]]]:
    """
    Low-level helper to fetch historical data by symbol.
    
    Returns: (result_object, error_dict_or_None)
    """
    client = get_client()
    if client is None:
        return None, {"error": "IBKR client not initialized"}
    conid = client.search_contract_by_symbol(symbol=symbol).data[0]['conid']
    if not conid:
        return None, {"error": f"Failed to resolve conid for symbol: {symbol}"}
    return await get_historical_data_by_conid(conid=conid, bar=bar, period=period, exchange=exchange, outside_rth=outside_rth)

if __name__ == "__main__":
    print("Testing market data retrieval...")
    test_conids = get_conids(['AAPL', 'MSFT', 'GOOGL'])
    print(f"Retrieved conids: {test_conids}")
    market_data = iterate_to_fetch_market_data(conids=test_conids, fields=['31', '292', '293'])
    print("Market Data:")
    print(market_data)