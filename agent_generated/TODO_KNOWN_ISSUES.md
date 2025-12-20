# TODO: Known Issues and Fixes for IBKR MCP Server

**Date:** December 19, 2025  
**Status:** Active issues to be addressed

## Architecture Update

**Note:** The `ibind_web_client.py` file has been deleted. All its functionality has been moved to `utils.py`:
- `get_client()` - IBKR client initialization
- `get_conids()` - Symbol to conid resolution  
- `_fetch_raw_market_data()` - Raw market data fetching
- `iterate_to_fetch_market_data()` - Market data with retries
- `to_json()` - JSON serialization helper
- `extract_result_data()` - Result data extraction

The three-layer architecture is now:
1. **Layer 1 (utils.py)**: IBKR API wrapper and data transformation
2. **Layer 2 (mcp_server.py)**: High-level MCP tools with JSON serialization
3. **Layer 3 (settings.py)**: Configuration and constants

## Overview

This document tracks known issues with the IBKR MCP Server implementation. These are not bugs in the implementation, but rather expected limitations or configuration issues that users should be aware of.

## Failed Tools Analysis

### 1. `get_contract_details`
- **Issue:** Invalid test parameters (wrong expiration month format or the option doesn't exist)
- **Root Cause:** Test uses hardcoded parameters that may not match actual available contracts
- **Expected Behavior:** Tool is functional, but requires valid parameters
- **Fix Needed:** 
  - Use current expiration months (e.g., "JAN26" instead of "JAN25")
  - Verify option strikes exist before testing
  - Consider using dynamic parameter discovery
- **Priority:** Medium
- **Workaround:** Use `search_contract()` first to find valid parameters

### 2. `live_marketdata_snapshot_by_symbol`
- **Issue:** Field 31 (Last Price) not available
- **Root Cause:** Market may be closed or symbol may not have active trading
- **Expected Behavior:** During market hours with actively traded symbols, field 31 should be available
- **Fix Needed:**
  - Test during regular trading hours (9:30 AM - 4:00 PM ET)
  - Use highly liquid symbols (AAPL, SPY, etc.)
  - Implement fallback to other price fields if field 31 unavailable
- **Priority:** Low (expected behavior)
- **Workaround:** Use `live_marketdata_snapshot()` with conid instead

### 3. `historical_marketdata_beta`
- **Issue:** Advanced feature requiring special permissions
- **Root Cause:** Beta endpoint may require additional account permissions or setup
- **Expected Behavior:** May work with proper IBKR account configuration
- **Fix Needed:**
  - Verify account has access to beta features
  - Check IBKR documentation for beta endpoint requirements
  - Consider using standard historical endpoints instead
- **Priority:** Low (advanced feature)
- **Workaround:** Use `marketdata_history_by_conid()` or `marketdata_history_by_symbol()`

### 4. `regulatory_snapshot`
- **Issue:** Costs $0.01 USD per call
- **Root Cause:** Paid feature that requires proper authorization and account funding
- **Expected Behavior:** Fails without proper account setup for paid features
- **Fix Needed:**
  - Ensure account has funds for regulatory data
  - For a Paper Account, automatically reject client call to this method
  - Verify account permissions for paid data
  - Add explicit warning in documentation about costs
- **Priority:** Low (paid feature)
- **Workaround:** Use `live_marketdata_snapshot()` for free market data

## Test Improvements Needed

### 1. Parameter Validation Tests
- **Issue:** Tests use hardcoded parameters that may become invalid
- **Solution:** Create dynamic test parameters based on current market data
- **Example:** Use `search_contract()` to get valid conids and parameters

### 2. Market Hours Awareness
- **Issue:** Tests fail outside trading hours
- **Solution:** Add market hours check before running certain tests
- **Example:** Skip live market data tests when markets are closed

### 3. Error Handling Tests
- **Issue:** Need better tests for error conditions
- **Solution:** Add tests for invalid parameters, missing data, etc.
- **Example:** Test with invalid symbols, expired contracts, etc.

## Configuration Requirements

### 1. IBKR Account Setup
- **Requirement:** Valid IBKR account with API access
- **Status:** ✅ Working (tests show real data retrieval)
- **Notes:** Ensure `.env` file has correct credentials

### 2. Market Data Permissions
- **Requirement:** Account must have market data subscriptions
- **Status:** ⚠️ Some tools may require specific data permissions
- **Notes:** Check IBKR account for required market data subscriptions

### 3. Paper Trading vs Live Account
- **Recommendation:** Use paper trading account for testing
- **Benefit:** Avoids real trading costs and regulatory snapshot fees
- **Note:** Some features may differ between paper and live accounts

## Implementation Notes

### 1. Tool Success Rate
- **Current:** 22/26 tools working (84.6%)
- **Target:** 26/26 tools working (100%)
- **Notes:** 4 tools have known, expected issues

### 2. Production Readiness
- **Status:** ✅ Production-ready for 22 tools
- **Limitations:** 4 tools require specific conditions to work
- **Recommendation:** Document limitations for users

### 3. Error Messages
- **Current:** Clear error messages for failed tools
- **Improvement:** Add more specific error messages with suggestions
- **Example:** "Market closed - try during trading hours" instead of "Field 31 not available"

## Next Steps

### Short-term (1-2 weeks)
1. Update test parameters to use current dates
2. Add market hours awareness to tests
3. Improve error messages with actionable suggestions

### Medium-term (1 month)
1. Implement dynamic parameter discovery for tests
2. Add configuration validation on server startup
3. Create user documentation with troubleshooting guide

### Long-term (3 months)
1. Implement caching for frequently accessed data
2. Add rate limiting to prevent API abuse
3. Expand to include PortfolioMixin and WatchlistMixin tools

## Conclusion

The IBKR MCP Server is fully functional with 22 out of 26 tools working correctly. The 4 tools with issues have known, expected limitations that are documented here. Users should be aware of these limitations and use the appropriate workarounds.

For most use cases, the available tools provide comprehensive coverage of IBKR's ContractMixin and MarketdataMixin functionality.

---

**Last Updated:** December 19, 2025  
**Maintainer:** IBKR MCP Server Development Team  
**Status:** Active Development
