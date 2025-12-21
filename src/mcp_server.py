"""
MCP Server: IBKR ContractMixin + MarketdataMixin Tools - Complete Implementation

Exposes ALL Interactive Brokers ContractMixin and MarketdataMixin methods via FastMCP.
Provides comprehensive contract search, market data retrieval, and trading information.

Usage:
  cd /home/john/CodingProjects/llm_public
  PYTHONPATH=./src python src/mcp_server.py
"""

from typing import Optional, Union, List
from fastmcp import FastMCP

from dotenv import load_dotenv
from ibind.client.ibkr_utils import StockQueries
from ibind.support.py_utils import OneOrMany

from pydantic import Json

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
    
    Upstream docs:
        https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#trsrv-conid-contract
    Upstream endpoint:
        GET /trsrv/secdef
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

    Upstream docs:
        https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#info-conid-contract

    Upstream endpoint:
        GET /iserver/contract/{conid}/info
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


# @server.tool()
async def algo_params(
    conid: str,
    algos: Optional[str] = None,
    add_description: Optional[bool] = None,
    add_params: Optional[bool] = None
) -> str:
    """
    Not exposed as a mcp tool.

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


# @server.tool()
async def all_exchange_contracts(exchange: str) -> str:
    """
    Not exposed as a mcp tool.
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
# TOOL 14: Search Stock Information by Symbol
# ============================================================================

