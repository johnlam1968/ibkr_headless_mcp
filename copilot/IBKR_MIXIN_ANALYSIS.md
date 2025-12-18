# IBKR Client Mixin Analysis: Data Retrieval Methods

## Overview
This document provides a comprehensive analysis of the IBKR client mixin classes from the `ibind` package. The five primary mixins expose a rich set of data retrieval methods for interacting with the Interactive Brokers Web API.

**Analyzed Mixins:**
- `AccountsMixin` - Account and credential management
- `ContractMixin` - Contract/instrument search and lookup
- `MarketdataMixin` - Live and historical market data
- `PortfolioMixin` - Portfolio positions and performance
- `WatchlistMixin` - Watchlist management

---

## 1. AccountsMixin

**Purpose:** Retrieve and manage brokerage account information.

**Public API Data Retrieval Methods:** 2

### Method Signatures

#### 1.1 `receive_brokerage_accounts()`
```python
def receive_brokerage_accounts(self: 'IbkrClient') -> Result
```

**Description:** Returns a list of accounts the user has trading access to, their respective aliases, and the currently selected account. This endpoint must be called before modifying an order or querying open orders.

**Parameters:** None

**Returns:** `Result` - Account list with aliases and current selection

**Usage Context:** Primary initialization method; should be called before accessing account-specific features.

---

#### 1.2 `search_dynamic_account(search_pattern: str)`
```python
def search_dynamic_account(self: 'IbkrClient', search_pattern: str) -> Result
```

**Description:** Searches for broker accounts configured with the DYNACCT (Dynamic Account) property using a specified pattern.

**Parameters:**
- `search_pattern` (str): The pattern used to describe credentials. Valid Format: "DU" to query all paper accounts.

**Returns:** `Result` - Matching dynamic accounts

**Usage Context:** Advanced feature for multi-account/tiered account structures.

**Note:** Customers without DYNACCT property receive a 503 error.

---

## 2. ContractMixin

**Purpose:** Search for and retrieve contract/instrument specifications.

**Public API Data Retrieval Methods:** 5

### Method Signatures

#### 2.1 `search_contract_by_symbol(symbol: str, name: bool = None, sec_type: str = None)`
```python
def search_contract_by_symbol(
    self: 'IbkrClient', 
    symbol: str, 
    name: bool = None, 
    sec_type: str = None
) -> Result
```

**Description:** Search by underlying symbol or company name. Returns what derivative contract(s) are available. **Must be called before using `/secdef/info` endpoint.**

**Parameters:**
- `symbol` (str): Underlying symbol of interest. Can also pass company name if `name=True`, or bond issuer type to retrieve bonds.
- `name` (bool, optional): If True, `symbol` is treated as company name; otherwise as ticker symbol.
- `sec_type` (str, optional): Valid values: "STK", "IND", "BOND". Declares underlying security type.

**Returns:** `Result` - Available derivative contracts for the symbol

**Usage Context:** Entry point for contract searches; must precede derivative lookups.

---

#### 2.2 `search_secdef_info_by_conid(conid: str, sec_type: str, month: str, exchange: str = None, strike: str = None, right: str = None, issuer_id: str = None)`
```python
def search_secdef_info_by_conid(
    self: 'IbkrClient', 
    conid: str, 
    sec_type: str, 
    month: str, 
    exchange: str = None, 
    strike: str = None, 
    right: str = None, 
    issuer_id: str = None
) -> Result
```

**Description:** Provides detailed contract specifications for Futures, Options, Warrants, Cash, and CFDs based on contract ID.

**Parameters:**
- `conid` (str): Contract identifier of the underlying (or final derivative conid directly).
- `sec_type` (str): Security type of the requested contract.
- `month` (str): **Required for derivatives.** Expiration month for the given derivative.
- `exchange` (str, optional): Specific exchange to receive information for.
- `strike` (str, optional): **Required for Options/Futures Options.** Strike price.
- `right` (str, optional): **Required for Options.** "C" for Call, "P" for Put.
- `issuer_id` (str, optional): **Required for Bonds.** Format: "e1234567"

**Returns:** `Result` - Complete contract details

**Usage Context:** Used after `search_contract_by_symbol()` to get detailed derivative specifications.

---

