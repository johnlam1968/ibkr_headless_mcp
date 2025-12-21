# IBKR Complete MCP Tools - Contract & Market Data Reference

## Available Tools (27 total)

### Search & Lookup Tools (8)

**1. security_definition(conids)**
Get security definitions for given contract IDs.
- Parameters: conids (comma-separated or single)
- Returns: Security definitions for each conid
- Examples: security_definition("265598"), security_definition("265598,9408,12345")

**2. contract_information(conid)**
Get full contract details for a specific contract ID.
- Parameters: conid (str)
- Returns: Complete contract information
- Examples: contract_information("265598"), contract_information("9408")

**3. search_possible_stocks_breadth_first(queries, default_filtering=None)**
Breadth-first search for stock information by symbol with advanced filtering.
- Parameters: queries (StockQueries or comma-separated string), default_filtering (bool)
- Returns: Stock information with precise filtering
- Examples: search_possible_stocks_breadth_first("AAPL"), search_possible_stocks_breadth_first("AAPL,MSFT,GOOGL")

**4. search_unique_stocks_depth_first(query, name_match=None, contract_conditions=None, return_conid_only=True)**
Depth-first search for stock information by symbol or company name.
- Parameters: query (symbol or name), name_match (partial name), contract_conditions (dict), return_conid_only (bool)
- Returns: Conid(s) or full contract information
- Examples: search_unique_stocks_depth_first("AAPL"), search_unique_stocks_depth_first("Apple", name_match="Apple Inc")

**5. search_underlier(symbol, search_by_name=None, underlying_security_type=None)**
Search for underlying symbol or company name to find derivative contracts. Use this to find index.
- Parameters: symbol (ticker or name), search_by_name (bool), underlying_security_type (STK/IND/BOND)
- Returns: Matching contracts with derivative availability
- Examples: search_underlier("ES"), search_underlier("HSI"), search_underlier("SPX"), search_underlier("Apple", search_by_name=True)

**6. search_futures(symbols)**
Get non-expired future contracts for given symbol(s).
- Parameters: symbols (comma-separated or single)
- Returns: Available futures contracts
- Examples: search_futures("ES"), search_futures("ES,NQ,GC")

**7. currency_pairs(currency)**
Get available currency pairs for a target currency.
- Parameters: currency (str, e.g., "USD")
- Returns: Available currency pairs
- Examples: currency_pairs("USD"), currency_pairs("EUR")

**8. preflight_receive_brokerage_accounts()**
Get list of brokerage accounts available for trading. **PREREQUISITE FOR ACCOUNT OPERATIONS**
- Parameters: None
- Returns: Account list with aliases and current selection
- Examples: preflight_receive_brokerage_accounts()

---

### Contract Details Tools (3)

**9. get_derivative_contract_details(conid, security_type, expiration_month, exchange=None, strike=None, option_right=None, bond_issuer_id=None)**
Get detailed specifications for derivative contracts.
- Parameters: conid, security_type (OPT/FUT/WAR/CASH/CFD/BOND), expiration_month, strike*, option_right*, bond_issuer_id*
- Returns: Full contract specifications
- Examples:
  - get_derivative_contract_details("265598", "OPT", "JAN25", strike="150", option_right="C")
  - get_derivative_contract_details("209", "FUT", "JAN25")

**10. get_option_strikes(conid, security_type, expiration_month, exchange=None)**
Get list of available strike prices for options or warrants.
- Parameters: conid, security_type (OPT/WAR), expiration_month, exchange (optional)
- Returns: List of available strikes
- Examples: get_option_strikes("265598", "OPT", "JAN25")

**11. trading_schedule(asset_class, symbol, exchange=None, exchange_filter=None)**
Get trading schedule (hours) for a contract.
- Parameters: asset_class (STK/OPT/FUT/etc), symbol, exchange, exchange_filter
- Returns: Trading schedule information
- Examples: trading_schedule("STK", "AAPL"), trading_schedule("FUT", "ES")

---

### Trading Rules & Info Tools (3)

**12. get_trading_rules(conid, exchange=None, is_buy=None, modify_order=None, order_id=None)**
Get trading constraints and rules for a contract.
- Parameters: conid, exchange, is_buy (True/False), modify_order, order_id (required if modify_order=True)
- Returns: Position limits, minimums, constraints
- Examples:
  - get_trading_rules("265598")
  - get_trading_rules("265598", modify_order=True, order_id=12345)

**13. contract_info_and_rules(conid, is_buy=None)**
Get both contract info and trading rules in one request.
- Parameters: conid, is_buy (True/False)
- Returns: Combined contract info and rules
- Examples: contract_info_and_rules("265598"), contract_info_and_rules("265598", is_buy=True)

