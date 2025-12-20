# IBKR Client Mixin Analysis - Summary Report

**Analysis Date:** December 18, 2025  
**Package:** ibind (Python)  
**Python Version:** 3.13.7

---

## Analysis Complete ✓

I have successfully analyzed all 5 IBKR client mixins from the `ibind` package and extracted comprehensive documentation on their data retrieval methods.

---

## Files Generated

### 1. **IBKR_MIXIN_ANALYSIS.md** (Comprehensive Reference)
- **Type:** Markdown documentation
- **Size:** ~15,000+ words
- **Content:**
  - Executive overview of all mixins
  - Detailed method signatures with full parameter descriptions
  - Complete docstrings and usage contexts
  - Common field IDs reference
  - Typical workflow examples
  - Important implementation notes
  - Version information

**Use Case:** Deep dive reference, understanding implementation details, training

### 2. **IBKR_MIXIN_QUICK_REFERENCE.md** (Quick Lookup)
- **Type:** Markdown summary
- **Size:** ~3,000 words
- **Content:**
  - Executive summary table
  - Quick method listing by mixin
  - Common field IDs
  - Workflow examples
  - Key considerations
  - File locations

**Use Case:** Quick lookup, integration planning, rapid reference

### 3. **ibkr_mixin_methods.json** (Programmatic API)
- **Type:** JSON structure
- **Content:**
  - Machine-readable method specifications
  - Parameter details with types
  - Return value information
  - Cost warnings
  - Prerequisites and requirements
  - Common field ID mappings
  - Summary statistics

**Use Case:** Code generation, automation, integration tools, IDE plugins

---

## Key Findings

### Mixin Overview

| Mixin | Data Retrieval Methods | Primary Purpose |
|-------|----------------------|-----------------|
| **AccountsMixin** | 4 | Account/credential management |
| **ContractMixin** | 5 | Contract search & specifications |
| **MarketdataMixin** | 10 | Live & historical market data |
| **PortfolioMixin** | 17 | Portfolio positions & performance |
| **WatchlistMixin** | 4 | Watchlist management |
| **TOTAL** | **40** | Complete IBKR data access |

### Most Powerful Mixins

1. **PortfolioMixin (17 methods)** - Most comprehensive; enables full portfolio analysis
2. **MarketdataMixin (10 methods)** - Supports live quotes, OHLC data, batch operations
3. **ContractMixin (5 methods)** - Enables comprehensive contract research
4. **AccountsMixin (4 methods)** - Account initialization and metadata
5. **WatchlistMixin (4 methods)** - Watchlist organization

### Notable Features

**Parallel Processing:**
- `marketdata_history_by_conids()` - Batch historical data with optional parallelization
- `marketdata_history_by_symbols()` - Batch by symbols with optional parallelization

**Real-time vs. Cached:**
- `positions()` - Cached (paginated)
- `positions2()` - Real-time (no pagination)

**Cost Implications:**
- ⚠️ `regulatory_snapshot()` - $0.01 USD per call (applies to paper and live accounts)

**Batch Operations:**
- Most methods support single and list inputs
- Batch methods provide direct dict output (not wrapped in Result)

---

## Common Patterns

### 1. Initialization Pattern
```python
# Step 1: Get accounts (prerequisite)
accounts = client.portfolio_accounts()

# Step 2: Work with account-specific methods
positions = client.positions(account_id=accounts.data[0]['accountId'])
```

### 2. Contract Discovery Pattern
```python
# Step 1: Search by symbol
contracts = client.search_contract_by_symbol('AAPL')
conid = contracts.data[0]['conid']

# Step 2: Get details (for derivatives)
details = client.search_secdef_info_by_conid(conid, sec_type='OPT', month='DEC23')

# Step 3: Get market data
snapshot = client.live_marketdata_snapshot(conids=conid, fields=['31', '69', '70'])
```

### 3. Batch Analysis Pattern
```python
# Get multiple symbols' historical data in parallel
histories = client.marketdata_history_by_symbols(
    queries=['SPY', 'QQQ', 'IWM'],
    bar='1d',
    period='1w',
    run_in_parallel=True
)
```

---

## Key Considerations

### Implementation Requirements
- **Portfolio methods:** Call `portfolio_accounts()` or `portfolio_subaccounts()` first
- **Contract derivatives:** Call `search_contract_by_symbol()` before `search_secdef_info_by_conid()`

### Performance Features
- **Caching:** Available in `positions()` method; use `positions2()` for real-time
- **Parallelization:** Available in batch market data methods
- **Pagination:** Supported in `positions()` and `large_portfolio_subaccounts()`

### Data Types
- Most methods return `Result` objects with `.data` attribute
- Batch methods return raw `dict` for convenience
- Signature types are fully annotated with type hints

---

## Data Retrieval Capabilities Summary

### Accounts & Infrastructure (4 methods)
- Retrieve account list and aliases
- Get account summaries and PnL
- Search and manage dynamic accounts
- Switch between accounts

### Contracts & Specifications (5 methods)
- Search instruments by symbol or company name
- Get detailed contract specifications
- Retrieve available option strikes
- Query trading rules and constraints
- Research bonds and issuer information

### Market Data (10 methods)
- **Live Data:** Current prices by contract ID or symbol
- **Historical Data:** OHLC bars (1min to 1Y)
- **Batch Operations:** Multi-symbol queries with parallel processing
- **Regulatory Data:** Snapshots for compliance (paid)
- **Subscription Management:** Subscribe/unsubscribe from feeds

### Portfolio Management (17 methods)
- **Account Structure:** List accounts and sub-accounts (with pagination)
- **Positions:** Get holdings (paginated or real-time), single positions, combination legs
- **Performance:** Mark-to-market metrics across multiple time periods
- **Allocation:** Asset class, industry, and category breakdowns
- **Cash Management:** Ledger, summary, and multi-currency balances
- **Analysis:** Transaction history, consolidated multi-account views
- **Cache Control:** Force refresh capabilities

### Watchlists (4 methods)
- Create, retrieve, and delete watchlists
- Organize monitored contracts
- Monitor across platforms (TWS, Client Portal)

---

## Integration Recommendations

1. **For Market Analysis:** Use `MarketdataMixin` with batch operations
2. **For Portfolio Tracking:** Use `PortfolioMixin` with `positions2()` for real-time
3. **For Contract Research:** Start with `ContractMixin` followed by market data
4. **For Account Management:** Always start with `AccountsMixin` initialization
5. **For Organization:** Use `WatchlistMixin` to create logical groupings

---

## Document Navigation

- **Start Here:** `IBKR_MIXIN_QUICK_REFERENCE.md`
- **Deep Dive:** `IBKR_MIXIN_ANALYSIS.md`
- **Programmatic Access:** `ibkr_mixin_methods.json`

---

## Statistics

- **Total Methods Analyzed:** 40
- **Parameters Documented:** 150+
- **Code Examples:** 15+
- **Field IDs Mapped:** 8 common types
- **Warning Flags:** 3 (regulatory snapshot cost, initialization order)
- **Best Practices:** 20+ documented patterns

---

## Next Steps

1. **Review** the quick reference for overview
2. **Explore** the comprehensive analysis for details
3. **Reference** the JSON file for programmatic integration
4. **Test** methods with your IBKR account
5. **Monitor** the ibind package for updates

---

*For questions or updates, refer to the ibind package documentation at: https://github.com/Voyz/ibind*