#### 2.3 `search_strikes_by_conid(conid: str, sec_type: str, month: str, exchange: str = None)`
```python
def search_strikes_by_conid(
    self: 'IbkrClient', 
    conid: str, 
    sec_type: str, 
    month: str, 
    exchange: str = None
) -> Result
```

**Description:** Query to receive a list of potential strikes supported for a given underlying.

**Parameters:**
- `conid` (str): Contract Identifier number for the underlying.
- `sec_type` (str): Security type of derivatives. Valid values: "OPT" (Option) or "WAR" (Warrant).
- `month` (str): Expiration month and year. Format: `{3-char month}{2-char year}`. Example: "AUG23"
- `exchange` (str, optional): Exchange from which derivatives should be retrieved. Defaults to "SMART".

**Returns:** `Result` - List of available strike prices

**Usage Context:** Used to find available options/warrants for a given underlying before requesting specific strikes.

---

#### 2.4 `search_contract_rules(conid: str, exchange: str = None, is_buy: bool = None, modify_order: bool = None, order_id: int = None)`
```python
def search_contract_rules(
    self: 'IbkrClient', 
    conid: str, 
    exchange: str = None, 
    is_buy: bool = None, 
    modify_order: bool = None, 
    order_id: int = None
) -> Result
```

**Description:** Returns trading-related rules for a specific contract and side (buy/sell).

**Parameters:**
- `conid` (str): Contract identifier for the interested contract.
- `exchange` (str, optional): Specific exchange for which to receive trading rules.
- `is_buy` (bool, optional): Side of market. `True` for Buy, `False` for Sell. Defaults to `True`.
- `modify_order` (bool, optional): If True, find trading rules related to modifying an existing order.
- `order_id` (int, optional): **Required if `modify_order=True`.** Order identifier to track.

**Returns:** `Result` - Trading rules (position limits, minimum order size, etc.)

**Usage Context:** Used before placing orders to understand contract trading constraints.

---

#### 2.5 `search_bond_filter_information(symbol: str, issuer_id: str)`
```python
def search_bond_filter_information(
    self: 'IbkrClient', 
    symbol: str, 
    issuer_id: str
) -> Result
```

**Description:** Request a list of filters relating to a given Bond issuerID.

**Parameters:**
- `symbol` (str): Should always be set to "BOND".
- `issuer_id` (str): Specifies the issuerId value used to designate the bond issuer type.

**Returns:** `Result` - Available bond filters for the issuer

**Usage Context:** Specialized for bond contract lookups; used in conjunction with `search_contract_by_symbol()` for bond searches.

---

## 3. MarketdataMixin

**Purpose:** Retrieve live and historical market data for contracts.

**Public API Data Retrieval Methods:** 9

### Method Signatures

#### 3.1 `live_marketdata_snapshot(conids: Union[str, List[str]], fields: Union[str, List[str]])`
```python
def live_marketdata_snapshot(
    self: 'IbkrClient', 
    conids: Union[str, List[str]], 
    fields: Union[str, List[str]]
) -> Result
```

**Description:** Get current market data for the given contract ID(s). **A pre-flight request must be made prior to receiving data.**

**Parameters:**
- `conids` (Union[str, List[str]]): Contract identifier(s). Can be single string or list.
- `fields` (Union[str, List[str]]): Field IDs to retrieve. Can be single string or list.

**Returns:** `Result` - Current market data snapshot

**Common Field IDs:**
- `31` - Last Price
- `66` - Bid Size
- `68` - Ask Size
- `84` - Mark Price
- `85` - Bid/Ask Change
- `86` - Mark Change
- `69` - Bid Price
- `70` - Ask Price

**Usage Context:** Core method for getting current market prices and data.

---

#### 3.2 `live_marketdata_snapshot_by_symbol(queries: Union[StockQuery, str, List[...]], fields: Union[str, List[str]])`
```python
def live_marketdata_snapshot_by_symbol(
    self: 'IbkrClient', 
    queries: Union[StockQuery, str, List[Union[StockQuery, str]]], 
    fields: Union[str, List[str]]
) -> dict
```

**Description:** Get market data for the given symbol(s). Wrapper around `live_marketdata_snapshot()` that accepts symbols instead of conids. Returns dict directly (not Result).

