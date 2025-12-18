"""
IBKR MCP Server - Code Examples
================================

This file contains practical code examples for using the IBKR MCP server tools.
All examples assume the MCP server is running and tools are available.
"""

import json
import asyncio


# ============================================================================
# EXAMPLE 1: Basic Market Data Retrieval
# ============================================================================

async def example_get_stock_prices():
    """Get real-time prices for multiple stocks."""
    symbols = ["AAPL", "MSFT", "GOOGL"]
    
    result = await get_market_snapshot(symbols)
    data = json.loads(result)
    
    if "error" in data:
        print(f"Error: {data['error']}")
        return
    
    print(f"Market Data ({data['timestamp']}):")
    for conid, market_data in data['data'].items():
        last_price = market_data.get('31')
        bid = market_data.get('293')
        ask = market_data.get('292')
        print(f"  {conid}: Last=${last_price}, Bid=${bid}, Ask=${ask}")


# ============================================================================
# EXAMPLE 2: Symbol Verification
# ============================================================================

async def example_verify_symbol():
    """Verify a symbol exists and get contract details."""
    symbol = "AAPL"
    
    result = await get_symbol_details(symbol)
    data = json.loads(result)
    
    if "error" in data:
        print(f"Symbol '{symbol}' not found: {data['error']}")
        return None
    
    print(f"Found {data['count']} contract(s) for {symbol}:")
    for i, contract in enumerate(data['matches'], 1):
        print(f"  {i}. {contract.get('description')}")
        print(f"     Exchange: {contract.get('exchange')}")
        print(f"     ConID: {contract.get('conid')}")
    
    return data['matches'][0] if data['matches'] else None


# ============================================================================
# EXAMPLE 3: Portfolio Monitoring
# ============================================================================

async def example_portfolio_overview():
    """Get current portfolio positions and P&L."""
    # Get account summary first
    accounts_result = await get_account_summary()
    accounts_data = json.loads(accounts_result)
    
    if "error" in accounts_data:
        print(f"Error getting accounts: {accounts_data['error']}")
        return
    
    print(f"Connected accounts: {len(accounts_data['accounts'])}")
    
    # Get positions for first account
    positions_result = await get_portfolio_positions()
    positions_data = json.loads(positions_result)
    
    if "error" in positions_data:
        print(f"Error getting positions: {positions_data['error']}")
        return
    
    account_id = positions_data['account_id']
    positions = positions_data['positions']
    
    print(f"\nPortfolio for account {account_id}:")
    print("-" * 70)
    
    total_value = 0
    total_pnl = 0
    
    for pos in positions:
        symbol = pos.get('symbol')
        quantity = pos.get('quantity', 0)
        price = pos.get('marketPrice', 0)
        value = pos.get('marketValue', 0)
        pnl = pos.get('unrealizedPnl', 0)
        pnl_pct = pos.get('unrealizedPnlPercent', 0)
        
        print(f"{symbol:10} {quantity:>8} shares @ ${price:>8.2f} "
              f"= ${value:>12.2f} | P&L: ${pnl:>10.2f} ({pnl_pct:>6.2f}%)")
        
        total_value += value
        total_pnl += pnl
    
    print("-" * 70)
    print(f"{'TOTAL':10} {'':>8} {' ':>8} {' ':>8} "
          f"= ${total_value:>12.2f} | P&L: ${total_pnl:>10.2f}")


# ============================================================================
# EXAMPLE 4: Enhanced Market Data with Volatility
# ============================================================================

async def example_options_analysis():
    """Get market data including volatility for options analysis."""
    symbols = ["AAPL", "SPY"]
    
    result = await get_market_data_enhanced(
        symbols=symbols,
        include_bid_ask=True
    )
    data = json.loads(result)
    
    if "error" in data:
        print(f"Error: {data['error']}")
        return
    
    print(f"Enhanced Market Data ({data['timestamp']}):")
    print(f"Symbols: {', '.join(data['symbols'])}")
    print(f"Fields: {', '.join(data['fields_included'])}\n")
    
    for symbol, conid in zip(data['symbols'], data['data'].keys()):
        market_data = data['data'][conid]
        print(f"{symbol}:")
        print(f"  Price: ${market_data.get('last_price'):.2f}")
        print(f"  Bid: ${market_data.get('bid'):.2f}")
        print(f"  Ask: ${market_data.get('ask'):.2f}")
        print(f"  Historical Volatility: {market_data.get('historical_volatility'):.2%}")
        print(f"  Implied Volatility: {market_data.get('implied_volatility'):.2%}")
        print()


