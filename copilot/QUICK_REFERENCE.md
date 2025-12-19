# MCP Server Quick Reference Guide

## 🚀 Quick Start

```bash
cd /home/john/CodingProjects/llm_public
PYTHONPATH=./src python src/mcp_server.py
```

---

## 📋 All 13 Tools

### 1️⃣ Symbol Lookup
```python
get_symbol_details_ibkr("AAPL")
→ {symbol, matches[], count}
```

### 2️⃣ Real-Time Market Data
```python
get_watchlist_market_data(["AAPL", "SPY"])
→ {timestamp, symbols, conids, data{}}

get_market_snapshot_of_predefined_watchlist()
→ {market data for 31 configured symbols}
```

### 3️⃣ Account & Portfolio
```python
get_account_summary_ibkr()
→ {accounts[]}

get_portfolio_positions_ibkr("account_id")
→ {positions[]}
```

### 4️⃣ Historical Data (Single)
```python
get_historical_data_by_conid_ibkr("265598", "1h", "1d")
→ {conid, bar, period, data[]}

get_historical_data_by_symbol_ibkr("AAPL", "1h", "1d")
→ {symbol_requested, conid_resolved, bar, period, data[]}
```

### 5️⃣ Historical Data (Batch)
```python
get_historical_data_batch_by_conids(["265598", "1418773"], "1h", "1d")
→ {conids[], bar, period, parallel, data{}}

get_historical_data_batch_by_symbols(["AAPL", "GOOGL"], "1h", "1d")
→ {symbols[], conids_resolved[], bar, period, parallel, data{}}
```

### 6️⃣ Analysis Context
```python
get_market_snapshot_of_predefined_watchlist()
→ {31 watchlist instruments}
```

### 7️⃣ LLM Integration
```python
get_custom_prompt()
→ Analysis instructions for LLM

analyze_question("What is market sentiment?")
→ LLM analysis with context

generate_narrative()
→ Detailed market narrative
```

---

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────┐
│  Layer 3: MCP Server Tools              │  (13 high-level tools)
│  └→ get_symbol_details_ibkr()           │
│  └→ get_watchlist_market_data()         │
│  └→ get_account_summary_ibkr()          │
│  └→ ... (10 more tools)                 │
├─────────────────────────────────────────┤
│  Layer 2: Data Transformation (utils)   │  (Data cleaning & validation)
│  └→ get_market_data_of_watchlist()      │
│  └→ get_market_data_json()              │
│  └→ _sanitize_for_json()                │
│  └→ _remove_metadata()                  │
│  └→ _has_valid_prices()                 │
├─────────────────────────────────────────┤
│  Layer 1: IBKR API (ibind_web_client)   │  (Low-level API calls)
│  └→ get_conids()                        │
│  └→ iterate_to_fetch_market_data()      │
│  └→ get_historical_data_by_conid()      │
│  └→ get_historical_data_batch_by_conids()
└─────────────────────────────────────────┘
```

---

## 🔄 Data Flow Example

```
User Query: "Get AAPL price"
        ↓
[Layer 3] get_watchlist_market_data(["AAPL"])
        ↓
[Layer 2] get_market_data_of_watchlist(conids=[265598])
        ↓
[Layer 2] Validate prices with _has_valid_prices()
        ↓
[Layer 2] Remove metadata with _remove_metadata()
        ↓
[Layer 2] Sanitize with _sanitize_for_json()
        ↓
[Layer 1] iterate_to_fetch_market_data(conids=[265598])
        ↓
[Layer 1] Call IBKR API via _get_client()
        ↓
IBKR Server Response
        ↓
Format as JSON
        ↓
User Response: {symbol, conid, price, bid, ask, ...}
```

---

## 📊 Predefined Watchlist (31 Symbols)

```
Volatility Indices:
  VVIX, VIX, VXM, VIX1D, VIX9D, VIX3M, VIX6M, VIX1Y

Equity Indices:
  SPX, SPY, RSP, DIA, QQQ, IWM, MES, HSI, N225, XINA50, FXI

Futures:
  MBT, MCL, MGC

Forex:
  USD.JPY, DX

Treasuries:
  FVX, TNX, TYX

Alternative Assets:
  XAGUSD

Options Metrics:
  VOLI, SDEX, TDEX
```

---

## ⚙️ Configuration

### Settings File: `src/settings.py`

```python
# Watchlist symbols (configurable)
PREDEFINED_WATCHLIST_SYMBOLS = [
    "VVIX", "VIX", "VXM", "MBT", ...
]

# Market data fields (16 IBKR field IDs)
DEFAULT_FIELDS = ['55', '7051', '7635', '31', '70', ...]

