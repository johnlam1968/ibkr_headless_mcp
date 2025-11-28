from dotenv import load_dotenv
from ibind import IbkrClient
from ibind.client.ibkr_definitions import snapshot_by_id
import time
# from typing import Optional, Union, List, Dict


WATCHLIST_SYMBOLS = [
    "VVIX",
    "VIX",
    "VXM", 
    "MBT", 
    "MES", 
    "MCL", 
    "MGC", 
    "USD.JPY", 
    "SPX", 
    "SPY", 
    "RSP", 
    "DIA", 
    "QQQ", 
    "IWM", 
    "HSI", 
    "FXI", 
    "XINA50", 
    "N225", 
    "XAGUSD", 
    "DX", 
    "FVX", 
    "TNX", 
    "TYX", 
    "VOLI", 
    "SDEX", 
    "TDEX", 
    "VIX1D", 
    "VIX9D", 
    "VIX3M", 
    "VIX6M", 
    "VIX1Y"
]
FIELDS = ['55','7051','7635','31','70','71','7295','7741', '7293','7294', '7681', '7724', '7679', '7678','7283', '7087']

load_dotenv()

# Lazy-load IBKR client on first use to avoid connection errors at import time
_client = None

def _get_client():
    """Get or initialize the IBKR client (lazy-loaded).
    
    Returns None if connection fails, allowing imports to continue.
    """
    global _client
    if _client is None:
        try:
            _client = IbkrClient()
        except Exception as e:
            # Log but don't raise - allows imports to succeed
            print(f"⚠️ IBKR Connection Error: {type(e).__name__}: {str(e)}")
            print("   Functions requiring market data will fail until connection is established")
            return None
    return _client

accounts = None

# def _get_accounts() -> Optional[Union[List[str], Dict[str,str]]] | None:
#     """Get brokerage accounts (lazy-loaded)."""
#     global accounts
#     if accounts is None:
#         try:
#             client = _get_client()
#             _result = client.receive_brokerage_accounts()
#         except Exception as e:
#             print(f"⚠️ Warning: Failed to get accounts: {e}")
#             return None
#     return _result.data

def get_conids(symbols: list[str]) -> list[int]:
    client = _get_client()
    if client is None:
        return []
    
    symbol_conids = []
    for _symbol in symbols:
        try:
            _symbol_result = client.search_contract_by_symbol(_symbol)
            conid = _symbol_result.data[0]['conid']
            symbol_conids.append(conid)
        except Exception as e:
            print(e)
            continue
    return symbol_conids

def one_shot_retrieve_watchlist_market_data(conids, fields):
    """Fetch market data snapshot and post-process field IDs.
    
    Field '31' (last price) is required to consider the data valid.
    """
    client = _get_client()
    if client is None:
        return None
    
    response = client.live_marketdata_snapshot(conids=conids, fields=fields)
    entries = response.data
    
    if not entries:
        return None
    
    results = {}
    for entry in entries:
        try:
            result = {}
            for key, value in entry.items():
                if key not in snapshot_by_id:
                    result[key] = value
                    continue
                result[snapshot_by_id[key]] = value
            results[entry['conid']] = result
        except (KeyError, IndexError, AttributeError) as e:
            print(f'⚠️ Error processing entry: {str(e)}')
    
    if entries and '31' in entries[0]:
        return results
    return None

def iterate_to_get_data(conids, fields, max_attempts=10):
    """Fetch market data with retries.
    
    Args:
        conids: List of contract IDs
        fields: List of field IDs
        max_attempts: Max retry attempts (default: 10)
        
    Returns:
        Market data dict or None if all attempts fail
    """
    for attempt in range(max_attempts):
        data_result = one_shot_retrieve_watchlist_market_data(conids=conids, fields=fields)
        if data_result:
            return data_result
        
        if attempt < max_attempts - 1:  # Don't sleep on last iteration
            time.sleep(1)
    
    print(f"⚠️ Failed to retrieve market data after {max_attempts} attempts")
    return None



