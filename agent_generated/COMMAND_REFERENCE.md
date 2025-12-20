# Command Reference: IBKR ContractMixin MCP Server

## Essential Commands

### Start the Server
```bash
cd /home/john/CodingProjects/llm_public
PYTHONPATH=./src /home/john/CodingProjects/llm/.venv/bin/python src/mcp_server.py
```

### Run Tests
```bash
cd /home/john/CodingProjects/llm_public
/home/john/CodingProjects/llm/.venv/bin/python test_contract_tools.py
```

### Check Server Status (Quick Test)
```bash
timeout 3 bash -c 'PYTHONPATH=./src /home/john/CodingProjects/llm/.venv/bin/python src/mcp_server.py 2>&1' || true
```

### View Server Code
```bash
cat src/mcp_server.py
```

### View Test Suite
```bash
cat test_contract_tools.py
```

### Count Lines of Code
```bash
wc -l src/mcp_server.py test_contract_tools.py IMPLEMENTATION.md QUICK_START.md
```

---

## Tool Invocations (via MCP Client)

### 1. Search Contract
```
Tool: search_contract
Parameters:
  symbol: "AAPL"
  search_by_name: null (optional)
  security_type: null (optional)
```

### 2. Get Contract Details
```
Tool: get_contract_details
Parameters:
  conid: "265598"
  security_type: "OPT"
  expiration_month: "JAN25"
  strike: "150"
  option_right: "C"
  exchange: null (optional)
  bond_issuer_id: null (optional)
```

### 3. Get Option Strikes
```
Tool: get_option_strikes
Parameters:
  conid: "265598"
  security_type: "OPT"
  expiration_month: "JAN25"
  exchange: null (optional)
```

### 4. Get Trading Rules
```
Tool: get_trading_rules
Parameters:
  conid: "265598"
  exchange: null (optional)
  is_buy: null (optional)
  modify_order: null (optional)
  order_id: null (optional)
```

### 5. Get Bond Filters
```
Tool: get_bond_filters
Parameters:
  bond_issuer_id: "e123456"
```

### 6. List Tools
```
Tool: list_tools
Parameters: (none)
```

---

## Verification Commands

### Verify FastMCP Installation
```bash
/home/john/CodingProjects/llm/.venv/bin/python -c "from fastmcp import FastMCP; print('✅ fastmcp installed')"
```

### Verify ibind Installation
```bash
/home/john/CodingProjects/llm/.venv/bin/python -c "from ibind import IbkrClient; print('✅ ibind installed')"
```

### Verify Server Loads
```bash
/home/john/CodingProjects/llm/.venv/bin/python -c "import sys; sys.path.insert(0, './src'); from mcp_server import server; print(f'✅ Server loaded: {server.name}')"
```

### Verify All Tools
```bash
/home/job/CodingProjects/llm/.venv/bin/python -c "
import sys
sys.path.insert(0, './src')
from mcp_server import (
    search_contract, 
    get_contract_details, 
    get_option_strikes, 
    get_trading_rules, 
    get_bond_filters, 
    list_tools
)
print('✅ All 6 tools imported successfully')
"
```

---

## Troubleshooting Commands

### Check Python Version
```bash
/home/john/CodingProjects/llm/.venv/bin/python --version
```

### Check Virtual Environment
```bash
which python
echo $VIRTUAL_ENV
```

### List Installed Packages
```bash
/home/john/CodingProjects/llm/.venv/bin/pip list | grep -E "fastmcp|ibind"
```

### Check Server Code for Syntax Errors
```bash
/home/john/CodingProjects/llm/.venv/bin/python -m py_compile src/mcp_server.py && echo "✅ No syntax errors"
```

### Check Test Code for Syntax Errors
```bash
/home/john/CodingProjects/llm/.venv/bin/python -m py_compile test_contract_tools.py && echo "✅ No syntax errors"
```

### Run Single Test
```bash
/home/john/CodingProjects/llm/.venv/bin/python -c "
import asyncio, sys, json
sys.path.insert(0, './src')
from test_contract_tools import test_json_serialization
asyncio.run(test_json_serialization())
"
```

---

## Integration Commands

### Add to Claude Desktop Config
```bash
# View current config
cat ~/.config/claude_desktop_config.json

# Add MCP server (edit manually or use this as template):
{
  \"mcpServers\": {
    \"ibkr-contract-search\": {
      \"command\": \"/home/john/CodingProjects/llm/.venv/bin/python\",
      \"args\": [\"/home/john/CodingProjects/llm_public/src/mcp_server.py\"],
      \"env\": {
        \"PYTHONPATH\": \"/home/john/CodingProjects/llm_public/src\"
      }
    }
  }
}
```

