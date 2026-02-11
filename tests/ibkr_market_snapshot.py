#!/usr/bin/env python3
"""
IBKR Market Data Wrapper - Get live market snapshots

Usage:
  python3 ibkr_market_snapshot.py <conid> [conid2] [conid3]...
  python3 ibkr_market_snapshot.py --help

Example:
  python3 ibkr_market_snapshot.py 842913519 842382870
  python3 ibkr_market_snapshot.py 842913519 --fields 31,84,86,70,71

Output:
  === 100 ===
  Symbol: 100
  Last: 523.50
  Bid: 523.50
  Ask: 525.00
  High: 555.00
  Low: 521.50
  Change: -15.50
  ChangePct: -2.88
  Volume: 572K
  MarketCap: 164.188B
"""

import sys
import json
import urllib.request

MCP_URL = "http://localhost:8000/mcp"
DEFAULT_FIELDS = "31,84,86,70,71,55,82,83,7289"

FIELD_NAMES = {
    "31": "Last",
    "55": "Symbol",
    "70": "High",
    "71": "Low",
    "82": "Change",
    "83": "ChangePct",
    "84": "Bid",
    "85": "AskSize",
    "86": "Ask",
    "87": "Volume",
    "7289": "MarketCap",
    "7290": "PE",
}


def mcp_request(url, data, headers, session_id=None):
    """Make MCP request."""
    headers = {**headers}
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode(), resp.headers.get("mcp-session-id")


def parse_sse_response(data):
    """Parse SSE response and extract market data."""
    try:
        # Response format: "data: {...}\r\n\r"
        if 'data:' in data:
            idx = data.index('data:') + 5
            json_str = data[idx:].strip()
            result = json.loads(json_str)
            
            content = result.get("result", {}).get("content", [])
            if content:
                inner_text = content[0].get("text", "")
                # Format: "NOTE: ... \n\n[{...}]"
                # Split on literal \n\n (backslash-n in the string)
                if '\\n\\n' in inner_text:
                    market_data = inner_text.split('\\n\\n', 1)[1]
                    # Unescape: \" -> "
                    market_data = market_data.encode().decode('unicode_escape')
                    # Extract the JSON array
                    start = market_data.find('[')
                    end = market_data.rfind(']') + 1
                    market_data = market_data[start:end]
                    parsed = json.loads(market_data)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        return parsed[0]
                    elif isinstance(parsed, dict):
                        return parsed
    except Exception as e:
        print(f"Parse error: {e}", file=sys.stderr)
    return None


def get_market_snapshot(conids, fields=None):
    """Get market data for given conid(s)."""
    fields = fields or DEFAULT_FIELDS
    
    # 1. Initialize
    print("=== 1. Initialize ===")
    init_data = {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                  "clientInfo": {"name": "ibkr-market-snapshot", "version": "1.0"}}
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    _, session_id = mcp_request(MCP_URL, init_data, headers)
    
    if not session_id:
        print("Failed to initialize MCP session", file=sys.stderr)
        sys.exit(1)
    print(f"Session: {session_id}")
    
    # 2. Authenticate
    print("\n=== 2. iserver/accounts ===")
    auth_data = {
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": "call_endpoint", "arguments": {"path": "iserver/accounts", "params": {}}}
    }
    mcp_request(MCP_URL, auth_data, headers, session_id)
    print("Authenticated")
    
    # 3. Get market data (CALL TWICE)
    results = []
    for conid in conids.split(","):
        conid = conid.strip()
        print(f"\n=== 3. marketdata/snapshot for {conid} ===")
        
        # First call - initialize subscription
        snapshot_data = {
            "jsonrpc": "2.0", "id": 10, "method": "tools/call",
            "params": {"name": "call_endpoint",
                      "arguments": {"path": "iserver/marketdata/snapshot",
                                  "params": {"conids": conid, "fields": fields}}}
        }
        resp, _ = mcp_request(MCP_URL, snapshot_data, headers, session_id)
        print(f"  Call 1 done")
        
        # Second call - get actual data
        snapshot_data["id"] = 11
        resp, _ = mcp_request(MCP_URL, snapshot_data, headers, session_id)
        print(f"  Call 2 done")
        
        data = parse_sse_response(resp)
        if data:
            results.append(data)
            print(f"  Parsed: {data.get('55', 'Unknown')} - Last: {data.get('31', 'N/A')}")
        else:
            print(f"  Failed to parse data")
    
    return results


def format_output(data_list):
    """Format market data for display."""
    for data in data_list:
        symbol = data.get("55", "Unknown")
        print(f"\n=== {symbol} ===")
        
        for field_id, field_name in FIELD_NAMES.items():
            value = data.get(field_id, "")
            if value:
                print(f"{field_name}: {value}")
        
        if len(data) <= 3:
            print("Raw:", json.dumps(data, indent=2))


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "-h"]:
        print(__doc__)
        sys.exit(0)
    
    conids = sys.argv[1]
    fields = sys.argv[2] if len(sys.argv) > 2 else None
    
    results = get_market_snapshot(conids, fields)
    
    if results:
        print("\n" + "="*50)
        format_output(results)
    else:
        print("No market data returned", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
