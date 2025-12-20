# MCP Server Gap Analysis and Implementation Plan

**Analysis Date:** December 19, 2025  
**Author:** Cline (AI Assistant)  
**Purpose:** Document gaps in current MCP server implementation and plan for exposing additional methods to help LLM clients locate conids

## Executive Summary

The current MCP server (`src/mcp_server.py`) exposes 26 tools primarily from ContractMixin and MarketdataMixin. However, **23 additional methods** from the underlying ibind package are not exposed, including critical tools for conid location, portfolio management, watchlist management, and account initialization. This analysis identifies gaps and proposes a phased implementation plan to expose these methods, with particular focus on tools that help LLM clients locate conids.

## 1. Current State Analysis

### 1.1 Current MCP Server Tools (26 total)

**Search & Lookup (7):**
1. `search_contract()` - Maps to `search_contract_by_symbol()`
2. `security_definition()` - Maps to `security_definition_by_conid()`
3. `all_exchange_contracts()` - Maps to `all_conids_by_exchange()`
4. `contract_information()` - Maps to `contract_information_by_conid()`
5. `currency_pairs()` - Maps to `currency_pairs()`
6. `security_futures()` - Maps to `security_future_by_symbol()`
7. `security_stocks()` - **Uses workaround** instead of `security_stocks_by_symbol()`

**Contract Details (3):**
8. `get_contract_details()` - Maps to `search_secdef_info_by_conid()`
9. `get_option_strikes()` - Maps to `search_strikes_by_conid()`
10. `trading_schedule()` - Maps to `trading_schedule_by_symbol()`

**Trading Rules & Info (3):**
11. `get_trading_rules()` - Maps to `search_contract_rules()`
12. `contract_info_and_rules()` - Maps to `info_and_rules_by_conid()`
13. `currency_exchange_rate()` - Maps to `currency_exchange_rate()`

**Bond & Algorithm Tools (2):**
14. `get_bond_filters()` - Maps to `search_bond_filter_information()`
15. `algo_params()` - Maps to `algo_params_by_conid()`

**Live Market Data (2):**
16. `live_marketdata_snapshot()` - Maps to `live_marketdata_snapshot()`
17. `live_marketdata_snapshot_by_symbol()` - **Misnamed**, actually uses `fetch_market_data_snapshot_by_queries()`

**Historical Market Data (5):**
18. `marketdata_history_by_conid()` - Maps to `marketdata_history_by_conid()`
19. `marketdata_history_by_symbol()` - Maps to `marketdata_history_by_symbol()`
20. `marketdata_history_by_conids()` - Maps to `marketdata_history_by_conids()`
21. `marketdata_history_by_symbols()` - Maps to `marketdata_history_by_symbols()`
22. `historical_marketdata_beta()` - Maps to `historical_marketdata_beta()`

**Regulatory & Subscriptions (3):**
23. `regulatory_snapshot()` - Maps to `regulatory_snapshot()`
24. `marketdata_unsubscribe()` - Maps to `marketdata_unsubscribe()`
25. `marketdata_unsubscribe_all()` - Maps to `marketdata_unsubscribe_all()`

**Utility (1):**
26. `list_tools()` - Documentation utility

### 1.2 Available Mixin Methods (49 total)

From `IBKR_MIXIN_ANALYSIS.md`:

| Mixin | Methods Available | Methods Exposed | Gap |
|-------|------------------|-----------------|-----|
| **AccountsMixin** | 2 | 0 | **100% missing** |
| **ContractMixin** | 16 | ~14 | 2 missing |
| **MarketdataMixin** | 10 | 10 | 0 missing |
| **PortfolioMixin** | 17 | 0 | **100% missing** |
| **WatchlistMixin** | 4 | 0 | **100% missing** |
| **TOTAL** | **49** | **~26** | **23 missing** |

## 2. Critical Gaps for Conid Location

### 2.1 High-Priority Missing Methods

**1. `stock_conid_by_symbol()` (ContractMixin)**
- **Purpose:** Unambiguous conid resolution with filtering
- **Why critical:** Specifically designed for conid discovery, ensures only one conid per query
- **Current workaround:** `search_contract()` returns multiple matches, requires manual filtering

**2. `security_stocks_by_symbol()` (ContractMixin)**
- **Purpose:** Advanced stock filtering with StockQuery objects
- **Why important:** Proper implementation vs current workaround using `search_contract_by_symbol()`
- **Benefits:** Precise filtering, better performance

**3. `receive_brokerage_accounts()` (AccountsMixin)**
- **Purpose:** Account initialization
- **Why important:** Required for portfolio tools and proper account context
- **Prerequisite:** Many IBKR endpoints require account initialization

