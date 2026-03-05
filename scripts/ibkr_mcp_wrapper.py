#!/usr/bin/env python3
"""
IBKR MCP Wrapper - For IBKR-endpoints MCP server

Usage: python3 ibkr_mcp_wrapper.py <tool> [arg:value ...]
       python3 ibkr_mcp_wrapper.py --list        # List available tools

Examples:
  # List available tools
  python3 ibkr_mcp_wrapper.py --list

  # Get account info
  python3 ibkr_mcp_wrapper.py call_endpoint path:iserver/accounts params:'{}'

  # Search contract by symbol
  python3 ibkr_mcp_wrapper.py call_endpoint path:iserver/secdef/search params:'{"symbol":"AAPL","sectype":"STK"}'

  # Get market snapshot (MUST call iserver/accounts first)
  python3 ibkr_mcp_wrapper.py call_endpoint path:iserver/marketdata/snapshot params:'{"conids":"265598","fields":"31,84,86"}'

  # Get historical data
  python3 ibkr_mcp_wrapper.py call_endpoint path:iserver/marketdata/history params:'{"conid":"265598","period":"5d","bar":"1d"}'

  # Get API documentation
  python3 ibkr_mcp_wrapper.py endpoint_instructions

  # Get market data fields (if available)
  python3 ibkr_mcp_wrapper.py market_data_fields

Environment Variables:
  IBKR_SERVER - MCP server URL (default: http://mcp-server:8000/mcp)

Note: Market snapshot requires calling iserver/accounts first, then calling snapshot twice.
"""

import json
import sys
import os
import urllib.request
import urllib.error

# Make server URL configurable via environment variable
IBKR_SERVER = os.environ.get("IBKR_SERVER", "http://mcp-server:8000/mcp")

# Counter for unique request IDs
_request_id_counter = 0
_session_id = None


def parse_sse(text):
    """Parse SSE response, returning all events found."""
    events = []
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('data:'):
            try:
                events.append(json.loads(line[5:].strip()))
            except json.JSONDecodeError:
                pass
    return events


def mcp_request(method, params=None, session_id=None):
    """Make an MCP request to the server."""
    global _request_id_counter
    _request_id_counter += 1
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    if session_id:
        headers["mcp-session-id"] = str(session_id)
    
    payload = {
        "jsonrpc": "2.0",
        "id": str(_request_id_counter),
        "method": method,
        "params": params or {}
    }
    
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(IBKR_SERVER, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=30) as response:
            text = response.read().decode()
            new_sess = response.headers.get("mcp-session-id")
            return text, new_sess or session_id
    except urllib.error.HTTPError as e:
        return json.dumps({"error": f"HTTP {e.code}: {e.reason}"}), session_id
    except Exception as e:
        return json.dumps({"error": str(e)}), session_id


def initialize():
    """Initialize MCP session and return session ID."""
    global _session_id
    
    init_text, _session_id = mcp_request("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "ibkr-wrapper", "version": "1.1.0"}
    })
    
    init_events = parse_sse(init_text)
    if not init_events:
        print(json.dumps({"error": "No response from MCP server"}, indent=2))
        return None
    
    init_parsed = init_events[-1]
    if "error" in init_parsed:
        print(json.dumps(init_parsed, indent=2))
        return None
    
    return _session_id


def list_tools():
    """List all available tools from the MCP server."""
    global _session_id
    
    if not _session_id:
        initialize()
    
    if not _session_id:
        print(json.dumps({"error": "Failed to initialize MCP session"}, indent=2))
        return
    
    # Get tools/list
    result_text, _ = mcp_request("tools/list", {}, _session_id)
    result_events = parse_sse(result_text)
    
    for event in result_events:
        if "result" in event:
            tools = event["result"].get("tools", [])
            print(f"Available tools ({len(tools)}):")
            for t in tools:
                name = t.get("name", "unknown")
                desc = t.get("description", "")
                print(f"  - {name}")
                if desc:
                    # Indent description
                    for line in desc.split('\n'):
                        print(f"    {line}")
            return
    
    # If no tools found, print raw response
    print(result_text)


def call_tool(tool, args):
    """Call a specific tool with given arguments."""
    global _session_id
    
    if not _session_id:
        initialize()
    
    if not _session_id:
        print(json.dumps({"error": "Failed to initialize MCP session"}, indent=2))
        return
    
    result_text, new_session_id = mcp_request("tools/call", {
        "name": tool,
        "arguments": args
    }, _session_id)
    
    if new_session_id:
        _session_id = new_session_id
    
    result_events = parse_sse(result_text)
    
    if not result_events:
        print(json.dumps({"error": "No response from MCP server"}, indent=2))
        return
    
    found_result = False
    for event in result_events:
        if "error" in event:
            print(json.dumps(event, indent=2))
            return
        elif "result" in event:
            found_result = True
            content = event["result"].get("content", [])
            for item in content:
                if item.get("type") == "text":
                    print(item["text"])
                else:
                    print(json.dumps(item, indent=2))
    
    if not found_result:
        print(result_text)


def main():
    global _session_id
    
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    # Check for --list flag
    if sys.argv[1] == "--list":
        initialize()
        list_tools()
        sys.exit(0)
    
    tool = sys.argv[1]
    
    # Parse args - handle special formats
    args = {}
    for arg in sys.argv[2:]:
        if ":" in arg:
            key, value = arg.split(":", 1)
            if value.lower() == "null":
                value = None
            elif value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.startswith("{"):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass
            elif value.startswith("["):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass
            args[key] = value
    
    # Call the tool
    call_tool(tool, args)


if __name__ == "__main__":
    main()
