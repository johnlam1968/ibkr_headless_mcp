# MCP Server Tests

This directory contains test scripts for validating the IBKR MCP server functionality.

## Test Files

### `test_mcp_client.py`
Tests basic MCP server connectivity and tool availability:
- Initialize MCP session
- List available tools
- Test `call_endpoint` tool with various IBKR endpoints
- Test `endpoint_instructions` tool

Usage:
```bash
python3 tests/test_mcp_client.py
```

### `run_all_tests.sh`
Comprehensive test suite that runs multiple test scenarios:
- **Localhost connection tests** - Tests from outside Docker container
- **Symbol search tests** - Tests market data retrieval using `test_symbol.py`
- **Docker container tests** - Tests from inside Docker container

Usage:
```bash
./tests/run_all_tests.sh              # Run all tests
./tests/run_all_tests.sh --localhost  # Test only localhost connection
./tests/run_all_tests.sh --symbol     # Test market data with AAPL
./tests/run_all_tests.sh --container  # Test Docker container connection
./tests/run_all_tests.sh --help      # Show all options
```

### `test_symbol.py`
Comprehensive symbol workflow test using httpx:
- Initialize MCP session
- List available tools (required by MCP protocol)
- Test `get_accounts` endpoint
- Test `search_conids` endpoint (resolves symbols to conids)
- Test `get_snapshot_by_symbols` endpoint (handles session + symbol resolution + snapshot)
- Find contract by symbol (iserver/secdef/search)
- Get historical data (iserver/marketdata/history)

Usage:
```bash
python3 tests/test_symbol.py AAPL
python3 tests/test_symbol.py TSLA
```

**Note:** This script now works correctly! It demonstrates the full workflow including:
- Proper MCP session initialization with `clientInfo` parameter
- Using lowercase `"mcp-session-id"` header (case-sensitive)
- Parsing SSE responses that contain JSON strings
- Using the convenience endpoints that handle IBKR's dual-call requirement internally

## Test Requirements

### For Localhost Tests
- MCP server running on `http://localhost:8000`
- Python 3.11+ with `httpx` installed:
  ```bash
  pip install httpx
  ```

### For Docker Container Tests
- Docker installed and running
- `mcp-server` container running
- Docker network configured (script handles this automatically)

### For Market Data Tests
- Valid IBKR OAuth credentials configured in `.env` file
- IBKR account with market data subscription active
- Market open during testing hours

## Test Results

The `run_all_tests.sh --symbol` test validates that snapshot fields are properly populated using the `get_snapshot_by_symbols` endpoint which returns:
- **Symbol** (field 55)
- **Last Price** (field 31)
- **Bid** (field 84)
- **Ask** (field 86)
- **High** (field 70)
- **Low** (field 71)
- **Change** (field 82)
- **Change %** (field 83)

If any of these fields are empty, the test will fail with a warning about possible causes:
- Market is closed (outside trading hours)
- IBKR account not authenticated for market data
- Market data subscription not active

## Running Tests

### Quick Test (Localhost Only)
```bash
./tests/run_all_tests.sh --localhost
```

### Market Data Test (Most Common)
```bash
./tests/run_all_tests.sh --symbol
```

### Full Test Suite
```bash
./tests/run_all_tests.sh --all
```

### Individual Test Scripts
```bash
# Basic MCP connectivity
python3 tests/test_mcp_client.py

# Symbol workflow (comprehensive)
python3 tests/test_symbol.py AAPL
```

## Troubleshooting

### "Server not running on localhost:8000"
- Start the MCP server: `python3 src/endpoint_server.py`

### "Market data test failed - snapshot fields may be empty"
- Check that IBKR OAuth credentials are configured in `.env`
- Verify your IBKR account has market data subscription
- Ensure market is open (not outside trading hours)

### "mcp-server container is not running"
- Start the Docker container: `docker-compose up -d`
- Or manually: `docker run --name mcp-server -p 8000:8000 ibkr-mcp`

### Container network errors
- The test script automatically creates/uses `openclaw_default` network
- If you have network conflicts, use `--no-network` flag with `--container`