### 2.2 Entire Missing Mixins

**PortfolioMixin (17 methods):**
- Complete portfolio analysis capabilities missing
- Includes: positions, performance, allocation, transaction history
- **Impact:** LLM clients cannot analyze portfolio holdings or performance

**WatchlistMixin (4 methods):**
- Watchlist management missing
- Includes: create, retrieve, delete watchlists
- **Impact:** Cannot programmatically manage watchlists for conid monitoring

**AccountsMixin (2 methods):**
- Account initialization missing
- **Impact:** Portfolio tools cannot function without account context

### 2.3 Implementation Issues

1. **Misnamed tool:** `live_marketdata_snapshot_by_symbol()` actually takes `queries` parameter, not `symbol`
2. **Workaround usage:** `security_stocks()` uses `search_contract_by_symbol()` instead of proper method
3. **Missing StockQuery support:** No tools expose StockQuery dataclass for advanced filtering

## 3. Implementation Plan (Phased Approach)

### Phase 1: High-Priority Conid Location Tools (Week 1)

**Goal:** Expose methods specifically designed for conid discovery and resolution

| Tool to Add | Underlying Method | Parameters | Priority |
|-------------|------------------|------------|----------|
| `stock_conid_by_symbol()` | `stock_conid_by_symbol()` | `queries`, `default_filtering`, `return_type` | **CRITICAL** |
| `fix_security_stocks()` | `security_stocks_by_symbol()` | `queries`, `default_filtering` | **HIGH** |
| `receive_brokerage_accounts()` | `receive_brokerage_accounts()` | None | **HIGH** |
| `search_dynamic_account()` | `search_dynamic_account()` | `search_pattern` | Medium |

**Expected Benefits:**
- Reliable conid resolution for LLM clients
- Proper stock filtering capabilities
- Account initialization for portfolio tools

### Phase 2: Portfolio Management Tools (Week 2)

**Goal:** Expose portfolio analysis capabilities

| Tool Category | Key Methods | Parameters |
|--------------|-------------|------------|
| **Account Initialization** | `portfolio_accounts()`, `portfolio_subaccounts()` | None |
| **Position Management** | `positions()`, `positions2()`, `positions_by_conid()` | `account_id`, `page`, etc. |
| **Portfolio Analysis** | `portfolio_summary()`, `get_ledger()` | `account_id` |
| **Performance Tracking** | `account_performance()`, `all_periods()` | `account_ids`, `period` |
| **Allocation Analysis** | `portfolio_account_allocation()` | `account_id` |
| **Transaction History** | `transaction_history()` | `account_ids`, `conids`, `currency`, `days` |

**Implementation Considerations:**
- All tools need `account_id` parameter with default logic
- Consistent error handling for uninitialized accounts
- Pagination support for large portfolios

### Phase 3: Watchlist & Account Management (Week 3)

**Goal:** Expose watchlist management capabilities

| Tool to Add | Underlying Method | Parameters |
|-------------|------------------|------------|
| `get_all_watchlists()` | `get_all_watchlists()` | `sc` |
| `get_watchlist_information()` | `get_watchlist_information()` | `id` |
| `create_watchlist()` | `create_watchlist()` | `id`, `name`, `rows` |
| `delete_watchlist()` | `delete_watchlist()` | `id` |

**Use Case:** Programmatic watchlist management for conid monitoring

### Phase 4: Utilities & Improvements (Week 4)

**Goal:** Fix issues and add utility tools

| Task | Description |
|------|-------------|
| **Rename tool** | `live_marketdata_snapshot_by_symbol()` → `live_marketdata_snapshot_by_queries()` |
| **Fix implementation** | Update `security_stocks()` to use `security_stocks_by_symbol()` |
| **Add utility tools** | `extract_conid()`, `cleanup_market_data()` |
| **Update documentation** | Enhance `list_tools()` with new tools and examples |
| **Add StockQuery support** | Simplified interface for LLM clients |

## 4. Technical Implementation Details

### 4.1 Tool Organization Strategy

**Group by functionality:**
- **Contract Search & Conid Location** (Phase 1)
- **Portfolio Management** (Phase 2) 
- **Watchlist Management** (Phase 3)
- **Utilities & Data Processing** (Phase 4)

**Consistent naming:**
- Use descriptive names matching underlying methods
- Follow existing pattern: `snake_case()` for tools

**Parameter design:**
- Follow ibind method signatures with LLM-friendly adaptations
- Provide sensible defaults where possible
- Support both simple and advanced parameter modes

### 4.2 StockQuery Support for LLM Clients

