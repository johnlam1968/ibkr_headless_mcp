import json
import sys
import os
import time
from typing import Optional, List
from fastmcp import FastMCP
from using_external_llm import (
    analyze_market,
    narrate_market_with_instructions
)
from utils import get_market_data
from web_api_client import (
    get_conids, 
    iterate_to_get_data,
    one_shot_retrieve_watchlist_market_data,
    _get_client
)

# IBKR market data field mappings
MARKET_DATA_FIELDS = {
    '31': 'last_price',
    '292': 'ask',
    '293': 'bid',
    '7': 'option_call_volume',
    '8': 'option_put_volume',
    '9': 'option_put_call_ratio',
    '10': 'historical_volatility',
    '11': 'option_implied_volatility',
}

server = FastMCP("market-analysis-server")

# ============================================================================
# IBKR BROKER DATA RETRIEVAL TOOLS
# ============================================================================

@server.tool()
async def get_market_snapshot_ibkr(symbols: List[str]) -> str:
    """
    Get real-time market data snapshot for multiple symbols.
    
    Args:
        symbols: List of ticker symbols (e.g., ['AAPL', 'MSFT', 'GOOGL'])
    
    Returns:
        JSON string with market data including last price, bid, ask for each symbol.
    """
    try:
        conids = get_conids(symbols)
        if not conids:
            return json.dumps({"error": "Failed to resolve any symbols", "symbols": symbols})
        
        fields = ['31', '292', '293']  # last_price, ask, bid
        market_data = iterate_to_get_data(conids=conids, fields=fields, max_attempts=10)
        
        if not market_data:
            return json.dumps({"error": "Failed to retrieve market data", "conids": conids})
        
        result = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "symbols": symbols,
            "data": market_data
        }
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Market snapshot failed: {str(e)}"})


