# IBKR Mixin Analysis - Complete Index

## 📋 Quick Navigation

| Document | Size | Purpose | Audience |
|----------|------|---------|----------|
| **[ANALYSIS_SUMMARY.md](./ANALYSIS_SUMMARY.md)** | 3 KB | Overview & findings | Everyone |
| **[IBKR_MIXIN_QUICK_REFERENCE.md](./IBKR_MIXIN_QUICK_REFERENCE.md)** | 15 KB | Lookup reference | Developers |
| **[IBKR_MIXIN_ANALYSIS.md](./IBKR_MIXIN_ANALYSIS.md)** | 50+ KB | Comprehensive guide | Deep-dive readers |
| **[ibkr_mixin_methods.json](./ibkr_mixin_methods.json)** | 30 KB | Machine-readable API | Tools/automation |

---

## 📊 What's Included

### AccountsMixin (4 methods)
- `receive_brokerage_accounts()` - Get accessible accounts
- `account_summary()` - Account information
- `search_dynamic_account()` - Search FA accounts
- `account_profit_and_loss()` - Get account P&L

### ContractMixin (5 methods)
- `search_contract_by_symbol()` - Search for contracts ⭐ **Required first**
- `search_secdef_info_by_conid()` - Get contract details
- `search_strikes_by_conid()` - List available strikes
- `search_contract_rules()` - Trading constraints
- `search_bond_filter_information()` - Bond-specific lookup

### MarketdataMixin (10 methods)
- **Live:** `live_marketdata_snapshot()`, `live_marketdata_snapshot_by_symbol()`
- **Historical:** `marketdata_history_by_conid()`, `marketdata_history_by_symbol()`
- **Batch:** `marketdata_history_by_conids()`, `marketdata_history_by_symbols()` ⭐ **Parallel**
- **Advanced:** `historical_marketdata_beta()`
- **Regulatory:** `regulatory_snapshot()` ⚠️ **$0.01 per call**
- **Management:** `marketdata_unsubscribe()`, `marketdata_unsubscribe_all()`

### PortfolioMixin (17 methods)
- **Account Setup:** `portfolio_accounts()` ⭐ **Required first**, `portfolio_subaccounts()`, `large_portfolio_subaccounts()`
- **Positions:** `positions()`, `positions2()` (real-time), `positions_by_conid()`, `combination_positions()`
- **Account Info:** `portfolio_account_information()`, `portfolio_summary()`, `get_ledger()`
- **Allocation:** `portfolio_account_allocation()`, `portfolio_account_allocations()`
- **Performance:** `account_performance()`, `all_periods()`
- **History:** `transaction_history()`
- **Control:** `invalidate_backend_portfolio_cache()`, `position_and_contract_info()`

### WatchlistMixin (4 methods)
- `get_all_watchlists()` - List watchlists
- `get_watchlist_information()` - Get watchlist contents
- `create_watchlist()` - Create new watchlist
- `delete_watchlist()` - Remove watchlist

---

## 🚀 Getting Started

### For a Quick Overview
1. Read **ANALYSIS_SUMMARY.md** (5 min)
2. Check **IBKR_MIXIN_QUICK_REFERENCE.md** for your use case (10 min)

### For Implementation
1. Start with **IBKR_MIXIN_QUICK_REFERENCE.md** workflow examples
2. Reference **IBKR_MIXIN_ANALYSIS.md** for detailed method signatures
3. Use **ibkr_mixin_methods.json** for integration/code generation

### For Automation/Tools
1. Use **ibkr_mixin_methods.json** as input
2. Parse method signatures and parameters
3. Generate integration code or documentation

---

## 💡 Key Insights

### Initialization Requirements
```python
# Always start with this
accounts = client.portfolio_accounts()

# Then use account-specific methods
positions = client.positions(account_id=accounts.data[0]['accountId'])
```

### Contract Search Pattern
```python
# Step 1 (required)
contracts = client.search_contract_by_symbol('SPY')

# Step 2 (for derivatives)
details = client.search_secdef_info_by_conid(conid, sec_type='OPT', ...)
```

