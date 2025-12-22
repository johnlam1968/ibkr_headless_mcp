"""
MCP Server: IBKR ContractMixin + MarketdataMixin Tools - Complete Implementation

Exposes ALL Interactive Brokers ContractMixin and MarketdataMixin methods via FastMCP.
Provides comprehensive contract search, market data retrieval, and trading information.

Usage:
  cd /home/john/CodingProjects/llm_public
  PYTHONPATH=./src python src/mcp_server.py
"""

from typing import Any, Dict, Optional, Union, List
# from fastmcp import FastMCP # tool reponse duplicate content and structuredContent, double the tokens?
# https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1576
from mcp.server.fastmcp import FastMCP # to avoid high tokens in tool responses, because it has @server.tool(structured_output=False)

from dotenv import load_dotenv
from ibind.client.ibkr_utils import StockQueries # type: ignore
from ibind.support.py_utils import OneOrMany # type: ignore
from ibind import Result # type: ignore


from utils import fetch_raw_market_data, extract_result_data, to_json, get_client

load_dotenv()


server = FastMCP("ibkr-contract-server")


# ============================================================================
# CUSTOM DECORATOR FOR MCP TOOLS
# ============================================================================

# Create a custom decorator that wraps @server.tool with structured_output=False
from typing import Callable, TypeVar, Awaitable

# Type variables for the decorator
F = TypeVar('F', bound=Callable[..., Awaitable[str]])

def mcp_tool(func: F) -> F:
    """Custom decorator for MCP tools that automatically sets structured_output=False"""
    return server.tool(structured_output=False)(func)  # type: ignore


@mcp_tool
async def instrument_definition(
    conids: str
) -> str:
    """
    Get definitions of instruments for given contract IDs.
    
    Returns a list of instruments definitions with detailed contract information.
    Useful for retrieving multiple contracts at once.
    
    Args:
        conids: Comma-separated contract IDs (e.g., "265598,9408,12345")
                Can also be a single conid (e.g., "265598")
    
    Returns:
        JSON with instruments definitions for each conid or error dict.
        Response Object:
            secdef: array.
            Returns the contents of the request with the array.

            conid: int.
            Returns the conID

            currency: String.
            Returns the traded currency for the contract.

            time: int.
            Returns amount of time in ms to generate the data.

            chineseName: String.
            Returns the Chinese characters for the symbol.

            allExchanges: String*.
            Returns a series of exchanges the given symbol can trade on.

            listingExchange: String.
            Returns the primary or listing exchange the contract is hosted on.

            countryCode: String.
            Returns the country code the contract is traded on.

            name: String.
            Returns the comapny name.

            assetClass: String.
            Returns the asset class or security type of the contract.

            expiry: String.
            Returns the expiry of the contract. Returns null for non-expiry instruments.

            lastTradingDay: String.
            Returns the last trading day of the contract.

            group: String.
            Returns the group or industry the contract is affilated with.

            putOrCall: String.
            Returns if the contract is a Put or Call option.

            sector: String.
            Returns the contract’s sector.

            sectorGroup: String.
            Returns the sector’s group.

            strike: String.
            Returns the strike of the contract.

            ticker: String.
            Returns the ticker symbol of the traded contract.

            undConid: int.
            Returns the contract’s underlyer.

            multiplier: float,
            Returns the contract multiplier.

            type: String.
            Returns stock type.

            hasOptions: bool.
            Returns if contract has tradable options contracts.

            fullName: String.
            Returns symbol name for requested contract.

            isUS: bool.
            Returns if the contract is US based or not.

            incrementRules & displayRule: Array.
            Returns rules regarding incrementation for order placement. Not functional for all exchanges. Please see /iserver/contract/rules for more accurate rule details.

            isEventContract: bool.
            Returns if the contract is an event contract or not.

            pageSize: int.
            Returns the content size of the request.
    
    
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
                "error": "No instruments definitions found",
                "conids": conids
            })
        
        return to_json({"definitions": data})
    
    except Exception as e:
        return to_json({
            "error": "instruments definition lookup failed",
            "exception": str(e),
            "conids": conids
        })

@mcp_tool
async def contract_information(conid: str) -> str:
    """
    Get full contract details for a specific contract ID.
    
    Returns comprehensive contract information including trading hours,
    multiplier, tick size, and other contract specifications.
    
    Args:
        conid: Contract ID (e.g., "265598" for Apple stock)
    
    Returns:
        JSON with complete contract information or error dict.
        Response Object:
            conid: int.
            Contract ID of the requested contract.

            ticker: String.
            Ticker symbol of the requested contract.

            secType: String.
            Security type of the requested contract.

            listingExchange: String.
            Primary exchange of the requested contract.

            exchange: String.
            Traded exchange of the requested contract set in the request.

            companyName: String.
            Company name of the requested contract.

            currency: String.
            National currency of the requested contract.

            validExchanges: String.
            All valid exchanges of the requested contract.

            priceRendering: String.
            Render price of the requested contract.

            maturityDate: String.
            Maturity, or expiration date, of the requested contract.

            right: String.
            Right, put or call, of the requested contract.

            strike: int.
            Strike price of the requested contract.
    

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

