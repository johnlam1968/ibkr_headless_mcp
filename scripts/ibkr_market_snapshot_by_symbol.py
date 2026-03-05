#!/usr/bin/env python3
"""
IBKR Market Snapshot by Symbol
Takes ticker symbol (e.g., QQQ, AAPL) as input, resolves to conid, then fetches market data.
Usage: python3 ibkr_market_snapshot_by_symbol.py <SYMBOL> [--delay SECONDS]
"""

import argparse
import json
import subprocess
import sys
import shlex

def search_conid(symbol):
    """Find conid for a given ticker symbol."""
    params = f'{{"symbol":"{symbol}","sectype":"STK"}}'
    cmd = f'python3 /home/node/.openclaw/workspace/bin/ibkr_mcp_wrapper.py call_endpoint path:iserver/secdef/search params:\'{params}\''
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        if data.get("data"):
            # Return first STK match
            for item in data["data"]:
                if item.get("symbol", "").upper() == symbol.upper():
                    return item.get("conid")
            # If exact match not found, return first
            return data["data"][0].get("conid")
    except Exception as e:
        print(f"Error searching for {symbol}: {e}", file=sys.stderr)
        print(f"stdout: {result.stdout}", file=sys.stderr)
        print(f"stderr: {result.stderr}", file=sys.stderr)
    return None

def get_snapshot(conid, delay=50):
    """Fetch market snapshot for conid."""
    params = f'{{"conids":"{conid}","fields":"31,55,70,71,82,83,84,86,87,6008,6070,6457,7051,7084,7085,7086,7087,7088,7089,7282,7283,7285,7289,7290,7291,7293,7294,7295,7296,7607,7633,7638,7644,7655,7674,7675,7676,7677,7682,7683,7684,7685,7686,7687,7688,7689,7690,7718,7741,7762"}}'
    
    cmd = f'python3 /home/node/.openclaw/workspace/bin/ibkr_mcp_wrapper.py call_endpoint path:iserver/marketdata/snapshot params:\'{params}\''
    
    print(f"Fetching market snapshot for conid {conid} (delay={delay}s)...", file=sys.stderr)
    
    # First call
    subprocess.run(cmd, shell=True, capture_output=True)
    
    # Wait for data to populate
    import time
    time.sleep(delay)
    
    # Second call
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

def main():
    parser = argparse.ArgumentParser(description="IBKR Market Snapshot by Symbol")
    parser.add_argument("symbol", help="Ticker symbol (e.g., QQQ, AAPL)")
    parser.add_argument("--delay", "-d", type=int, default=50, help="Delay seconds between API calls")
    args = parser.parse_args()

    print(f"Resolving {args.symbol} to conid...", file=sys.stderr)
    conid = search_conid(args.symbol)
    
    if not conid:
        print(f"Error: Could not find conid for {args.symbol}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found conid: {conid}", file=sys.stderr)
    
    # Get snapshot
    output = get_snapshot(conid, args.delay)
    
    # Parse and add symbol to output
    try:
        data = json.loads(output)
        if data.get("data") and len(data["data"]) > 0:
            data["data"][0]["requested_symbol"] = args.symbol
            print(json.dumps(data, indent=2))
        else:
            print(output)
    except:
        print(output)

if __name__ == "__main__":
    main()
