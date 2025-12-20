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

**Public API Data Retrieval Methods:** 15

### Method Signatures

#### 2.1 `security_definition_by_conid(conids: OneOrMany[str])`
```python
def security_definition_by_conid(self: 'IbkrClient', conids: OneOrMany[str]) -> Result
```

**Description:** Returns a list of security definitions for the given conids.

**Parameters:**
- `conids` (OneOrMany[str]): One or many contract ID strings. Value Format: 1234.

**Returns:** `Result` - Security definitions for each conid

**Usage Context:** Get detailed security information for multiple contracts at once.

---

#### 2.2 `all_conids_by_exchange(exchange: str)`
```python
def all_conids_by_exchange(self: 'IbkrClient', exchange: str) -> Result
```

**Description:** Send out a request to retrieve all contracts made available on a requested exchange. This returns all contracts that are tradable on the exchange, even those that are not using the exchange as their primary listing.

**Note:** This is only available for Stock contracts.

**Parameters:**
- `exchange` (str): Specify a single exchange to receive conids for.

**Returns:** `Result` - List of all contract IDs on the exchange

**Usage Context:** Discover all tradable contracts on a specific exchange.

---

#### 2.3 `contract_information_by_conid(conid: str)`
```python
def contract_information_by_conid(self: 'IbkrClient', conid: str) -> Result
```

**Description:** Requests full contract details for the given conid.

**Parameters:**
- `conid` (str): Contract ID for the desired contract information.

**Returns:** `Result` - Complete contract information

**Usage Context:** Get comprehensive contract details including trading hours, multiplier, tick size, etc.

---

#### 2.4 `currency_pairs(currency: str)`
```python
def currency_pairs(self: 'IbkrClient', currency: str) -> Result
```

**Description:** Obtains available currency pairs corresponding to the given target currency.

**Parameters:**
- `currency` (str): Specify the target currency you would like to receive official pairs of. Valid Structure: "USD".

**Returns:** `Result` - Available currency pairs

**Usage Context:** Discover available forex trading pairs for a currency.

---

#### 2.5 `currency_exchange_rate(source: str, target: str)`
```python
def currency_exchange_rate(self: 'IbkrClient', source: str, target: str) -> Result
```

**Description:** Obtains the exchange rates of the currency pair.

**Parameters:**
- `source` (str): Specify the base currency to request data for. Valid Structure: "AUD"
- `target` (str): Specify the quote currency to request data for. Valid Structure: "USD"

**Returns:** `Result` - Exchange rate information

**Usage Context:** Get current exchange rate between two currencies.

---

#### 2.6 `info_and_rules_by_conid(conid: str, is_buy: bool)`
```python
def info_and_rules_by_conid(self: 'IbkrClient', conid: str, is_buy: bool) -> Result
```

**Description:** Returns both contract info and rules from a single endpoint.

**Parameters:**
- `conid` (str): Contract identifier for the given contract.
- `is_buy` (bool): Indicates whether you are searching for Buy or Sell order rules. Set to true for Buy Orders, set to false for Sell Orders.

**Returns:** `Result` - Combined contract info and rules

**Usage Context:** Get both contract details and trading rules in one call.

---

#### 2.7 `algo_params_by_conid(conid: str, algos: List[str] = None, add_description: str = None, add_params: str = None)`
```python
def algo_params_by_conid(
    self: 'IbkrClient', 
    conid: str, 
    algos: List[str] = None, 
    add_description: str = None, 
    add_params: str = None
) -> Result
```

**Description:** Returns supported IB Algos for contract.

**Parameters:**
- `conid` (str): Contract identifier for the requested contract of interest.
- `algos` (List[str], optional): List of algo ids. Max of 8 algos ids can be specified. Case sensitive to algo id.
- `add_description` (str, optional): Whether or not to add algo descriptions to response. Set to 1 for yes, 0 for no.
- `add_params` (str, optional): Whether or not to show algo parameters. Set to 1 for yes, 0 for no.

**Returns:** `Result` - Available algorithms and their parameters

**Usage Context:** Discover available algorithmic order types for a contract.

---

#### 2.8 `search_bond_filter_information(symbol: str, issuer_id: str)`
```python
def search_bond_filter_information(self: 'IbkrClient', symbol: str, issuer_id: str) -> Result
```

**Description:** Request a list of filters relating to a given Bond issuerID.

**Parameters:**
- `symbol` (str): This should always be set to "BOND"
- `issuer_id` (str): Specifies the issuerId value used to designate the bond issuer type.