---

## File Management

### View Implementation Files
```bash
ls -lh src/mcp_server.py test_contract_tools.py IMPLEMENTATION.md QUICK_START.md
```

### Count Total Lines
```bash
find . -name "*.md" -o -name "*mcp_server.py" -o -name "*test_*.py" | xargs wc -l
```

### Check File Sizes
```bash
du -h src/mcp_server.py test_contract_tools.py *.md
```

### Backup Implementation
```bash
tar -czf ibkr_mcp_server_backup.tar.gz src/mcp_server.py test_contract_tools.py *.md
```

---

## Monitoring & Logging

### Monitor Server (with output)
```bash
timeout 5 bash -c 'PYTHONPATH=./src /home/john/CodingProjects/llm/.venv/bin/python -u src/mcp_server.py 2>&1' | tee server.log
```

### Check Error Messages
```bash
timeout 3 bash -c 'PYTHONPATH=./src /home/john/CodingProjects/llm/.venv/bin/python src/mcp_server.py 2>&1' | grep -i error || echo "No errors"
```

### Run Tests with Output
```bash
/home/john/CodingProjects/llm/.venv/bin/python test_contract_tools.py 2>&1 | tee test_results.txt
```

---

## Development Commands

### Format Code (if black installed)
```bash
/home/john/CodingProjects/llm/.venv/bin/pip install black
/home/john/CodingProjects/llm/.venv/bin/black src/mcp_server.py test_contract_tools.py
```

### Type Check (if mypy installed)
```bash
/home/john/CodingProjects/llm/.venv/bin/pip install mypy
/home/john/CodingProjects/llm/.venv/bin/mypy src/mcp_server.py
```

### Lint Code (if pylint installed)
```bash
/home/john/CodingProjects/llm/.venv/bin/pip install pylint
/home/john/CodingProjects/llm/.venv/bin/pylint src/mcp_server.py
```

---

## Quick Diagnostics Script

```bash
#!/bin/bash
echo "=== IBKR MCP Server Diagnostics ==="
echo ""
echo "Python Version:"
/home/john/CodingProjects/llm/.venv/bin/python --version
echo ""
echo "Required Packages:"
/home/john/CodingProjects/llm/.venv/bin/pip list | grep -E "fastmcp|ibind|python-dotenv"
echo ""
echo "File Status:"
ls -lh src/mcp_server.py test_contract_tools.py 2>/dev/null || echo "Files not found"
echo ""
echo "Syntax Check:"
/home/john/CodingProjects/llm/.venv/bin/python -m py_compile src/mcp_server.py && echo "✅ mcp_server.py" || echo "❌ mcp_server.py"
/home/john/CodingProjects/llm/.venv/bin/python -m py_compile test_contract_tools.py && echo "✅ test_contract_tools.py" || echo "❌ test_contract_tools.py"
echo ""
echo "Server Load Test:"
timeout 2 bash -c 'PYTHONPATH=./src /home/john/CodingProjects/llm/.venv/bin/python src/mcp_server.py 2>&1 | head -20' || true
```

---

## Performance Commands

### Measure Startup Time
```bash
time timeout 5 bash -c 'PYTHONPATH=./src /home/john/CodingProjects/llm/.venv/bin/python src/mcp_server.py >/dev/null 2>&1' || true
```

### Test Suite Execution Time
```bash
time /home/john/CodingProjects/llm/.venv/bin/python test_contract_tools.py >/dev/null
```

---

## Useful Aliases

Add to `.bashrc` or `.zshrc` for convenience:

```bash
# Start IBKR MCP Server
alias ibkr-mcp-start='cd /home/john/CodingProjects/llm_public && PYTHONPATH=./src /home/john/CodingProjects/llm/.venv/bin/python src/mcp_server.py'

# Run IBKR MCP Tests
alias ibkr-mcp-test='cd /home/john/CodingProjects/llm_public && /home/john/CodingProjects/llm/.venv/bin/python test_contract_tools.py'

# Quick diagnostics
alias ibkr-mcp-diag='/home/john/CodingProjects/llm/.venv/bin/python -c "import sys; sys.path.insert(0, \"./src\"); from mcp_server import server; print(f\"✅ Server: {server.name}\")"'

# View docs
alias ibkr-mcp-docs='cat /home/john/CodingProjects/llm_public/QUICK_START.md'
```

---

**Version:** 1.0.0  
**Last Updated:** December 19, 2025
