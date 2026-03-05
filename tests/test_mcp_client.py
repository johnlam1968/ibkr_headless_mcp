#!/usr/bin/env python3
"""Test client for the MCP server using SSE transport."""

import asyncio
import json
import sys
import httpx


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
                        print(f"   Received: {json.dumps(parsed)[:100]}...")
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


async def test_mcp_server():
    """Connect to MCP server and test tools."""
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
                        desc = tool.get('description', '')[:50]
                        print(f"     {desc}...")
    
    # Call call_endpoint tool
    print("\n3. Testing call_endpoint (iserver/accounts)...")
    auth_failed = False
    async with httpx.AsyncClient(timeout=60.0) as client:
        call_request = {
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": "call_endpoint", "arguments": {"path": "iserver/accounts", "params": {}}},
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
    
    # Call endpoint_instructions
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
    
    # Test secdef/search
    print("\n5. Testing secdef/search (AAPL)...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        call_request = {
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": "call_endpoint", "arguments": {"path": "iserver/secdef/search", "params": {"symbol": "AAPL", "sectype": "STK"}}},
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
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_mcp_server())