**Parameters:**
- `queries` (Union[StockQuery, str, List]): Symbol(s) or StockQuery object(s).
- `fields` (Union[str, List[str]]): Field IDs to retrieve.

**Returns:** `dict` - Market data by symbol

**Usage Context:** Convenient alternative when working with symbols rather than contract IDs.

---

#### 3.3 `marketdata_history_by_conid(conid: str, bar: str, exchange: str = None, period: str = None, outside_rth: bool = None, start_time: datetime = None)`
```python
def marketdata_history_by_conid(
    self: 'IbkrClient', 
    conid: str, 
    bar: str, 
    exchange: str = None, 
    period: str = None, 
    outside_rth: bool = None, 
    start_time: datetime = None
) -> Result
```

**Description:** Get historical market data for a given contract ID. Data length controlled by `period` and `bar` parameters.

**Parameters:**
- `conid` (str): Contract identifier.
- `bar` (str): Bar size. Common values: "1min", "5min", "1h", "1d"
- `exchange` (str, optional): Specific exchange.
- `period` (str, optional): Data duration. Common values: "1min", "1d", "1w", "1m"
- `outside_rth` (bool, optional): Include trades outside regular trading hours.
- `start_time` (datetime, optional): UTC start time. Format: "YYYYMMDD-HH:mm:ss"

**Returns:** `Result` - Historical OHLC data

**Usage Context:** Retrieve historical price data for technical analysis or backtesting.

---

#### 3.4 `marketdata_history_by_symbol(symbol: Union[str, StockQuery], bar: str, exchange: str = None, period: str = None, outside_rth: bool = None, start_time: datetime = None)`
```python
def marketdata_history_by_symbol(
    self: 'IbkrClient', 
    symbol: Union[str, StockQuery], 
    bar: str, 
    exchange: str = None, 
    period: str = None, 
    outside_rth: bool = None, 
    start_time: datetime = None
) -> Result
```

**Description:** Get historical market data by symbol instead of conid. Wrapper around `marketdata_history_by_conid()`.

**Parameters:** Same as `marketdata_history_by_conid()`, except first parameter is symbol/StockQuery.

**Returns:** `Result` - Historical OHLC data

**Usage Context:** Symbol-based alternative to conid-based historical data retrieval.

---

#### 3.5 `marketdata_history_by_conids(conids: Union[List[str], Dict], period: str = '1min', bar: str = '1min', outside_rth: bool = True, start_time: datetime = None, raise_on_error: bool = False, run_in_parallel: bool = True)`
```python
def marketdata_history_by_conids(
    self: 'IbkrClient', 
    conids: Union[List[str], Dict[Hashable, str]], 
    period: str = '1min', 
    bar: str = '1min', 
    outside_rth: bool = True, 
    start_time: datetime = None, 
    raise_on_error: bool = False, 
    run_in_parallel: bool = True
) -> dict
```

**Description:** Extended version for batch retrieval. Queries history for multiple conids, cleans up results, and returns unified data directly (not Result). **Parallel execution by default.**

**Parameters:**
- `conids` (Union[List[str], Dict]): Contract IDs or dict mapping to conids.
- `period` (str): Data duration. Default: '1min'
- `bar` (str): Bar size. Default: '1min'
- `outside_rth` (bool): Include after-hours data. Default: True
- `start_time` (datetime, optional): UTC start time.
- `raise_on_error` (bool): Whether to raise on individual failures. Default: False
- `run_in_parallel` (bool): Run requests in parallel. Default: True

**Returns:** `dict` - Unified, cleaned historical data

**Usage Context:** Efficient batch retrieval for multiple symbols with automatic cleanup.

---

#### 3.6 `marketdata_history_by_symbols(queries: Union[StockQuery, str, List[...]], period: str = '1min', bar: str = '1min', outside_rth: bool = True, start_time: datetime = None, raise_on_error: bool = False, run_in_parallel: bool = True)`
```python
def marketdata_history_by_symbols(
    self: 'IbkrClient', 
    queries: Union[StockQuery, str, List[Union[StockQuery, str]]], 
    period: str = '1min', 
    bar: str = '1min', 
    outside_rth: bool = True, 
    start_time: datetime = None, 
    raise_on_error: bool = False, 
    run_in_parallel: bool = True
) -> dict
```