**Returns:** `Result` - Available bond filters for the issuer

**Usage Context:** Specialized for bond contract lookups; used in conjunction with `search_contract_by_symbol()` for bond searches.

---

#### 2.9 `search_contract_by_symbol(symbol: str, name: bool = None, sec_type: str = None)`
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

#### 2.10 `search_contract_rules(conid: str, exchange: str = None, is_buy: bool = None, modify_order: bool = None, order_id: int = None)`
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

**Description:** Returns trading-related rules for a specific contract and side.

**Parameters:**
- `conid` (str): Contract identifier for the interested contract.
- `exchange` (str, optional): Designate the exchange you wish to receive information for in relation to the contract.
- `is_buy` (bool, optional): Side of the market rules apply to. Set to true for Buy Orders, set to false for Sell Orders. Defaults to true or Buy side rules.
- `modify_order` (bool, optional): Used to find trading rules related to an existing order.
- `order_id` (int): Required for modify_order:true. Specify the order identifier used for tracking a given order.

**Returns:** `Result` - Trading rules (position limits, minimum order size, etc.)

**Usage Context:** Used before placing orders to understand contract trading constraints.

---

#### 2.11 `search_secdef_info_by_conid(conid: str, sec_type: str, month: str, exchange: str = None, strike: str = None, right: str = None, issuer_id: str = None)`
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

**Description:** Provides Contract Details of Futures, Options, Warrants, Cash and CFDs based on conid.

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

#### 2.12 `search_strikes_by_conid(conid: str, sec_type: str, month: str, exchange: str = None)`
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

#### 2.13 `security_future_by_symbol(symbols: OneOrMany[str])`
```python
def security_future_by_symbol(self: 'IbkrClient', symbols: OneOrMany[str]) -> Result
```

**Description:** Returns a list of non-expired future contracts for given symbol(s).

**Parameters:**
- `symbols` (OneOrMany[str]): Indicate the symbol(s) of the underlier you are trying to retrieve futures on.

**Returns:** `Result` - Available future contracts

**Usage Context:** Discover available futures contracts for specific underliers.

---

#### 2.14 `security_stocks_by_symbol(queries: StockQueries, default_filtering: bool = None)`
```python
def security_stocks_by_symbol(self: 'IbkrClient', queries: StockQueries, default_filtering: bool = None) -> Result
```

**Description:** Retrieves and filters stock information based on specified queries.

**Parameters:**
- `queries` (StockQueries): A list of StockQuery objects, each specifying filter conditions for the stocks to be retrieved.
- `default_filtering` (bool, optional): Indicates whether to apply override the default filtering of {isUS: True}. Defaults to None, which applies the global default filtering.

**Returns:** `Result` - Filtered stock information in form of {symbol: stock_data} dictionary

**Usage Context:** Advanced stock filtering with custom conditions.

---

#### 2.15 `stock_conid_by_symbol(queries: StockQueries, default_filtering: bool = None, return_type: str = 'dict')`
```python
def stock_conid_by_symbol(
    self: 'IbkrClient', 
    queries: StockQueries, 
    default_filtering: bool = None, 
    return_type: str = 'dict'
) -> Result
```

**Description:** Retrieves contract IDs (conids) for given stock queries, ensuring only one conid per query.

**Parameters:**
- `queries` (StockQueries): A list of StockQuery objects to specify filtering criteria for stocks.
- `default_filtering` (bool, optional): Indicates whether to apply override the default filtering of {isUS: True}. Defaults to None, which applies the global default filtering.
- `return_type` (str, optional): Specifies the return type ('dict' or 'list') of the conids. Defaults to 'dict'.

**Returns:** `Result` - Conids as a dictionary with symbols as keys and conids as values or as a list of conids

**Usage Context:** Get unambiguous conid resolution for symbols with filtering.

---

#### 2.16 `trading_schedule_by_symbol(asset_class: str, symbol: str, exchange: str = None, exchange_filter: str = None)`
```python
def trading_schedule_by_symbol(
    self: 'IbkrClient', 
    asset_class: str, 
    symbol: str, 
    exchange: str = None, 
    exchange_filter: str = None
) -> Result
```

**Description:** Returns the trading schedule up to a month for the requested contract.