# ============================================================================
# EXAMPLE 5: LLM Integration - Stock Analyst
# ============================================================================

async def example_stock_analyst():
    """Use LLM to analyze stock prices."""
    analyst_persona = """You are an expert stock market analyst with 20+ years experience.
    Given real-time market data, provide:
    1. Technical analysis (trends, support/resistance)
    2. Sentiment analysis (positive/negative indicators)
    3. Investment recommendation (BUY/HOLD/SELL)
    4. Price target for next 3 months
    
    Be concise but comprehensive. Focus on actionable insights."""
    
    # Get market data
    symbols = ["AAPL"]
    market_result = await get_market_snapshot(symbols)
    market_data = json.loads(market_result)
    
    if "error" in market_data:
        print(f"Error getting market data: {market_data['error']}")
        return
    
    # Send to LLM analyst
    query = f"""Analyze this stock market data:
    
    {json.dumps(market_data, indent=2)}
    
    Provide your professional investment recommendation."""
    
    analysis = await call_llm(
        persona=analyst_persona,
        query=query,
        model="anthropic/claude-3.5-sonnet",
        temperature=0.7
    )
    
    print("STOCK ANALYST REPORT")
    print("=" * 70)
    print(analysis)


# ============================================================================
# EXAMPLE 6: LLM Integration - Portfolio Manager
# ============================================================================

async def example_portfolio_manager():
    """Use LLM to suggest portfolio rebalancing."""
    portfolio_manager_persona = """You are a professional portfolio manager specializing in:
    - Asset allocation optimization
    - Risk management and diversification
    - Tactical rebalancing
    - Market opportunity identification
    
    Analyze the provided portfolio and provide specific, actionable recommendations.
    Consider market conditions, volatility, and concentration risk."""
    
    # Get portfolio data
    positions_result = await get_portfolio_positions()
    positions_data = json.loads(positions_result)
    
    if "error" in positions_data:
        print(f"Error getting portfolio: {positions_data['error']}")
        return
    
    # Get volatility data for held symbols
    symbols = []
    for pos in positions_data.get('positions', []):
        if pos.get('symbol'):
            symbols.append(pos['symbol'])
    
    if symbols:
        vol_result = await get_market_data_enhanced(
            symbols=symbols,
            include_bid_ask=True
        )
        vol_data = json.loads(vol_result)
    else:
        vol_data = {}
    
    # Send to LLM portfolio manager
    query = f"""Review this portfolio and market conditions:
    
    Portfolio:
    {json.dumps(positions_data, indent=2)}
    
    Market Data:
    {json.dumps(vol_data, indent=2)}
    
    Provide rebalancing recommendations."""
    
    recommendations = await call_llm(
        persona=portfolio_manager_persona,
        query=query,
        model="google/gemini-2.0-flash-001",
        temperature=0.5
    )
    
    print("PORTFOLIO MANAGER RECOMMENDATIONS")
    print("=" * 70)
    print(recommendations)


# ============================================================================
# EXAMPLE 7: Risk Monitor
# ============================================================================

async def example_risk_monitor():
    """Monitor portfolio for risk exposures."""
    risk_monitor_persona = """You are a risk management specialist. Analyze portfolios for:
    - Concentration risk (single stock/sector exposure)
    - Volatility exposure
    - Correlation risk
    - Downside protection needs
    
    Identify risks and suggest mitigation strategies."""
    
    # Get portfolio positions
    positions_result = await get_portfolio_positions()
    positions_data = json.loads(positions_result)
    
    if "error" in positions_data:
        print(f"Error: {positions_data['error']}")
        return
    
    # Get market data with volatility
    symbols = [p['symbol'] for p in positions_data.get('positions', []) if p.get('symbol')]
    
    if not symbols:
        print("No positions to analyze")
        return
    
    vol_result = await get_market_data_enhanced(
        symbols=symbols,
        include_bid_ask=True
    )
    vol_data = json.loads(vol_result)
    
    # Analyze risk
    query = f"""Risk Assessment:
    
    Positions:
    {json.dumps(positions_data, indent=2)}
    
    Volatility Data:
    {json.dumps(vol_data, indent=2)}
    
    Assess portfolio risk and recommend hedging strategies."""
    
    risk_report = await call_llm(
        persona=risk_monitor_persona,
        query=query,
        model="anthropic/claude-3.5-sonnet",
        temperature=0.6
    )
    
    print("RISK ANALYSIS REPORT")
    print("=" * 70)
    print(risk_report)


# ============================================================================
# EXAMPLE 8: Error Handling Pattern
# ============================================================================