@mcp_tool
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

        Response Object
            cfi_code: String.
            Classification of Financial Instrument codes

            symbol: String.
            Underlying symbol

            cusip: String.
            Returns the CUSIP for the given instrument.
            Only used in BOND trading.

            expiry_full: String.
            Returns the expiration month of the contract.
            Formatted as “YYYYMM”

            con_id: int.
            Indicates the contract identifier of the given contract.

            maturity_date: String.
            Indicates the final maturity date of the given contract.
            Formatted as “YYYYMMDD”

            industry: String.
            Specific group of companies or businesses.

            instrument_type: String.
            Asset class of the instrument.

            trading_class: String.
            Designated trading class of the contract.

            valid_exchanges: String.
            Comma separated list of support exchanges or trading venues.

            allow_sell_long: bool.
            Allowed to sell shares you own.

            is_zero_commission_security: bool.
            Indicates if the contract supports zero commission trading.

            local_symbol: String.
            Contract’s symbol from primary exchange. For options it is the OCC symbol.

            contract_clarification_type: null

            classifier: null.

            currency: String.
            Base currency contract is traded in.

            text: String.
            Indicates the display name of the contract, as shown with Client Portal.

            underlying_con_id: int.
            Underlying contract identifier for the requested contract.

            r_t_h: bool.
            Indicates if the contract can be traded outside regular trading hours or not.

            multiplier: String.
            Indicates the multiplier of the contract.

            underlying_issuer: String.
            Indicates the issuer of the underlying.

            contract_month: String.
            Indicates the year and month the contract expires.
            Value Format: “YYYYMM”

            company_name: String.
            Indicates the name of the company or index.

            smart_available: bool.
            Indicates if the contract can be smart routed or not.

            exchange: String.
            Indicates the primary exchange for which the contract can be traded.

            category: String.
            Indicates the industry category of the instrument.

            rules: Object.
            See the /iserver/contract/rules endpoint.
    
    Examples:
        contract_info_and_rules("265598")
        contract_info_and_rules("265598", is_buy=True)
        contract_info_and_rules("265598", is_buy=False)
    Upstream docs:
        https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#info-rules-contract

    Upstream endpoint:
        GET /iserver/contract/{{ conid }}/info-and-rules
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

@mcp_tool
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
            from ibind.client.ibkr_utils import StockQuery # type: ignore
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

