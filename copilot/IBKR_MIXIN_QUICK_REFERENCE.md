# IBKR Client Mixin Summary - Quick Reference

## Executive Summary

This document provides a quick reference for the **5 primary IBKR client mixins** and their data retrieval capabilities. A comprehensive analysis is available in `IBKR_MIXIN_ANALYSIS.md`.

---

## Mixin Overview

| Mixin | Methods | Primary Purpose | Common Use Cases |
|-------|---------|-----------------|------------------|
| **AccountsMixin** | 2 | Account/credential retrieval | Get available accounts, search dynamic accounts |
| **ContractMixin** | 5 | Contract/instrument search | Find contracts, get contract details, bond lookups |
| **MarketdataMixin** | 10 | Live & historical market data | Get prices, OHLC data, market snapshots |
| **PortfolioMixin** | 17 | Portfolio positions & performance | Track holdings, get account allocations, performance metrics |
| **WatchlistMixin** | 4 | Watchlist management | Create/retrieve watchlists, organize favorites |
| | **TOTAL** | **38** | | |

---

## 1. AccountsMixin (2 Methods)

### Data Retrieval Methods:
1. **`receive_brokerage_accounts()`** → List of accessible accounts and aliases
2. **`search_dynamic_account(pattern)`** → Dynamic account search (for FA accounts)

### Key Use Case:
Get the list of available trading accounts before accessing other endpoints.

---

## 2. ContractMixin (5 Methods)

### Data Retrieval Methods:
1. **`search_contract_by_symbol(symbol, name=False, sec_type=None)`** → Find contracts by symbol/name
2. **`search_secdef_info_by_conid(conid, sec_type, month, ...)`** → Get detailed contract specifications
3. **`search_strikes_by_conid(conid, sec_type, month, ...)`** → List available option/warrant strikes
4. **`search_contract_rules(conid, ...)`** → Trading rules (position limits, minimums)
5. **`search_bond_filter_information(symbol, issuer_id)`** → Bond-specific filters

### Key Use Case:
Search for instruments and retrieve trading rules before placing orders.

---

## 3. MarketdataMixin (10 Methods)

### Live Market Data (3 methods):
1. **`live_marketdata_snapshot(conids, fields)`** → Current prices by contract ID
2. **`live_marketdata_snapshot_by_symbol(symbols, fields)`** → Current prices by symbol
3. **`regulatory_snapshot(conid)`** → Regulatory data ($0.01 per call ⚠️)

### Historical Data (5 methods):
4. **`marketdata_history_by_conid(conid, bar, period, ...)`** → OHLC data for one contract
5. **`marketdata_history_by_symbol(symbol, bar, period, ...)`** → OHLC data by symbol
6. **`marketdata_history_by_conids(conids, bar, period, ...)`** → Batch OHLC (parallel)
7. **`marketdata_history_by_symbols(symbols, bar, period, ...)`** → Batch OHLC by symbols (parallel)
8. **`historical_marketdata_beta(conid, period, bar, ...)`** → Beta endpoint for historical data

### Subscription Management (2 methods):
9. **`marketdata_unsubscribe(conids)`** → Cancel subscription for specific contracts
10. **`marketdata_unsubscribe_all()`** → Cancel all subscriptions

### Key Use Case:
Retrieve live price quotes and historical OHLC data for technical analysis.

---

## 4. PortfolioMixin (17 Methods)

### Account Structure (3 methods):
1. **`portfolio_accounts()`** → Get list of accessible accounts ⚠️ *Required first*
2. **`portfolio_subaccounts()`** → Get sub-accounts (max 100)
3. **`large_portfolio_subaccounts(page)`** → Paginated sub-accounts (20/page)

### Positions (5 methods):
4. **`positions(account_id, page, ...)`** → Paginated positions (max 100/page, cached)
5. **`positions2(account_id, ...)`** → All positions (real-time, no cache)
6. **`positions_by_conid(account_id, conid)`** → Position for specific contract
7. **`position_and_contract_info(conid)`** → Position + contract details combined
8. **`combination_positions(account_id, no_cache)`** → Multi-leg combination positions

### Account Information (4 methods):
9. **`portfolio_account_information(account_id)`** → Account metadata
10. **`portfolio_summary(account_id)`** → Cash and currency balances
11. **`get_ledger(account_id)`** → Ledger (cash) information
12. **`transaction_history(account_ids, conids, currency, days)`** → Trade history

