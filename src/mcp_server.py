"""
MCP Server: IBKR ContractMixin Tools

Exposes Interactive Brokers contract search and specification retrieval via FastMCP.
Implements all 5 ContractMixin methods as async MCP tools with JSON responses.

Tools:
  1. search_contract() - Symbol/company name to contracts
  2. get_contract_details() - Detailed contract specs (options, futures, bonds)
  3. get_option_strikes() - Available strikes for options/warrants
  4. get_trading_rules() - Trading constraints for a contract
  5. get_bond_filters() - Bond issuer filters

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
            print("   Contract search tools will fail until connection is established")
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

server = FastMCP("contract-search-server")


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
    Must be called before using get_contract_details() endpoint.
    
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
        → [{"conid": "265598", "symbol": "AAPL", "description": "Apple Inc"}, ...]
        
        search_contract("Apple Inc", search_by_name=True)
        → [{"conid": "265598", "symbol": "AAPL", ...}, ...]
        
        search_contract("US0378691033", security_type="BOND")
        → [{"conid": "...", "description": "US Treasury Bond", ...}]
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
                "security_type": security_type,
                "suggestion": "Try different symbol or enable search_by_name=true for company names"
            })
        
        return _to_json({"contracts": data})
    
    except Exception as e:
        return _to_json({
            "error": "Contract search failed",
            "exception": str(e),
            "symbol": symbol
        })


# ============================================================================
# TOOL 2: Get Detailed Contract Specifications
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
    Retrieve detailed contract specifications for derivatives (futures, options, bonds, etc).
    
    Provides complete trading details including multiplier, tick size, trading hours,
    position limits, and more.
    
    Args:
        conid: Contract ID of the underlying (or final derivative conid directly).
        security_type: Type of contract. Valid: "FUT" (Futures), "OPT" (Options), 
                       "WAR" (Warrants), "CASH", "CFD", "BOND"
        expiration_month: Expiration month/year. Format: "{3-char month}{2-char year}"
                         Examples: "JAN25", "DEC24"
        exchange: Specific exchange for contract details (optional).
        strike: Strike price. **Required for options/warrants/futures options**.
        option_right: Option direction. **Required for options**: "C" (Call) or "P" (Put).
        bond_issuer_id: Issuer ID for bonds. **Required for bonds**: Format "e1234567".
    
    Returns:
        JSON with full contract specifications or error dict if lookup fails.
    
    Examples:
        get_contract_details("265598", "OPT", "JAN25", strike="150", option_right="C")
        → {"conid": "...", "multiplier": 100, "tick_size": 0.01, ...}
        
        get_contract_details("209", "FUT", "JAN25")
        → {"conid": "...", "multiplier": 50, "contract": "ES", ...}
    """
    # Validate required parameters BEFORE client check for better UX
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
            "conid": conid,
            "security_type": security_type
        })


