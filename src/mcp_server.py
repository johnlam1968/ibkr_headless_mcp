"""
MCP Server: IBKR ContractMixin + MarketdataMixin Tools - Complete Implementation

Exposes ALL Interactive Brokers ContractMixin and MarketdataMixin methods via FastMCP.
Provides comprehensive contract search, market data retrieval, and trading information.

All 26 Tools:
  Search & Lookup (7):
    1. search_contract() - Search by symbol/name/issuer
    2. security_definition() - Get security definitions by conids
    3. all_exchange_contracts() - Get all contracts on an exchange
    4. contract_information() - Full contract details
    5. currency_pairs() - Available currency pairs
    6. security_futures() - Future contracts by symbol
    7. security_stocks() - Stock information by queries

  Contract Details (3):
    8. get_contract_details() - Derivative specifications (options/futures/bonds)
    9. get_option_strikes() - Available option/warrant strikes
    10. trading_schedule() - Trading hours by symbol/exchange

  Trading Rules & Info (3):
    11. get_trading_rules() - Trading constraints for a contract
    12. contract_info_and_rules() - Combined contract info + rules
    13. currency_exchange_rate() - Exchange rates between currencies

  Bond & Algorithm Tools (2):
    14. get_bond_filters() - Bond issuer filtering options
    15. algo_params() - IB Algo parameters for a contract

  Live Market Data (2):
    16. live_marketdata_snapshot() - Current bid/ask/last price by conid
    17. live_marketdata_snapshot_by_symbol() - Current market data by symbol

  Historical Market Data (5):
    18. marketdata_history_by_conid() - OHLC historical data by conid
    19. marketdata_history_by_symbol() - OHLC historical data by symbol
    20. marketdata_history_by_conids() - Batch OHLC by conids (parallel)
    21. marketdata_history_by_symbols() - Batch OHLC by symbols (parallel)
    22. historical_marketdata_beta() - Advanced OHLC with custom time range

  Regulatory & Subscriptions (3):
    23. regulatory_snapshot() - Regulatory market data (costs $0.01 USD per call)
    24. marketdata_unsubscribe() - Cancel market data subscription for a contract
    25. marketdata_unsubscribe_all() - Cancel all market data subscriptions

  Utility (1):
    26. list_tools() - Show documentation with all tools

Usage:
  cd /home/john/CodingProjects/llm_public
  PYTHONPATH=./src python src/mcp_server.py
"""

from typing import Optional
from fastmcp import FastMCP

from dotenv import load_dotenv
from ibind.client.ibkr_utils import StockQueries

from utils import fetch_market_data_snapshot_by_queries, fetch_raw_market_data, extract_result_data, to_json, get_client

load_dotenv()


# ============================================================================
# CLIENT INITIALIZATION (Lazy-Loading)
# ============================================================================



# ============================================================================
# MCP SERVER SETUP
# ============================================================================

server = FastMCP("ibkr-contract-server")


# ============================================================================
# TOOL 1: Search Contract by Symbol or Company Name
# ============================================================================

@server.tool()
async def search_contract(
    symbol: str,
    search_by_name: Optional[bool] = None,
    security_type: Optional[str] = None
) -> str:
    """
    Search for contracts by underlying symbol or company name.
    
    Returns what derivative contracts are available for the given underlying.
    This endpoint must be called before using get_contract_details().
    
    Args:
        symbol: Ticker symbol (e.g., "AAPL") or company name if search_by_name=True.
                Can also be bond issuer type to retrieve bonds.
        search_by_name: If True, treat symbol as company name instead of ticker.
        security_type: Filter by type. Valid: "STK", "IND", "BOND"
    
    Returns:
        JSON with matching contracts (conid, symbol, description, exchange, etc.)
        or error dict if search fails.
    
    Examples:
        search_contract("AAPL") 
        search_contract("Apple", search_by_name=True)
        search_contract("US Treasury", security_type="BOND")
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        if search_by_name is not None and security_type is not None:
            result = client.search_contract_by_symbol(
                symbol=symbol,
                name=search_by_name,
                sec_type=security_type
            )
        elif search_by_name is not None:
            result = client.search_contract_by_symbol(
                symbol=symbol,
                name=search_by_name
            )
        elif security_type is not None:
            result = client.search_contract_by_symbol(
                symbol=symbol,
                sec_type=security_type
            )
        else:
            result = client.search_contract_by_symbol(symbol=symbol)
        
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No contracts found",
                "searched": symbol,
                "search_by_name": search_by_name,
                "security_type": security_type
            })
        
        return to_json({"contracts": data})
    
    except Exception as e:
        return to_json({
            "error": "Contract search failed",
            "exception": str(e),
            "symbol": symbol
        })


# ============================================================================
# TOOL 2: Get Security Definitions by Conids
# ============================================================================

@server.tool()
async def security_definition(
    conids: str
) -> str:
    """
    Get security definitions for given contract IDs.
    
    Returns a list of security definitions with detailed contract information.
    Useful for retrieving multiple contracts at once.
    
    Args:
        conids: Comma-separated contract IDs (e.g., "265598,9408,12345")
                Can also be a single conid (e.g., "265598")
    
    Returns:
        JSON with security definitions for each conid or error dict.
    
    Examples:
        security_definition("265598")
        security_definition("265598,9408,12345")
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.security_definition_by_conid(conids.split(','))
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No security definitions found",
                "conids": conids
            })
        
        return to_json({"definitions": data})
    
    except Exception as e:
        return to_json({
            "error": "Security definition lookup failed",
            "exception": str(e),
            "conids": conids
        })


# ============================================================================
# TOOL 3: Get All Contracts on an Exchange
# ============================================================================

@server.tool()
async def all_exchange_contracts(exchange: str) -> str:
    """
    Get all tradable contracts on a specific exchange.
    
    Returns all contracts available on the exchange, including those not
    using the exchange as their primary listing.
    
    Note: Only available for Stock contracts.
    
    Args:
        exchange: Single exchange identifier (e.g., "NASDAQ", "NYSE", "SMART")
    
    Returns:
        JSON list of all contract IDs on the exchange or error dict.
    
    Examples:
        all_exchange_contracts("NASDAQ")
        all_exchange_contracts("NYSE")
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.all_conids_by_exchange(exchange)
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No contracts found for exchange",
                "exchange": exchange,
                "suggestion": "Note: This endpoint only supports stock contracts"
            })
        
        return to_json({"contracts": data, "exchange": exchange})
    
    except Exception as e:
        return to_json({
            "error": "Exchange contract lookup failed",
            "exception": str(e),
            "exchange": exchange
        })


# ============================================================================
# TOOL 4: Get Full Contract Information by Conid
# ============================================================================

@server.tool()
async def contract_information(conid: str) -> str:
    """
    Get full contract details for a specific contract ID.
    
    Returns comprehensive contract information including trading hours,
    multiplier, tick size, and other contract specifications.
    
    Args:
        conid: Contract ID (e.g., "265598" for Apple stock)
    
    Returns:
        JSON with complete contract information or error dict.
    
    Examples:
        contract_information("265598")  # Apple stock
        contract_information("9408")    # ES (E-mini S&P 500)
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.contract_information_by_conid(conid)
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No contract information found",
                "conid": conid
            })
        
        return to_json({"information": data})
    
    except Exception as e:
        return to_json({
            "error": "Contract information lookup failed",
            "exception": str(e),
            "conid": conid
        })


# ============================================================================
# TOOL 5: Get Currency Pairs
# ============================================================================