# Custom analysis instructions
NARRATIVE_INSTRUCTIONS = "..."
```

---

## 🔧 Key Functions by Layer

### Layer 1: Low-Level API
| Function | Purpose | Returns |
|----------|---------|---------|
| `get_client()` | Initialize IBKR client | IbkrClient or None |
| `get_conids(symbols)` | Resolve symbols to IDs | list[int] |
| `iterate_to_fetch_market_data(conids, fields)` | Fetch with retry logic | dict or None |
| `get_historical_data_by_conid()` | Single historical fetch | (result, error) tuple |
| `get_historical_data_batch_by_conids()` | Batch historical fetch | (result, error) tuple |

### Layer 2: Transformation
| Function | Purpose | Returns |
|----------|---------|---------|
| `get_market_data_of_watchlist()` | Fetch & validate | dict or None |
| `get_market_data_json()` | Formatted output | JSON string |
| `_sanitize_for_json()` | Make JSON-safe | serializable object |
| `_remove_metadata()` | Clean IBKR fields | cleaned dict |
| `_has_valid_prices()` | Validate data | bool |

### Layer 3: MCP Tools
| Tool | Input | Output | Use Case |
|------|-------|--------|----------|
| `get_symbol_details_ibkr()` | symbol | JSON | Contract lookup |
| `get_watchlist_market_data()` | symbols, fields | JSON | Price snapshot |
| `get_market_snapshot_of_predefined_watchlist()` | none | JSON | Context for LLM |
| `get_historical_data_by_symbol_ibkr()` | symbol, bar, period | JSON | Technical analysis |
| ... | ... | ... | ... |

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastmcp'"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "IBKR client not initialized"
**Solution:** Ensure IBKR API credentials in `.env`:
```bash
cat .env
# Should have IBKR_ACCOUNT=... and other credentials
```

### Issue: "Failed to resolve symbol"
**Solution:** Check if symbol is valid:
```python
get_symbol_details_ibkr("SYMBOL")  # Verify first
```

### Issue: "No market data available"
**Solution:** Verify IBKR connection and market hours:
```python
get_market_snapshot_of_predefined_watchlist()  # Test watchlist
```

---

## 📈 Performance Notes

- **Symbol Resolution:** ~100ms per symbol via IBKR API
- **Market Data Fetch:** ~200-500ms for 31 symbols with retry logic
- **Historical Data:** ~300-1000ms per symbol depending on period
- **Batch Operations:** Parallelized when specified
- **No Caching:** Fresh data on every call (appropriate for MCP servers)

---

## 🔐 Security

- All IBKR credentials in `.env` (not in code)
- API key rotation supported
- No data persistence
- JSON output sanitized
- Error messages don't leak sensitive data

---

## 📚 File Structure

```
llm_public/
├── src/
│   ├── mcp_server.py           # 13 MCP tools (Layer 3)
│   ├── utils.py                # Data transformation (Layer 2)
│   ├── ibind_web_client.py    # IBKR API wrapper (Layer 1)
│   ├── settings.py             # Configuration
│   ├── using_external_llm.py   # LLM integration
│   └── ...
├── requirements.txt            # Dependencies
├── .env                        # IBKR credentials
├── TEST_RESULTS.md             # Test results
├── test_architecture.py        # Architecture tests
└── test_mcp_tools.py          # Tool tests
```

---

## 🎯 Common Use Cases

### Use Case 1: Get Market Context for LLM
```python
await get_market_snapshot_of_predefined_watchlist()
# Pass to LLM as context for analysis
```

### Use Case 2: Analyze Specific Symbols
```python
await get_watchlist_market_data(["AAPL", "GOOGL"])
# Check real-time prices
```

### Use Case 3: Historical Technical Analysis
```python
await get_historical_data_batch_by_symbols(
    ["AAPL", "SPY"],
    bar="1h",
    period="1w"
)
# Analyze price action
```

### Use Case 4: Portfolio Monitoring
```python
await get_portfolio_positions_ibkr()
# Track positions and P&L
```

### Use Case 5: LLM-Driven Analysis
```python
context = await get_market_snapshot_of_predefined_watchlist()
question = "What's the market sentiment?"
await analyze_question(question)  # Returns LLM analysis with context
```

---

## 📞 Support

For issues or questions:
1. Check `TEST_RESULTS.md` for validation results
2. Run `python test_architecture.py` to verify setup
3. Check IBKR connection: `python -c "from ibind_web_client import get_conids; print(get_conids(['AAPL']))"`
4. Review `.env` for credentials

---

**Last Updated:** December 19, 2025  
**Status:** ✅ Production Ready  
**Tools:** 13 available  
**Architecture:** 3-layer design
