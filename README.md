# IBKR Headless MCP Server for Market Analysis

This project provides an MCP (Model Context Protocol) server and tools for analyzing Interactive Brokers (IBKR) market data using external LLMs (DeepSeek, OpenAI).

Using ibind's oauth feature, this headless application runs independent of a IBKR TWS/gateway or helper java program.

## Features
- Fetch live market data for watchlist symbols via IBKR API (ibind). 
- LangChain agents/tools for market queries and narratives.
- FastMCP server exposing tools: `get_market_snapshot`, `analyze_question`, `generate_narrative`.
- Multi-LLM support (DeepSeek default).
- Examples for standalone usage.

## Prerequisites
1. **IBKR Account**: Paper/live trading account with API access enabled.
2. **DeepSeek API Key**: Set `DEEPSEEK_API_KEY` in `.env`.
3. **oauth files stored in local folder. Refer to https://github.com/Voyz/ibind/wiki/OAuth-1.0a

## Quick Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy example config (create if missing)
cp src/settings.py.example src/settings.py  # Edit WATCHLIST_SYMBOLS, FIELDS as needed

# Set API key
echo "DEEPSEEK_API_KEY=your_key_here" > .env
```

**Note**: `src/settings.py` is required but not created automatically. Use the content below or customize:

```python
WATCHLIST_SYMBOLS = ["SPY", "QQQ", "IWM", "TLT", "GLD", "AAPL", "MSFT", "NVDA", "TSLA", "AMZN"]
FIELDS = [31, 66, 68, 84, 85, 86, 69, 70]  # lastPrice, change, etc.
NARRATIVE_INSTRUCTIONS = """[Your custom prompt for narratives]"""
```

## Usage

### 1. Test Standalone Examples
```bash
cd src
PYTHONPATH=.. python examples.py
```
- Generates market narrative.

### 2. Run MCP Server
```bash
cd /workspaces/ibkr_headless_mcp  # or project root
PYTHONPATH=./src python src/mcp_server.py
```
- Server runs on stdio transport (for MCP clients).
- Tools available: `list_market_tools`, `get_market_snapshot`, `analyze_question(question)`, `generate_narrative`.

### 3. LangChain Agent
```python
from src.langchain_agent import Agent
agent = Agent(model="deepseek-chat")
print(agent.ask("Compare SPY and QQQ?"))
```

## Architecture
```
src/
├── web_api_client.py  # IBKR API (ibind)
├── utils.py           # Data fetch/cache/JSON
├── langchain_tools.py # LangChain tools
├── langchain_agent.py # Agent factory
├── mcp_server.py      # FastMCP server
├── using_external_llm.py # LLM wrappers
└── examples.py        # Standalone tests
```

## Development
- Add symbols to `WATCHLIST_SYMBOLS`.
- Customize `NARRATIVE_INSTRUCTIONS`.
- Extend tools in `mcp_server.py`.

License: MIT