**Description:** Extended version for batch retrieval by symbols. Queries history for multiple symbols, cleans up results, and returns unified data. **Parallel execution by default.**

**Parameters:** Same as `marketdata_history_by_conids()`, except accepts symbols/StockQuery objects.

**Returns:** `dict` - Unified, cleaned historical data

**Usage Context:** Convenient bulk historical data retrieval when working with symbol lists.

---

#### 3.7 `historical_marketdata_beta(conid: str, period: str, bar: str, outside_rth: bool = None, start_time: datetime = None, direction: str = None, bar_type: str = None)`
```python
def historical_marketdata_beta(
    self: 'IbkrClient', 
    conid: str, 
    period: str, 
    bar: str, 
    outside_rth: bool = None, 
    start_time: datetime = None, 
    direction: str = None, 
    bar_type: str = None
) -> Result
```

**Description:** Using a direct connection to the market data farm, provides historical market data (beta endpoint).

**Parameters:**
- `conid` (str): Contract identifier.
- `period` (str): Duration for requested data. See HMDS Period Units.
- `bar` (str): Bar size. See HMDS Bar Sizes.
- `outside_rth` (bool, optional): Include trades outside regular trading hours.
- `start_time` (datetime, optional): UTC start time. Format: "YYYYMMDD-HH:mm:ss"
- `direction` (str, optional): Data direction (forward/backward).
- `bar_type` (str, optional): Type of bars (e.g., "TRADES", "MIDPOINT").

**Returns:** `Result` - Historical market data from direct market data farm connection

**Usage Context:** Advanced/experimental alternative to standard historical data retrieval.

---

#### 3.8 `regulatory_snapshot(conid: str)`
```python
def regulatory_snapshot(self: 'IbkrClient', conid: str) -> Result
```

**Description:** Send a request for a regulatory snapshot. **⚠️ WARNING: Each regulatory snapshot incurs a $0.01 USD fee.**

**Parameters:**
- `conid` (str): Contract identifier.

**Returns:** `Result` - Regulatory snapshot data

**Usage Context:** Specialized use case; verify fee implications before use.

**⚠️ Important:** This applies to both live and paper accounts. Repeated calls can quickly accumulate fees.

---

#### 3.9 `marketdata_unsubscribe(conids: Union[str, List[str]])`
```python
def marketdata_unsubscribe(self: 'IbkrClient', conids: Union[str, List[str]]) -> List[Result]
```

**Description:** Cancel market data subscription for given contract ID(s).

**Parameters:**
- `conids` (Union[str, List[str]]): Contract identifier(s) to unsubscribe from.

**Returns:** `List[Result]` - Unsubscription results

**Usage Context:** Clean up subscriptions to reduce API load; clears cached market data feeds.

---

#### 3.10 `marketdata_unsubscribe_all()`
```python
def marketdata_unsubscribe_all(self: 'IbkrClient') -> Result
```

**Description:** Cancel all outstanding market data request(s). Alternative to specifying individual conids.

**Parameters:** None

**Returns:** `Result` - Unsubscription result

**Usage Context:** Bulk cleanup of all active subscriptions.

---

## 4. PortfolioMixin

**Purpose:** Retrieve portfolio positions, performance, and account information.

**Public API Data Retrieval Methods:** 16

### Method Signatures

#### 4.1 `portfolio_accounts()`
```python
def portfolio_accounts(self: 'IbkrClient') -> Result
```

**Description:** In non-tiered account structures, returns a list of accounts for which the user can view position and account information. **Must be called prior to other `/portfolio` endpoints.**

**Parameters:** None

**Returns:** `Result` - Account list

**Usage Context:** Initialization; required before accessing account-specific portfolio data.

---

#### 4.2 `portfolio_subaccounts()`
```python
def portfolio_subaccounts(self: 'IbkrClient') -> Result
```

**Description:** Used in tiered account structures (Financial Advisor, IBroker). Returns list of up to 100 sub-accounts for viewing position and account information. **Must be called prior to other `/portfolio` endpoints for sub-accounts.**

**Parameters:** None

**Returns:** `Result` - Sub-account list (max 100)

**Usage Context:** For tiered/FA account structures.

---

#### 4.3 `large_portfolio_subaccounts(page: int = 0)`
```python
def large_portfolio_subaccounts(self: 'IbkrClient', page: int = 0) -> Result
```

