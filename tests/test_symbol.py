#!/usr/bin/env python3
"""Test MCP server with a specific symbol workflow, including detailed market data check."""

import asyncio
import httpx
import json
import sys


async def read_sse(response):
    """Parse SSE response into list of events."""
    results = []
    buffer = ""
    async for chunk in response.aiter_bytes():
        buffer += chunk.decode('utf-8')
        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            if line.startswith('data:'):
                data = line[5:].strip()
                if data:
                    try:
                        results.append(json.loads(data))
                    except:
                        pass
    return results

def parse_sse_response(event):
    """Parse SSE response event and extract market data."""
    try:
        # event is already parsed JSON from SSE
        content = event.get("result", {}).get("content", [])
        if content:
            inner_text = content[0].get("text", "")
            # The text field is a JSON string that needs to be decoded first
            # Format: "NOTE: ... \n\n[{...}]"
            
            # First, decode the JSON string (since it's wrapped in quotes)
            if inner_text.startswith('"'):
                inner_text = json.loads(inner_text)
            
            # Now find the JSON array pattern
            start = inner_text.find('[')
            if start != -1:
                end = inner_text.rfind(']') + 1
                if end > start:
                    json_str = inner_text[start:end]
                    parsed = json.loads(json_str)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        return parsed[0]
                    elif isinstance(parsed, dict):
                        return parsed
    except Exception as e:
        print(f"Parse error: {e}")
        import traceback
        traceback.print_exc()
    return None