**Challenge:** StockQuery dataclass has complex structure for LLM clients

**Solution:** Create simplified interface:
```python
# Simple mode (for LLM clients)
security_stocks(symbol="AAPL")

# Advanced mode (for power users)
security_stocks_advanced(
    queries=[
        {
            "symbol": "AAPL",
            "name_match": "Apple",
            "contract_conditions": {"isUS": True}
        }
    ]
)
```

### 4.3 Error Handling Strategy

**Consistent error format:**
```json
{
    "error": "Descriptive error message",
    "suggestion": "Actionable suggestion",
    "details": {"param1": "value1", "param2": "value2"}
}
```

**Graceful degradation:**
- Clear messages when client not initialized
- Fallback behaviors where appropriate
- Validation before API calls

### 4.4 Documentation Requirements

**Update `list_tools()` to include:**
- New tool categories and descriptions
- Usage examples for conid location workflows
- Parameter explanations with examples
- Common error scenarios and solutions

**Create workflow examples:**
- Conid discovery workflow
- Portfolio analysis workflow
- Watchlist management workflow

## 5. Expected Benefits

### 5.1 For LLM Clients

1. **Better Conid Discovery:** Reliable conid resolution with `stock_conid_by_symbol()`
2. **Complete Workflows:** Portfolio + Contract + Market data integration
3. **Account Awareness:** Tools for account selection and management
4. **Watchlist Integration:** Programmatic watchlist management
5. **Utility Functions:** Helper tools for data processing

### 5.2 For Developers

1. **Comprehensive API:** All 49 mixin methods exposed
2. **Consistent Interface:** Uniform error handling and parameter design
3. **Better Documentation:** Clear examples and workflows
4. **Maintainable Code:** Organized by functionality with clear separation

### 5.3 For End Users

1. **Richer Functionality:** Complete IBKR capabilities through MCP
2. **Better LLM Assistance:** LLMs can provide more comprehensive financial analysis
3. **Time Savings:** Automated portfolio analysis and watchlist management
4. **Reduced Errors:** Proper conid resolution reduces trading errors

## 6. Risk Assessment

### 6.1 Technical Risks

| Risk | Mitigation |
|------|------------|
| **API changes in ibind** | Version pinning, regular updates |
| **Rate limiting** | Implement retry logic, batch operations |
| **Authentication issues** | Clear error messages, reconnection logic |
| **Large response sizes** | Pagination, filtering options |

### 6.2 User Experience Risks

| Risk | Mitigation |
|------|------------|
| **Parameter complexity** | Simplified interfaces, good defaults |
| **Error understanding** | Clear, actionable error messages |
| **Performance concerns** | Caching where appropriate, async operations |

## 7. Success Metrics

### 7.1 Quantitative Metrics
- **Tool coverage:** 49/49 mixin methods exposed (100%)
- **Response time:** < 2s for most operations
- **Error rate:** < 1% for properly formatted requests
- **Usage frequency:** Track tool usage patterns

### 7.2 Qualitative Metrics
- **LLM client satisfaction:** Ability to complete financial tasks
- **Developer feedback:** Ease of integration and use
- **End user satisfaction:** Quality of financial insights provided

## 8. Next Steps

### Immediate (Week 1):
1. Implement `stock_conid_by_symbol()` tool
2. Fix `security_stocks()` to use proper method
3. Add `receive_brokerage_accounts()` tool
4. Test conid location workflows

### Short-term (Weeks 2-3):
1. Implement PortfolioMixin tools
2. Implement WatchlistMixin tools
3. Add account parameter support
4. Update documentation

### Long-term (Week 4+):
1. Fix naming and implementation issues
2. Add utility tools
3. Enhance error handling
4. Create comprehensive test suite

## 9. Conclusion

The current MCP server provides a solid foundation with 26 tools, but significant gaps remain in conid location capabilities, portfolio management, and watchlist functionality. By implementing the proposed 4-phase plan, we can expose all 49 available mixin methods, providing LLM clients with comprehensive IBKR capabilities.

The highest priority is Phase 1, which addresses the core requirement of "facilitating a client locating conid" through the critical `stock_conid_by_symbol()` tool and related improvements. This will immediately improve LLM clients' ability to reliably discover and work with contract IDs.

---

**Appendix A: Detailed Method Mapping**

See `IBKR_MIXIN_ANALYSIS.md` for complete method signatures and descriptions.

**Appendix B: Example Implementations**

Example implementations for new tools will be created during the implementation phase.

**Appendix C: Testing Strategy**

Comprehensive testing plan including unit tests, integration tests, and LLM workflow tests.