**Description:** Returns paginated list of sub-accounts (up to 20 per page) for tiered account structures with large numbers of sub-accounts.

**Parameters:**
- `page` (int): Page number (0-indexed). Default: 0

**Returns:** `Result` - Paginated sub-account list (max 20 per page)

**Usage Context:** For large FA/IBroker accounts exceeding 100 sub-accounts.

---

#### 4.4 `portfolio_account_information(account_id: str = None)`
```python
def portfolio_account_information(self: 'IbkrClient', account_id: str = None) -> Result
```

**Description:** Account information related to account ID. `/portfolio/accounts` or `/portfolio/subaccounts` must be called first.

**Parameters:**
- `account_id` (str, optional): Account ID to retrieve portfolio info for. If not specified, uses default.

**Returns:** `Result` - Account information

**Usage Context:** Get account-level portfolio metadata.

---

#### 4.5 `positions(account_id: str = None, page: int = 0, model: str = None, sort: str = None, direction: str = None, period: str = None)`
```python
def positions(
    self: 'IbkrClient', 
    account_id: str = None, 
    page: int = 0, 
    model: str = None, 
    sort: str = None, 
    direction: str = None, 
    period: str = None
) -> Result
```

**Description:** Returns a list of positions for the given account. Supports paging—each page returns up to 100 positions.

**Parameters:**
- `account_id` (str, optional): Account ID. If not specified, uses default.
- `page` (int): Page number (0-indexed). Default: 0
- `model` (str, optional): Sorting model.
- `sort` (str, optional): Field to sort by.
- `direction` (str, optional): Sort direction (asc/desc).
- `period` (str, optional): Time period for analysis.

**Returns:** `Result` - Paginated position list (max 100 per page)

**Usage Context:** Retrieve portfolio holdings with pagination support.

---

#### 4.6 `positions2(account_id: str = None, model: str = None, sort: str = None, direction: str = None)`
```python
def positions2(
    self: 'IbkrClient', 
    account_id: str = None, 
    model: str = None, 
    sort: str = None, 
    direction: str = None
) -> Result
```

**Description:** Returns positions without paging. `/portfolio/accounts` or `/portfolio/subaccounts` must be called first. Provides **near-real-time updates** with no caching, unlike `positions()`.

**Parameters:**
- `account_id` (str, optional): Account ID.
- `model` (str, optional): Sorting model.
- `sort` (str, optional): Field to sort by.
- `direction` (str, optional): Sort direction (asc/desc).

**Returns:** `Result` - All positions (no pagination)

**Usage Context:** Real-time position updates; preferred for smaller portfolios or when caching is undesirable.

---

#### 4.7 `positions_by_conid(account_id: str, conid: str)`
```python
def positions_by_conid(self: 'IbkrClient', account_id: str, conid: str) -> Result
```

**Description:** Returns position details **only for the specified contract ID**.

**Parameters:**
- `account_id` (str): Account ID (required).
- `conid` (str): Contract ID to retrieve position for.

**Returns:** `Result` - Position for specified contract

**Usage Context:** Retrieve position for a specific security quickly.

---

#### 4.8 `position_and_contract_info(conid: str)`
```python
def position_and_contract_info(self: 'IbkrClient', conid: str) -> Result
```

**Description:** Returns an object containing information about a given **position along with its contract details**.

**Parameters:**
- `conid` (str): Contract ID.

**Returns:** `Result` - Combined position + contract information

**Usage Context:** Single call to get both position and contract metadata.

---

#### 4.9 `portfolio_summary(account_id: str = None)`
```python
def portfolio_summary(self: 'IbkrClient', account_id: str = None) -> Result
```

**Description:** Information regarding settled cash, cash balances, etc. in the account's base currency and any other cash balances held in other currencies. `/portfolio/accounts` or `/portfolio/subaccounts` must be called first.

**Parameters:**
- `account_id` (str, optional): Account ID.

**Returns:** `Result` - Portfolio summary with cash balances

**Supported Currencies:** See https://www.interactivebrokers.com/en/index.php?f=3185

**Usage Context:** Get account cash and currency information.

---

#### 4.10 `get_ledger(account_id: str = None)`
```python
def get_ledger(self: 'IbkrClient', account_id: str = None) -> Result
```