async def test_symbol_workflow(symbol):
    """Test symbol workflow: find contract, get market data with dual calls."""
    base_url = "http://localhost:8000/mcp"
    session_id = None
    
    print("============================================================")
    print(f"MCP Server Test - Symbol: {symbol}")
    print("============================================================")
    
    # Initialize session
    print("\n1. Initializing MCP session...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        init_req = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-symbol", "version": "1.0.0"}},
            "id":1
        }
        async with client.stream("POST", base_url, content=json.dumps(init_req),
                               headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}) as resp:
            session_id = resp.headers.get("mcp-session-id")
            print(f"   Session ID: {session_id}")
    
    # List tools first (as test_mcp_client.py does)
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("\n   Listing available tools...")
        tools_req = {
            "jsonrpc": "2.0", "method": "tools/list",
            "params": {},
            "id": 2
        }
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "mcp-session-id": session_id}
        async with client.stream("POST", base_url, content=json.dumps(tools_req),
                               headers=headers) as resp:
            events = await read_sse(resp)
            for e in events:
                if 'result' in e:
                    print(f"   ✓ Tools listed")
                elif 'error' in e:
                    print(f"   ✗ Error: {e['error']}")
    
    # Authenticate first (required before any market data calls)
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("\n   Authenticating with IBKR (iserver/accounts)...")
        auth_req = {
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": "call_endpoint", "arguments": {"path": "iserver/accounts", "params": {}}},
            "id": 3
        }
        async with client.stream("POST", base_url, content=json.dumps(auth_req),
                               headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "mcp-session-id": session_id}) as resp:
            events = await read_sse(resp)
            for e in events:
                if 'result' in e:
                    print(f"   ✓ Authenticated")
                elif 'error' in e:
                    print(f"   ✗ Auth error: {e['error']}")
    
    # Find contract
    conid = None
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"\n2. Finding contract for '{symbol}' (iserver/secdef/search)...")
        call_req = {
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": "call_endpoint", "arguments": {"path": "iserver/secdef/search", "params": {"symbol": symbol, "sectype": "STK"}}},
            "id": 2
        }
        async with client.stream("POST", base_url, content=json.dumps(call_req),
                               headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "mcp-session-id": session_id}) as resp:
            events = await read_sse(resp)
            for e in events:
                if 'error' in e:
                    print(f"   Error response: {e['error']}")
                if 'result' in e:
                    content = e['result'].get('content', [])
                    for item in content:
                        if item.get('type') == 'text':
                            text = item.get('text', '')
                            try:
                                data = json.loads(text)
                                if data:
                                    conid = data[0].get('conid')
                                    sym = data[0].get('symbol')
                                    print(f"   ✓ Found: {sym} - conid: {conid}")
                                else:
                                    print("   No results found")
                            except Exception as err:
                                print(f"   Error parsing: {err}")
    
    if not conid:
        print("   ✗ Could not get contract ID for market data test")
        print("\n" + "=" * 60)
        print("Test completed!")
        print("=" * 60)
        return
    
    # Market snapshot - Call TWICE as per IBKR API requirements
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"\n3. Getting market snapshot for {symbol} (conid={conid})")
        print("   Note: IBKR requires TWO calls to get market data")
        
        # First call - initialize subscription
        print("   Call 1: Initialize subscription")
        call_req = {
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": "call_endpoint", "arguments": {"path": "iserver/marketdata/snapshot", "params": {"conids": conid, "fields": "31,84,86,70,71,55,82,83"}}},
            "id": 3
        }
        async with client.stream("POST", base_url, content=json.dumps(call_req),
                               headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "mcp-session-id": session_id}) as resp:
            events = await read_sse(resp)
            for e in events:
                if 'result' in e:
                    content = e['result'].get('content', [])
                    for item in content:
                        if item.get('type') == 'text':
                            result = item.get('text', '')[:200]
                            print(f"   ✓ Call 1 response: {result}...")
                elif 'error' in e:
                    print(f"   ✗ Call 1 error: {e['error']}")
        
        # Second call - get actual data
        print("   Call 2: Retrieve market data")
        call_req["id"] = 4
        async with client.stream("POST", base_url, content=json.dumps(call_req),
                               headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "mcp-session-id": session_id}) as resp:
            events = await read_sse(resp)
            for e in events:
                if 'result' in e:
                    content = e['result'].get('content', [])
                    for item in content:
                        if item.get('type') == 'text':
                            result = item.get('text', '')
                            # Use the proper parser that handles escaped characters
                            market_data = parse_sse_response(e)
                            
                            if market_data:
                                print(f"   ✓ Call 2 response received")
                                print(f"   Fields available: {list(market_data.keys())}")
                                
                                # Check for price fields
                                price_fields = {
                                    "31": "Last Price",
                                    "84": "Bid",
                                    "86": "Ask",
                                    "70": "High",
                                    "71": "Low",
                                    "82": "Change",
                                    "83": "Change %",
                                    "55": "Symbol"
                                }
                                
                                print(f"\n   Price Data Analysis:")
                                has_price_data = False
                                for field_id, field_name in price_fields.items():
                                    value = market_data.get(field_id, "MISSING")
                                    if value is not None and value != "" and value != "MISSING":
                                        print(f"      {field_name} ({field_id}): {value}")
                                        # Convert field_id to int for comparison since dictionary keys are strings
                                        if int(field_id) in [31, 84, 86, 70, 71, 82, 83]:
                                            has_price_data = True
                                
                                if not has_price_data:
                                    print(f"      ⚠ WARNING: No price data (fields 31,84,86,70,71,82,83) returned")
                                    print(f"      This may be due to:")
                                    print(f"      - Market is closed (outside trading hours)")
                                    print(f"      - IBKR account not authenticated for market data")
                                    print(f"      - Market data subscription not active")
                                else:
                                    print(f"      ✓ Price data available")
                            else:
                                print(f"   ✗ Failed to parse market data from response")
    
    # Historical data
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"\n4. Getting historical data for {symbol}...")
        call_req = {
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": "call_endpoint", "arguments": {"path": "iserver/marketdata/history", "params": {"conid": conid, "period": "1d", "bar": "5min"}}},
            "id": 5
        }
        async with client.stream("POST", base_url, content=json.dumps(call_req),
                               headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "mcp-session-id": session_id}) as resp:
            events = await read_sse(resp)
            for e in events:
                if 'result' in e:
                    content = e['result'].get('content', [])
                    for item in content:
                        if item.get('type') == 'text':
                            result = item.get('text', '')[:200]
                            print(f"   ✓ Historical data retrieved: {result}...")
                elif 'error' in e:
                    print(f"   ✗ Historical data error: {e['error']}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    asyncio.run(test_symbol_workflow(symbol))