@server.tool()
async def currency_pairs(currency: str) -> str:
    """
    Get available currency pairs for a target currency.
    
    Returns official currency pairs corresponding to the given target currency.
    
    Args:
        currency: Target currency code (e.g., "USD", "EUR", "GBP")
    
    Returns:
        JSON with available currency pairs or error dict.
    
    Examples:
        currency_pairs("USD")
        currency_pairs("EUR")
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.currency_pairs(currency)
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No currency pairs found",
                "currency": currency
            })
        
        return to_json({"pairs": data, "currency": currency})
    
    except Exception as e:
        return to_json({
            "error": "Currency pairs lookup failed",
            "exception": str(e),
            "currency": currency
        })


# ============================================================================
# TOOL 6: Get Exchange Rate Between Currencies
# ============================================================================

@server.tool()
async def currency_exchange_rate(source: str, target: str) -> str:
    """
    Get the exchange rate between two currencies.
    
    Returns current exchange rate from source currency to target currency.
    
    Args:
        source: Base currency code (e.g., "USD", "EUR")
        target: Quote currency code (e.g., "EUR", "GBP")
    
    Returns:
        JSON with exchange rate information or error dict.
    
    Examples:
        currency_exchange_rate("USD", "EUR")
        currency_exchange_rate("EUR", "GBP")
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.currency_exchange_rate(source, target)
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No exchange rate found",
                "source": source,
                "target": target
            })
        
        return to_json({"rate": data, "source": source, "target": target})
    
    except Exception as e:
        return to_json({
            "error": "Exchange rate lookup failed",
            "exception": str(e),
            "source": source,
            "target": target
        })


# ============================================================================
# TOOL 7: Get Contract Info and Rules Combined
# ============================================================================

@server.tool()
async def contract_info_and_rules(conid: str, is_buy: Optional[bool] = None) -> str:
    """
    Get both contract information and trading rules in a single request.
    
    Combines contract details with trading rules for the specified contract
    and order side.
    
    Args:
        conid: Contract ID
        is_buy: Order side. True for Buy orders, False for Sell orders.
                Defaults to True if not specified.
    
    Returns:
        JSON with combined contract info and rules or error dict.
    
    Examples:
        contract_info_and_rules("265598")
        contract_info_and_rules("265598", is_buy=True)
        contract_info_and_rules("265598", is_buy=False)
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        buy_side = is_buy if is_buy is not None else True
        result = client.info_and_rules_by_conid(conid, buy_side)
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No contract info and rules found",
                "conid": conid,
                "is_buy": is_buy
            })
        
        return to_json({"info_and_rules": data})
    
    except Exception as e:
        return to_json({
            "error": "Contract info and rules lookup failed",
            "exception": str(e),
            "conid": conid
        })


# ============================================================================
# TOOL 8: Get Algorithm Parameters for Contract
# ============================================================================

@server.tool()
async def algo_params(
    conid: str,
    algos: Optional[str] = None,
    add_description: Optional[bool] = None,
    add_params: Optional[bool] = None
) -> str:
    """
    Get supported IB Algo parameters for a contract.
    
    Returns list of supported algorithmic order types and their parameters.
    
    Args:
        conid: Contract ID
        algos: Comma-separated list of algo IDs (case-sensitive, max 8)
        add_description: If True, include algorithm descriptions
        add_params: If True, show algorithm parameters
    
    Returns:
        JSON with available algorithms and parameters or error dict.
    
    Examples:
        algo_params("265598")
        algo_params("265598", algos="AD,TWAP", add_description=True)
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        algo_list = algos.split(',') if algos else None  # type: ignore
        desc_str = "1" if add_description else "0" if add_description is not None else None
        params_str = "1" if add_params else "0" if add_params is not None else None
        
        result = client.algo_params_by_conid(
            conid,
            algos=algo_list,  # type: ignore
            add_description=desc_str,  # type: ignore
            add_params=params_str  # type: ignore
        )
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No algo parameters found",
                "conid": conid,
                "algos": algos
            })
        
        return to_json({"algorithms": data})
    
    except Exception as e:
        return to_json({
            "error": "Algorithm parameters lookup failed",
            "exception": str(e),
            "conid": conid
        })


# ============================================================================
# TOOL 9: Get Bond Issuer Filters
# ============================================================================