@server.tool()
async def search_possible_stocks_breadth_first(
    queries: StockQueries,
    default_filtering: Optional[bool] = None
) -> str:
    """
    Only search for stocks. Do not use to search for other securities such as indices.

    Breadth-first search for stock information by symbol.
    Get relevant stocks information for given symbols with advanced filtering.
    
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

        Response Object
            symbol: Array of Json
            Contains a series of Json for all contracts that match the symbol.

            name: String.
            Full company name for the given contract.

            chineseName: String.
            Chinese name for the given company.

            assetClass: String.
            Asset class for the given company.

            contracts: Array.
            A series of arrays pertaining to the same company listed by “name”.
            Typically differentiated based on currency of the primary exchange.

            conid: int.
            Contract ID for the specific contract.

            exchange: String.
            Primary exchange for the given contract.

            isUS: bool.
            States whether the contract is hosted in the United States or not.
    Examples:
        # Simple string usage (recommended for LLM clients)
        search_stocks("AAPL")
        search_stocks("AAPL,MSFT,GOOGL")
        
        # Advanced StockQuery usage
        search_stocks([
            {"symbol": "AAPL", "contract_conditions": {"isUS": True}},
            {"symbol": "MSFT", "name_match": "Microsoft"}
        ])
        
        # With default filtering
        search_stocks("AAPL,MSFT", default_filtering=True)
        
    Common Contract Conditions for filtering:
        - "isUS": True/False - US-listed contracts
        - "exchange": "NASDAQ"/"NYSE" - Specific exchange
        - "currency": "USD" - Trading currency
        - "assetClass": "STK" - Asset class
    
    Upstream docs:
    https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#trsrv-stock-contract

    Upstream endpoint:
    GET /trsrv/stocks
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
# TOOL 17: Search Stock Information by StockQuery and Filters
# ============================================================================

@server.tool()
async def search_unique_stocks_depth_first(
    query: str,
    name_match: Optional[str] = None,
    contract_conditions: Optional[dict] = None,
    return_conid_only: bool = True
) -> str:
    """
    Only search for stocks. Do not use to search for other securities such as indices.

    Depth-first search for stock information by symbol or company name.

    Compare to search_possible_stocks, this method forces a unique match.
    
    This is the recommended method for LLM clients to find contracts and their conids.
    It provides a simple, consistent interface for all contract lookup needs.
    
    Args:
        query: Stock symbol or company name to search for.
               Examples: "AAPL", "Apple", "MSFT"
        
        name_match: Optional partial name match for company names.
                   Example: "Micro" for "Microsoft"
        
        contract_conditions: Optional dictionary of contract filtering conditions.
                            Common conditions:
                            - "isUS": True/False - US-listed contracts only
                            - "exchange": "NASDAQ"/"NYSE" - Specific exchange
                            - "currency": "USD" - Trading currency
                            - "assetClass": "STK" - Asset class
                            Example: {"isUS": True, "exchange": "NASDAQ"}
        
        return_conid_only: If True, returns only the conid(s).
                          If False, returns full contract information.
                          Default: True (recommended for conid lookup)
    
    Returns:
        JSON with conid(s) or full contract information.
    
    Examples:
        # Simple symbol lookup (returns conid)
        find_contract("AAPL")
        
        # Company name lookup with partial match
        find_contract("Apple", name_match="Apple Inc")
        
        # Filter for US contracts on NASDAQ
        find_contract("AAPL", contract_conditions={"isUS": True, "exchange": "NASDAQ"})
        
        # Get full contract information instead of just conid
        find_contract("AAPL", return_conid_only=False)
        
        # Multiple symbols (comma-separated)
        find_contract("AAPL,MSFT,GOOGL")

    Upstreamstream docs:
    https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#trsrv-stock-contract

    Upstream endpoint:
    GET /trsrv/stocks
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        from ibind.client.ibkr_utils import StockQuery
        
        # Handle multiple symbols (comma-separated)
        if ',' in query:
            symbols = [s.strip() for s in query.split(',')]
            stock_queries = []
            for symbol in symbols:
                stock_query = StockQuery(
                    symbol=symbol,
                    name_match=name_match,
                    contract_conditions=contract_conditions
                )
                stock_queries.append(stock_query)
            
            # Use stock_conid_by_symbol for multiple symbols
            result = client.stock_conid_by_symbol(
                queries=stock_queries,
                return_type="dict"
            )
            data = extract_result_data(result)
            
            if not data:
                return to_json({
                    "error": "No contracts found for the given symbols",
                    "query": query,
                    "name_match": name_match,
                    "contract_conditions": contract_conditions
                })
            
            if return_conid_only:
                return to_json({"conids": data})
            else:
                # Get full information for each conid
                conids = list(data.values()) if isinstance(data, dict) else data
                conid_str = ','.join(str(c) for c in conids)
                return await security_definition(conid_str)
        
        else:
            # Single symbol - use StockQuery
            stock_query = StockQuery(
                symbol=query,
                name_match=name_match,
                contract_conditions=contract_conditions
            )
            
            if return_conid_only:
                # Get conid using stock_conid_by_symbol
                result = client.stock_conid_by_symbol(
                    queries=[stock_query],
                    return_type="dict"
                )
                data = extract_result_data(result)
                
                if not data or query not in data:
                    return to_json({
                        "error": "No contract found for the given query",
                        "query": query,
                        "name_match": name_match,
                        "contract_conditions": contract_conditions,
                        "suggestion": "Try without filters or check symbol/name"
                    })
                
                conid = data[query]
                return to_json({
                    "conid": conid,
                    "symbol": query,
                    "name_match": name_match,
                    "contract_conditions": contract_conditions
                })
            
            else:
                # Get full contract information using security_stocks_by_symbol
                result = client.security_stocks_by_symbol(queries=[stock_query])
                data = extract_result_data(result)
                
                if not data:
                    return to_json({
                        "error": "No contract information found",
                        "query": query,
                        "name_match": name_match,
                        "contract_conditions": contract_conditions
                    })
                
                return to_json({"contract": data})
    
    except Exception as e:
        return to_json({
            "error": "Contract lookup failed",
            "exception": str(e),
            "query": query,
            "name_match": name_match,
            "contract_conditions": contract_conditions,
            "suggestion": "Check the query format and filtering conditions"
        })


# ============================================================================
# TOOL 15: Get Contract IDs by Symbol (Unambiguous Conid Resolution)
# ============================================================================
# This is almost the same as search_unique_stocks_depth_first, but with a different name and slightly different implementation.
# @server.tool()
# async def stock_conid_by_symbol(
#     queries: StockQueries,
#     default_filtering: Optional[bool] = None,
#     return_type: str = "dict"
# ) -> str:
#     """
#     Get unambiguous contract IDs (conids) for given stock symbols with filtering.
    