### Performance & Allocation (5 methods):
13. **`account_performance(account_ids, period)`** → Mark-to-market performance
14. **`all_periods(account_ids)`** → Performance for all available periods
15. **`portfolio_account_allocation(account_id)`** → Asset allocation breakdown
16. **`portfolio_account_allocations(account_ids)`** → Multi-account consolidated allocation
17. **`invalidate_backend_portfolio_cache(account_id)`** → Force cache refresh

### Key Use Case:
Monitor portfolio positions, track performance, analyze allocation.

---

## 5. WatchlistMixin (4 Methods)

### Data Retrieval Methods:
1. **`get_all_watchlists(sc='USER_WATCHLIST')`** → List all watchlists
2. **`get_watchlist_information(id)`** → Get contracts in a watchlist
3. **`create_watchlist(id, name, rows)`** → Create a new watchlist
4. **`delete_watchlist(id)`** → Delete a watchlist

### Key Use Case:
Organize and manage contract watchlists for monitoring.

---

## Common Field IDs for Market Data

| Field ID | Description | Example Values |
|----------|-------------|-----------------|
| `31` | Last Price | Current trade price |
| `66` | Bid Size | Number of shares at bid |
| `68` | Ask Size | Number of shares at ask |
| `69` | Bid Price | Current bid price |
| `70` | Ask Price | Current ask price |
| `84` | Mark Price | Fair value estimate |
| `85` | Bid/Ask Change | Change from previous |
| `86` | Mark Change | Mark price change |

---

## Typical Workflow Examples

### Example 1: Get Current Stock Price
```python
from ibind import IbkrClient

client = IbkrClient()

# Get accounts
accounts = client.receive_brokerage_accounts()

# Search for stock
contracts = client.search_contract_by_symbol('AAPL')
conid = contracts.data[0]['conid']

# Get current price
snapshot = client.live_marketdata_snapshot(conids=conid, fields=['31', '69', '70'])
# Result: Last price, Bid, Ask
```

### Example 2: Get Portfolio Holdings
```python
# Get accounts (required first!)
accounts = client.portfolio_accounts()
account_id = accounts.data[0]['accountId']

# Get positions
positions = client.positions(account_id=account_id)

# Analyze allocation
allocation = client.portfolio_account_allocation(account_id=account_id)

# Check performance
performance = client.account_performance(account_ids=account_id, period='1m')
```

### Example 3: Historical Data for Analysis
```python
# Get 1-week of daily OHLC data
history = client.marketdata_history_by_symbol(
    symbol='SPY',
    bar='1d',
    period='1w',
    outside_rth=False
)

# Batch retrieve for multiple symbols (parallel)
symbols = ['SPY', 'QQQ', 'IWM']
histories = client.marketdata_history_by_symbols(
    queries=symbols,
    bar='1d',
    period='1w',
    run_in_parallel=True
)
```

### Example 4: Options Research
```python
# Find contracts for SPY options
contracts = client.search_contract_by_symbol('SPY', sec_type='OPT')

# Get available strike prices
strikes = client.search_strikes_by_conid(
    conid='756033',  # SPY conid
    sec_type='OPT',
    month='DEC23'
)

# Get details for specific option
option_details = client.search_secdef_info_by_conid(
    conid='756033',
    sec_type='OPT',
    month='DEC23',
    strike='400',
    right='C'  # Call option
)
```

---

## Important Notes

### Initialization Requirements
- **Portfolio methods:** Call `portfolio_accounts()` or `portfolio_subaccounts()` first
- **Derivative searches:** Call `search_contract_by_symbol()` before `search_secdef_info_by_conid()`

### Performance Features
- **Batch methods:** `marketdata_history_by_conids()` and `marketdata_history_by_symbols()` support parallel execution
- **Caching:** `positions()` uses caching; use `positions2()` for real-time data
- **Pagination:** `positions()` and `large_portfolio_subaccounts()` support paging

### Cost Considerations
- **⚠️ Regulatory Snapshot:** $0.01 USD per call (applies to paper and live accounts!)

### Data Types
- Most methods return `Result` objects containing `.data` attribute
- Batch methods like `marketdata_history_by_symbols()` return raw `dict` for convenience

---

## Files Location
- **Full Analysis:** `/home/john/CodingProjects/llm_public/IBKR_MIXIN_ANALYSIS.md`
- **Quick Reference:** This file
- **Source Package:** `ibind` (Python package installed in environment)

---

**Generated:** December 18, 2025  
**Package Version:** ibind (latest)  
**Python Version:** 3.13.7