@server.tool()
async def get_bond_filters(bond_issuer_id: str) -> str:
    """
    Get available filters for a bond issuer.
    
    Returns filtering options for researching bonds from a specific issuer.
    Used for bond contract searches and refinement.
    
    Args:
        bond_issuer_id: Issuer identifier (format: "e1234567")
    
    Returns:
        JSON with available bond filters or error dict.
    
    Examples:
        get_bond_filters("e1359061") for issuer United States Treasury
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.search_bond_filter_information(
            symbol="BOND",
            issuer_id=bond_issuer_id
        )
        
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No bond filters found",
                "bond_issuer_id": bond_issuer_id,
                "suggestion": "Check issuer_id format (should be like 'e123456')"
            })
        
        return to_json({"filters": data})
    
    except Exception as e:
        return to_json({
            "error": "Bond filters lookup failed",
            "exception": str(e),
            "bond_issuer_id": bond_issuer_id
        })


# ============================================================================
# TOOL 10: Get Contract Details (Options/Futures/Bonds)
# ============================================================================

@server.tool()
async def get_contract_details(
    conid: str,
    security_type: str,
    expiration_month: str,
    exchange: Optional[str] = None,
    strike: Optional[str] = None,
    option_right: Optional[str] = None,
    bond_issuer_id: Optional[str] = None
) -> str:
    """
    Get detailed contract specifications for derivatives.
    
    Provides complete trading details including multiplier, tick size,
    trading hours, position limits, and more.
    
    Args:
        conid: Contract ID of the underlying (or final derivative conid)
        security_type: Type of contract ("OPT", "FUT", "WAR", "CASH", "CFD", "BOND")
        expiration_month: Expiration in format "{3-char month}{2-char year}" (e.g., "JAN25")
        exchange: Specific exchange (optional)
        strike: **Required for options/warrants/futures options**
        option_right: **Required for options**: "C" (Call) or "P" (Put)
        bond_issuer_id: **Required for bonds**: Format "e1234567"
    
    Returns:
        JSON with full contract specifications or error dict.
    
    Examples:
        get_contract_details("265598", "OPT", "JAN25", strike="150", option_right="C")
        get_contract_details("209", "FUT", "JAN25")
    """
    if security_type in ["OPT", "WAR"] and (not strike or not option_right):
        return to_json({
            "error": "Missing required parameters for options/warrants",
            "required_for_options": ["strike", "option_right"],
            "provided": {"strike": strike, "option_right": option_right}
        })
    
    if security_type == "BOND" and not bond_issuer_id:
        return to_json({
            "error": "Missing required parameter for bonds",
            "required_for_bonds": ["bond_issuer_id"],
            "issuer_id_format": "e1234567"
        })
    
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.search_secdef_info_by_conid(
            conid=conid,
            sec_type=security_type,
            month=expiration_month,
            exchange=exchange or "",
            strike=strike or "",
            right=option_right or "",
            issuer_id=bond_issuer_id or ""
        )
        
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No contract details found",
                "conid": conid,
                "security_type": security_type,
                "expiration_month": expiration_month
            })
        
        return to_json({"details": data})
    
    except Exception as e:
        return to_json({
            "error": "Contract details lookup failed",
            "exception": str(e),
            "conid": conid
        })


# ============================================================================
# TOOL 11: Get Available Option/Warrant Strikes
# ============================================================================

@server.tool()
async def get_option_strikes(
    conid: str,
    security_type: str,
    expiration_month: str,
    exchange: Optional[str] = None
) -> str:
    """
    Get list of available strike prices for options or warrants.
    
    Returns all possible strikes supported for a given underlying and expiration.
    
    Args:
        conid: Contract ID of the underlying
        security_type: "OPT" (Options) or "WAR" (Warrants)
        expiration_month: Format "{3-char month}{2-char year}" (e.g., "JAN25")
        exchange: Specific exchange (optional, defaults to "SMART")
    
    Returns:
        JSON list of available strike prices or error dict.
    
    Examples:
        get_option_strikes("265598", "OPT", "JAN25")
        get_option_strikes("265598", "OPT", "JAN25", exchange="CBOE")
    """
    if security_type not in ["OPT", "WAR"]:
        return to_json({
            "error": f"Invalid security_type: {security_type}",
            "valid_types": ["OPT", "WAR"],
            "suggestion": "Use 'OPT' for options or 'WAR' for warrants"
        })
    
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.search_strikes_by_conid(
            conid=conid,
            sec_type=security_type,
            month=expiration_month,
            exchange=exchange or ""
        )
        
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No strikes found",
                "conid": conid,
                "security_type": security_type,
                "expiration_month": expiration_month
            })
        
        count = len(data) if isinstance(data, list) else "unknown"  # type: ignore
        return to_json({"strikes": data, "count": count})
    
    except Exception as e:
        return to_json({
            "error": "Strike lookup failed",
            "exception": str(e),
            "conid": conid
        })


# ============================================================================
# TOOL 12: Get Trading Rules for a Contract
# ============================================================================

@server.tool()
async def get_trading_rules(
    conid: str,
    exchange: Optional[str] = None,
    is_buy: Optional[bool] = None,
    modify_order: Optional[bool] = None,
    order_id: Optional[int] = None
) -> str:
    """
    Get trading-related rules and constraints for a specific contract.
    
    Returns position limits, minimum order size, trading hours, and other
    constraints that apply when trading this contract.
    
    Args:
        conid: Contract ID
        exchange: Specific exchange (optional)
        is_buy: Side of market (True=Buy, False=Sell). Defaults to True.
        modify_order: If True, get rules for modifying an existing order
        order_id: **Required if modify_order=True**
    
    Returns:
        JSON with trading rules and constraints or error dict.
    
    Examples:
        get_trading_rules("265598")
        get_trading_rules("265598", is_buy=False)
        get_trading_rules("265598", modify_order=True, order_id=12345)
    """
    if modify_order and order_id is None:
        return to_json({
            "error": "Missing required parameter",
            "requirement": "order_id must be provided when modify_order=True",
            "modify_order": modify_order
        })
    
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.search_contract_rules(
            conid=conid,
            exchange=exchange or "",
            is_buy=is_buy if is_buy is not None else False,
            modify_order=modify_order if modify_order is not None else False,
            order_id=order_id or 0
        )
        
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No trading rules found",
                "conid": conid,
                "exchange": exchange,
                "is_buy": is_buy
            })
        
        return to_json({"rules": data})
    
    except Exception as e:
        return to_json({
            "error": "Trading rules lookup failed",
            "exception": str(e),
            "conid": conid
        })


# ============================================================================
# TOOL 13: Get Future Contracts by Symbol
# ============================================================================

@server.tool()
async def security_futures(symbols: str) -> str:
    """
    Get list of non-expired future contracts for given symbol(s).
    
    Returns all available futures contracts for the specified underlying(s).
    
    Args:
        symbols: Comma-separated symbol list (e.g., "ES,NQ,GC")
                 Can also be a single symbol (e.g., "ES")
    
    Returns:
        JSON with available future contracts or error dict.
    
    Examples:
        security_futures("ES")
        security_futures("ES,NQ,GC")
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.security_future_by_symbol(symbols.split(','))
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No futures contracts found",
                "symbols": symbols
            })
        
        return to_json({"futures": data, "symbols": symbols})
    
    except Exception as e:
        return to_json({
            "error": "Futures contract lookup failed",
            "exception": str(e),
            "symbols": symbols
        })


# ============================================================================
# TOOL 14: Get Stock Information by Symbol
# ============================================================================

@server.tool()
async def security_stocks(
    queries: StockQueries,
    default_filtering: Optional[bool] = None
) -> str:
    """
    Get stock information for given symbols with advanced filtering.
    
    Retrieves and filters stock information based on StockQuery objects.
    This is the proper implementation using security_stocks_by_symbol().
    
    Args:
        queries: StockQueries object or list of StockQuery objects.
                 Can also be a comma-separated string of symbols for simple usage.
                 Example strings: "AAPL", "AAPL,MSFT,GOOGL"
                 
                 **For LLM Clients:**
                 - **Simple usage:** Use comma-separated string: "AAPL,MSFT,GOOGL"
                 - **Advanced filtering:** Use StockQuery objects for precise control
                 
                 **StockQuery Structure:**
                 ```python
                 {
                     "symbol": "AAPL",                    # Required: Stock symbol
                     "name_match": "Apple",              # Optional: Partial name match
                     "instrument_conditions": {          # Optional: Exact instrument matches
                         "some_instrument_field": "value"
                     },
                     "contract_conditions": {            # Optional: Exact contract matches
                         "isUS": True,                   # Filter for US contracts
                         "exchange": "NASDAQ"            # Filter by exchange
                     }
                 }
                 ```
                 
        default_filtering: Whether to apply default US contract filtering {isUS: True}.
                          Defaults to None (uses global default).
                          Set to True to filter for US contracts only.
                          Set to False to disable default filtering.
    
    Returns:
        JSON with stock information or error dict.
    
    Examples:
        # Simple string usage (recommended for LLM clients)
        security_stocks("AAPL")
        security_stocks("AAPL,MSFT,GOOGL")
        
        # Advanced StockQuery usage
        security_stocks([
            {"symbol": "AAPL", "contract_conditions": {"isUS": True}},
            {"symbol": "MSFT", "name_match": "Microsoft"}
        ])
        
        # With default filtering
        security_stocks("AAPL,MSFT", default_filtering=True)
        
    Common Contract Conditions for filtering:
        - "isUS": True/False - US-listed contracts
        - "exchange": "NASDAQ"/"NYSE" - Specific exchange
        - "currency": "USD" - Trading currency
        - "assetClass": "STK" - Asset class
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        # Handle simple string input (comma-separated symbols)
        if isinstance(queries, str):
            # Convert comma-separated string to list of StockQuery objects
            from ibind.client.ibkr_utils import StockQuery
            symbol_list = [s.strip() for s in queries.split(',')]
            queries = [StockQuery(symbol=symbol) for symbol in symbol_list]
        
        # Call method with conditional parameters
        if default_filtering is not None:
            result = client.security_stocks_by_symbol(
                queries=queries,
                default_filtering=default_filtering
            )
        else:
            result = client.security_stocks_by_symbol(queries=queries)
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No stock information found",
                "queries": str(queries),
                "default_filtering": default_filtering
            })
        
        return to_json({"stocks": data})
    
    except Exception as e:
        return to_json({
            "error": "Stock lookup failed",
            "exception": str(e),
            "queries": str(queries)
        })


# ============================================================================
# TOOL 15: Get Contract IDs by Symbol (Unambiguous Conid Resolution)
# ============================================================================

@server.tool()
async def stock_conid_by_symbol(
    queries: StockQueries,
    default_filtering: Optional[bool] = None,
    return_type: str = "dict"
) -> str:
    """
    Get unambiguous contract IDs (conids) for given stock symbols with filtering.
    
    Returns contract IDs for stock queries, ensuring only one conid per query.
    This is the recommended method for conid resolution when you need precise
    mapping from symbols to contract IDs.
    
    Args:
        queries: StockQueries object or list of StockQuery objects.
                 Can also be a comma-separated string of symbols for simple usage.
                 Example strings: "AAPL", "AAPL,MSFT,GOOGL"
                 
                 **For LLM Clients:**
                 - **Simple usage:** Use comma-separated string: "AAPL,MSFT,GOOGL"
                 - **Advanced filtering:** Use StockQuery objects for precise control
                 
                 **StockQuery Structure:**
                 ```python
                 {
                     "symbol": "AAPL",                    # Required: Stock symbol
                     "name_match": "Apple",              # Optional: Partial name match
                     "instrument_conditions": {          # Optional: Exact instrument matches
                         "some_instrument_field": "value"
                     },
                     "contract_conditions": {            # Optional: Exact contract matches
                         "isUS": True,                   # Filter for US contracts
                         "exchange": "NASDAQ"            # Filter by exchange
                     }
                 }
                 ```
                 
        default_filtering: Whether to apply default US contract filtering {isUS: True}.
                          Defaults to None (uses global default).
                          Set to True to filter for US contracts only.
                          Set to False to disable default filtering.
        return_type: Return format - "dict" for {symbol: conid} mapping or 
                    "list" for list of conids. Default: "dict"
    
    Returns:
        JSON with conid mapping or list, or error dict.
    
    Examples:
        # Simple string usage (recommended for LLM clients)
        stock_conid_by_symbol("AAPL")
        stock_conid_by_symbol("AAPL,MSFT,GOOGL")
        stock_conid_by_symbol("AAPL,MSFT,GOOGL", return_type="list")
        
        # Advanced StockQuery usage
        stock_conid_by_symbol([
            {"symbol": "AAPL", "contract_conditions": {"isUS": True}},
            {"symbol": "MSFT", "name_match": "Microsoft"}
        ])
        
        # With default filtering
        stock_conid_by_symbol("AAPL,MSFT", default_filtering=True)
        
    Common Contract Conditions for filtering:
        - "isUS": True/False - US-listed contracts
        - "exchange": "NASDAQ"/"NYSE" - Specific exchange
        - "currency": "USD" - Trading currency
        - "assetClass": "STK" - Asset class
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        # Handle simple string input (comma-separated symbols)
        if isinstance(queries, str):
            # Convert comma-separated string to list of StockQuery objects
            from ibind.client.ibkr_utils import StockQuery
            symbol_list = [s.strip() for s in queries.split(',')]
            queries = [StockQuery(symbol=symbol) for symbol in symbol_list]
        
        # Call method with conditional parameters
        if default_filtering is not None:
            result = client.stock_conid_by_symbol(
                queries=queries,
                default_filtering=default_filtering,
                return_type=return_type
            )
        else:
            result = client.stock_conid_by_symbol(
                queries=queries,
                return_type=return_type
            )
        
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No conids found for the given symbols",
                "queries": str(queries),
                "default_filtering": default_filtering
            })
        
        return to_json({"conids": data, "return_type": return_type})
    
    except Exception as e:
        return to_json({
            "error": "Conid resolution failed",
            "exception": str(e),
            "queries": str(queries)
        })