#     Returns contract IDs for stock queries, ensuring only one conid per query.
#     This is the recommended method for conid resolution when you need precise
#     mapping from symbols to contract IDs.
    
#     Args:
#         queries: StockQueries object or list of StockQuery objects.
#                  Can also be a comma-separated string of symbols for simple usage.
#                  Example strings: "AAPL", "AAPL,MSFT,GOOGL"
                 
#                  **For LLM Clients:**
#                  - **Simple usage:** Use comma-separated string: "AAPL,MSFT,GOOGL"
#                  - **Advanced filtering:** Use StockQuery objects for precise control
                 
#                  **StockQuery Structure:**
#                  ```python
#                  {
#                      "symbol": "AAPL",                    # Required: Stock symbol
#                      "name_match": "Apple",              # Optional: Partial name match
#                      "instrument_conditions": {          # Optional: Exact instrument matches
#                          "some_instrument_field": "value"
#                      },
#                      "contract_conditions": {            # Optional: Exact contract matches
#                          "isUS": True,                   # Filter for US contracts
#                          "exchange": "NASDAQ"            # Filter by exchange
#                      }
#                  }
#                  ```
                 
#         default_filtering: Whether to apply default US contract filtering {isUS: True}.
#                           Defaults to None (uses global default).
#                           Set to True to filter for US contracts only.
#                           Set to False to disable default filtering.
#         return_type: Return format - "dict" for {symbol: conid} mapping or 
#                     "list" for list of conids. Default: "dict"
    
#     Returns:
#         JSON with conid mapping or list, or error dict.
    
#     Examples:
#         # Simple string usage (recommended for LLM clients)
#         stock_conid_by_symbol("AAPL")
#         stock_conid_by_symbol("AAPL,MSFT,GOOGL")
#         stock_conid_by_symbol("AAPL,MSFT,GOOGL", return_type="list")
        
#         # Advanced StockQuery usage
#         stock_conid_by_symbol([
#             {"symbol": "AAPL", "contract_conditions": {"isUS": True}},
#             {"symbol": "MSFT", "name_match": "Microsoft"}
#         ])
        
#         # With default filtering
#         stock_conid_by_symbol("AAPL,MSFT", default_filtering=True)
        
#     Common Contract Conditions for filtering:
#         - "isUS": True/False - US-listed contracts
#         - "exchange": "NASDAQ"/"NYSE" - Specific exchange
#         - "currency": "USD" - Trading currency
#         - "assetClass": "STK" - Asset class
#     """
#     try:
#         client = get_client()
#         if client is None:
#             return to_json({
#                 "error": "IBKR client not initialized",
#                 "suggestion": "Check credentials and internet connection"
#             })
        
#         # Handle simple string input (comma-separated symbols)
#         if isinstance(queries, str):
#             # Convert comma-separated string to list of StockQuery objects
#             from ibind.client.ibkr_utils import StockQuery
#             symbol_list = [s.strip() for s in queries.split(',')]
#             queries = [StockQuery(symbol=symbol) for symbol in symbol_list]
        
#         # Call method with conditional parameters
#         if default_filtering is not None:
#             result = client.stock_conid_by_symbol(
#                 queries=queries,
#                 default_filtering=default_filtering,
#                 return_type=return_type
#             )
#         else:
#             result = client.stock_conid_by_symbol(
#                 queries=queries,
#                 return_type=return_type
#             )
        
#         data = extract_result_data(result)
        
#         if not data:
#             return to_json({
#                 "error": "No conids found for the given symbols",
#                 "queries": str(queries),
#                 "default_filtering": default_filtering
#             })
        
#         return to_json({"conids": data, "return_type": return_type})
    
#     except Exception as e:
#         return to_json({
#             "error": "Conid resolution failed",
#             "exception": str(e),
#             "queries": str(queries)
#         })