**Description:** Information regarding settled cash, cash balances, etc. Similar to `portfolio_summary()`. `/portfolio/accounts` or `/portfolio/subaccounts` must be called first.

**Parameters:**
- `account_id` (str, optional): Account ID.

**Returns:** `Result` - Ledger information

**Supported Currencies:** See https://www.interactivebrokers.com/en/index.php?f=3185

**Usage Context:** Alias for detailed cash/ledger information.

---

#### 4.11 `portfolio_account_allocation(account_id: str = None)`
```python
def portfolio_account_allocation(self: 'IbkrClient', account_id: str = None) -> Result
```

**Description:** Portfolio allocation information by **Asset Class, Industry, and Category**. `/portfolio/accounts` or `/portfolio/subaccounts` must be called first.

**Parameters:**
- `account_id` (str, optional): Account ID.

**Returns:** `Result` - Allocation breakdown

**Usage Context:** Analyze portfolio diversification and asset allocation.

---

#### 4.12 `portfolio_account_allocations(account_ids: Union[str, List[str]])`
```python
def portfolio_account_allocations(self: 'IbkrClient', account_ids: Union[str, List[str]]) -> Result
```

**Description:** Similar to `portfolio_account_allocation()` but returns **consolidated view** for multiple accounts.

**Parameters:**
- `account_ids` (Union[str, List[str]]): Account ID(s).

**Returns:** `Result` - Consolidated allocation

**Usage Context:** Multi-account allocation analysis.

---

#### 4.13 `account_performance(account_ids: Union[str, List[str]], period: str)`
```python
def account_performance(self: 'IbkrClient', account_ids: Union[str, List[str]], period: str) -> Result
```

**Description:** Returns **Mark-to-Market (MTM) performance** for given accounts. If multiple accounts, result is **consolidated**.

**Parameters:**
- `account_ids` (Union[str, List[str]]): Account ID(s).
- `period` (str): Time period (e.g., "1d", "1w", "1m", "YTD").

**Returns:** `Result` - MTM performance data

**Usage Context:** Track account profitability over specific periods.

---

#### 4.14 `all_periods(account_ids: Union[str, List[str]])`
```python
def all_periods(self: 'IbkrClient', account_ids: Union[str, List[str]]) -> Result
```

**Description:** Returns **performance across all available time periods** for given accounts. Result **consolidated** if multiple accounts.

**Parameters:**
- `account_ids` (Union[str, List[str]]): Account ID(s).

**Returns:** `Result` - Performance data for all available periods

**Usage Context:** Comprehensive performance analysis across multiple timeframes.

---

#### 4.15 `combination_positions(account_id: str = None, no_cache: bool = False)`
```python
def combination_positions(self: 'IbkrClient', account_id: str = None, no_cache: bool = False) -> Result
```

**Description:** Provides all positions held in the account **acquired as a combination**, including values such as ratios, size, and market value.

**Parameters:**
- `account_id` (str, optional): Account ID.
- `no_cache` (bool): Bypass cache. Default: False

**Returns:** `Result` - Combination positions with metadata

**Usage Context:** Analyze complex multi-leg positions.

---

#### 4.16 `transaction_history(account_ids: Union[str, List[str]], conids: Union[str, List[str]], currency: str, days: int = None)`
```python
def transaction_history(
    self: 'IbkrClient', 
    account_ids: Union[str, List[str]], 
    conids: Union[str, List[str]], 
    currency: str, 
    days: int = None
) -> Result
```

**Description:** Transaction history for given conids and accounts. **Types:** dividend payments, buy/sell transactions, transfers.

**Parameters:**
- `account_ids` (Union[str, List[str]]): Account ID(s).
- `conids` (Union[str, List[str]]): Contract ID(s) to retrieve history for.
- `currency` (str): Currency code (e.g., "USD", "EUR").
- `days` (int, optional): Number of days of history to retrieve.

**Returns:** `Result` - Transaction list

**Usage Context:** Audit account activity and generate trade history reports.

---

#### 4.17 `invalidate_backend_portfolio_cache(account_id: str = None)`
```python
def invalidate_backend_portfolio_cache(self: 'IbkrClient', account_id: str = None) -> Result
```

**Description:** Invalidates cached portfolio data and automatically calls `/portfolio/{accountId}/positions/0`.

