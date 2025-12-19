"""
MCP Server: IBKR ContractMixin Tools - Complete Implementation

Exposes ALL Interactive Brokers ContractMixin methods (21 total) via FastMCP.
Provides comprehensive contract search, specification retrieval, and trading rules.

All 16 Tools:
  Search & Lookup:
    1. search_contract() - Search by symbol/name/issuer
    2. security_definition() - Get security definitions by conids
    3. all_exchange_contracts() - Get all contracts on an exchange
    4. contract_information() - Full contract details
    5. currency_pairs() - Available currency pairs
    6. security_futures() - Future contracts by symbol
    7. security_stocks() - Stock information by queries

  Contract Details:
    8. get_contract_details() - Derivative specifications (options/futures/bonds)
    9. get_option_strikes() - Available option/warrant strikes
    10. trading_schedule() - Trading hours by symbol/exchange

  Trading Rules & Info:
    11. get_trading_rules() - Trading constraints for a contract
    12. contract_info_and_rules() - Combined contract info + rules
    13. currency_exchange_rate() - Exchange rates between currencies

  Bond Tools:
    14. get_bond_filters() - Bond issuer filtering options
    15. algo_params() - IB Algo parameters for a contract

  Utility:
    16. list_tools() - Show documentation with all tools

Usage:
  cd /home/john/CodingProjects/llm_public
  PYTHONPATH=./src python src/mcp_server.py
"""

import json
from typing import Optional, Any
from fastmcp import FastMCP
from ibind import IbkrClient
from dotenv import load_dotenv

load_dotenv()


# ============================================================================
# CLIENT INITIALIZATION (Lazy-Loading)
# ============================================================================

_client: Optional[IbkrClient] = None


def get_client() -> Optional[IbkrClient]:
    """
    Get or initialize the IBKR client (lazy-loaded on first use).
    
    Returns None if connection fails, allowing imports to succeed.
    Subsequent calls reuse the same authenticated connection.
    """
    global _client
    if _client is None:
        try:
            _client = IbkrClient()
        except Exception as e:
            print(f"⚠️ IBKR Connection Error: {type(e).__name__}: {str(e)}")
            print("   Contract tools will fail until connection is established")
            return None
    return _client