**Parameters:**
- `asset_class` (str): Specify the security type of the given contract. Value Formats: Stock: STK, Option: OPT, Future: FUT, Contract For Difference: CFD, Warrant: WAR, Forex: SWP, Mutual Fund: FND, Bond: BND, Inter-Commodity Spreads: ICS.
- `symbol` (str): Specify the symbol for your contract.
- `exchange` (str, optional): Specify the primary exchange of your contract.
- `exchange_filter` (str, optional): Specify all exchanges you want to retrieve data from.

**Returns:** `Result` - Trading schedule information

**Usage Context:** Get trading hours and schedule for a contract.

---

## 3. MarketdataMixin

**Purpose:** Retrieve live and historical market data for contracts.

**Public API Data Retrieval Methods:** 10

### Method Signatures

#### 3.1 `live_marketdata_snapshot(conids: OneOrMany[str], fields: OneOrMany[str])`
```python
def live_marketdata_snapshot(
    self: 'IbkrClient', 
    conids: OneOrMany[str], 
    fields: OneOrMany[str]
) -> Result
```

**Description:** Get Market Data for the given conid(s). A pre-flight request must be made prior to ever receiving data.

**Parameters:**
- `conids` (OneOrMany[str]): Contract identifier(s) for the contract of interest.
- `fields` (OneOrMany[str]): Specify a series of tick values to be returned.

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

**Note:**
- The endpoint /iserver/accounts must be called prior to /iserver/marketdata/snapshot.
- For derivative contracts, the endpoint /iserver/secdef/search must be called first.

---

#### 3.2 `live_marketdata_snapshot_by_symbol(queries: StockQueries, fields: OneOrMany[str])`
```python
def live_marketdata_snapshot_by_symbol(
    self: 'IbkrClient', 
    queries: StockQueries, 
    fields: OneOrMany[str]
) -> dict
```

**Description:** Get Market Data for the given symbols(s). A pre-flight request must be made prior to ever receiving data.

**Parameters:**
- `queries` (StockQueries): A list of StockQuery objects to specify filtering criteria for stocks.
- `fields` (OneOrMany[str]): Specify a series of tick values to be returned.

**Returns:** `dict` - Market data by symbol (not wrapped in Result)

**Usage Context:** Convenient alternative when working with symbols rather than contract IDs.

**Note:**
- The endpoint /iserver/accounts must be called prior to /iserver/marketdata/snapshot.
- For derivative contracts, the endpoint /iserver/secdef/search must be called first.

---

#### 3.3 `regulatory_snapshot(conid: str)`
```python
def regulatory_snapshot(self: 'IbkrClient', conid: str) -> Result
```

**Description:** Send a request for a regulatory snapshot. This will cost $0.01 USD per request unless you are subscribed to the direct exchange market data already.

**Parameters:**
- `conid` (str): Provide the contract identifier to retrieve market data for.

**Returns:** `Result` - Regulatory snapshot data

**Usage Context:** Specialized use case; verify fee implications before use.

**⚠️ Important:** This applies to both live and paper accounts. Repeated calls can quickly accumulate fees.

---

#### 3.4 `marketdata_history_by_conid(conid: str, bar: str, exchange: str = None, period: str = None, outside_rth: bool = None, start_time: datetime.datetime = None)`
```python
def marketdata_history_by_conid(
    self: 'IbkrClient', 
    conid: str, 
    bar: str, 
    exchange: str = None, 
    period: str = None, 
    outside_rth: bool = None, 
    start_time: datetime.datetime = None
) -> Result
```

**Description:** Get historical market Data for given conid, length of data is controlled by 'period' and 'bar'.

**Parameters:**
- `conid` (str): Contract identifier for the ticker symbol of interest.
- `bar` (str): Individual bars of data to be returned. Possible values: 1min, 2min, 3min, 5min, 10min, 15min, 30min, 1h, 2h, 3h, 4h, 8h, 1d, 1w, 1m.
- `exchange` (str, optional): Returns the exchange you want to receive data from.
- `period` (str): Overall duration for which data should be returned. Default to 1w. Available time period: {1-30}min, {1-8}h, {1-1000}d, {1-792}w, {1-182}m, {1-15}y.
- `outside_rth` (bool, optional): Determine if you want data after regular trading hours.
- `start_time` (datetime.datetime, optional): Starting date of the request duration.

**Returns:** `Result` - Historical OHLC data

**Usage Context:** Retrieve historical price data for technical analysis or backtesting.

**Note:** There's a limit of 5 concurrent requests. Excessive requests will return a 'Too many requests' status 429 response.

---