**Parameters:**
- `account_id` (str, optional): Account ID.

**Returns:** `Result` - Cache invalidation result

**Usage Context:** Force refresh of cached portfolio data for consistency.

---

## 5. WatchlistMixin

**Purpose:** Manage watchlists for monitoring specific contracts.

**Public API Data Retrieval Methods:** 4

### Method Signatures

#### 5.1 `get_all_watchlists(sc: str = 'USER_WATCHLIST')`
```python
def get_all_watchlists(self: 'IbkrClient', sc: str = 'USER_WATCHLIST') -> Result
```

**Description:** Retrieve a list of all available watchlists for the account.

**Parameters:**
- `sc` (str): Scope of the request. Valid values: "USER_WATCHLIST". Default: "USER_WATCHLIST"

**Returns:** `Result` - List of all watchlists

**Usage Context:** Enumerate available watchlists before retrieving specific data.

---

#### 5.2 `get_watchlist_information(id: str)`
```python
def get_watchlist_information(self: 'IbkrClient', id: str) -> Result
```

**Description:** Request the **contracts listed in a particular watchlist**.

**Parameters:**
- `id` (str): Watchlist ID to retrieve data for.

**Returns:** `Result` - Contracts in the watchlist

**Usage Context:** Retrieve detailed information about a specific watchlist's holdings.

---

#### 5.3 `create_watchlist(id: str, name: str, rows: List[Dict[str, Union[str, int]]])`
```python
def create_watchlist(
    self: 'IbkrClient', 
    id: str, 
    name: str, 
    rows: List[Dict[str, Union[str, int]]]
) -> Result
```

**Description:** Create a watchlist to monitor a series of contracts.

**Parameters:**
- `id` (str): Unique identifier to track the watchlist. Must be numeric.
- `name` (str): Human-readable name displayed in TWS and Client Portal.
- `rows` (List[Dict]): Details for each contract or blank space. Each object may include:
  - `C` (int): Contract ID (conid) to add
  - `H` (str): Blank row separator between contracts

**Returns:** `Result` - Creation result

**Usage Context:** Programmatically create custom watchlists.

**Example:**
```python
rows = [
    {'C': 265598},  # AAPL
    {'C': 272093},  # MSFT
    {'H': ''},      # Blank row
    {'C': 108602},  # GOOGL
]
client.create_watchlist(id='1', name='Tech Stocks', rows=rows)
```

---

#### 5.4 `delete_watchlist(id: str)`
```python
def delete_watchlist(self: 'IbkrClient', id: str) -> Result
```

**Description:** Permanently delete a specific watchlist for all platforms.

**Parameters:**
- `id` (str): Watchlist ID to delete.

**Returns:** `Result` - Deletion result

**Usage Context:** Remove unwanted watchlists.

---

## Summary Table