# ============================================================================
# TOOL 1: Search Underlying
# ============================================================================

@server.tool()
async def search_underlier(
    symbol: str,
    search_by_name: Optional[bool] = None,
    underlying_security_type: Optional[str] = None
) -> str:
    """
    Search for underlying symbol or company name. Use this to search for an index's conid.
    
    Returns the conid of an underlier, and what derivative contracts and their expiration months are available for the given underlying.
    This endpoint must be called before using get_derivative_contract_details().
    
    Args:
        symbol: Ticker symbol (e.g., "SPX", or "HSI") or company name if search_by_name=True.
                Can also be bond issuer type to retrieve bonds.
        search_by_name: If True, treat symbol as company name instead of ticker. Determines if symbol reflects company name or ticker symbol. If company name is included will only receive limited response: conid, companyName, companyHeader and symbol. The inclusion of the name field will prohibit the /iserver/secdef/strikes endpoint from returning data. After retrieving your expected contract, customers looking to create option chains should remove the name field from the request.
        underlying_security_type: Filter by type. Valid: "STK" for stock, "IND" for index, "BOND" for bond.
    
    Returns:
        JSON with matching contracts (conid, symbol, description, exchange, etc.)
        or error dict if search fails.
        Response Object
            “conid”: String.
            Conid of the given contract.

            “companyHeader”: String.
            Extended company name and primary exchange.

            “companyName”: String.
            Name of the company.

            “symbol”: String.
            Company ticker symbol.

            “description”: String.
            Primary exchange of the contract.

            “restricted”: bool.
            Returns if the contract is available for trading.

            “sections”: Array of objects

            “secType”: String.
            Given contracts security type.

            “months”: String.
            Returns a string of dates, separated by semicolons.
            Value Format: “JANYY;FEBYY;MARYY”

            “symbol”: String.
            Symbol of the instrument.

            “exchange”: String.
            Returns a string of exchanges, separated by semicolons.
            Value Format: “EXCH;EXCH;EXCH”

            Unique for Bonds
            “issuers”: Array of objects
            Array of objects containing the id and name for each bond issuer.

            “id”: String.
            Issuer Id for the given contract.

            “name”: String.
            Name of the issuer.

            “bondid”: int.
            Bond type identifier.

            “conid”: String.
            Contract ID for the given bond.

            “companyHeader”: String.
            Name of the bond type
            Value Format: “Corporate Fixed Income”

            “companyName”: null
            Returns ‘null’ for bond contracts.

            “symbol”:null
            Returns ‘null’ for bond contracts.

            “description”:null
            Returns ‘null’ for bond contracts.

            “restricted”:null
            Returns ‘null’ for bond contracts.

            “fop”:null
            Returns ‘null’ for bond contracts.

            “opt”:null
            Returns ‘null’ for bond contracts.

            “war”:null
            Returns ‘null’ for bond contracts.

            “sections”: Array of objects
            Only relays “secType”:”BOND” in the Bonds section.
    
    Examples:
        preflight_underlying_search_for_finding_derivatives(symbol="SPX", search_by_name=False, underlying_security_type="IND")) 

        preflight_underlying_search_for_finding_derivatives("Apple", search_by_name=True, underlying_security_type="STK")

        For bonds, enter the family type in the symbol field to receive the issuerID used in the /iserver/secdef/info endpoint.
        preflight_underlying_search_for_finding_derivatives("US Treasury", underlying_security_type="BOND")
    
    Uptream docs:
    https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#search-symbol-contract

    Upstream endpoint:
    GET /iserver/secdef/search
    """
    try:
        client = get_client()
        if client is None:
            return to_json({
                "error": "IBKR client not initialized",
                "suggestion": "Check credentials and internet connection"
            })
        
        if search_by_name is not None and underlying_security_type is not None:
            result = client.search_contract_by_symbol(
                symbol=symbol,
                name=search_by_name,
                sec_type=underlying_security_type
            )
        elif search_by_name is not None:
            result = client.search_contract_by_symbol(
                symbol=symbol,
                name=search_by_name
            )
        elif underlying_security_type is not None:
            result = client.search_contract_by_symbol(
                symbol=symbol,
                sec_type=underlying_security_type
            )
        else:
            result = client.search_contract_by_symbol(symbol=symbol)
        
        data = extract_result_data(result)
        
        if not data:
            return to_json({
                "error": "No contracts found",
                "searched": symbol,
                "search_by_name": search_by_name,
                "security_type": underlying_security_type
            })
        
        return to_json({"contracts": data})
    
    except Exception as e:
        return to_json({
            "error": "Contract search failed",
            "exception": str(e),
            "symbol": symbol
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
        e.g.:
                    {
        "bondFilters": [
            {
            "displayText": "Exchange",
            "columnId": 0,
            "options": [
            {
                "value": "SMART"
            }]
            },
            {
            "displayText": "Maturity Date",
            "columnId": 27,
            "options": [
                {
                "text": "Jan 2025",
                "value": "202501"
            }]
            },
            {
            "displayText": "Issue Date",
            "columnId": 28,
            "options": [{
                "text": "Sep 18 2014",
                "value": "20140918"
            }]
            },
            {
            "displayText": "Coupon",
            "columnId": 25,
            "options": [{
                "value": "1.301"
            }]
            },
            {
            "displayText": "Currency",
            "columnId": 5,
            "options": [{
                "value": "EUR"
            }]
            }
        ]
        }
    Examples:
        get_bond_filters("e1359061") for issuer United States Treasury
    
    Upstream docs:
        https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#secdef-bond-filters

    Upstream endpoint:
        GET iserver/secdef/bond-filters
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
async def get_derivative_contract_details(
    conid: str,
    security_type: str,
    expiration_month: str,
    exchange: Optional[str] = None,
    strike: Optional[str] = None,
    option_right: Optional[str] = None,
    bond_issuer_id: Optional[str] = None
) -> str:
    """
    Must call preflight_underlying_search_for_finding_derivatives() first.

    Get Contract Details of Futures, Options, Warrants, Cash and CFDs based on conid.
    
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
        get_derivative_contract_details("265598", "OPT", "JAN25", strike="150", option_right="C")
        get_derivative_contract_details("209", "FUT", "JAN25")

    Upstream docs:
        https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#secdef-info-contract
    
    Upstream endpoint:
        GET /iserver/secdef/info
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
# TOOL 13: Get Future Contracts by Symbol
# ============================================================================

@server.tool()
async def search_futures(symbols: str) -> str:
    """
    Get list of non-expired future contracts for given symbol(s).
    
    Returns all available futures contracts for the specified underlying(s).
    
    Args:
        symbols: Comma-separated symbol list (e.g., "ES,NQ,GC") of the underlier you are trying to retrieve futures on.
                 Can also be a single symbol (e.g., "ES")
    
    Returns:
        JSON with available future contracts or error dict. Data will include conids of futures, as well as the underlier conid.

        If you inadvertently use this method to search for an index, you will need to use the underlier conid, not the futures conid.
    
    Examples:
        search_futures("ES")
        search_futures("ES,NQ,GC")

    Upstream docs:
        https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#trsrv-future-contract

    Upstream endpoint:
        GET /trsrv/futures
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
# TOOL 16: Get Brokerage Accounts (Account Initialization)
# ============================================================================

@server.tool()
async def preflight_receive_brokerage_accounts() -> str:
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
        preflight_receive_brokerage_accounts()
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
# TOOL 18: Search Dynamic Accounts
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
# TOOL 19: Get Trading Schedule by Symbol and Exchange
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
async def fields_definitions_to_keys() -> str:
    """
    Definitions of what various IBKR market data snapshot fields stand for.
    
    Returns:
        JSON string with field definitions and numeric keys.
    """
    import json
    from ibind.client.ibkr_definitions import snapshot_by_key
    return json.dumps(snapshot_by_key)

@server.tool()
async def numeric_key_to_field_definitions() -> str:
    """
    Definitions of what various IBKR market data snapshot fields stand for.
    
    Returns:
        JSON string with numeric keys and field definitions.
    """
    import json
    from ibind.client.ibkr_definitions import snapshot_by_id
    return json.dumps(snapshot_by_id)

@server.tool()
async def live_marketdata_snapshot(
    conids: OneOrMany[str],
    fields: Optional[Union[str, List[int], List[str]]] = None
) -> str:
    """
    Get live market data snapshot for a contract.
    
    Returns current market data including bid, ask, last price, bid/ask size, etc.
    Per IBKR documentation, the first request requires a preflight. This method
    handles retries automatically until valid data (Last Price) is received.
    
    Args:
        conids: Contract ID(s) (e.g., "265598" for AAPL)
        fields: Field IDs to retrieve. Can be:
                - Comma-separated string: "31,69,70"
                - List of integers: [31, 69, 70]
                - List of strings: ["31", "69", "70"]
                - None: returns default fields
                
                See: fields_definitions_to_keys_for_marketdata_snapshot() and numeric_key_to_field_definitions_for_marketdata_snapshot() for more details.  
    Returns:
        JSON with current market data snapshot or error dict.
    
    Examples:
        # String format (comma-separated)
        live_marketdata_snapshot("265598")
        live_marketdata_snapshot("265598", fields="69,70,31")
        live_marketdata_snapshot("265598", fields="31")
        
        # Array format (LLM-friendly)
        live_marketdata_snapshot("265598", fields=[31, 69, 70, 84, 85, 86])
        live_marketdata_snapshot("265598", fields=["31", "69", "70"])
    """
    import time
    
    max_attempts = 10
    
    # Prepare field list - convert to list[str] for fetch_raw_market_data
    if fields is not None:
        if isinstance(fields, str):
            # Comma-separated string: "31,69,70"
            field_list = [str(f.strip()) for f in fields.split(',')]
        else:
            # Must be a list (Union[str, List[int], List[str]] ensures this)
            # List of integers or strings: [31, 69, 70] or ["31", "69", "70"]
            field_list = [str(f) for f in fields]  # type: ignore[arg-type]
    else:
        field_list = ['55','7051','7635','31','70','71','7295','7741', '7293','7294', '7681', '7724', '7679', '7678','7283', '7087']
    
    # Retry loop with validation
    for attempt in range(max_attempts):
        try:
            data = fetch_raw_market_data(conids, field_list)
            if data:
                return to_json({"snapshot": data})
            
            # Retry with delay (but not on last attempt)
            if attempt < max_attempts - 1:
                time.sleep(1)
                continue
            
            # All attempts exhausted
            return to_json({
                "error": "No market data available after retries",
                "conids": conids,
                "attempts": max_attempts,
                "fields": fields
            })
        
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(1)
                continue
            
            return to_json({
                "error": "Live market data snapshot failed",
                "exception": str(e),
                "conids": conids,
                "attempts": max_attempts,
                "fields": fields
            })
    
    return to_json({
        "error": "Live market data snapshot failed after maximum retries",
        "conids": conids,
        "max_attempts": max_attempts,
        "fields": fields
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

        fields: Comma-separated field IDs to retrieve.

                See: fields_definitions_to_keys_for_marketdata_snapshot() and numeric_key_to_field_definitions_for_marketdata_snapshot() for more details.  

    
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

        StockQueries = OneOrMany[Union[StockQuery, str]]

    """
    import time
    
    max_attempts = 10
    
    # Prepare field list
    if fields is not None:
        field_list = [str(f.strip()) for f in fields.split(',')]
    else:
        field_list = ['55','7051','7635','31','70','71','7295','7741', '7293','7294', '7681', '7724', '7679', '7678','7283', '7087']
    
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
    import os
    # Read the documentation from the external file
    file_path = os.path.join(os.path.dirname(__file__), "tools_documentation.md")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: Documentation file not found at {file_path}"
    except Exception as e:
        return f"Error reading documentation: {str(e)}"

if __name__ == "__main__":
    server.run()