async def example_error_handling():
    """Demonstrate proper error handling."""
    
    # Test invalid symbol
    print("Testing invalid symbol...")
    result = await get_market_snapshot(["INVALID_XYZ_999"])
    data = json.loads(result)
    
    if "error" in data:
        print(f"✓ Handled error gracefully: {data['error']}")
    else:
        print("✓ Got market data (unexpected)")
    
    # Test with empty list
    print("\nTesting empty symbol list...")
    result = await get_market_snapshot([])
    data = json.loads(result)
    
    if "error" in data:
        print(f"✓ Handled empty list: {data['error']}")
    else:
        print("✓ Got market data (unexpected)")
    
    # Test with valid symbol
    print("\nTesting valid symbol...")
    result = await get_market_snapshot(["AAPL"])
    data = json.loads(result)
    
    if "error" in data:
        print(f"✗ Unexpected error: {data['error']}")
    else:
        print(f"✓ Got valid market data for {len(data.get('data', {}))} symbols")


# ============================================================================
# EXAMPLE 9: Batch Symbol Processing
# ============================================================================

async def example_batch_processing():
    """Process multiple symbols efficiently."""
    
    # Batch 1: Large-cap tech
    tech_symbols = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]
    
    # Batch 2: Index ETFs
    index_symbols = ["SPY", "QQQ", "IWM"]
    
    # Batch 3: Bonds
    bond_symbols = ["BND", "TLT", "AGG"]
    
    all_batches = [
        ("Technology", tech_symbols),
        ("Indices", index_symbols),
        ("Bonds", bond_symbols)
    ]
    
    results = {}
    
    for batch_name, symbols in all_batches:
        print(f"Getting {batch_name} data...")
        result = await get_market_snapshot(symbols)
        data = json.loads(result)
        
        if "error" not in data:
            results[batch_name] = data['data']
            print(f"  ✓ Retrieved {len(data['data'])} items")
        else:
            print(f"  ✗ Error: {data['error']}")
    
    # Summary
    print(f"\nTotal batches: {len(all_batches)}")
    print(f"Successful: {len(results)}")
    print(f"Total symbols retrieved: {sum(len(v) for v in results.values())}")


# ============================================================================
# EXAMPLE 10: Watchlist Monitoring
# ============================================================================

async def example_watchlist():
    """Monitor a watchlist of symbols."""
    
    watchlist = ["AAPL", "MSFT", "NVDA", "TSM", "ASML"]
    
    print(f"Monitoring {len(watchlist)} stocks...")
    print("-" * 70)
    
    result = await watch_symbols(watchlist)
    data = json.loads(result)
    
    if "error" in data:
        print(f"Error: {data['error']}")
        return
    
    print(f"Status: {data['status']}")
    print(f"Timestamp: {data['timestamp']}")
    print()
    
    # Show price data
    print("Watched Symbols:")
    for symbol, conid in zip(data['watched_symbols'], data['market_data'].keys()):
        market_data = data['market_data'][conid]
        last_price = market_data.get('31')
        bid = market_data.get('293')
        ask = market_data.get('292')
        spread = ask - bid if (ask and bid) else 0
        
        print(f"  {symbol:8} | Last: ${last_price:>8.2f} | "
              f"Bid: ${bid:>8.2f} | Ask: ${ask:>8.2f} | Spread: ${spread:.4f}")


# ============================================================================
# MAIN - Run all examples
# ============================================================================

async def main():
    """Run all examples (choose which ones to execute)."""
    
    examples = [
        ("Market Data Retrieval", example_get_stock_prices),
        ("Symbol Verification", example_verify_symbol),
        ("Portfolio Overview", example_portfolio_overview),
        ("Enhanced Market Data", example_options_analysis),
        ("Stock Analyst LLM", example_stock_analyst),
        ("Portfolio Manager LLM", example_portfolio_manager),
        ("Risk Monitor", example_risk_monitor),
        ("Error Handling", example_error_handling),
        ("Batch Processing", example_batch_processing),
        ("Watchlist Monitoring", example_watchlist),
    ]
    
    print("=" * 70)
    print("IBKR MCP Server - Code Examples")
    print("=" * 70)
    print()
    
    # Uncomment the examples you want to run:
    for name, example_func in examples:
        try:
            print(f"\n{'=' * 70}")
            print(f"EXAMPLE: {name}")
            print('=' * 70)
            await example_func()
        except Exception as e:
            print(f"Error in {name}: {str(e)}")
        
        # Uncomment below to run only first example
        # break


if __name__ == "__main__":
    asyncio.run(main())