# ============================================================================
# TOOL 16: Get Brokerage Accounts (Account Initialization)
# ============================================================================

@server.tool()
async def receive_brokerage_accounts() -> str:
    """
    Get list of brokerage accounts available for trading.
    
    Returns a list of accounts the user has trading access to, their respective
    aliases, and the currently selected account. This endpoint must be called
    before modifying an order or querying open orders.
    
    This is a prerequisite for many IBKR operations and should be called
    early in any workflow that involves account-specific operations.
    
    Returns:
        JSON with account list, aliases, and current selection or error dict.
    
    Examples:
        receive_brokerage_accounts()
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.receive_brokerage_accounts()
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No brokerage accounts found",
                "suggestion": "Check if IBKR credentials are valid and account is active"
            })
        
        return to_json({"accounts": data})
    
    except Exception as e:
        return to_json({
            "error": "Brokerage accounts retrieval failed",
            "exception": str(e),
            "suggestion": "This is often the first call needed to initialize account context"
        })


# ============================================================================
# TOOL 17: Search Dynamic Accounts
# ============================================================================

@server.tool()
async def search_dynamic_account(search_pattern: str) -> str:
    """
    Search for broker accounts configured with DYNACCT (Dynamic Account) property.
    
    Searches for broker accounts using a specified pattern. This is used for
    multi-account/tiered account structures (Financial Advisor, IBroker accounts).
    
    Note: Customers without DYNACCT property will receive a 503 error.
    
    Args:
        search_pattern: Pattern used to describe credentials.
                       Valid Format: "DU" to query all paper accounts.
    
    Returns:
        JSON with matching dynamic accounts or error dict.
    
    Examples:
        search_dynamic_account("DU")  # Query all paper accounts
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.search_dynamic_account(search_pattern)
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No dynamic accounts found",
                "search_pattern": search_pattern,
                "suggestion": "Check if you have DYNACCT property enabled on your account"
            })
        
        return to_json({"dynamic_accounts": data, "search_pattern": search_pattern})
    
    except Exception as e:
        return to_json({
            "error": "Dynamic account search failed",
            "exception": str(e),
            "search_pattern": search_pattern,
            "note": "Customers without DYNACCT property receive 503 error"
        })


# ============================================================================
# TOOL 18: Get Trading Schedule by Symbol and Exchange
# ============================================================================

