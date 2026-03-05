#!/usr/bin/env python3
"""Unified test client for the MCP server.

Tests MCP server connectivity, IBKR authentication, and market data functionality.
"""

import asyncio
import json
import sys
import httpx


# ============================================================================
# Helper Functions
# ============================================================================

async def read_sse_response(response):
    """Read all SSE events from a response stream."""
    results = []
    buffer = ""
    
    async for chunk in response.aiter_bytes():
        buffer += chunk.decode('utf-8')
        
        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            line = line.strip()
            
            if line.startswith('data:'):
                data = line[5:].strip()
                if data:
                    try:
                        parsed = json.loads(data)
                        results.append(parsed)
                    except json.JSONDecodeError:
                        pass
    
    return results


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


# ============================================================================
# Test 1: MCP Server Connection Tests
# ============================================================================

async def test_mcp_server_connection():
    """Test MCP server connectivity and tools listing."""
    base_url = "http://localhost:8000/mcp"
    session_id = None
    
    # Test initialize
    print("\n1. Initializing MCP session...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            },
            "id": 1
        }
        
        async with client.stream(
            "POST", base_url,
            content=json.dumps(init_request),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        ) as response:
            print(f"   Status: {response.status_code}")
            session_id = response.headers.get("mcp-session-id")
            print(f"   Session ID: {session_id}")
            
            events = await read_sse_response(response)
            for event in events:
                if 'result' in event:
                    server_info = event['result'].get('serverInfo', {})
                    print(f"   Server: {server_info.get('name')}")
                    print(f"   Version: {server_info.get('version')}")
    
    # List tools
    print("\n2. Listing available tools...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        tools_request = {
            "jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2
        }
        
        async with client.stream(
            "POST", base_url,
            content=json.dumps(tools_request),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": session_id
            }
        ) as response:
            events = await read_sse_response(response)
            for event in events:
                if 'result' in event:
                    tools = event['result'].get('tools', [])
                    for tool in tools:
                        print(f"   - {tool.get('name')}")
    
    return session_id


async def test_ibkr_auth(session_id):
    """Test IBKR authentication by calling get_accounts endpoint."""
    base_url = "http://localhost:8000/mcp"
    auth_failed = False
    
    # Call get_accounts to test IBKR authentication
    print("\n3. Testing IBKR authentication (get_accounts)...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        call_request = {
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": "get_accounts", "arguments": {}},
            "id": 3
        }
        
        async with client.stream(
            "POST", base_url,
            content=json.dumps(call_request),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": session_id
            }
        ) as response:
            events = await read_sse_response(response)
            for event in events:
                if 'result' in event:
                    content = event['result'].get('content', [])
                    for item in content:
                        if item.get('type') == 'text':
                            text = item.get('text', '')
                            print(f"   Response: {text[:300]}...")
                            if check_auth_error(text):
                                auth_failed = True
                elif 'error' in event:
                    print(f"   Error: {event['error']}")
                    auth_failed = True
    
    if auth_failed:
        print("\n" + "=" * 50)
        print("ERROR: IBKR authentication failed!")
        print("Please check your OAuth credentials in the .env file")
        print("Exiting early...")
        print("=" * 50)
        sys.exit(1)


async def test_endpoint_instructions(session_id):
    """Test endpoint_instructions tool."""
    base_url = "http://localhost:8000/mcp"
    
    print("\n4. Testing endpoint_instructions...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        call_request = {
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": "endpoint_instructions", "arguments": {}},
            "id": 4
        }
        
        async with client.stream(
            "POST", base_url,
            content=json.dumps(call_request),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": session_id
            }
        ) as response:
            events = await read_sse_response(response)
            for event in events:
                if 'result' in event:
                    content = event['result'].get('content', [])
                    for item in content:
                        if item.get('type') == 'text':
                            print(f"   Response preview: {item.get('text', '')[:200]}...")
                elif 'error' in event:
                    print(f"   Error: {event['error']}")