# ============================================================================
# TOOL 3: Get Available Option/Warrant Strikes
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
    Call this before get_contract_details() to find valid strikes for your query.
    
    Args:
        conid: Contract ID of the underlying.
        security_type: Derivative type. Valid: "OPT" (Options) or "WAR" (Warrants).
        expiration_month: Expiration month/year. Format: "{3-char month}{2-char year}"
                         Examples: "JAN25", "DEC24"
        exchange: Specific exchange (optional, defaults to "SMART").
    
    Returns:
        JSON list of available strike prices or error dict if lookup fails.
    
    Examples:
        get_option_strikes("265598", "OPT", "JAN25")
        → {"strikes": [140, 145, 150, 155, 160, ...]}
        
        get_option_strikes("265598", "OPT", "JAN25", exchange="CBOE")
        → {"strikes": [140, 145, 150, ...], "exchange": "CBOE"}
    """
    # Validate security type BEFORE client check for better UX
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
                "expiration_month": expiration_month,
                "exchange": exchange
            })
        
        count = len(data) if isinstance(data, list) else "unknown"  # type: ignore
        return _to_json({"strikes": data, "count": count})
    
    except Exception as e:
        return _to_json({
            "error": "Strike lookup failed",
            "exception": str(e),
            "conid": conid,
            "security_type": security_type
        })


# ============================================================================
# TOOL 4: Get Trading Rules for a Contract
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
    Call this before placing orders to understand contract limitations.
    
    Args:
        conid: Contract ID.
        exchange: Specific exchange for rules (optional).
        is_buy: Side of market. True for Buy orders, False for Sell. Defaults to True.
        modify_order: If True, retrieve rules for modifying an existing order.
        order_id: Order ID to track. **Required if modify_order=True**.
    
    Returns:
        JSON with trading rules and constraints or error dict if lookup fails.
    
    Examples:
        get_trading_rules("265598")
        → {"min_size": 1, "position_limit": 500000, "trading_hours": {...}}
        
        get_trading_rules("265598", is_buy=False)
        → {"min_size": 1, "position_limit": 500000, "sell_rules": {...}}
        
        get_trading_rules("265598", modify_order=True, order_id=12345)
        → {"modification_rules": {...}, "order_id": 12345}
    """
    # Validate parameters BEFORE client check for better UX
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
# TOOL 5: Get Bond Issuer Filters
# ============================================================================

@server.tool()
async def get_bond_filters(bond_issuer_id: str) -> str:
    """
    Get available filters for a bond issuer.
    
    Returns filtering options for researching bonds from a specific issuer.
    Used for bond contract searches and refinement.
    
    Args:
        bond_issuer_id: Issuer identifier. Format: typically starts with "e" followed by digits.
                       Examples: "e123456" for US Treasuries, other formats for corporate bonds.
    
    Returns:
        JSON with available bond filters or error dict if lookup fails.
    
    Examples:
        get_bond_filters("e123456")
        → {"filters": {"maturity": [...], "rating": [...], "yield": [...]}}
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
# UTILITY TOOL: List All Available Tools
# ============================================================================

@server.tool()
async def list_tools() -> str:
    """
    List all available contract search tools and typical usage workflows.
    
    Returns:
        Markdown formatted documentation of all tools, parameters, and examples.
    """
    return """# IBKR Contract Search MCP Tools

## Available Tools (6 total)

### 1. search_contract(symbol, search_by_name=None, security_type=None)
Search for contracts by ticker symbol, company name, or bond issuer.

**Parameters:**
- `symbol` (str): Ticker (e.g., "AAPL") or company name or bond issuer type
- `search_by_name` (bool, optional): If True, treat symbol as company name
- `security_type` (str, optional): Filter by "STK", "IND", or "BOND"

**Returns:** List of matching contracts with conid, symbol, description, exchange

**Example:** search_contract("AAPL") → Returns all AAPL contracts
**Example:** search_contract("Apple", search_by_name=True) → Returns Apple Inc contracts

---

### 2. get_contract_details(conid, security_type, expiration_month, exchange=None, strike=None, option_right=None, bond_issuer_id=None)
Get detailed specifications for a specific derivative contract.

**Parameters:**
- `conid` (str): Contract ID (from search_contract result)
- `security_type` (str): "OPT", "FUT", "WAR", "CASH", "CFD", "BOND"
- `expiration_month` (str): Month/year format "JAN25", "DEC24"
- `strike` (str, optional): **Required for OPT/WAR/FUT options**
- `option_right` (str, optional): **Required for options**: "C" or "P"
- `bond_issuer_id` (str, optional): **Required for BOND**: Format "e1234567"
- `exchange` (str, optional): Specific exchange

**Returns:** Full contract specifications (multiplier, tick size, trading hours, etc.)

**Example:** get_contract_details("265598", "OPT", "JAN25", strike="150", option_right="C")
**Example:** get_contract_details("209", "FUT", "JAN25")

---

### 3. get_option_strikes(conid, security_type, expiration_month, exchange=None)
Find all available strike prices for options/warrants on a given underlying.