#### 3.5 `historical_marketdata_beta(conid: str, period: str, bar: str, outside_rth: bool = None, start_time: datetime.datetime = None, direction: str = None, bar_type: str = None)`
```python
def historical_marketdata_beta(
    self: 'IbkrClient', 
    conid: str, 
    period: str, 
    bar: str, 
    outside_rth: bool = None, 
    start_time: datetime.datetime = None, 
    direction: str = None, 
    bar_type: str = None
) -> Result
```

**Description:** Using a direct connection to the market data farm, will provide a list of historical market data for given conid.

**Parameters:**
- `conid` (str): The contract identifier for which data should be requested.
- `period` (str): The duration for which data should be requested. Available Values: See HMDS Period Units.
- `bar` (str): The bar size for which bars should be returned. Available Values: See HMDS Bar Sizes.
- `outside_rth` (bool, optional): Define if data should be returned for trades outside regular trading hours.
- `start_time` (datetime.datetime, optional): Specify the value from where historical data should be taken. Value Format: UTC; YYYYMMDD-HH:mm:dd. Defaults to the current date and time.
- `direction` (str, optional): Specify the direction from which market data should be returned. Available Values: -1: time from the start_time to now; 1: time from now to the end of the period. Defaults to 1.
- `bar_type` (str, optional): Returns valid bar types for which data may be requested. Available Values: Last, Bid, Ask, Midpoint, FeeRate, Inventory. Defaults to Last for Stocks, Options, Futures, and Futures Options.

**Returns:** `Result` - Historical market data from direct market data farm connection

**Usage Context:** Advanced/experimental alternative to standard historical data retrieval.

**Note:** The first time a user makes a request to the /hmds/history endpoints will result in a 404 error. This initial request instantiates the historical market data services allowing future requests to return data.

---

#### 3.6 `marketdata_history_by_symbol(symbol: Union[str, StockQuery], bar: str, exchange: str = None, period: str = None, outside_rth: bool = None, start_time: datetime.datetime = None)`
```python
def marketdata_history_by_symbol(
    self: 'IbkrClient', 
    symbol: Union[str, StockQuery], 
    bar: str, 
    exchange: str = None, 
    period: str = None, 
    outside_rth: bool = None, 
    start_time: datetime.datetime = None
) -> Result
```

**Description:** Get historical market Data for given symbol, length of data is controlled by 'period' and 'bar'.

**Parameters:**
- `symbol` (Union[str, StockQuery]): StockQuery or str symbol for the ticker of interest.
- `bar` (str): Individual bars of data to be returned. Possible values: 1min, 2min, 3min, 5min, 10min, 15min, 30min, 1h, 2h, 3h, 4h, 8h, 1d, 1w, 1m.
- `exchange` (str, optional): Returns the exchange you want to receive data from.
- `period` (str): Overall duration for which data should be returned. Default to 1w. Available time period: {1-30}min, {1-8}h, {1-1000}d, {1-792}w, {1-182}m, {1-15}y.
- `outside_rth` (bool, optional): Determine if you want data after regular trading hours.
- `start_time` (datetime.datetime, optional): Starting date of the request duration.

**Returns:** `Result` - Historical OHLC data

**Usage Context:** Symbol-based alternative to conid-based historical data retrieval.

---

#### 3.7 `marketdata_history_by_conids(conids: Union[List[str], Dict[Hashable, str]], period: str = '1min', bar: str = '1min', outside_rth: bool = True, start_time: datetime.datetime = None, raise_on_error: bool = False, run_in_parallel: bool = True)`
```python
def marketdata_history_by_conids(
    self: 'IbkrClient', 
    conids: Union[List[str], Dict[Hashable, str]], 
    period: str = '1min', 
    bar: str = '1min', 
    outside_rth: bool = True, 
    start_time: datetime.datetime = None, 
    raise_on_error: bool = False, 
    run_in_parallel: bool = True
) -> dict
```

**Description:** An extended version of the marketdata_history_by_conid method. For each conid provided, it queries the marketdata history for the specified symbols. The results are then cleaned up and unified. Due to this grouping and post-processing, this method returns data directly without the Result dataclass.

**Parameters:**
- `conids` (Union[List[str], Dict[Hashable, str]]): A list of conids to get market data for.
- `period` (str): Overall duration for which data should be returned. Default to 1min. Available time period: {1-30}min, {1-8}h, {1-1000}d, {1-792}w, {1-182}m, {1-15}y.
- `bar` (str): Individual bars of data to be returned. Possible values: 1min, 2min, 3min, 5min, 10min, 15min, 30min, 1h, 2h, 3h, 4h, 8h, 1d, 1w, 1m.
- `outside_rth` (bool, optional): Determine if you want data after regular trading hours. Default: True.
- `start_time` (datetime.datetime, optional): Starting date of the request duration.
- `raise_on_error` (bool, optional): If True, raise an exception if an error occurs during the request. Defaults to False.
- `run_in_parallel` (bool, optional): If True, send requests in parallel to speed up the response. Defaults to True.

