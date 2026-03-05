#!/usr/bin/env python3
"""Test MCP server with a specific symbol workflow, including detailed market data check."""

import asyncio
import httpx
import json
import sys


def check_auth_error(content_text):
    """Check if the response contains an authentication error.
    
    Returns True if there's an auth error (should exit), False if OK.
    """
    if not content_text:
        return False
    
    # Check for common auth error patterns
    error_patterns = [
        "IBKR client not initialized",
        "invalid consumer",
        "Session expired",
        "Unauthorized",
        "not authenticated",
    ]
    
    for pattern in error_patterns:
        if pattern.lower() in content_text.lower():
            return True
    
    return False


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
    
    # Test get_accounts endpoint
    auth_failed = False
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("\n   Testing get_accounts endpoint...")
        auth_req = {
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": "get_accounts", "arguments": {}},
            "id": 3
        }
        async with client.stream("POST", base_url, content=json.dumps(auth_req),
                               headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "mcp-session-id": session_id}) as resp:
            events = await read_sse(resp)
            for e in events:
                if 'result' in e:
                    content = e['result'].get('content', [])
                    for item in content:
                        if item.get('type') == 'text':
                            text = item.get('text', '')
                            print(f"   Response: {text[:200]}...")
                            if check_auth_error(text):
                                auth_failed = True
                elif 'error' in e:
                    print(f"   ✗ Auth error: {e['error']}")
                    auth_failed = True
    
    if auth_failed:
        print("\n" + "=" * 60)
        print("ERROR: IBKR authentication failed!")
        print("Please check your OAuth credentials in the .env file")
        print("Exiting early...")
        print("=" * 60)
        sys.exit(1)
    
    # Test search_conids endpoint
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"\n   Testing search_conids endpoint for '{symbol}'...")
        search_req = {
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": "search_conids", "arguments": {"symbols": symbol}},
            "id": 3
        }
        async with client.stream("POST", base_url, content=json.dumps(search_req),
                               headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "mcp-session-id": session_id}) as resp:
            events = await read_sse(resp)
            for e in events:
                if 'result' in e:
                    content = e['result'].get('content', [])
                    for item in content:
                        if item.get('type') == 'text':
                            text = item.get('text', '')
                            try:
                                data = json.loads(text)
                                if data and data.get('results'):
                                    conid = data['results'][0].get('conid')
                                    sym = data['results'][0].get('symbol')
                                    print(f"   ✓ search_conids found: {sym} - conid: {conid}")
                            except Exception as err:
                                print(f"   Error parsing: {err}")
                elif 'error' in e:
                    print(f"   ✗ Search error: {e['error']}")
    
    # Test get_snapshot_by_symbols endpoint
    async with httpx.AsyncClient(timeout=120.0) as client:
        print(f"\n   Testing get_snapshot_by_symbols endpoint for '{symbol}'...")
        snapshot_req = {
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": "get_snapshot_by_symbols", "arguments": {"symbols": symbol, "delay": 2}},
            "id": 3
        }
        async with client.stream("POST", base_url, content=json.dumps(snapshot_req),
                               headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "mcp-session-id": session_id}) as resp:
            events = await read_sse(resp)
            for e in events:
                if 'result' in e:
                    content = e['result'].get('content', [])
                    for item in content:
                        if item.get('type') == 'text':
                            text = item.get('text', '')
                            try:
                                data = json.loads(text)
                                if data and data.get('data'):
                                    market_data = data['data']
                                    print(f"   ✓ get_snapshot_by_symbols response received")
                                    print(f"   Fields: {list(market_data[0].keys())[:10]}...")
                            except Exception as err:
                                print(f"   Error parsing: {err}")
                elif 'error' in e:
                    print(f"   ✗ Snapshot error: {e['error']}")
    
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
    
    # Historical data
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"\n3. Getting historical data for {symbol}...")
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