@server.tool()
async def trading_schedule(
    asset_class: str,
    symbol: str,
    exchange: Optional[str] = None,
    exchange_filter: Optional[str] = None
) -> str:
    """
    Get trading schedule (hours) for a contract.
    
    Returns the trading schedule up to one month for the requested contract.
    
    Args:
        asset_class: Security type ("STK", "OPT", "FUT", "CFD", "WAR", "SWP", "FND", "BND")
        symbol: Contract symbol (e.g., "AAPL", "ES")
        exchange: Primary exchange of the contract (optional)
        exchange_filter: All exchanges to retrieve data from (optional)
    
    Returns:
        JSON with trading schedule information or error dict.
    
    Examples:
        trading_schedule("STK", "AAPL")
        trading_schedule("FUT", "ES", exchange="CME")
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        kwargs = {
            "asset_class": asset_class,
            "symbol": symbol
        }
        if exchange:
            kwargs["exchange"] = exchange
        if exchange_filter:
            kwargs["exchange_filter"] = exchange_filter
        
        result = client.trading_schedule_by_symbol(**kwargs)  # type: ignore
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No trading schedule found",
                "asset_class": asset_class,
                "symbol": symbol
            })
        
        return to_json({"schedule": data})
    
    except Exception as e:
        return to_json({
            "error": "Trading schedule lookup failed",
            "exception": str(e),
            "symbol": symbol
        })


# ============================================================================
# MARKETDATA TOOLS (10) - Live, Historical, and Regulatory Data
# ============================================================================

@server.tool()
async def live_marketdata_snapshot(
    conid: str,
    fields: Optional[str] = None
) -> str:
    """
    Get live market data snapshot for a contract.
    
    Returns current market data including bid, ask, last price, bid/ask size, etc.
    Per IBKR documentation, the first request requires a preflight. This method
    handles retries automatically until valid data (Last Price) is received.
    
    Args:
        conid: Contract ID (e.g., "265598" for AAPL)
        fields: Comma-separated field IDs to retrieve. Common fields:
                31=Last Price, 66=Bid Size, 68=Ask Size, 69=Bid, 70=Ask,
                84=Mark Price, 85=Bid/Ask Change, 86=Mark Change
                If None, returns all available fields.
    
    Returns:
        JSON with current market data snapshot or error dict.
    
    Examples:
        live_marketdata_snapshot("265598")
        live_marketdata_snapshot("265598", fields="69,70,31")  # Bid, Ask, Last Price
    """
    import time
    
    max_attempts = 10
    
    # Prepare field list
    if fields is not None:
        field_list = [str(f.strip()) for f in fields.split(',')]
    else:
        field_list = ['31', '69', '70']  # Default: Last Price, Bid, Ask
    
    # Retry loop with validation
    for attempt in range(max_attempts):
        try:
            data = fetch_raw_market_data(conid, field_list)
            if data:
                return to_json({"snapshot": data})
            
            # Retry with delay (but not on last attempt)
            if attempt < max_attempts - 1:
                time.sleep(1)
                continue
            
            # All attempts exhausted
            return to_json({
                "error": "No market data available after retries",
                "conid": conid,
                "attempts": max_attempts
            })
        
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(1)
                continue
            
            return to_json({
                "error": "Live market data snapshot failed",
                "exception": str(e),
                "conid": conid,
                "attempts": max_attempts
            })
    
    return to_json({
        "error": "Live market data snapshot failed after maximum retries",
        "conid": conid,
        "max_attempts": max_attempts
    })


@server.tool()
async def live_marketdata_snapshot_by_queries(
    queries: StockQueries,
    fields: Optional[str] = None
) -> str:
    """
    Get live market data snapshot for a contract by queries.
    
    Returns current market data for the given symbol including bid, ask, last price, etc.
    Per IBKR documentation, the first request requires a preflight. This method
    handles retries automatically until valid data (field 31) is received.
    
    Args:
        queries (List[StockQuery]): A list of StockQuery objects to specify filtering criteria for stocks.

        fields: Comma-separated field IDs to retrieve. Common fields:
                31=Last Price, 66=Bid Size, 68=Ask Size, 69=Bid, 70=Ask,
                84=Mark Price, 85=Bid/Ask Change, 86=Mark Change
    
    Returns:
        JSON with current market data snapshot or error dict.
    
    About StockQuery:
        class StockQuery:
            A class to encapsulate query parameters for filtering stock data.

            This class is used to define a set of criteria for filtering stocks, which includes the stock symbol,
            name matching pattern, and conditions for instruments and contracts.

            Attributes:
                symbol (str): The stock symbol to query.
                name_match (Optional[str], optional): A string pattern to match against stock names. Optional.
                instrument_conditions (Optional[dict], optional): Key-value pairs representing conditions to apply to
                    stock instruments. Each condition is matched exactly against the instrument's attributes.
                contract_conditions (Optional[dict], optional): Key-value pairs representing conditions to apply to
                    stock contracts. Each condition is matched exactly against the contract's attributes.

    Examples:
        live_marketdata_snapshot_by_symbol("AAPL")
        live_marketdata_snapshot_by_symbol("ES", fields="69,70,31")
    """
    import time
    
    max_attempts = 10
    
    # Prepare field list
    if fields is not None:
        field_list = [str(f.strip()) for f in fields.split(',')]
    else:
        field_list = ['31', '69', '70']  # Default: Last Price, Bid, Ask
    
    # Retry loop with validation
    for attempt in range(max_attempts):
        try:
            data = fetch_market_data_snapshot_by_queries(queries, field_list)
            if data:
                return to_json({"snapshot": data})
            
            # Retry with delay (but not on last attempt)
            if attempt < max_attempts - 1:
                time.sleep(1)
                continue
            
            # All attempts exhausted
            return to_json({
                "error": "No market data available (field 31 not received after retries)",
                "queries": queries,
                "attempts": max_attempts
            })
        
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(1)
                continue
            
            return to_json({
                "error": "Live market data snapshot by queries failed",
                "exception": str(e),
                "queries": str(queries),
                "attempts": max_attempts
            })
    
    return to_json({
        "error": "Live market data snapshot failed after maximum retries",
        "queries": str(queries),
        "max_attempts": max_attempts
    })


@server.tool()
async def marketdata_history_by_conid(
    conid: str,
    period: str,
    bar_size: str = "1d",
    outside_rth: bool = False
) -> str:
    """
    Get historical market data (OHLC) for a contract by conid.
    
    Returns historical OHLC (Open, High, Low, Close, Volume) data.
    
    Args:
        conid: Contract ID (e.g., "265598")
        period: Time period (e.g., "1mo", "3mo", "1y", "all")
                Format: "{number}{unit}" where unit is "d", "w", "mo", "y"
        bar_size: Bar size/resolution (default: "1d")
                  Options: "1min", "5min", "15min", "30min", "1h", "1d", "1w", "1mo"
        outside_rth: Include outside regular trading hours (default: False)
    
    Returns:
        JSON with OHLC bars, volume, and timestamp information or error dict.
    
    Examples:
        marketdata_history_by_conid("265598", "1y")
        marketdata_history_by_conid("265598", "3mo", "1h", outside_rth=True)
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.marketdata_history_by_conid(
            conid=conid,
            bar=bar_size,
            period=period,
            outside_rth=outside_rth
        )
        
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No historical data available",
                "conid": conid,
                "period": period
            })
        
        return to_json({"history": data, "bars": len(data) if isinstance(data, (list, dict)) else "unknown"})  # type: ignore[arg-type]
    
    except Exception as e:
        return to_json({
            "error": "Historical market data retrieval failed",
            "exception": str(e),
            "conid": conid
        })


@server.tool()
async def marketdata_history_by_symbol(
    symbol: str,
    period: str,
    bar_size: str = "1d",
    outside_rth: bool = False
) -> str:
    """
    Get historical market data (OHLC) for a contract by symbol.
    
    Returns historical OHLC (Open, High, Low, Close, Volume) data.
    
    Args:
        symbol: Ticker symbol (e.g., "AAPL", "ES")
        period: Time period (e.g., "1mo", "3mo", "1y", "all")
                Format: "{number}{unit}" where unit is "d", "w", "mo", "y"
        bar_size: Bar size/resolution (default: "1d")
                  Options: "1min", "5min", "15min", "30min", "1h", "1d", "1w", "1mo"
        outside_rth: Include outside regular trading hours (default: False)
    
    Returns:
        JSON with OHLC bars, volume, and timestamp information or error dict.
    
    Examples:
        marketdata_history_by_symbol("AAPL", "1y")
        marketdata_history_by_symbol("ES", "3mo", "1h", outside_rth=True)
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.marketdata_history_by_symbol(
            symbol,
            period=period,
            bar=bar_size,
            outside_rth=outside_rth
        )
        
        data = result  # This method returns dict directly, not Result
        
        if not data:
            return to_json({
                "error": "No historical data available",
                "symbol": symbol,
                "period": period
            })
        
        return to_json({"history": data, "bars": len(data) if isinstance(data, (list, dict)) else "unknown"})  # type: ignore[arg-type]
    
    except Exception as e:
        return to_json({
            "error": "Historical market data retrieval failed",
            "exception": str(e),
            "symbol": symbol
        })


@server.tool()
async def marketdata_history_by_conids(
    conids: str,
    period: str,
    bar_size: str = "1d",
    outside_rth: bool = False
) -> str:
    """
    Get historical market data for multiple contracts by conids (batch).
    
    Returns historical OHLC data for all specified contracts.
    Can process multiple conids in parallel.
    
    Args:
        conids: Comma-separated contract IDs (e.g., "265598,9408,12345")
        period: Time period (e.g., "1mo", "3mo", "1y", "all")
        bar_size: Bar size/resolution (default: "1d")
        outside_rth: Include outside regular trading hours (default: False)
    
    Returns:
        JSON with historical data for each conid or error dict.
    
    Examples:
        marketdata_history_by_conids("265598,9408", "1y")
        marketdata_history_by_conids("265598,9408,12345", "1mo", "1h")
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        conid_list = conids.split(',')
        result = client.marketdata_history_by_conids(  # type: ignore[attr-defined]
            conids=conid_list,
            period=period,
            bar=bar_size,
            outside_rth=outside_rth,
            run_in_parallel=True
        )
        
        data = result  # type: ignore[assignment] - This method returns dict directly, not Result
        
        if not data:
            return to_json({
                "error": "No historical data available",
                "conids": conids,
                "period": period
            })
        
        return to_json({"histories": data, "conid_count": len(conid_list)})
    
    except Exception as e:
        return to_json({
            "error": "Batch historical market data retrieval failed",
            "exception": str(e),
            "conids": conids
        })