| Mixin | Method | Data Type | Key Parameters |
|-------|--------|-----------|-----------------|
| **AccountsMixin** | `receive_brokerage_accounts()` | Accounts | None |
| | `search_dynamic_account()` | Dynamic Accounts | pattern |
| **ContractMixin** | `search_contract_by_symbol()` | Contracts | symbol, name, sec_type |
| | `search_secdef_info_by_conid()` | Contract Details | conid, sec_type, month, strike, right |
| | `search_strikes_by_conid()` | Strike Prices | conid, sec_type, month |
| | `search_contract_rules()` | Trading Rules | conid, exchange, is_buy |
| | `search_bond_filter_information()` | Bond Filters | symbol, issuer_id |
| **MarketdataMixin** | `live_marketdata_snapshot()` | Live Prices | conids, fields |
| | `live_marketdata_snapshot_by_symbol()` | Live Prices (Symbols) | queries, fields |
| | `marketdata_history_by_conid()` | OHLC Data | conid, bar, period |
| | `marketdata_history_by_symbol()` | OHLC Data (Symbols) | symbol, bar, period |
| | `marketdata_history_by_conids()` | Batch OHLC | conids, bar, period |
| | `marketdata_history_by_symbols()` | Batch OHLC (Symbols) | queries, bar, period |
| | `historical_marketdata_beta()` | Historical Data (Beta) | conid, period, bar |
| | `regulatory_snapshot()` | Regulatory Data | conid |
| | `marketdata_unsubscribe()` | Subscription Cancel | conids |
| | `marketdata_unsubscribe_all()` | Bulk Cancel | None |
| **PortfolioMixin** | `portfolio_accounts()` | Accounts | None |
| | `portfolio_subaccounts()` | Sub-accounts | None |
| | `large_portfolio_subaccounts()` | Paginated Sub-accounts | page |
| | `portfolio_account_information()` | Account Info | account_id |
| | `positions()` | Positions (Paginated) | account_id, page |
| | `positions2()` | Positions (Real-time) | account_id |
| | `positions_by_conid()` | Position (Single) | account_id, conid |
| | `position_and_contract_info()` | Position + Contract | conid |
| | `portfolio_summary()` | Summary/Cash | account_id |
| | `get_ledger()` | Ledger | account_id |
| | `portfolio_account_allocation()` | Allocation | account_id |
| | `portfolio_account_allocations()` | Multi-Account Allocation | account_ids |
| | `account_performance()` | MTM Performance | account_ids, period |
| | `all_periods()` | Performance (All Periods) | account_ids |
| | `combination_positions()` | Combination Positions | account_id |
| | `transaction_history()` | Transactions | account_ids, conids, currency |
| | `invalidate_backend_portfolio_cache()` | Cache Control | account_id |
| **WatchlistMixin** | `get_all_watchlists()` | Watchlist List | sc |
| | `get_watchlist_information()` | Watchlist Contracts | id |
| | `create_watchlist()` | Create Watchlist | id, name, rows |
| | `delete_watchlist()` | Delete Watchlist | id |

---

## Usage Patterns

### 1. **Basic Market Data Flow**
```python
client = IbkrClient()

# Get accounts
accounts = client.receive_brokerage_accounts()

# Search for contract
contracts = client.search_contract_by_symbol('AAPL')
conid = contracts.data[0]['conid']

# Get live market data
snapshot = client.live_marketdata_snapshot(conids=conid, fields=['31', '66', '68'])

# Get historical data
history = client.marketdata_history_by_conid(conid, bar='1d', period='1w')
```

### 2. **Portfolio Analysis**
```python
# Retrieve account structure
accounts = client.portfolio_accounts()
positions = client.positions(account_id='accounts[0]')

# Get allocation and performance
allocation = client.portfolio_account_allocation()
performance = client.account_performance(account_ids='account_id', period='1m')

# Check ledger
ledger = client.get_ledger()
```

### 3. **Options Research**
```python
# Find options for an underlying
contracts = client.search_contract_by_symbol('SPY', sec_type='OPT')

# Get available strikes
strikes = client.search_strikes_by_conid(conid='756033', sec_type='OPT', month='DEC23')

# Get detailed contract info for specific option
details = client.search_secdef_info_by_conid(
    conid='...', 
    sec_type='OPT', 
    month='DEC23',
    strike='400',
    right='C'
)
```

### 4. **Watchlist Management**
```python
# Get all watchlists
all_lists = client.get_all_watchlists()

# Get contracts in a watchlist
watchlist = client.get_watchlist_information(id='1')

# Create new watchlist
rows = [
    {'C': 265598},   # AAPL
    {'C': 272093},   # MSFT
]
client.create_watchlist(id='2', name='My Stocks', rows=rows)
```

---

## Key Considerations

1. **Initialization Order:** Several endpoints require prerequisites:
   - `portfolio_*` methods require calling `portfolio_accounts()` or `portfolio_subaccounts()` first
   - Contract derivative searches require calling `search_contract_by_symbol()` before `search_secdef_info_by_conid()`

2. **Parallel Processing:** Batch methods like `marketdata_history_by_conids()` and `marketdata_history_by_symbols()` support parallel execution by default for efficiency.

3. **Caching:** Some endpoints (like `positions()`) use caching; use `positions2()` for real-time data or `invalidate_backend_portfolio_cache()` to force refresh.

4. **Rate Limiting:** Historical market data and snapshots may be subject to rate limits; use batch methods with parallel=False if experiencing rate limit issues.

5. **Fee Implications:** `regulatory_snapshot()` charges $0.01 per call on both live and paper accounts.

---

## Version Info
- **Package:** ibind
- **Analysis Date:** December 18, 2025
- **Python Version:** 3.13.7