@mcp_tool
async def search_unique_stocks_depth_first(
    query: str,
    name_match: Optional[str] = None,
    contract_conditions: Optional[dict[str, Any]] = None,
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
        
        from ibind.client.ibkr_utils import StockQuery # type: ignore
        
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
                stock_queries.append(stock_query) # type: ignore
            
            # Use stock_conid_by_symbol for multiple symbols
            result = client.stock_conid_by_symbol(
                queries=stock_queries, # type: ignore
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
                conids = list(data.values()) if isinstance(data, dict) else data # type: ignore
                conid_str = ','.join(str(c) for c in conids) # type: ignore
                return await instrument_definition(conid_str)
        
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

@mcp_tool
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

@mcp_tool
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
        
    """
    if params:
        _result = _call_endpoint(path, params)
    else:
        _result = _call_endpoint(path, {})
    return to_json(_result.data) # type: ignore

def _call_endpoint(path: str, params: Dict[str, Any]) -> Result:

    client = get_client()
    return client.get(path=path, params=params) # type: ignore

@mcp_tool
async def get_treasury_bond_details() -> str:
    """
    Get Contract Details of US Treasury Bonds.
    Returns:
        JSON with contract details or error dict.
        
    """
    _ = _call_endpoint("/iserver/secdef/search", {"symbol":"US-T", "sectype":"BOND"})
    _result = _call_endpoint("/iserver/secdef/info", {"conid":"-1", "sectype":"BOND", "issuerId":"e1359061"})
    return to_json(_result.data) # type: ignore

@mcp_tool
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

    Get Contract Details of Bond, Futures, Options, Warrants, Cash and CFDs based on conid.
    
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
        Response Object:
            conid: int.
            Contract Identifier of the given contract

            ticker: String
            Ticker symbol for the given contract

            secType: String.
            Security type for the given contract.

            listingExchange: String.
            Primary listing exchange for the given contract.

            exchange: String.
            Exchange requesting data for.

            companyName: String.
            Name of the company for the given contract.

            currency: String
            Traded currency allowed for the given contract.

            validExchanges: String*
            Series of all valid exchanges the contract can be traded on in a single comma-separated string.
            priceRendering: null.

            maturityDate: String
            Date of expiration for the given contract.

            right: String.
            Right (P or C) for the given contract.

            strike: Float.
            Returns the given strike value for the given contract.
    
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

@mcp_tool
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

    Upstream docs:
        https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#strike-conid-contract

    Upstream endpoint:
        GET /iserver/secdef/strikes
        This endpoint will always return empty arrays unless /iserver/secdef/search is called for the same underlying symbol beforehand. The inclusion of the name field with the /iserver/secdef/search endpoint will prohibit the strikes endpoint from returning data. After retrieving your expected contract from the initial search, developers looking to create option chains should remove the name field from the request.
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

@mcp_tool
async def search_futures(symbols: str) -> str:
    """
    Get list of non-expired future contracts for given symbol(s).
    
    Returns all available futures contracts for the specified underlying(s).
    
    Args:
        symbols: Comma-separated symbol list (e.g., "ES,NQ,GC") of the underlier you are trying to retrieve futures on.
                 Can also be a single symbol (e.g., "ES")
    
    Returns:
        JSON with available future contracts or error dict. Data will include conids of futures, as well as the underlier conid.
        Response Body:
            symbol: Array
            Displayed as the string of your symbol
            Contains a series of objects for each symbol that matches the requested.

            symbol: String.
            The requested symbol value.

            conid: int.
            Contract identifier for the specific symbol

            underlyingConid: int.
            Contract identifier for the future’s underlying contract.

            expirationDate: int.
            Expiration date of the specific future contract.

            ltd: int.
            Last trade date of the future contract.

            shortFuturesCutOff: int.
            Represents the final day for contract rollover for shorted futures.

            longFuturesCutOff: int.
            Represents the final day for contract rollover for long futures.
 
    Note:
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

@mcp_tool
async def currency_pairs(currency: str) -> str:
    """
    Get available currency pairs for a target currency.
    
    Returns official currency pairs corresponding to the given target currency.
    
    Args:
        currency: Target currency code (e.g., "USD", "EUR", "GBP")
    
    Returns:
        JSON with available currency pairs or error dict.
        Response Object:
            {{currency}}: List of Objects.
            [{
            symbol: String.
            The official symbol of the given currency pair.

            conid: int.
            The official contract identifier of the given currency pair.

            ccyPair: String.
            Returns the counterpart of
            }]
    
    Examples:
        currency_pairs("USD")
        currency_pairs("EUR")

    Upstream docs:
        https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#get-currency-pairs
    
    Upstream endpoint:
        GET /iserver/currency/pairs
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

@mcp_tool
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

    Upstream docs:
        https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#get-exchange-rate

    Upstream endpoint:
        GET /iserver/exchangerate
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

@mcp_tool
async def preflight_receive_brokerage_accounts() -> str:
    """
    Get list of brokerage accounts available for trading.
    
    Returns a list of accounts the user has trading access to, their respective
    aliases, and the currently selected account. This endpoint must be called
    before modifying an order or querying open orders.
    
    # Note this endpoint must be called before modifying an order or querying open orders. This is a prerequisite for many IBKR operations and should be called
    # early in any workflow that involves account-specific operations.
    
    Returns:
        JSON with account list, aliases, and current selection or error dict.
        Response Object:
            accounts: Array of Strings.
            Returns an array of all accessible accountIds.

            acctProps: Json Object.
            Returns an json object for each accessible account’s properties.

            hasChildAccounts: bool.
            Returns whether or not child accounts exist for the account.

            supportsCashQty: bool
            Returns whether or not the account can use Cash Quantity for trading.

            supportsFractions: bool.
            Returns whether or not the account can submit fractional share orders.

            allowCustomerTime: bool.
            Returns whether or not the account must submit “manualOrderTime” with orders or not.
            If true, manualOrderTime must be included.
            If false, manualOrderTime cannot be included.

            aliases: JSON Object.
            Returns any available aliases for the account.

            allowFeatures: JSON object
            JSON of allowed features for the account.

            showGFIS: bool.
            Returns if the account can access market data.

            showEUCostReport: bool.
            Returns if the account can view the EU Cost Report

            allowFXConv: bool.
            Returns if the account can convert currencies.

            allowFinancialLens: bool.
            Returns if the account can access the financial lens.

            allowMTA: bool.
            Returns if the account can use mobile trading alerts.

            allowTypeAhead: bool.
            Returns if the account can use Type-Ahead support for Client Portal.

            allowEventTrading: bool.
            Returns if the account can use Event Trader.

            snapshotRefreshTimeout: int.
            Returns the snapshot refresh timeout window for new data.

            liteUser: bool.
            Returns if the account is an IBKR Lite user.

            showWebNews: bool.
            Returns if the account can use News feeds via the web.
            research: bool.

            debugPnl: bool.
            Returns if the account can use the debugPnl endpoint.

            showTaxOpt: bool.
            Returns if the account can use the Tax Optimizer tool

            showImpactDashboard: bool.
            Returns if the account can view the Impact Dashboard.

            allowDynAccount: bool.
            Returns if the account can use dynamic account changes.

            allowCrypto: bool.
            Returns if the account can trade crypto currencies.

            allowedAssetTypes: bool.
            Returns a list of asset types the account can trade.

            chartPeriods: Json Object.
            Returns available trading times for all available security types.

            groups: Array.
            Returns an array of affiliated groups.

            profiles: Array.
            Returns an array of affiliated profiles.

            selectedAccount: String.
            Returns currently selected account. See Switch Account for more details.

            serverInfo: JSON Object.
            Returns information about the IBKR session. Unrelated to Client Portal Gateway.

            sessionId: String.
            Returns current session ID.

            isFT: bool.
            Returns fractional trading access.

            isPaper: bool.
            Returns account type status.
    
    Examples:
        preflight_receive_brokerage_accounts()

    Upstream docs:
        https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#get-brokerage-accounts

    Upstream endpoint:
        GET /iserver/accounts
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

@mcp_tool
async def fields_definitions_to_keys() -> str:
    """
    Definitions of what various IBKR market data snapshot fields stand for.
    
    Returns:
        JSON string with field definitions and numeric keys.
    """
    import json
    from ibind.client.ibkr_definitions import snapshot_by_key # type: ignore
    return json.dumps(snapshot_by_key)

@mcp_tool
async def numeric_key_to_field_definitions() -> str:
    """
    Definitions of what various IBKR market data snapshot fields stand for.
    
    Returns:
        JSON string with numeric keys and field definitions.
    """
    import json
    from ibind.client.ibkr_definitions import snapshot_by_id # type: ignore
    return json.dumps(snapshot_by_id)

@mcp_tool
async def live_marketdata_snapshot(
    conids: OneOrMany[str],
    fields: Optional[Union[str, List[int], List[str]]] = None
) -> str:
    """
    Get live market data snapshot for a contract.

    A pre-flight request must be made prior to ever receiving data. For some fields, it may take more than a few moments to receive information.

    See response fields for a list of available fields that can be request via fields argument.

    The endpoint /iserver/accounts must be called prior to /iserver/marketdata/snapshot.

    For derivative contracts the endpoint /iserver/secdef/search must be called first.
    
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
        Response Object:
            server_id: String.
            Returns the request’s identifier.

            conidEx: String.
            Returns the passed conid field. May include exchange if specified in request.

            conid: int.
            Returns the contract id of the request

            _updated: int*.
            Returns the epoch time of the update in a 13 character integer .

            6119: String.
            Field value of the server_id. Returns the request’s identifier.

            fields*: String.
            Returns a response for each request. Some fields not be as readily available as others. See the Market Data section for more details.

            6509: String.
            Returns a multi-character value representing the Market Data Availability. https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#md-availability
                Code	Name	Description
                R	RealTime	Data is relayed back in real time without delay, market data subscription(s) are required.
                D	Delayed	Data is relayed back 15-20 min delayed.
                Z	Frozen	Last recorded data at market close, relayed back in real time.
                Y	Frozen Delayed	Last recorded data at market close, relayed back delayed.
                N	Not Subscribed	User does not have the required market data subscription(s) to relay back either real time or delayed data.
                O	Incomplete Market Data API Acknowledgement	The annual Market Data API Acknowledgement has not been completed for the given user. 
                P	Snapshot	Snapshot request is available for contract.
                p	Consolidated	Market data is aggregated across multiple exchanges or venues.
                B	Book	Top of the book data is available for contract.
                d	Performance Details Enabled	Additional performance details are available for this contract. Internal use intended.
    
    Examples:
        # String format (comma-separated)
        live_marketdata_snapshot("265598")
        live_marketdata_snapshot("265598", fields="69,70,31")
        live_marketdata_snapshot("265598", fields="31")
        
        # Array format (LLM-friendly)
        live_marketdata_snapshot("265598", fields=[31, 69, 70, 84, 85, 86])
        live_marketdata_snapshot("265598", fields=["31", "69", "70"])

    Upstream docs:
        https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#md-snapshot

    Upstream endpoint:
        GET /iserver/marketdata/snapshot
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

@mcp_tool
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
        Response Object:
            serverId: String.
            Internal request identifier.

            symbol: String.
            Returns the ticker symbol of the contract.

            text: String.
            Returns the long name of the ticker symbol.

            priceFactor: String.
            Returns the price increment obtained from the display rules.

            startTime: String.
            Returns the initial time of the historical data request.
            Returned in UTC formatted as YYYYMMDD-HH:mm:ss

            high: String.
            Returns the High values during this time series with format %h/%v/%t.
            %h is the high price (scaled by priceFactor),
            %v is volume (volume factor will always be 100 (reported volume = actual volume/100))
            %t is minutes from start time of the chart

            low: String.
            Returns the low value during this time series with format %l/%v/%t.
            %l is the low price (scaled by priceFactor),
            %v is volume (volume factor will always be 100 (reported volume = actual volume/100))
            %t is minutes from start time of the chart

            timePeriod: String.
            Returns the duration for the historical data request

            barLength: int.
            Returns the number of seconds in a bar.

            mdAvailability: String.
            Returns the Market Data Availability.
            See the Market Data Availability section for more details.

            mktDataDelay: int.
            Returns the amount of delay, in milliseconds, to process the historical data request.

            outsideRth: bool.
            Defines if the market data returned was inside regular trading hours or not.

            volumeFactor: int.
            Returns the factor the volume is multiplied by.

            priceDisplayRule: int.
            Presents the price display rule used.
            For internal use only.

            priceDisplayValue: String.
            Presents the price display rule used.
            For internal use only.

            negativeCapable: bool.
            Returns whether or not the data can return negative values.

            messageVersion: int.
            Internal use only.

            data: Array of objects.
            Returns all historical bars for the requested period.
            [{
            o: float.
            Returns the Open value of the bar.

            c: float.
            Returns the Close value of the bar.

            h: float.
            Returns the High value of the bar.

            l: float.
            Returns the Low value of the bar.

            v: float.
            Returns the Volume of the bar.

            t: int.
            Returns the Operator Timezone Epoch Unix Timestamp of the bar.
            }],

            points: int.
            Returns the total number of data points in the bar.

            travelTime: int.
            Returns the amount of time to return the details.
    Note:
        https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#hmds-period-bar-size
        Step Size:
            A step size is the permitted minimum and maximum bar size for any given period.

            period	1min	1h	1d	1w	1m	3m	6m	1y	2y	3y	15y
            bar	1min	1min – 8h	1min – 8h	10min – 1w	1h – 1m	2h – 1m	4h – 1m	8h – 1m	1d – 1m	1d – 1m	1w – 1m
            default bar	1min	1min	1min	15min	30min	1d	1d	1d	1d	1w	1w

        There’s a limit of 5 concurrent requests. Excessive requests will return a ‘Too many requests’ status 429 response.
        This endpoint provides a maximum of 1000 data points.
        https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#unavailable-hist-data
        Unavailable Historical Data:
            Bars whose size is 30 seconds or less older than six months
            Expired futures data older than two years counting from the future’s expiration date.
            Expired options, FOPs, warrants and structured products.
            End of Day (EOD) data for options, FOPs, warrants and structured products.
            Data for expired future spreads
            Data for securities which are no longer trading.
            Native historical data for combos. Historical data is not stored in the IB database separately for combos.; combo historical data in TWS or the API is the sum of data from the legs.
            Historical data for securities which move to a new exchange will often not be available prior to the time of the move.
            Studies and indicators such as Weighted Moving Averages or Bollinger Bands are not available from the API.

    Examples:
        marketdata_history_by_conid("265598", "1y")
        marketdata_history_by_conid("265598", "3mo", "1h", outside_rth=True)

    Upstream docs:
        https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#hist-md
        
        Upstream endpoint:
            GET /iserver/marketdata/history
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

@mcp_tool
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

@mcp_tool
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