@server.tool()
async def marketdata_history_by_symbols(
    symbols: str,
    period: str,
    bar_size: str = "1d",
    outside_rth: bool = False
) -> str:
    """
    Get historical market data for multiple contracts by symbols (batch).
    
    Returns historical OHLC data for all specified symbols.
    Can process multiple symbols in parallel.
    
    Args:
        symbols: Comma-separated ticker symbols (e.g., "AAPL,MSFT,GOOGL")
        period: Time period (e.g., "1mo", "3mo", "1y", "all")
        bar_size: Bar size/resolution (default: "1d")
        outside_rth: Include outside regular trading hours (default: False)
    
    Returns:
        JSON with historical data for each symbol or error dict.
    
    Examples:
        marketdata_history_by_symbols("AAPL,MSFT", "1y")
        marketdata_history_by_symbols("ES,NQ,GC", "1mo", "1h")
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        symbol_list = symbols.split(',')
        result = client.marketdata_history_by_symbols(  # type: ignore[attr-defined]
            symbol_list,  # type: ignore[arg-type]
            period=period,
            bar=bar_size,
            outside_rth=outside_rth,
            run_in_parallel=True
        )
        
        data = result  # type: ignore[assignment] - This method returns dict directly, not Result
        
        if not data:
            return to_json({
                "error": "No historical data available",
                "symbols": symbols,
                "period": period
            })
        
        return to_json({"histories": data, "symbol_count": len(symbol_list)})
    
    except Exception as e:
        return to_json({
            "error": "Batch historical market data retrieval failed",
            "exception": str(e),
            "symbols": symbols
        })


@server.tool()
async def historical_marketdata_beta(
    conid: str,
    start_time: str,
    end_time: str,
    bar_size: str = "1min"
) -> str:
    """
    Get advanced historical market data with custom time range (beta).
    
    Returns historical OHLC data for a custom time range with flexible bar sizing.
    Useful for intraday analysis and detailed price action studies.
    
    Args:
        conid: Contract ID (e.g., "265598")
        start_time: Start timestamp (format: ISO 8601 or Unix timestamp)
                   e.g., "2024-01-01T09:30:00Z" or "1704096600"
        end_time: End timestamp (format: ISO 8601 or Unix timestamp)
                 e.g., "2024-12-31T16:00:00Z" or "1735689600"
        bar_size: Bar size/resolution (default: "1min")
                  Options: "1min", "5min", "15min", "30min", "1h", "2h", "3h", "4h", "1d"
    
    Returns:
        JSON with detailed OHLC bars for the specified time range or error dict.
    
    Examples:
        historical_marketdata_beta("265598", "2024-01-01T00:00:00Z", "2024-12-31T23:59:59Z")
        historical_marketdata_beta("9408", "1704096600", "1735689600", "1h")
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.historical_marketdata_beta(
            conid=conid,
            period='1y',
            bar=bar_size,
            start_time=start_time  # type: ignore[arg-type]
        )
        
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No historical data available for time range",
                "conid": conid,
                "start_time": start_time,
                "end_time": end_time
            })
        
        return to_json({"history": data, "bars": len(data) if isinstance(data, (list, dict)) else "unknown"})  # type: ignore[arg-type]
    
    except Exception as e:
        return to_json({
            "error": "Advanced historical market data retrieval failed",
            "exception": str(e),
            "conid": conid
        })


@server.tool()
async def regulatory_snapshot(conid: str) -> str:
    """
    Get regulatory market data snapshot for a contract.
    
    Returns regulatory-compliant market data snapshot.
    
    ⚠️  IMPORTANT: This endpoint charges $0.01 USD per call on both paper and live accounts.
    
    Args:
        conid: Contract ID (e.g., "265598")
    
    Returns:
        JSON with regulatory market data snapshot or error dict.
    
    Examples:
        regulatory_snapshot("265598")
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.regulatory_snapshot(conid)
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No regulatory snapshot available",
                "conid": conid,
                "warning": "This endpoint costs $0.01 USD per call"
            })
        
        return to_json({
            "snapshot": data,
            "cost_warning": "This call cost $0.01 USD"
        })
    
    except Exception as e:
        return to_json({
            "error": "Regulatory snapshot failed",
            "exception": str(e),
            "conid": conid,
            "cost_warning": "This call may have cost $0.01 USD"
        })


@server.tool()
async def marketdata_unsubscribe(conid: str) -> str:
    """
    This is only a stub for future implementation of streaming real-time market data.
    Unsubscribe from market data for a specific contract.
    
    Cancels active market data subscription for the given contract.
    
    Args:
        conid: Contract ID to unsubscribe from (e.g., "265598")
    
    Returns:
        JSON with subscription status or error dict.
    
    Examples:
        marketdata_unsubscribe("265598")
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.marketdata_unsubscribe(conid)
        
        return to_json({
            "status": "unsubscribed",
            "conid": conid,
            "result": result
        })
    
    except Exception as e:
        return to_json({
            "error": "Unsubscribe failed",
            "exception": str(e),
            "conid": conid
        })


@server.tool()
async def marketdata_unsubscribe_all() -> str:
    """
    This is only a stub for future implementation of streaming real-time market data.

    Unsubscribe from all market data subscriptions.
    
    Cancels all active market data subscriptions.
    
    Returns:
        JSON with subscription status or error dict.
    
    Examples:
        marketdata_unsubscribe_all()
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.marketdata_unsubscribe_all()
        
        return to_json({
            "status": "all subscriptions cancelled",
            "result": result
        })
    
    except Exception as e:
        return to_json({
            "error": "Unsubscribe all failed",
            "exception": str(e)
        })


# ============================================================================
# UTILITY TOOL: List All Available Tools
# ============================================================================

@server.tool()
async def list_tools() -> str:
    """
    List all available IBKR contract search tools and typical usage workflows.
    
    Returns:
        Markdown formatted documentation of all tools, parameters, and examples.
    """
    return """# IBKR Complete MCP Tools - Contract & Market Data Reference

## Available Tools (29 total)

### Search & Lookup Tools (9)

**1. search_contract(symbol, search_by_name=None, security_type=None)**
Search for contracts by ticker symbol, company name, or bond issuer.
- Parameters: symbol (str), search_by_name (bool), security_type (str)
- Returns: List of matching contracts
- Examples: search_contract("AAPL"), search_contract("Apple", search_by_name=True)

**2. security_definition(conids)**
Get security definitions for given contract IDs.
- Parameters: conids (comma-separated or single)
- Returns: Security definitions for each conid
- Examples: security_definition("265598"), security_definition("265598,9408,12345")