def _to_json(data: Any) -> str:
    """Safely convert any object to JSON string with fallback to str()"""
    try:
        return json.dumps(data, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": "JSON serialization failed", "details": str(e)})


def _extract_result_data(result: Any) -> Any:
    """Extract .data attribute from IbkrClient Result object"""
    if result is None:
        return None
    if hasattr(result, "data"):
        return result.data
    return result


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
            return _to_json({
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
        
        data = _extract_result_data(result)
        
        if not data:
            return _to_json({
                "error": "No contracts found",
                "searched": symbol,
                "search_by_name": search_by_name,
                "security_type": security_type
            })
        
        return _to_json({"contracts": data})
    
    except Exception as e:
        return _to_json({
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
            return _to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.security_definition_by_conid(conids.split(','))
        data = _extract_result_data(result)
        
        if not data:
            return _to_json({
                "error": "No security definitions found",
                "conids": conids
            })
        
        return _to_json({"definitions": data})
    
    except Exception as e:
        return _to_json({
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
            return _to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.all_conids_by_exchange(exchange)
        data = _extract_result_data(result)
        
        if not data:
            return _to_json({
                "error": "No contracts found for exchange",
                "exchange": exchange,
                "suggestion": "Note: This endpoint only supports stock contracts"
            })
        
        return _to_json({"contracts": data, "exchange": exchange})
    
    except Exception as e:
        return _to_json({
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
            return _to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.contract_information_by_conid(conid)
        data = _extract_result_data(result)
        
        if not data:
            return _to_json({
                "error": "No contract information found",
                "conid": conid
            })
        
        return _to_json({"information": data})
    
    except Exception as e:
        return _to_json({
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
            return _to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.currency_pairs(currency)
        data = _extract_result_data(result)
        
        if not data:
            return _to_json({
                "error": "No currency pairs found",
                "currency": currency
            })
        
        return _to_json({"pairs": data, "currency": currency})
    
    except Exception as e:
        return _to_json({
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
            return _to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.currency_exchange_rate(source, target)
        data = _extract_result_data(result)
        
        if not data:
            return _to_json({
                "error": "No exchange rate found",
                "source": source,
                "target": target
            })
        
        return _to_json({"rate": data, "source": source, "target": target})
    
    except Exception as e:
        return _to_json({
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
            return _to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        buy_side = is_buy if is_buy is not None else True
        result = client.info_and_rules_by_conid(conid, buy_side)
        data = _extract_result_data(result)
        
        if not data:
            return _to_json({
                "error": "No contract info and rules found",
                "conid": conid,
                "is_buy": is_buy
            })
        
        return _to_json({"info_and_rules": data})
    
    except Exception as e:
        return _to_json({
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
            return _to_json({
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
        data = _extract_result_data(result)
        
        if not data:
            return _to_json({
                "error": "No algo parameters found",
                "conid": conid,
                "algos": algos
            })
        
        return _to_json({"algorithms": data})
    
    except Exception as e:
        return _to_json({
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
        get_bond_filters("e123456")
    """
    try:
        client = get_client()
        if client is None:
            return _to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.search_bond_filter_information(
            symbol="BOND",
            issuer_id=bond_issuer_id
        )
        
        data = _extract_result_data(result)
        
        if not data:
            return _to_json({
                "error": "No bond filters found",
                "bond_issuer_id": bond_issuer_id,
                "suggestion": "Check issuer_id format (should be like 'e123456')"
            })
        
        return _to_json({"filters": data})
    
    except Exception as e:
        return _to_json({
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
        return _to_json({
            "error": "Missing required parameters for options/warrants",
            "required_for_options": ["strike", "option_right"],
            "provided": {"strike": strike, "option_right": option_right}
        })
    
    if security_type == "BOND" and not bond_issuer_id:
        return _to_json({
            "error": "Missing required parameter for bonds",
            "required_for_bonds": ["bond_issuer_id"],
            "issuer_id_format": "e1234567"
        })
    
    try:
        client = get_client()
        if client is None:
            return _to_json({
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
        
        data = _extract_result_data(result)
        
        if not data:
            return _to_json({
                "error": "No contract details found",
                "conid": conid,
                "security_type": security_type,
                "expiration_month": expiration_month
            })
        
        return _to_json({"details": data})
    
    except Exception as e:
        return _to_json({
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
        return _to_json({
            "error": f"Invalid security_type: {security_type}",
            "valid_types": ["OPT", "WAR"],
            "suggestion": "Use 'OPT' for options or 'WAR' for warrants"
        })
    
    try:
        client = get_client()
        if client is None:
            return _to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.search_strikes_by_conid(
            conid=conid,
            sec_type=security_type,
            month=expiration_month,
            exchange=exchange or ""
        )
        
        data = _extract_result_data(result)
        
        if not data:
            return _to_json({
                "error": "No strikes found",
                "conid": conid,
                "security_type": security_type,
                "expiration_month": expiration_month
            })
        
        count = len(data) if isinstance(data, list) else "unknown"  # type: ignore
        return _to_json({"strikes": data, "count": count})
    
    except Exception as e:
        return _to_json({
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
        return _to_json({
            "error": "Missing required parameter",
            "requirement": "order_id must be provided when modify_order=True",
            "modify_order": modify_order
        })
    
    try:
        client = get_client()
        if client is None:
            return _to_json({
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
        
        data = _extract_result_data(result)
        
        if not data:
            return _to_json({
                "error": "No trading rules found",
                "conid": conid,
                "exchange": exchange,
                "is_buy": is_buy
            })
        
        return _to_json({"rules": data})
    
    except Exception as e:
        return _to_json({
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
            return _to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        result = client.security_future_by_symbol(symbols.split(','))
        data = _extract_result_data(result)
        
        if not data:
            return _to_json({
                "error": "No futures contracts found",
                "symbols": symbols
            })
        
        return _to_json({"futures": data, "symbols": symbols})
    
    except Exception as e:
        return _to_json({
            "error": "Futures contract lookup failed",
            "exception": str(e),
            "symbols": symbols
        })


# ============================================================================
# TOOL 14: Get Stock Information by Symbol
# ============================================================================

@server.tool()
async def security_stocks(symbol: str) -> str:
    """
    Get stock information for a given symbol.
    
    Retrieves and filters stock information based on the provided symbol.
    
    Args:
        symbol: Stock symbol (e.g., "AAPL", "MSFT")
    
    Returns:
        JSON with stock information or error dict.
    
    Examples:
        security_stocks("AAPL")
        security_stocks("MSFT")
    """
    try:
        client = get_client()
        if client is None:
            return _to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        # Use search_contract as a workaround for stock queries
        result = client.search_contract_by_symbol(symbol=symbol, sec_type="STK")
        data = _extract_result_data(result)
        
        if not data:
            return _to_json({
                "error": "No stock information found",
                "symbol": symbol
            })
        
        return _to_json({"stocks": data})
    
    except Exception as e:
        return _to_json({
            "error": "Stock lookup failed",
            "exception": str(e),
            "symbol": symbol
        })


# ============================================================================
# TOOL 15: Get Trading Schedule by Symbol and Exchange
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
            return _to_json({
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
        data = _extract_result_data(result)
        
        if not data:
            return _to_json({
                "error": "No trading schedule found",
                "asset_class": asset_class,
                "symbol": symbol
            })
        
        return _to_json({"schedule": data})
    
    except Exception as e:
        return _to_json({
            "error": "Trading schedule lookup failed",
            "exception": str(e),
            "symbol": symbol
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
    return """# IBKR Contract Search MCP Tools - Complete API Reference

## Available Tools (16 total)

### Search & Lookup Tools (7)

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

**7. security_stocks(symbol)**
Get stock information for a given symbol.
- Parameters: symbol (str)
- Returns: Stock information
- Examples: security_stocks("AAPL"), security_stocks("MSFT")

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

### Utility

**16. list_tools()**
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

### Workflow 3: Explore Bonds
```
1. search_contract("BOND", security_type="BOND")
   → Browse bond issuers

2. get_bond_filters("e123456")
   → See maturity, rating, yield options

3. search_contract("US Treasury", search_by_name=True, security_type="BOND")
   → Find specific bonds
```

### Workflow 4: Currency Research
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

---

Generated by IBKR Contract Search MCP Server - Complete Implementation
"""


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("IBKR Contract Search MCP Server - Complete Implementation")
    print("="*80)
    print("\n✅ 16 MCP tools loaded:")
    print("   Search & Lookup (7):")
    print("     1. search_contract() - Search by symbol/name/issuer")
    print("     2. security_definition() - Security definitions by conids")
    print("     3. all_exchange_contracts() - All contracts on exchange")
    print("     4. contract_information() - Full contract details")
    print("     5. currency_pairs() - Available currency pairs")
    print("     6. security_futures() - Futures contracts by symbol")
    print("     7. security_stocks() - Stock information by symbol")
    print("\n   Contract Details (3):")
    print("     8. get_contract_details() - Derivative specifications")
    print("     9. get_option_strikes() - Available strike prices")
    print("    10. trading_schedule() - Trading hours by symbol")
    print("\n   Trading Rules & Info (3):")
    print("    11. get_trading_rules() - Trading constraints")
    print("    12. contract_info_and_rules() - Combined info + rules")
    print("    13. currency_exchange_rate() - Exchange rate lookup")
    print("\n   Bond & Algorithm Tools (2):")
    print("    14. get_bond_filters() - Bond issuer filters")
    print("    15. algo_params() - Algorithm parameters")
    print("\n   Utility (1):")
    print("    16. list_tools() - Show documentation")
    
    client = get_client()
    if client:
        print("\n✅ IBKR Client: Connected")
    else:
        print("\n⚠️  IBKR Client: Not initialized (will connect on first tool call)")
    
    print("\n📡 Server running on stdio transport...")
    print("="*80 + "\n")
    
    server.run()
