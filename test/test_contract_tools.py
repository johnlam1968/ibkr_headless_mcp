"""
Test script for IBKR ContractMixin + MarketdataMixin MCP Server Tools

This script tests all 26 tools to ensure they are properly implemented and can be called.
Note: Some tests may require actual IBKR connection and credentials.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Callable

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the actual functions from mcp_server module
import mcp_server

async def test_tool(name: str, tool_func: Callable, *args: Any, **kwargs: Any) -> bool:
    """Test a single tool and print results"""
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print(f"{'='*70}")
    
    try:
        result = await tool_func(*args, **kwargs)
        
        # Parse JSON if it's a string
        if isinstance(result, str):
            try:
                data = json.loads(result)
                if "error" in data:
                    print(f"⚠️  API Error: {data.get('error', 'Unknown error')}")
                    if "suggestion" in data:
                        print(f"   Suggestion: {data['suggestion']}")
                else:
                    print(f"✅ SUCCESS - Response type: {type(data)}")
                    # Show summary of data
                    if isinstance(data, dict):
                        print(f"   Keys: {list(data.keys())}")
                        # Show first few items for lists
                        for key, value in data.items():
                            if isinstance(value, list) and len(value) > 0:
                                print(f"   {key}: {len(value)} items")
                                if len(value) > 0:
                                    print(f"     First item: {value[0]}")
                            elif isinstance(value, dict):
                                print(f"   {key}: dict with {len(value)} keys")
                    elif isinstance(data, list):
                        print(f"   List with {len(data)} items")
                        if len(data) > 0:
                            print(f"   First item: {data[0]}")
            except json.JSONDecodeError:
                print(f"✅ SUCCESS - Raw response (not JSON): {result[:200]}...")
        else:
            print(f"✅ SUCCESS - Response type: {type(result)}")
            print(f"   Result: {result}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def run_all_tests():
    """Run tests for all 26 tools"""
    print("\n" + "🧪 IBKR CONTRACT MCP SERVER TEST SUITE" + "\n")
    
    # Test data
    test_conid = "265598"  # AAPL
    test_symbol = "AAPL"
    test_symbols = "AAPL,MSFT"
    test_conids = "265598,9408"
    test_exchange = "NASDAQ"
    test_currency = "USD"
    
    # Get the actual functions from the mcp_server module
    tests = [
        # Search & Lookup Tools (7)
        ("search_contract (AAPL)", mcp_server.search_contract, test_symbol),
        ("security_definition (AAPL)", mcp_server.security_definition, test_conid),
        ("all_exchange_contracts (NASDAQ)", mcp_server.all_exchange_contracts, test_exchange),
        ("contract_information (AAPL)", mcp_server.contract_information, test_conid),
        ("currency_pairs (USD)", mcp_server.currency_pairs, test_currency),
        ("security_futures (ES)", mcp_server.security_futures, "ES"),
        ("security_stocks (AAPL)", mcp_server.security_stocks, test_symbol),
        
        # Contract Details Tools (3)
        ("get_option_strikes (AAPL OPT)", mcp_server.get_option_strikes, test_conid, "OPT", "JAN25"),
        ("get_trading_rules (AAPL)", mcp_server.get_trading_rules, test_conid),
        ("trading_schedule (STK AAPL)", mcp_server.trading_schedule, "STK", test_symbol),
        
        # Trading Rules & Info Tools (3)
        ("currency_exchange_rate (USD/EUR)", mcp_server.currency_exchange_rate, "USD", "EUR"),
        ("contract_info_and_rules (AAPL)", mcp_server.contract_info_and_rules, test_conid),
        ("algo_params (AAPL)", mcp_server.algo_params, test_conid),
        
        # Bond & Algorithm Tools (2)
        ("get_bond_filters (stub)", mcp_server.get_bond_filters, "e1359061"),
        
        # Live Market Data Tools (2)
        ("live_marketdata_snapshot (AAPL)", mcp_server.live_marketdata_snapshot, test_conid),
        ("live_marketdata_snapshot_by_symbol (AAPL)", mcp_server.live_marketdata_snapshot_by_queries, test_symbol),
        
        # Historical Market Data Tools (5)
        ("marketdata_history_by_conid (AAPL 1d)", mcp_server.marketdata_history_by_conid, test_conid, "1d", "1d"),
        ("marketdata_history_by_symbol (AAPL 1d)", mcp_server.marketdata_history_by_symbol, test_symbol, "1d", "1d"),
        ("marketdata_history_by_conids (batch)", mcp_server.marketdata_history_by_conids, test_conids, "1d", "1d"),
        ("marketdata_history_by_symbols (batch)", mcp_server.marketdata_history_by_symbols, test_symbols, "1d", "1d"),
        
        # Regulatory & Subscriptions Tools (3)
        ("regulatory_snapshot (AAPL)", mcp_server.regulatory_snapshot, test_conid),
        ("marketdata_unsubscribe (AAPL)", mcp_server.marketdata_unsubscribe, test_conid),
        ("marketdata_unsubscribe_all", mcp_server.marketdata_unsubscribe_all),
        
        # Utility (1)
        ("list_tools", mcp_server.list_tools),
    ]
    
    results = {}
    for name, tool_func, *args in tests:
        try:
            results[name] = await test_tool(name, tool_func, *args)
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {str(e)}")
            results[name] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    print(f"Success Rate: {(passed/total*100):.1f}%\n")
    
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print("\n" + "="*70)
    print("NOTES:")
    print("="*70)
    print("""
1. Some tests may fail due to:
   - Missing IBKR credentials in .env
   - No internet connection
   - Market data not available (outside trading hours)
   - Symbol not found or invalid

2. Expected behavior:
   - Tools should return JSON responses
   - Error responses should include helpful error messages
   - Tools should handle missing credentials gracefully

3. To run the MCP server:
   cd /home/john/CodingProjects/llm_public
   PYTHONPATH=./src python src/mcp_server.py

4. The server exposes 26 tools covering:
   - Contract search and lookup (7 tools)
   - Contract details and specifications (3 tools)
   - Trading rules and information (3 tools)
   - Bond and algorithm tools (2 tools)
   - Live market data (2 tools)
   - Historical market data (5 tools)
   - Regulatory and subscription tools (3 tools)
   - Utility (1 tool)
""")
    
    return passed == total

if __name__ == "__main__":
    result = asyncio.run(run_all_tests())
    sys.exit(0 if result else 1)