**3. all_exchange_contracts(exchange)**
Get all tradable contracts on a specific exchange (stocks only).
- Parameters: exchange (str)
- Returns: List of all contract IDs on exchange
- Examples: all_exchange_contracts("NASDAQ"), all_exchange_contracts("NYSE")

**4. contract_information(conid)**
Get full contract details for a specific contract ID.
- Parameters: conid (str)
- Returns: Complete contract information
- Examples: contract_information("265598"), contract_information("9408")

**5. currency_pairs(currency)**
Get available currency pairs for a target currency.
- Parameters: currency (str, e.g., "USD")
- Returns: Available currency pairs
- Examples: currency_pairs("USD"), currency_pairs("EUR")

**6. security_futures(symbols)**
Get non-expired future contracts for given symbol(s).
- Parameters: symbols (comma-separated or single)
- Returns: Available futures contracts
- Examples: security_futures("ES"), security_futures("ES,NQ,GC")

**7. security_stocks(queries, default_filtering=None)**
Get stock information for given symbols with advanced filtering.
- Parameters: queries (StockQueries or comma-separated string), default_filtering (bool)
- Returns: Stock information with precise filtering
- Examples: security_stocks("AAPL"), security_stocks("AAPL,MSFT,GOOGL")

**8. stock_conid_by_symbol(queries, default_filtering=None, return_type="dict")**
Get unambiguous contract IDs (conids) for stock symbols. **CRITICAL FOR CONID RESOLUTION**
- Parameters: queries (StockQueries or comma-separated string), default_filtering (bool), return_type ("dict" or "list")
- Returns: {symbol: conid} mapping or list of conids
- Examples: stock_conid_by_symbol("AAPL"), stock_conid_by_symbol("AAPL,MSFT,GOOGL", return_type="list")

**9. receive_brokerage_accounts()**
Get list of brokerage accounts available for trading. **PREREQUISITE FOR ACCOUNT OPERATIONS**
- Parameters: None
- Returns: Account list with aliases and current selection
- Examples: receive_brokerage_accounts()

---

### Contract Details Tools (3)

**8. get_contract_details(conid, security_type, expiration_month, exchange=None, strike=None, option_right=None, bond_issuer_id=None)**
Get detailed specifications for derivative contracts.
- Parameters: conid, security_type (OPT/FUT/WAR/CASH/CFD/BOND), expiration_month, strike*, option_right*, bond_issuer_id*
- Returns: Full contract specifications
- Examples: 
  - get_contract_details("265598", "OPT", "JAN25", strike="150", option_right="C")
  - get_contract_details("209", "FUT", "JAN25")

**9. get_option_strikes(conid, security_type, expiration_month, exchange=None)**
Get list of available strike prices for options or warrants.
- Parameters: conid, security_type (OPT/WAR), expiration_month, exchange (optional)
- Returns: List of available strikes
- Examples: get_option_strikes("265598", "OPT", "JAN25")

**10. trading_schedule(asset_class, symbol, exchange=None, exchange_filter=None)**
Get trading schedule (hours) for a contract.
- Parameters: asset_class (STK/OPT/FUT/etc), symbol, exchange, exchange_filter
- Returns: Trading schedule information
- Examples: trading_schedule("STK", "AAPL"), trading_schedule("FUT", "ES")

---

### Trading Rules & Info Tools (3)

**11. get_trading_rules(conid, exchange=None, is_buy=None, modify_order=None, order_id=None)**
Get trading constraints and rules for a contract.
- Parameters: conid, exchange, is_buy (True/False), modify_order, order_id (required if modify_order=True)
- Returns: Position limits, minimums, constraints
- Examples:
  - get_trading_rules("265598")
  - get_trading_rules("265598", modify_order=True, order_id=12345)

**12. contract_info_and_rules(conid, is_buy=None)**
Get both contract info and trading rules in one request.
- Parameters: conid, is_buy (True/False)
- Returns: Combined contract info and rules
- Examples: contract_info_and_rules("265598"), contract_info_and_rules("265598", is_buy=True)

**13. currency_exchange_rate(source, target)**
Get the exchange rate between two currencies.
- Parameters: source (str), target (str)
- Returns: Exchange rate information
- Examples: currency_exchange_rate("USD", "EUR"), currency_exchange_rate("EUR", "GBP")

---

### Bond & Algorithm Tools (2)

**14. get_bond_filters(bond_issuer_id)**
Get available filters for a bond issuer.
- Parameters: bond_issuer_id (e.g., "e123456")
- Returns: Available bond filters (maturity, rating, yield, etc.)
- Examples: get_bond_filters("e123456")

**15. algo_params(conid, algos=None, add_description=None, add_params=None)**
Get supported IB Algorithm parameters for a contract.
- Parameters: conid, algos (comma-separated), add_description (bool), add_params (bool)
- Returns: Available algorithms and their parameters
- Examples: algo_params("265598"), algo_params("265598", algos="AD,TWAP", add_description=True)

---

### Live Market Data Tools (2)

**16. live_marketdata_snapshot(conid, fields=None)**
Get live market data snapshot for a contract.
- Parameters: conid (str), fields (comma-separated field IDs)
- Returns: Current bid, ask, last price, and other market data
- Examples: 
  - live_marketdata_snapshot("265598")
  - live_marketdata_snapshot("265598", fields="69,70,31")  # Bid, Ask, Last Price
- Common Field IDs: 31=Last Price, 66=Bid Size, 68=Ask Size, 69=Bid, 70=Ask, 84=Mark, 85=Bid/Ask Change

**17. live_marketdata_snapshot_by_symbol(symbol, fields=None)**
Get live market data snapshot for a contract by symbol.
- Parameters: symbol (str), fields (comma-separated field IDs)
- Returns: Current market data snapshot
- Examples: live_marketdata_snapshot_by_symbol("AAPL"), live_marketdata_snapshot_by_symbol("ES", fields="69,70,31")

---

### Historical Market Data Tools (5)

**18. marketdata_history_by_conid(conid, period, bar_size="1d", outside_rth=False)**
Get historical OHLC data for a contract by conid.
- Parameters: conid (str), period (e.g., "1mo", "3mo", "1y", "all"), bar_size (default: "1d"), outside_rth (bool)
- Returns: OHLC bars with volume and timestamps
- Examples: marketdata_history_by_conid("265598", "1y"), marketdata_history_by_conid("265598", "3mo", "1h")

**19. marketdata_history_by_symbol(symbol, period, bar_size="1d", outside_rth=False)**
Get historical OHLC data for a contract by symbol.
- Parameters: symbol (str), period (e.g., "1mo", "3mo", "1y", "all"), bar_size (default: "1d"), outside_rth (bool)
- Returns: OHLC bars with volume and timestamps
- Examples: marketdata_history_by_symbol("AAPL", "1y"), marketdata_history_by_symbol("ES", "3mo", "1h")

**20. marketdata_history_by_conids(conids, period, bar_size="1d", outside_rth=False)**
Get historical OHLC data for multiple contracts (batch, parallel processing).
- Parameters: conids (comma-separated), period (e.g., "1mo", "3mo", "1y"), bar_size (default: "1d"), outside_rth (bool)
- Returns: OHLC data for each conid
- Examples: marketdata_history_by_conids("265598,9408", "1y"), marketdata_history_by_conids("265598,9408,12345", "1mo", "1h")

**21. marketdata_history_by_symbols(symbols, period, bar_size="1d", outside_rth=False)**
Get historical OHLC data for multiple contracts by symbols (batch, parallel processing).
- Parameters: symbols (comma-separated), period (e.g., "1mo", "3mo", "1y"), bar_size (default: "1d"), outside_rth (bool)
- Returns: OHLC data for each symbol
- Examples: marketdata_history_by_symbols("AAPL,MSFT", "1y"), marketdata_history_by_symbols("ES,NQ,GC", "1mo", "1h")

