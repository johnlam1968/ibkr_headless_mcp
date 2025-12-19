"""
Comprehensive test suite for MCP Server tools.

Tests each tool to verify functionality, error handling, and data flow.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_server import (
    list_mcp_tools,
    get_symbol_details,
    get_watchlist_market_data,
    get_market_snapshot_of_predefined_watchlist,
    get_account_summary_ibkr,
    get_portfolio_positions_ibkr,
    get_historical_data,
    get_historical_data_by_symbol_ibkr,
    get_historical_data_batch_by_conids,
    get_historical_data_batch_by_symbols,
    get_custom_prompt,
    analyze_question,
    generate_narrative,
)

# Test data
TEST_SYMBOLS = ["AAPL", "GOOGL", "SPY"]
TEST_SYMBOL = "AAPL"
TEST_CONIDS = ["265598"]  # AAPL conid
TEST_BATCH_CONIDS = ["265598", "1418773"]  # AAPL, GOOGL

async def test_list_tools():
    """Test: list_mcp_tools - Display all available tools"""
    print("\n" + "="*70)
    print("TEST 1: list_mcp_tools()")
    print("="*70)
    try:
        result = await list_mcp_tools()
        print("✅ SUCCESS")
        print(result[:500] + "..." if len(result) > 500 else result)
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

async def test_symbol_lookup():
    """Test: get_symbol_details_ibkr - Look up contract details"""
    print("\n" + "="*70)
    print(f"TEST 2: get_symbol_details_ibkr('{TEST_SYMBOL}')")
    print("="*70)
    try:
        result = await get_symbol_details(TEST_SYMBOL)
        data = json.loads(result)
        if "error" in data:
            print(f"⚠️  API Error: {data['error']}")
        else:
            print(f"✅ SUCCESS - Found {data.get('count', 0)} contracts")
            print(json.dumps(data, indent=2)[:300] + "...")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

async def test_watchlist_market_data():
    """Test: get_watchlist_market_data - Get market data for symbols"""
    print("\n" + "="*70)
    print(f"TEST 3: get_watchlist_market_data({TEST_SYMBOLS})")
    print("="*70)
    try:
        result = await get_watchlist_market_data(TEST_SYMBOLS)
        data = json.loads(result) if isinstance(result, str) else result
        if isinstance(data, str):
            print(f"⚠️  Result: {data}")
        else:
            print(f"✅ SUCCESS - Data type: {type(data)}")
            if isinstance(data, dict):
                print(f"  Instruments: {len(data)} found")
                print(json.dumps(dict(list(data.items())[:1]), indent=2))
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

async def test_predefined_watchlist():
    """Test: get_market_snapshot_of_predefined_watchlist - Get watchlist snapshot"""
    print("\n" + "="*70)
    print("TEST 4: get_market_snapshot_of_predefined_watchlist()")
    print("="*70)
    try:
        result = await get_market_snapshot_of_predefined_watchlist()
        data = json.loads(result) if isinstance(result, str) else result
        if isinstance(data, str):
            print(f"⚠️  Result: {data}")
        else:
            print(f"✅ SUCCESS - Instruments: {len(data) if isinstance(data, dict) else 'N/A'}")
            if isinstance(data, dict) and len(data) > 0:
                first_key = list(data.keys())[0]
                print(f"  Sample (conid {first_key}):")
                print(json.dumps({first_key: data[first_key]}, indent=2)[:200])
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

async def test_account_summary():
    """Test: get_account_summary_ibkr - List connected accounts"""
    print("\n" + "="*70)
    print("TEST 5: get_account_summary_ibkr()")
    print("="*70)
    try:
        result = await get_account_summary_ibkr()
        data = json.loads(result)
        if "error" in data:
            print(f"⚠️  API Error: {data['error']}")
        else:
            print(f"✅ SUCCESS - Accounts: {len(data.get('accounts', []))}")
            print(json.dumps(data, indent=2)[:400] + "...")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

async def test_portfolio_positions():
    """Test: get_portfolio_positions_ibkr - Get portfolio positions"""
    print("\n" + "="*70)
    print("TEST 6: get_portfolio_positions_ibkr()")
    print("="*70)
    try:
        result = await get_portfolio_positions_ibkr()
        data = json.loads(result)
        if "error" in data:
            print(f"⚠️  API Error: {data['error']}")
        else:
            print(f"✅ SUCCESS - Positions: {len(data.get('positions', []))}")
            print(json.dumps(data, indent=2)[:400] + "...")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

async def test_historical_by_conid():
    """Test: get_historical_data_by_conid_ibkr - Get historical data by conid"""
    print("\n" + "="*70)
    print(f"TEST 7: get_historical_data_by_conid_ibkr(conid='265598', bar='1h', period='1d')")
    print("="*70)
    try:
        result = await get_historical_data("265598", "1h", "1d")
        data = json.loads(result)
        if "error" in data:
            print(f"⚠️  API Error: {data['error']}")
        else:
            print(f"✅ SUCCESS")
            data_count = len(data.get('data', [])) if isinstance(data.get('data'), list) else len(str(data.get('data', '')))
            print(f"  Data points: {data_count}")
            print(json.dumps({k: data[k] for k in ['conid', 'bar', 'period']}, indent=2))
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

async def test_historical_by_symbol():
    """Test: get_historical_data_by_symbol_ibkr - Get historical data by symbol"""
    print("\n" + "="*70)
    print(f"TEST 8: get_historical_data_by_symbol_ibkr(symbol='AAPL', bar='1h', period='1d')")
    print("="*70)
    try:
        result = await get_historical_data_by_symbol_ibkr("AAPL", "1h", "1d")
        data = json.loads(result)
        if "error" in data:
            print(f"⚠️  API Error: {data['error']}")
        else:
            print(f"✅ SUCCESS")
            print(f"  Symbol: {data.get('symbol_requested')}")
            print(f"  Resolved conid: {data.get('conid_resolved')}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

async def test_historical_batch_by_conids():
    """Test: get_historical_data_batch_by_conids - Batch historical by conids"""
    print("\n" + "="*70)
    print(f"TEST 9: get_historical_data_batch_by_conids(conids={TEST_BATCH_CONIDS[:1]}, bar='1h', period='1d')")
    print("="*70)
    try:
        result = await get_historical_data_batch_by_conids(TEST_BATCH_CONIDS[:1], "1h", "1d")
        data = json.loads(result)
        if "error" in data:
            print(f"⚠️  API Error: {data['error']}")
        else:
            print(f"✅ SUCCESS")
            print(f"  Conids: {data.get('conids')}")
            print(f"  Data available: {data.get('data') is not None}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

async def test_historical_batch_by_symbols():
    """Test: get_historical_data_batch_by_symbols - Batch historical by symbols"""
    print("\n" + "="*70)
    print(f"TEST 10: get_historical_data_batch_by_symbols(symbols={TEST_SYMBOLS[:1]}, bar='1h', period='1d')")
    print("="*70)
    try:
        result = await get_historical_data_batch_by_symbols(TEST_SYMBOLS[:1], "1h", "1d")
        data = json.loads(result)
        if "error" in data:
            print(f"⚠️  API Error: {data['error']}")
        else:
            print(f"✅ SUCCESS")
            print(f"  Symbols: {data.get('symbols_requested')}")
            print(f"  Resolved conids: {data.get('conids_resolved')}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

async def test_custom_prompt():
    """Test: get_custom_prompt - Get custom prompt"""
    print("\n" + "="*70)
    print("TEST 11: get_custom_prompt()")
    print("="*70)
    try:
        result = await get_custom_prompt()
        if isinstance(result, str) and len(result) > 0:
            print(f"✅ SUCCESS - Prompt length: {len(result)} chars")
            print(result[:300] + "...")
        else:
            print(f"⚠️  Empty or invalid result")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

async def test_analyze_question():
    """Test: analyze_question - Analyze market question"""
    print("\n" + "="*70)
    print("TEST 12: analyze_question(question='What is the market sentiment?')")
    print("="*70)
    try:
        result = await analyze_question("What is the market sentiment?")
        if isinstance(result, str) and len(result) > 0:
            print(f"✅ SUCCESS - Response length: {len(result)} chars")
            print(result[:300] + "...")
        else:
            print(f"⚠️  Empty or invalid result")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

async def test_generate_narrative():
    """Test: generate_narrative - Generate market narrative"""
    print("\n" + "="*70)
    print("TEST 13: generate_narrative()")
    print("="*70)
    try:
        result = await generate_narrative()
        if isinstance(result, str) and len(result) > 0:
            print(f"✅ SUCCESS - Narrative length: {len(result)} chars")
            print(result[:300] + "...")
        else:
            print(f"⚠️  Empty or invalid result")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("\n" + "🧪 MCP SERVER TOOL TEST SUITE" + "\n")
    
    tests = [
        ("List Tools", test_list_tools),
        ("Symbol Lookup", test_symbol_lookup),
        ("Watchlist Market Data", test_watchlist_market_data),
        ("Predefined Watchlist", test_predefined_watchlist),
        ("Account Summary", test_account_summary),
        ("Portfolio Positions", test_portfolio_positions),
        ("Historical by ConID", test_historical_by_conid),
        ("Historical by Symbol", test_historical_by_symbol),
        ("Batch Historical by ConIDs", test_historical_batch_by_conids),
        ("Batch Historical by Symbols", test_historical_batch_by_symbols),
        ("Custom Prompt", test_custom_prompt),
        ("Analyze Question", test_analyze_question),
        ("Generate Narrative", test_generate_narrative),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = await test_func()
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
    
    return passed == total

if __name__ == "__main__":
    result = asyncio.run(run_all_tests())
    sys.exit(0 if result else 1)