@server.tool()
async def get_symbol_details_ibkr(symbol: str) -> str:
    """
    Search for and retrieve contract details for a symbol.
    
    Args:
        symbol: Ticker symbol to search for (e.g., 'AAPL')
    
    Returns:
        JSON string with contract information including conid, description, exchange.
    """
    try:
        client = _get_client()
        if client is None:
            return json.dumps({"error": "IBKR client not initialized"})
        
        result = client.search_contract_by_symbol(symbol)
        
        if not result.data or len(result.data) == 0:
            return json.dumps({"error": f"No contracts found for symbol: {symbol}"})
        
        contracts = result.data[:5]
        response = {
            "symbol": symbol,
            "matches": contracts,
            "count": len(contracts)
        }
        return json.dumps(response, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Symbol lookup failed: {str(e)}"})


@server.tool()
async def get_account_summary_ibkr() -> str:
    """
    Get summary of brokerage accounts connected to IBKR.
    
    Returns:
        JSON string with list of available accounts and their details.
    """
    try:
        client = _get_client()
        if client is None:
            return json.dumps({"error": "IBKR client not initialized"})
        
        result = client.receive_brokerage_accounts()
        
        if not result.data:
            return json.dumps({"error": "No accounts available"})
        
        response = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "accounts": result.data
        }
        return json.dumps(response, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Account retrieval failed: {str(e)}"})


@server.tool()
async def get_portfolio_positions_ibkr(account_id: Optional[str] = None) -> str:
    """
    Get current portfolio positions for an account.
    
    Args:
        account_id: Account ID to retrieve positions for. If None, uses default account.
    
    Returns:
        JSON string with current positions, quantities, and values.
    """
    try:
        client = _get_client()
        if client is None:
            return json.dumps({"error": "IBKR client not initialized"})
        
        if account_id is None:
            accounts_result = client.receive_brokerage_accounts()
            if not accounts_result.data or len(accounts_result.data) == 0:
                return json.dumps({"error": "No accounts available"})
            account_id = accounts_result.data[0]['account']
        
        result = client.get_portfolio(account_id=account_id)
        
        if not result.data:
            return json.dumps({"error": f"No positions found for account: {account_id}"})
        
        response = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "account_id": account_id,
            "positions": result.data
        }
        return json.dumps(response, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Portfolio retrieval failed: {str(e)}"})


@server.tool()
async def get_market_data_enhanced_ibkr(symbols: List[str], include_bid_ask: bool = True) -> str:
    """
    Get enhanced market data with bid/ask spreads and additional fields.
    
    Args:
        symbols: List of ticker symbols
        include_bid_ask: Whether to include bid/ask data (default: True)
    
    Returns:
        JSON string with detailed market data snapshot.
    """
    try:
        conids = get_conids(symbols)
        if not conids:
            return json.dumps({"error": "Failed to resolve symbols", "symbols": symbols})
        
        if include_bid_ask:
            fields = ['31', '292', '293', '10', '11']  # price, ask, bid, hist vol, impl vol
        else:
            fields = ['31']  # just last price
        
        market_data = iterate_to_get_data(conids=conids, fields=fields, max_attempts=10)
        
        if not market_data:
            return json.dumps({"error": "Failed to retrieve market data"})
        
        formatted_data = {}
        for conid, data in market_data.items():
            formatted_entry = {}
            for field_id, value in data.items():
                field_name = MARKET_DATA_FIELDS.get(str(field_id), field_id)
                formatted_entry[field_name] = value
            formatted_data[conid] = formatted_entry
        
        response = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "symbols": symbols,
            "data": formatted_data,
            "fields_included": [MARKET_DATA_FIELDS.get(f, f) for f in fields]
        }
        return json.dumps(response, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Enhanced market data failed: {str(e)}"})


@server.tool()
async def watch_symbols_ibkr(symbols: List[str]) -> str:
    """
    Watch symbols for real-time price updates. Returns current snapshot.
    
    Args:
        symbols: List of ticker symbols to watch
    
    Returns:
        JSON string with current prices and market data for watched symbols.
    """
    try:
        conids = get_conids(symbols)
        if not conids:
            return json.dumps({"error": "Failed to resolve symbols", "symbols": symbols})
        
        fields = ['31', '292', '293']  # last price, ask, bid
        market_data = iterate_to_get_data(conids=conids, fields=fields, max_attempts=5)
        
        if not market_data:
            return json.dumps({"error": "Failed to retrieve watchlist data"})
        
        response = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "watched_symbols": symbols,
            "market_data": market_data,
            "status": "monitoring"
        }
        return json.dumps(response, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Watchlist failed: {str(e)}"})


# ============================================================================
# HISTORICAL DATA TOOLS
# ============================================================================

@server.tool()
async def get_historical_data_by_conid_ibkr(conid: str, bar: str, period: Optional[str] = None, exchange: Optional[str] = None, outside_rth: bool = False) -> str:
    """
    Get historical market data for a given contract ID.
    
    Args:
        conid: Contract identifier
        bar: Bar size (e.g., "1min", "5min", "1h", "1d")
        period: Data duration (e.g., "1d", "1w", "1m", "1y")
        exchange: Specific exchange (optional)
        outside_rth: Include trades outside regular trading hours (default: False)
    
    Returns:
        JSON string with historical OHLC data
    """
    try:
        client = _get_client()
        if client is None:
            return json.dumps({"error": "IBKR client not initialized"})
        
        result = client.marketdata_history_by_conid(
            conid=conid,
            bar=bar,
            period=period,
            exchange=exchange,
            outside_rth=outside_rth
        )
        
        if not result.data:
            return json.dumps({"error": f"No historical data found for conid: {conid}"})
        
        response = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "conid": conid,
            "bar": bar,
            "period": period,
            "data": result.data
        }
        return json.dumps(response, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Historical data retrieval failed: {str(e)}"})


@server.tool()
async def get_historical_data_by_symbol_ibkr(symbol: str, bar: str, period: Optional[str] = None, exchange: Optional[str] = None, outside_rth: bool = False) -> str:
    """
    Get historical market data by symbol.
    
    Args:
        symbol: Ticker symbol
        bar: Bar size (e.g., "1min", "5min", "1h", "1d")
        period: Data duration (e.g., "1d", "1w", "1m", "1y")
        exchange: Specific exchange (optional)
        outside_rth: Include trades outside regular trading hours (default: False)
    
    Returns:
        JSON string with historical OHLC data
    """
    try:
        client = _get_client()
        if client is None:
            return json.dumps({"error": "IBKR client not initialized"})
        
        result = client.marketdata_history_by_symbol(
            symbol=symbol,
            bar=bar,
            period=period,
            exchange=exchange,
            outside_rth=outside_rth
        )
        
        if not result.data:
            return json.dumps({"error": f"No historical data found for symbol: {symbol}"})
        
        response = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": symbol,
            "bar": bar,
            "period": period,
            "data": result.data
        }
        return json.dumps(response, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Historical data retrieval failed: {str(e)}"})


@server.tool()
async def get_historical_data_batch_by_conids_ibkr(conids: List[str], bar: str = "1min", period: str = "1d", outside_rth: bool = True, run_in_parallel: bool = True) -> str:
    """
    Get historical data for multiple contract IDs in batch (parallel by default).
    
    Args:
        conids: List of contract identifiers
        bar: Bar size (default: "1min")
        period: Data duration (default: "1d")
        outside_rth: Include after-hours data (default: True)
        run_in_parallel: Execute in parallel (default: True)
    
    Returns:
        JSON string with historical data for all conids
    """
    try:
        client = _get_client()
        if client is None:
            return json.dumps({"error": "IBKR client not initialized"})
        
        result = client.marketdata_history_by_conids(
            conids=conids,
            bar=bar,
            period=period,
            outside_rth=outside_rth,
            run_in_parallel=run_in_parallel
        )
        
        if not result:
            return json.dumps({"error": f"No historical data found for conids"})
        
        response = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "conids": conids,
            "bar": bar,
            "period": period,
            "parallel": run_in_parallel,
            "data": result
        }
        return json.dumps(response, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Batch historical data retrieval failed: {str(e)}"})


@server.tool()
async def get_historical_data_batch_by_symbols_ibkr(symbols: List[str], bar: str = "1min", period: str = "1d", outside_rth: bool = True, run_in_parallel: bool = True) -> str:
    """
    Get historical data for multiple symbols in batch (parallel by default).
    
    Args:
        symbols: List of ticker symbols
        bar: Bar size (default: "1min")
        period: Data duration (default: "1d")
        outside_rth: Include after-hours data (default: True)
        run_in_parallel: Execute in parallel (default: True)
    
    Returns:
        JSON string with historical data for all symbols
    """
    try:
        client = _get_client()
        if client is None:
            return json.dumps({"error": "IBKR client not initialized"})
        
        result = client.marketdata_history_by_symbols(
            queries=symbols,
            bar=bar,
            period=period,
            outside_rth=outside_rth,
            run_in_parallel=run_in_parallel
        )
        
        if not result:
            return json.dumps({"error": f"No historical data found for symbols"})
        
        response = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "symbols": symbols,
            "bar": bar,
            "period": period,
            "parallel": run_in_parallel,
            "data": result
        }
        return json.dumps(response, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Batch historical data retrieval failed: {str(e)}"})


# ============================================================================
# EXISTING MARKET ANALYSIS TOOLS
# ============================================================================

@server.tool()
async def list_market_tools() -> str:
    """List available market analysis tools so the client knows what to call"""
    return """Available Tools:

REAL-TIME MARKET DATA:
  - get_market_snapshot_ibkr(symbols): Get real-time prices (bid/ask/last)
  - get_symbol_details_ibkr(symbol): Look up contract details
  - get_market_data_enhanced_ibkr(symbols, include_bid_ask): Get enhanced data with volatility
  - watch_symbols_ibkr(symbols): Monitor symbols for real-time updates

ACCOUNT & PORTFOLIO:
  - get_account_summary_ibkr(): List connected brokerage accounts
  - get_portfolio_positions_ibkr(account_id): Get current holdings and P&L

HISTORICAL DATA (Single):
  - get_historical_data_by_conid_ibkr(conid, bar, period): Historical data by contract ID
  - get_historical_data_by_symbol_ibkr(symbol, bar, period): Historical data by symbol

HISTORICAL DATA (Batch):
  - get_historical_data_batch_by_conids_ibkr(conids, bar, period): Batch historical by conids (parallel)
  - get_historical_data_batch_by_symbols_ibkr(symbols, bar, period): Batch historical by symbols (parallel)

EXISTING ANALYSIS TOOLS:
  - get_market_snapshot(): Get current market snapshot of predefined watchlist (internal data)
  - get_custom_prompt(): Get custom prompt instructions
  - analyze_question(question): Analyze market question with external LLM
  - generate_narrative(): Generate detailed market narrative with external LLM"""

@server.tool()
async def get_custom_prompt() -> str:
    """Get the user's custom prompt instructions for market analysis"""
    from settings import NARRATIVE_INSTRUCTIONS
    return NARRATIVE_INSTRUCTIONS

@server.tool()
async def get_market_snapshot() -> str:
    """Get current market snapshot of predefined watchlist of key instruments to serve as context, no analysis"""
    try:
        return json.dumps(get_market_data(), indent=2)
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def analyze_question(question: str) -> str:
    """Analyze market question with with an external LLM, then serve context"""
    try:
        return analyze_market(question)
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def generate_narrative() -> str:
    """Generate detailed market narrative analysis with an external LLM, then serve context"""
    try:
        return narrate_market_with_instructions()
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    server.run()

# to run the server from command line:
# cd /home/john/CodingProjects/llm_public && PYTHONPATH=./src python src/mcp_server.py