### High-Performance Data Retrieval
```python
# Batch with parallel processing (default)
data = client.marketdata_history_by_symbols(
    queries=['SPY', 'QQQ', 'IWM'],
    bar='1d',
    period='1w',
    run_in_parallel=True  # Enabled by default
)
```

### Real-Time vs. Cached Positions
```python
# Cached (paginated, faster)
pos = client.positions(account_id=account_id)

# Real-time (no cache, guaranteed current)
pos = client.positions2(account_id=account_id)
```

---

## ⚠️ Important Warnings

### Cost Implications
- **Regulatory Snapshot:** $0.01 USD per call (live AND paper accounts)
- Repeated calls accumulate costs quickly

### Method Prerequisites
- **Portfolio methods:** Must call `portfolio_accounts()` first
- **Contract derivatives:** Must call `search_contract_by_symbol()` first
- **Dynamic accounts:** `search_dynamic_account()` may fail with 503 if not available

### Performance Notes
- Batch methods support parallel execution (default: enabled)
- `positions()` uses caching; use `positions2()` for real-time
- Regulatory snapshot requests incur fees

---

## 📈 Statistics

| Metric | Count |
|--------|-------|
| Total Mixins | 5 |
| Total Methods | 40 |
| Parameters Documented | 150+ |
| Common Field IDs | 8 |
| Code Examples | 15+ |
| Warning Flags | 3 |
| Best Practices | 20+ |

---

## 🔗 Related Resources

- **ibind Package:** https://github.com/Voyz/ibind
- **IBKR API Docs:** https://ibkrcampus.com/ibkr-api-page/
- **Field ID Reference:** See IBKR_MIXIN_ANALYSIS.md section 3.1

---

## 📝 Document Details

- **Generated:** December 18, 2025
- **Package Analyzed:** ibind (latest)
- **Python Version:** 3.13.7
- **Analysis Scope:** Data retrieval methods (public API)
- **Excluded:** Internal methods, private APIs

---

## 🎯 Use Case Quick Links

### Market Analysis
- Primary: `MarketdataMixin` → Live snapshots + Historical data
- Supporting: `ContractMixin` → Find contracts
- Reference: IBKR_MIXIN_QUICK_REFERENCE.md - "Example 3"

### Portfolio Tracking
- Primary: `PortfolioMixin` → Positions, performance, allocation
- Starting: Must call `portfolio_accounts()` first
- Reference: IBKR_MIXIN_QUICK_REFERENCE.md - "Example 2"

### Options Research
- Primary: `ContractMixin` → Search, strikes, details
- Supporting: `MarketdataMixin` → Live prices
- Reference: IBKR_MIXIN_QUICK_REFERENCE.md - "Example 4"

### Account Management
- Primary: `AccountsMixin` → Accounts, summaries, P&L
- Supporting: `PortfolioMixin` → Account-level data
- Reference: IBKR_MIXIN_QUICK_REFERENCE.md - "Example 1"

### Watchlist Organization
- Primary: `WatchlistMixin` → Create, manage, retrieve
- Use With: Any data retrieval method
- Reference: IBKR_MIXIN_QUICK_REFERENCE.md

---

## 📞 Questions?

Refer to:
1. **IBKR_MIXIN_ANALYSIS.md** - Detailed method documentation
2. **ibkr_mixin_methods.json** - Machine-readable reference
3. **ibind GitHub** - Package source and issues
4. **IBKR Campus** - Official API documentation

---

## ✅ Analysis Checklist

- ✓ All 5 mixins analyzed
- ✓ 40 data retrieval methods documented
- ✓ Complete method signatures extracted
- ✓ Parameter descriptions included
- ✓ Return types specified
- ✓ Usage contexts provided
- ✓ Code examples included
- ✓ Warnings and caveats noted
- ✓ JSON reference created
- ✓ Quick reference compiled
- ✓ Comprehensive guide written

---

**Analysis Status: COMPLETE** ✓

*Last Updated: December 18, 2025*