**14. currency_exchange_rate(source, target)**
Get the exchange rate between two currencies.
- Parameters: source (str), target (str)
- Returns: Exchange rate information
- Examples: currency_exchange_rate("USD", "EUR"), currency_exchange_rate("EUR", "GBP")

---

### Bond Tools (1)

**15. get_bond_filters(bond_issuer_id)**
Get available filters for a bond issuer.
- Parameters: bond_issuer_id (e.g., "e123456")
- Returns: Available bond filters (maturity, rating, yield, etc.)
- Examples: get_bond_filters("e123456")

---

### Account Management Tools (2)

**16. search_dynamic_account(search_pattern)**
Search for broker accounts configured with DYNACCT (Dynamic Account) property.
- Parameters: search_pattern (str, e.g., "DU" for paper accounts)
- Returns: Matching dynamic accounts
- Examples: search_dynamic_account("DU")

**17. preflight_receive_brokerage_accounts()**
Get list of brokerage accounts available for trading.
- Parameters: None
- Returns: Account list with aliases and current selection
- Examples: preflight_receive_brokerage_accounts()

---

### Live Market Data Tools (2)

**18. live_marketdata_snapshot(conid, fields=None)**
Get live market data snapshot for a contract.
- Parameters: conid (str), fields (comma-separated field IDs or list)
- Returns: Current bid, ask, last price, and other market data
- Examples:
  - live_marketdata_snapshot("265598")
  - live_marketdata_snapshot("265598", fields="69,70,31")  # Bid, Ask, Last Price
- Common Field IDs: 31=Last Price, 66=Bid Size, 68=Ask Size, 69=Bid, 70=Ask, 84=Mark, 85=Bid/Ask Change

**19. live_marketdata_snapshot_by_queries(queries, fields=None)**
Get live market data snapshot for contracts by queries.
- Parameters: queries (StockQueries), fields (comma-separated field IDs)
- Returns: Current market data snapshot for multiple contracts
- Examples: live_marketdata_snapshot_by_queries("AAPL"), live_marketdata_snapshot_by_queries("AAPL,MSFT")

---

### Historical Market Data Tools (5)

**20. marketdata_history_by_conid(conid, period, bar_size="1d", outside_rth=False)**
Get historical OHLC data for a contract by conid.
- Parameters: conid (str), period (e.g., "1mo", "3mo", "1y", "all"), bar_size (default: "1d"), outside_rth (bool)
- Returns: OHLC bars with volume and timestamps
- Examples: marketdata_history_by_conid("265598", "1y"), marketdata_history_by_conid("265598", "3mo", "1h")

**21. marketdata_history_by_symbol(symbol, period, bar_size="1d", outside_rth=False)**
Get historical OHLC data for a contract by symbol.
- Parameters: symbol (str), period (e.g., "1mo", "3mo", "1y", "all"), bar_size (default: "1d"), outside_rth (bool)
- Returns: OHLC bars with volume and timestamps
- Examples: marketdata_history_by_symbol("AAPL", "1y"), marketdata_history_by_symbol("ES", "3mo", "1h")

**22. marketdata_history_by_conids(conids, period, bar_size="1d", outside_rth=False)**
Get historical OHLC data for multiple contracts (batch, parallel processing).
- Parameters: conids (comma-separated), period (e.g., "1mo", "3mo", "1y"), bar_size (default: "1d"), outside_rth (bool)
- Returns: OHLC data for each conid
- Examples: marketdata_history_by_conids("265598,9408", "1y"), marketdata_history_by_conids("265598,9408,12345", "1mo", "1h")

**23. marketdata_history_by_symbols(symbols, period, bar_size="1d", outside_rth=False)**
Get historical OHLC data for multiple contracts by symbols (batch, parallel processing).
- Parameters: symbols (comma-separated), period (e.g., "1mo", "3mo", "1y"), bar_size (default: "1d"), outside_rth (bool)
- Returns: OHLC data for each symbol
- Examples: marketdata_history_by_symbols("AAPL,MSFT", "1y"), marketdata_history_by_symbols("ES,NQ,GC", "1mo", "1h")

**24. historical_marketdata_beta(conid, start_time, end_time, bar_size="1min")**
Get advanced historical OHLC data with custom time range (beta).
- Parameters: conid (str), start_time (ISO 8601 or Unix timestamp), end_time (ISO 8601 or Unix timestamp), bar_size (default: "1min")
- Returns: Detailed OHLC bars for the specified time range
- Examples:
  - historical_marketdata_beta("265598", "2024-01-01T00:00:00Z", "2024-12-31T23:59:59Z")
  - historical_marketdata_beta("9408", "1704096600", "1735689600", "1h")