**22. historical_marketdata_beta(conid, start_time, end_time, bar_size="1min")**
Get advanced historical OHLC data with custom time range (beta).
- Parameters: conid (str), start_time (ISO 8601 or Unix timestamp), end_time (ISO 8601 or Unix timestamp), bar_size (default: "1min")
- Returns: Detailed OHLC bars for the specified time range
- Examples: 
  - historical_marketdata_beta("265598", "2024-01-01T00:00:00Z", "2024-12-31T23:59:59Z")
  - historical_marketdata_beta("9408", "1704096600", "1735689600", "1h")

---

### Regulatory & Subscriptions Tools (3)

**23. regulatory_snapshot(conid)**
Get regulatory market data snapshot for a contract.
- Parameters: conid (str)
- Returns: Regulatory-compliant market data snapshot
- ⚠️  WARNING: Costs $0.01 USD per call (applies to paper and live accounts)
- Examples: regulatory_snapshot("265598")

**24. marketdata_unsubscribe(conid)**
Unsubscribe from market data for a specific contract.
- Parameters: conid (str)
- Returns: Subscription cancellation status
- Examples: marketdata_unsubscribe("265598")

**25. marketdata_unsubscribe_all()**
Unsubscribe from all market data subscriptions.
- Parameters: None
- Returns: All subscriptions cancelled status
- Examples: marketdata_unsubscribe_all()

---

### Utility

**26. list_tools()**
Show this documentation with all tools and parameters.

---

## Typical Workflows

### Workflow 1: Find Apple Stock Call Options
```
1. search_contract("AAPL")
   → Extract conid (e.g., "265598")

2. get_option_strikes("265598", "OPT", "JAN25")
   → See available strikes: [140, 145, 150, ...]

3. get_contract_details("265598", "OPT", "JAN25", strike="150", option_right="C")
   → Full specs: multiplier=100, tick_size=0.01, ...

4. get_trading_rules("265598")
   → Position limits: 500000, min_size: 1, ...
```

### Workflow 2: Research a Futures Contract
```
1. security_futures("ES")
   → Find E-mini S&P 500 futures

2. get_contract_details(conid, "FUT", "JAN25")
   → Get specs: multiplier=50, tick_size=0.25, ...

3. get_trading_rules(conid, is_buy=True)
   → Check position limits
```

### Workflow 3: Analyze Market Data
```
1. live_marketdata_snapshot("265598", fields="69,70,31")
   → Get current bid, ask, last price

2. marketdata_history_by_conid("265598", "1mo", "1h")
   → Get 1-month hourly OHLC data

3. historical_marketdata_beta("265598", "2024-12-01T09:30:00Z", "2024-12-31T16:00:00Z", "5min")
   → Get detailed 5-minute intraday data for custom period
```

### Workflow 4: Batch Market Data Retrieval
```
1. marketdata_history_by_symbols("AAPL,MSFT,GOOGL", "1y", "1d")
   → Get 1-year daily data for 3 stocks (parallel processing)

2. live_marketdata_snapshot_by_symbol("AAPL", fields="69,70,84")
   → Get bid, ask, and mark price
```

### Workflow 5: Explore Bonds
```
1. search_contract("BOND", security_type="BOND")
   → Browse bond issuers

2. get_bond_filters("e1359061")
   → See maturity, rating, yield options
```

### Workflow 6: Currency Research
```
1. currency_pairs("USD")
   → See available pairs

2. currency_exchange_rate("USD", "EUR")
   → Get current exchange rate
```

---

## Notes

- **Prerequisites:** All tools require IBKR account authentication via .env credentials
- **Conid Required:** Most tools require conid from search_contract() output
- **Month Format:** Expiration months use "{3-char month}{2-char year}" (e.g., "JAN25")
- **Asterisk (*):** Indicates required parameters for specific security types
- **Comma-separated:** Multiple values should be comma-separated (e.g., "ES,NQ,GC")
- **Bar Sizes:** "1min", "5min", "15min", "30min", "1h", "2h", "3h", "4h", "1d", "1w", "1mo"
- **Period Format:** "{number}{unit}" where unit is "d" (day), "w" (week), "mo" (month), "y" (year)
- **Field IDs:** 31=Last, 66=BidSize, 68=AskSize, 69=Bid, 70=Ask, 84=Mark, 85=BidAskChange, 86=MarkChange
- **Batch Operations:** history_by_conids/symbols use parallel processing automatically
- **Cost Warning:** regulatory_snapshot() costs $0.01 USD per call on both paper and live accounts

---

Generated by IBKR Complete MCP Server - Contract & Market Data Implementation
"""


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("IBKR Complete MCP Server - Contract & Market Data Implementation")
    print("="*80)
    print("\n✅ 29 MCP tools loaded:")
    print("   Search & Lookup (9):")
    print("     1. search_contract() - Search by symbol/name/issuer")
    print("     2. security_definition() - Security definitions by conids")
    print("     3. all_exchange_contracts() - All contracts on exchange")
    print("     4. contract_information() - Full contract details")
    print("     5. currency_pairs() - Available currency pairs")
    print("     6. security_futures() - Futures contracts by symbol")
    print("     7. security_stocks() - Stock information by queries")
    print("     8. stock_conid_by_symbol() - Unambiguous conid resolution")
    print("     9. receive_brokerage_accounts() - Account initialization")
    print("\n   Contract Details (3):")
    print("    10. get_contract_details() - Derivative specifications")
    print("    11. get_option_strikes() - Available option/warrant strikes")
    print("    12. trading_schedule() - Trading hours by symbol/exchange")
    print("\n   Trading Rules & Info (3):")
    print("    13. get_trading_rules() - Trading constraints for a contract")
    print("    14. contract_info_and_rules() - Combined contract info + rules")
    print("    15. currency_exchange_rate() - Exchange rates between currencies")
    print("\n   Bond & Algorithm Tools (2):")
    print("    16. get_bond_filters() - Bond issuer filtering options")
    print("    17. algo_params() - IB Algo parameters for a contract")
    print("\n   Live Market Data (2):")
    print("    18. live_marketdata_snapshot() - Current bid/ask/last price by conid")
    print("    19. live_marketdata_snapshot_by_symbol() - Current market data by symbol")
    print("\n   Historical Market Data (5):")
    print("    20. marketdata_history_by_conid() - OHLC historical data by conid")
    print("    21. marketdata_history_by_symbol() - OHLC historical data by symbol")
    print("    22. marketdata_history_by_conids() - Batch OHLC by conids (parallel)")
    print("    23. marketdata_history_by_symbols() - Batch OHLC by symbols (parallel)")
    print("    24. historical_marketdata_beta() - Advanced OHLC with custom time range")
    print("\n   Regulatory & Subscriptions (3):")
    print("    25. regulatory_snapshot() - Regulatory market data (costs $0.01 USD)")
    print("    26. marketdata_unsubscribe() - Cancel market data subscription for a contract")
    print("    27. marketdata_unsubscribe_all() - Cancel all market data subscriptions")
    print("\n   Account Management (1):")
    print("    28. search_dynamic_account() - Search for dynamic accounts")
    print("\n   Utility (1):")
    print("    29. list_tools() - Show documentation with all tools")
    
    client = get_client()
    if client:
        print("\n✅ IBKR Client: Connected")
    else:
        print("\n⚠️  IBKR Client: Not initialized (will connect on first tool call)")
    
    print("\n📡 Server running on stdio transport...")
    print("="*80 + "\n")
    
    server.run()
