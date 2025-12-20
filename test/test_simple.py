"""
Simple test to verify the MCP server functions are properly defined.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import mcp_server

def test_function_definitions():
    """Test that all 26 functions are properly defined"""
    print("Testing function definitions...")
    
    # List of expected functions
    expected_functions = [
        'search_contract',
        'security_definition',
        'all_exchange_contracts',
        'contract_information',
        'currency_pairs',
        'currency_exchange_rate',
        'contract_info_and_rules',
        'algo_params',
        'get_bond_filters',
        'get_contract_details',
        'get_option_strikes',
        'get_trading_rules',
        'security_futures',
        'security_stocks',
        'trading_schedule',
        'live_marketdata_snapshot',
        'live_marketdata_snapshot_by_symbol',
        'marketdata_history_by_conid',
        'marketdata_history_by_symbol',
        'marketdata_history_by_conids',
        'marketdata_history_by_symbols',
        'historical_marketdata_beta',
        'regulatory_snapshot',
        'marketdata_unsubscribe',
        'marketdata_unsubscribe_all',
        'list_tools',
    ]
    
    missing = []
    for func_name in expected_functions:
        if hasattr(mcp_server, func_name):
            func = getattr(mcp_server, func_name)
            print(f"✅ {func_name}: {type(func)}")
        else:
            print(f"❌ {func_name}: NOT FOUND")
            missing.append(func_name)
    
    print(f"\nTotal functions found: {len(expected_functions) - len(missing)}/{len(expected_functions)}")
    
    if missing:
        print(f"Missing functions: {missing}")
        return False
    
    # Test that server is defined
    if hasattr(mcp_server, 'server'):
        print(f"\n✅ Server defined: {mcp_server.server.name}")
    else:
        print("\n❌ Server not defined")
        return False
    
    return True

def test_imports():
    """Test that all required imports work"""
    print("\nTesting imports...")
    
    try:
        from utils import get_client, extract_result_data, to_json
        print("✅ utils imports work")
    except Exception as e:
        print(f"❌ utils imports failed: {e}")
        return False
    
    try:
        from ibind import IbkrClient
        print("✅ ibind import works")
    except Exception as e:
        print(f"⚠️  ibind import warning: {e}")
        # This might be OK if credentials aren't set up
    
    return True

if __name__ == "__main__":
    print("🧪 SIMPLE MCP SERVER TEST")
    print("="*70)
    
    imports_ok = test_imports()
    functions_ok = test_function_definitions()
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    if imports_ok and functions_ok:
        print("✅ All basic tests passed!")
        print("\nTo run the MCP server:")
        print("  cd /home/john/CodingProjects/llm_public")
        print("  PYTHONPATH=./src python src/mcp_server.py")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