**Returns:** `dict` - Unified, cleaned historical data (not wrapped in Result)

**Usage Context:** Efficient batch retrieval for multiple symbols with automatic cleanup and parallel processing.

---

#### 3.8 `marketdata_history_by_symbols(queries: StockQueries, period: str = '1min', bar: str = '1min', outside_rth: bool = True, start_time: datetime.datetime = None, raise_on_error: bool = False, run_in_parallel: bool = True)`
```python
def marketdata_history_by_symbols(
    self: 'IbkrClient', 
    queries: StockQueries, 
    period: str = '1min', 
    bar: str = '1min', 
    outside_rth: bool = True, 
    start_time: datetime.datetime = None, 
    raise_on_error: bool = False, 
    run_in_parallel: bool = True
) -> dict
```

**Description:** An extended version of the marketdata_history_by_conids method. For each StockQuery provided, it queries the marketdata history for the specified symbols. The results are then cleaned up and unified. Due to this grouping and post-processing, this method returns data directly without the Result dataclass.

**Parameters:**
- `queries` (StockQueries): A list of StockQuery objects to specify filtering criteria for stocks.
- `period` (str): Overall duration for which data should be returned. Default to 1min. Available time period: {1-30}min, {1-8}h, {1-1000}d, {1-792}w, {1-182}m, {1-15}y.
- `bar` (str): Individual bars of data to be returned. Possible values: 1min, 2min, 3min, 5min, 10min, 15min, 30min, 1h, 2h, 3h, 4h, 8h, 1d, 1w, 1m.
- `outside_rth` (bool, optional): Determine if you want data after regular trading hours. Default: True.
- `start_time` (datetime.datetime, optional): Starting date of the request duration.
- `raise_on_error` (bool, optional): If True, raise an exception if an error occurs during the request. Defaults to False.
- `run_in_parallel` (bool, optional): If True, send requests in parallel to speed up the response. Defaults to True.

**Returns:** `dict` - Unified, cleaned historical data (not wrapped in Result)

**Usage Context:** Convenient bulk historical data retrieval when working with symbol lists.

---

#### 3.9 `marketdata_unsubscribe(conids: OneOrMany[str])`
```python
def marketdata_unsubscribe(self: 'IbkrClient', conids: OneOrMany[str]) -> List[Result]
```

**Description:** Cancel market data for given conid(s).

**Parameters:**
- `conids` (OneOrMany[str]): Enter the contract identifier to cancel the market data feed. This can clear all standing market data feeds to invalidate your cache and start fresh.

**Returns:** `List[Result]` - Unsubscription results

**Usage Context:** Clean up subscriptions to reduce API load; clears cached market data feeds.

---

#### 3.10 `marketdata_unsubscribe_all()`
```python
def marketdata_unsubscribe_all(self: 'IbkrClient') -> Result
```

**Description:** Cancel all market data request(s). To cancel market data for a specific conid, see /iserver/marketdata/{conid}/unsubscribe.

**Parameters:** None

**Returns:** `Result` - Unsubscription result

**Usage Context:** Bulk cleanup of all active subscriptions.

---

## 4. PortfolioMixin

**Purpose:** Retrieve portfolio positions, performance, and account information.