async def test_secdef_search(session_id, symbol="AAPL"):
    """Test secdef/search endpoint."""
    base_url = "http://localhost:8000/mcp"
    
    print(f"\n5. Testing secdef/search ({symbol})...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        call_request = {
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": "call_endpoint", "arguments": {"path": "iserver/secdef/search", "params": {"symbol": symbol, "sectype": "STK"}}},
            "id": 5
        }
        
        async with client.stream(
            "POST", base_url,
            content=json.dumps(call_request),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": session_id
            }
        ) as response:
            events = await read_sse_response(response)
            for event in events:
                if 'result' in event:
                    content = event['result'].get('content', [])
                    for item in content:
                        if item.get('type') == 'text':
                            print(f"   Response: {item.get('text', '')[:300]}...")
                elif 'error' in event:
                    print(f"   Error: {event['error']}")


# ============================================================================
# Test 2: Symbol/Market Data Tests
# ============================================================================

async def test_symbol_market_data(session_id, symbol="AAPL"):
    """Test symbol search and market data snapshot."""
    base_url = "http://localhost:8000/mcp"
    
    print("\n" + "=" * 60)
    print(f"Testing Symbol Market Data: {symbol}")
    print("=" * 60)
    
    # Test search_conids endpoint
    print(f"\n1. Testing search_conids for '{symbol}'...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        search_req = {
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": "search_conids", "arguments": {"symbols": symbol}},
            "id": 3
        }
        async with client.stream("POST", base_url, content=json.dumps(search_req),
                               headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "mcp-session-id": session_id}) as resp:
            events = await read_sse_response(resp)
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
    print(f"\n2. Testing get_snapshot_by_symbols for '{symbol}'...")
    async with httpx.AsyncClient(timeout=120.0) as client:
        snapshot_req = {
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": "get_snapshot_by_symbols", "arguments": {"symbols": symbol, "delay": 2}},
            "id": 3
        }
        async with client.stream("POST", base_url, content=json.dumps(snapshot_req),
                               headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "mcp-session-id": session_id}) as resp:
            events = await read_sse_response(resp)
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


# ============================================================================
# Main Entry Points
# ============================================================================

async def test_mcp_server():
    """Run MCP server connection tests."""
    print("=" * 50)
    print("MCP Server Connection Tests")
    print("=" * 50)
    
    # Test 1: Initialize and list tools
    session_id = await test_mcp_server_connection()
    
    # Test 2: Test IBKR authentication (with early exit on failure)
    await test_ibkr_auth(session_id)
    
    # Test 3: Test endpoint instructions
    await test_endpoint_instructions(session_id)
    
    # Test 4: Test secdef search
    await test_secdef_search(session_id)
    
    print("\n" + "=" * 50)
    print("All connection tests completed!")
    print("=" * 50)


async def test_market_data(symbol="AAPL"):
    """Run market data tests."""
    print("=" * 50)
    print(f"Market Data Tests for {symbol}")
    print("=" * 50)
    
    # Initialize session
    session_id = await test_mcp_server_connection()
    
    # Test IBKR authentication (with early exit on failure)
    await test_ibkr_auth(session_id)
    
    # Test symbol market data
    await test_symbol_market_data(session_id, symbol)
    
    print("\n" + "=" * 50)
    print("All market data tests completed!")
    print("=" * 50)


async def test_all(symbol="AAPL"):
    """Run all tests."""
    print("=" * 50)
    print("Running All Tests")
    print("=" * 50)
    
    # Initialize session
    session_id = await test_mcp_server_connection()
    
    # Test IBKR authentication (with early exit on failure)
    await test_ibkr_auth(session_id)
    
    # Test endpoint instructions
    await test_endpoint_instructions(session_id)
    
    # Test secdef search
    await test_secdef_search(session_id)
    
    # Test symbol market data
    await test_symbol_market_data(session_id, symbol)
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    print("=" * 50)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified MCP server test client")
    parser.add_argument("--mode", choices=["connection", "market-data", "all"], default="all",
                        help="Test mode: connection, market-data, or all (default: all)")
    parser.add_argument("--symbol", default="AAPL",
                        help="Symbol to test for market data (default: AAPL)")
    
    args = parser.parse_args()
    
    if args.mode == "connection":
        asyncio.run(test_mcp_server())
    elif args.mode == "market-data":
        asyncio.run(test_market_data(args.symbol))
    else:
        asyncio.run(test_all(args.symbol))