**Parameters:**
- `conid` (str): Contract ID of underlying
- `security_type` (str): "OPT" or "WAR"
- `expiration_month` (str): Format "JAN25", "DEC24"
- `exchange` (str, optional): Defaults to "SMART"

**Returns:** List of available strike prices

**Example:** get_option_strikes("265598", "OPT", "JAN25") → [140, 145, 150, ...]

---

### 4. get_trading_rules(conid, exchange=None, is_buy=None, modify_order=None, order_id=None)
Get trading constraints and rules for a contract before placing orders.

**Parameters:**
- `conid` (str): Contract ID
- `is_buy` (bool, optional): True for Buy, False for Sell. Default True.
- `exchange` (str, optional): Specific exchange
- `modify_order` (bool, optional): If True, get rules for modifying orders
- `order_id` (int, optional): **Required if modify_order=True**

**Returns:** Position limits, minimum order size, trading hours, other constraints

**Example:** get_trading_rules("265598") → Position limits, order minimums
**Example:** get_trading_rules("265598", modify_order=True, order_id=12345)

---

### 5. get_bond_filters(bond_issuer_id)
Get filtering options for researching bonds from a specific issuer.

**Parameters:**
- `bond_issuer_id` (str): Issuer ID (format: "e123456")

**Returns:** Available bond filters (maturity, rating, yield, etc.)

**Example:** get_bond_filters("e123456") → Maturity ranges, ratings, yields

---

### 6. list_tools()
Show this documentation with all tools, parameters, and examples.

---

## Typical Workflows

### Workflow 1: Find an Apple Stock Call Option
```
1. search_contract("AAPL") 
   → Extract conid (e.g., "265598")

2. get_option_strikes("265598", "OPT", "JAN25")
   → See available strikes: [140, 145, 150, ...]

3. get_contract_details("265598", "OPT", "JAN25", strike="150", option_right="C")
   → Full option specs: multiplier=100, tick_size=0.01, ...

4. get_trading_rules("265598")
   → Trading constraints: position_limit=500000, min_size=1, ...
```

### Workflow 2: Research a Futures Contract
```
1. search_contract("ES")
   → Find E-mini S&P 500 futures contract

2. get_contract_details(conid, "FUT", "JAN25")
   → Get specs: multiplier=50, tick_size=0.25, ...

3. get_trading_rules(conid, is_buy=True)
   → Check position limits and order minimums
```

### Workflow 3: Search for Bonds
```
1. search_contract("BOND", security_type="BOND")
   → Browse available bond issuers

2. get_bond_filters("e123456")
   → See maturity, rating, and yield options

3. search_contract("US Treasury", search_by_name=True, security_type="BOND")
   → Find specific bond contracts
```

---

## Notes

- **Prerequisites:** All tools require IBKR account authentication via .env credentials
- **Conid Required:** Most tools require a conid from search_contract() output
- **Month Format:** Expiration months use "{3-char month}{2-char year}" format (e.g., "JAN25")
- **Option Parameters:** strike and option_right are required for options queries
- **Bond Format:** Issuer IDs typically start with "e" (e.g., "e123456")

---

Generated by IBKR Contract Search MCP Server
"""


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("IBKR Contract Search MCP Server")
    print("="*70)
    print("\n✅ 6 MCP tools loaded:")
    print("   1. search_contract() - Search by symbol/name/issuer")
    print("   2. get_contract_details() - Get derivative specs")
    print("   3. get_option_strikes() - Find available strikes")
    print("   4. get_trading_rules() - Get trading constraints")
    print("   5. get_bond_filters() - Get bond issuer filters")
    print("   6. list_tools() - Show this documentation")
    
    client = get_client()
    if client:
        print("\n✅ IBKR Client: Connected")
    else:
        print("\n⚠️  IBKR Client: Not initialized (will connect on first tool call)")
    
    print("\n📡 Server running on stdio transport...")
    print("="*70 + "\n")
    
    server.run()