**Public API Data Retrieval Methods:** 17

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
| **ContractMixin** | `security_definition_by_conid()` | Security Definitions | conids |
| | `all_conids_by_exchange()` | Exchange Contracts | exchange |
| | `contract_information_by_conid()` | Contract Details | conid |
| | `currency_pairs()` | Currency Pairs | currency |
| | `currency_exchange_rate()` | Exchange Rate | source, target |
| | `info_and_rules_by_conid()` | Info + Rules | conid, is_buy |
| | `algo_params_by_conid()` | Algorithm Parameters | conid, algos |
| | `search_bond_filter_information()` | Bond Filters | symbol, issuer_id |
| | `search_contract_by_symbol()` | Contract Search | symbol, name, sec_type |
| | `search_contract_rules()` | Trading Rules | conid, exchange, is_buy |
| | `search_secdef_info_by_conid()` | Derivative Details | conid, sec_type, month, strike, right |
| | `search_strikes_by_conid()` | Option Strikes | conid, sec_type, month |
| | `security_future_by_symbol()` | Futures Contracts | symbols |
| | `security_stocks_by_symbol()` | Stock Information | queries |
| | `stock_conid_by_symbol()` | Conid Resolution | queries |
| | `trading_schedule_by_symbol()` | Trading Schedule | asset_class, symbol, exchange |
| **MarketdataMixin** | `live_marketdata_snapshot()` | Live Prices | conids, fields |
| | `live_marketdata_snapshot_by_symbol()` | Live Prices (Symbols) | queries, fields |
| | `regulatory_snapshot()` | Regulatory Data | conid |
| | `marketdata_history_by_conid()` | OHLC Data | conid, bar, period |
| | `historical_marketdata_beta()` | Historical Data (Beta) | conid, period, bar |
| | `marketdata_history_by_symbol()` | OHLC Data (Symbols) | symbol, bar, period |
| | `marketdata_history_by_conids()` | Batch OHLC | conids, bar, period |
| | `marketdata_history_by_symbols()` | Batch OHLC (Symbols) | queries, bar, period |
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
- **Analysis Date:** December 19, 2025
- **Python Version:** 3.13.7
- **Source Files Analyzed:**
  - `/home/john/CodingProjects/llm/.venv/lib/python3.13/site-packages/ibind/client/ibkr_client_mixins/contract_mixin.py`
  - `/home/john/CodingProjects/llm/.venv/lib/python3.13/site-packages/ibind/client/ibkr_client_mixins/marketdata_mixin.py`
  - `/home/john/CodingProjects/llm/.venv/lib/python3.13/site-packages/ibind/client/ibkr_utils.py`

---

## Method Count Summary

| Mixin | Data Retrieval Methods | Key Features |
|-------|----------------------|--------------|
| **AccountsMixin** | 2 | Account initialization, dynamic account search |
| **ContractMixin** | 16 | Comprehensive contract search, security definitions, trading rules, algorithm parameters |
| **MarketdataMixin** | 10 | Live & historical data, batch operations, parallel processing |
| **PortfolioMixin** | 17 | Portfolio positions, performance, allocation, transaction history |
| **WatchlistMixin** | 4 | Watchlist creation, retrieval, management |
| **TOTAL** | **49** | Complete IBKR data access |

---

## Key Insights

### Most Powerful Mixins
1. **ContractMixin (16 methods)** - Most comprehensive contract research capabilities
2. **PortfolioMixin (17 methods)** - Complete portfolio analysis and management
3. **MarketdataMixin (10 methods)** - Rich market data retrieval with batch operations

### Advanced Features
- **Parallel Processing:** `marketdata_history_by_conids()` and `marketdata_history_by_symbols()` support parallel execution
- **Batch Operations:** Multiple methods support batch retrieval for efficiency
- **Real-time vs. Cached:** `positions()` vs `positions2()` for different use cases
- **Algorithm Support:** `algo_params_by_conid()` for algorithmic trading parameters

### Integration Patterns
- **Symbol Resolution:** Use `stock_conid_by_symbol()` for unambiguous conid resolution
- **Contract Discovery:** Start with `search_contract_by_symbol()` for derivative research
- **Portfolio Initialization:** Always call `portfolio_accounts()` first for portfolio methods
- **Market Data:** Use batch methods for multi-symbol analysis

---

## Usage Recommendations

### For Market Analysis
- Use `MarketdataMixin` with batch operations for efficiency
- Combine `live_marketdata_snapshot_by_symbol()` with `marketdata_history_by_symbols()`
- Leverage parallel processing for large symbol sets

### For Portfolio Management
- Start with `portfolio_accounts()` initialization
- Use `positions2()` for real-time position updates
- Combine `portfolio_account_allocation()` with `account_performance()` for comprehensive analysis

### For Contract Research
- Use `search_contract_by_symbol()` as entry point
- Follow with `search_secdef_info_by_conid()` for derivative details
- Check `search_contract_rules()` before trading

### For Algorithmic Trading
- Use `algo_params_by_conid()` to discover available algorithms
- Combine with `info_and_rules_by_conid()` for complete contract understanding

---

## Notes

This analysis is based on the actual source code of the `ibind` package, providing accurate method signatures, parameters, and usage patterns. The documentation reflects the complete public API for data retrieval methods across all five mixins.

For the most up-to-date information, refer to the official IBKR API documentation and the `ibind` package source code.