---

### Regulatory & Subscriptions Tools (3)

**25. regulatory_snapshot(conid)**
Get regulatory market data snapshot for a contract.
- Parameters: conid (str)
- Returns: Regulatory-compliant market data snapshot
- ⚠️  WARNING: Costs $0.01 USD per call (applies to paper and live accounts)
- Examples: regulatory_snapshot("265598")

**26. marketdata_unsubscribe(conid)**
Unsubscribe from market data for a specific contract.
- Parameters: conid (str)
- Returns: Subscription cancellation status
- Examples: marketdata_unsubscribe("265598")

**27. marketdata_unsubscribe_all()**
Unsubscribe from all market data subscriptions.
- Parameters: None
- Returns: All subscriptions cancelled status
- Examples: marketdata_unsubscribe_all()

---

### Utility

**28. list_tools()**
Show this documentation with all tools and parameters.

**29. fields_definitions_to_keys()**
Definitions of fields for marketdata snapshot.

**30. numeric_key_to_field_definitions()**
Definitions of fields for marketdata snapshot.

---

## Typical Workflows

### Workflow 1: Find Apple Stock Call Options
```
1. search_unique_stocks_depth_first("AAPL")
   → Extract conid (e.g., "265598")

2. get_option_strikes("265598", "OPT", "JAN25")
   → See available strikes: [140, 145, 150, ...]

3. get_derivative_contract_details("265598", "OPT", "JAN25", strike="150", option_right="C")
   → Full specs: multiplier=100, tick_size=0.01, ...

4. get_trading_rules("265598")
   → Position limits: 500000, min_size: 1, ...
```

### Workflow 2: Research a Futures Contract
```
1. search_futures("ES")
   → Find E-mini S&P 500 futures

2. get_derivative_contract_details(conid, "FUT", "JAN25")
   → Get specs: multiplier=50, tick_size=0.25, ...

3. get_trading_rules(conid, is_buy=True)
   → Check position limits
```

### Workflow 3: Analyze Market Data
```
1. live_marketdata_snapshot("265598", fields="31,69,70")
   → Get current bid, ask, last price for AAPL

2. marketdata_history_by_conid("265598", "1mo", "1h")
   → Get hourly OHLC data for the past month

3. marketdata_history_by_symbols("AAPL,MSFT,GOOGL", "1y", "1d")
   → Compare daily performance of tech stocks over the past year
```

### Workflow 4: Currency Analysis
```
1. currency_pairs("USD")
   → See all available currency pairs for USD

2. currency_exchange_rate("USD", "EUR")
   → Get current USD/EUR exchange rate

3. currency_exchange_rate("EUR", "GBP")
   → Get current EUR/GBP exchange rate
```

### Workflow 5: Bond Research
```
1. preflight_underlying_search_for_finding_derivatives("US Treasury", underlying_security_type="BOND")
   → Find bond issuer ID for US Treasury

2. get_bond_filters("e1359061")
   → Get available filters for US Treasury bonds

3. get_derivative_contract_details(conid, "BOND", "JAN25", bond_issuer_id="e1359061")
   → Get detailed specifications for a specific bond
```

## Quick Reference

### Common Field IDs for Market Data
- `31`: Last Price
- `66`: Bid Size
- `68`: Ask Size
- `69`: Bid Price
- `70`: Ask Price
- `84`: Mark Price
- `85`: Bid/Ask Change
- `86`: Mark Change

### Common Security Types
- `STK`: Stock
- `OPT`: Option
- `FUT`: Future
- `WAR`: Warrant
- `CASH`: Cash
- `CFD`: Contract for Difference
- `BOND`: Bond
- `IND`: Index

### Time Period Formats
- `1d`: 1 day
- `1w`: 1 week
- `1mo`: 1 month
- `3mo`: 3 months
- `1y`: 1 year
- `all`: All available data

### Bar Sizes
- `1min`: 1 minute
- `5min`: 5 minutes
- `15min`: 15 minutes
- `30min`: 30 minutes
- `1h`: 1 hour
- `1d`: 1 day
- `1w`: 1 week
- `1mo`: 1 month

## Notes
- Always call `preflight_receive_brokerage_accounts()` before account-specific operations
- `regulatory_snapshot()` costs $0.01 USD per call
- Use `search_unique_stocks_depth_first()` for unambiguous conid resolution
- Batch operations (`marketdata_history_by_conids`, `marketdata_history_by_symbols`) support parallel processing
- First market data requests may require retries until valid data (field 31) is received
