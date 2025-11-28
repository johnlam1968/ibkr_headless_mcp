"""
LangChain foundation for multi-LLM support with market data context.

This module provides:
- LangChain Tool definitions for market data queries
- Multi-LLM provider instantiation (DeepSeek, OpenAI, etc.)
- Agent creation and invocation with market data context
- Direct IBKR client integration via web_api_client
"""

import json
import time
from typing import Any, Optional, Dict, List
from datetime import date, datetime
from decimal import Decimal

from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek

from web_api_client import iterate_to_get_data, get_conids, WATCHLIST_SYMBOLS, FIELDS


# ============================================================================
# Utility Functions
# ============================================================================

def _sanitize_for_json(obj: Any) -> Any:
    """Recursively sanitize the payload so it's JSON-serializable.

    - Converts bytes to UTF-8 strings
    - Converts datetimes/dates/Decimal to strings
    - Recurses into lists/tuples/sets/dicts
    - Falls back to str() for unknown types
    """
    # Basic primitives are safe
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # Bytes -> string
    if isinstance(obj, (bytes, bytearray)):
        try:
            return obj.decode("utf-8")
        except Exception:
            return str(obj)

    # Datetime/Date/Decimal -> iso / string
    if isinstance(obj, (datetime, date, Decimal)):
        try:
            return obj.isoformat()
        except Exception:
            return str(obj)

    # Dict-like: recurse
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for k, v in obj.items():
            try:
                key = str(k)
            except Exception:
                key = repr(k)
            out[key] = _sanitize_for_json(v)
        return out

    # Iterable: listify and recurse
    if isinstance(obj, (list, tuple, set)):
        return [_sanitize_for_json(v) for v in obj]

    # Last resort: try json.dumps, else str()
    try:
        json.dumps(obj)
        return obj
    except Exception:
        return str(obj)


def _remove_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove IBKR metadata fields not relevant for LLM analysis."""
    metadata_keys = {"_updated", "server_id", "conidEx", "market_data_marker", "market_data_availability", "service_params"}
    return {
        conid: {k: v for k, v in fields_dict.items() if k not in metadata_keys}
        if isinstance(fields_dict, dict) else fields_dict
        for conid, fields_dict in data.items()
    }


def _has_valid_prices(data: Dict[str, Any]) -> bool:
    """Check if data contains at least one instrument with a valid price."""
    if not data:
        return False
    price_keys = ("last_price", "Last", "mark_price")
    for fields_dict in data.values():
        if isinstance(fields_dict, dict):
            for key in price_keys:
                if fields_dict.get(key) not in (None, "N/A"):
                    return True
    return False


# Global cache for market data
_data_cache: Optional[Dict[str, Any]] = None
_conids_cache: Optional[List[str]] = None


def _get_watchlist_market_data(refresh: bool = False) -> Optional[Dict[str, Any]]:
    """
    Retrieve market data for all configured symbols.
    
    Args:
        refresh: Force refresh from API (bypass cache)
        
    Returns:
        Market data dict keyed by conid, or None if fetch fails
    """
    global _data_cache, _conids_cache
    
    if not refresh and _data_cache is not None:
        return _data_cache

    # Ensure we have conids
    if _conids_cache is None:
        from web_api_client import get_conids
        _conids_cache = get_conids(WATCHLIST_SYMBOLS)

    for attempt in range(3):
        data = iterate_to_get_data(conids=_conids_cache, fields=FIELDS)
        if data and _has_valid_prices(data):
            _data_cache = data
            return _data_cache
        if attempt < 2:
            time.sleep(0.5)
    
    _data_cache = data
    return _data_cache


def _get_market_json() -> str:
    """Fetch market data, remove metadata, sanitize, and return as JSON string."""
    data = _get_watchlist_market_data()
    if not data:
        return "Market data unavailable."
    
    filtered = _remove_metadata(data)
    sanitized = _sanitize_for_json(filtered)
    try:
        return json.dumps(sanitized, indent=2, default=str)
    except Exception:
        return json.dumps(sanitized, separators=(",", ":"), default=str)


# ============================================================================
# LangChain Tool Definitions
# ============================================================================


@tool
def get_market_data_tool() -> str:
    """Retrieve current market data for all configured financial instruments.
    Returns formatted data including price, change, and volatility metrics.
    Use this when the user asks for market conditions or current market state.
    """
    return _get_market_json()


@tool
def refresh_data() -> str:
    """Force refresh of all market data from the Interactive Brokers API.
    Use this to get the latest live data instead of cached data.
    Returns: Confirmation message with market data summary.
    """
    global _data_cache
    _data_cache = None  # Clear cache to force refresh
    return "Market data refreshed. " + _get_market_json()


# List of all available tools
MARKET_DATA_TOOLS = [
    get_market_data_tool,
    refresh_data,
]


# Public market data retrieval functions
def get_market_data(refresh: bool = False) -> Optional[Dict[str, Any]]:
    """Public wrapper for retrieving market data."""
    return _get_watchlist_market_data(refresh=refresh)


def get_market_summary() -> str:
    """Public wrapper for getting market summary."""
    return _get_market_json()



# ============================================================================
# Multi-LLM Support
# ============================================================================

class Agent:
    """Factory for creating and managing LLM agents with market data tools."""

    def __init__(self, model: str = "deepseek-chat", temperature: float = 0.7):
        """Initialize agent with LLM configuration."""
        self.model = model
        self.temperature = temperature
        self._agent = None

    def get_llm(self):
        """Instantiate the LLM for the current model."""
        if "deepseek" in self.model.lower():
            return ChatDeepSeek(model=self.model, temperature=self.temperature)
        elif "gpt" in self.model.lower() or "openai" in self.model.lower():
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=self.model, temperature=self.temperature)
        else:
            return ChatDeepSeek(model=self.model, temperature=self.temperature)

    def _create_agent(self, tools: list = None) -> Any:
        """Create a compiled agent with market data tools and optional extra tools."""
        llm = self.get_llm()
        agent_tools = tools if tools else MARKET_DATA_TOOLS
        
        # Use a basic system prompt for agent
        system_prompt = """You are a helpful financial market analysis assistant. 
Use the available tools to retrieve market data and provide insightful analysis.
Always provide clear, concise responses based on the data available."""
        
        agent = create_agent(
            llm, 
            tools=agent_tools, 
            system_prompt=system_prompt,
            debug=False
        )
        self._agent = agent
        return agent

    async def aask(self, query: str) -> str:
        """Async invoke the agent with a user query and return the final response."""
        if self._agent is None:
            self._create_agent()
        
        response_parts = []
        async for chunk in self._agent.astream({"input": query}):
            if "output" in chunk:
                response_parts.append(chunk["output"])
        
        return "".join(response_parts)

    def ask(self, query: str) -> str:
        """Synchronous wrapper for agent invocation (blocking call)."""
        if self._agent is None:
            self._create_agent()
        
        response = self._agent.invoke({"input": query})
        return response.get("output", str(response))


# ============================================================================
# Convenience API
# ============================================================================

def analyze_market(
    question: str,
    model: str = "deepseek-chat",
    temperature: float = 0.7,
) -> str:
    """Ask a question about market data and get an LLM response.
    
    Args:
        question: Natural language question about market data
        model: LLM model to use (default: deepseek-chat)
        temperature: LLM temperature (default: 0.7)
        
    Returns:
        LLM's response with market data context
    """
    agent = Agent(model=model, temperature=temperature)
    return agent.ask(question)


def narrate_market(
    model: str = "deepseek-chat",
    temperature: float = 0.7,
) -> str:
    """Generate a market narrative analysis using the LLM with market data.
    
    Args:
        model: LLM model to use (default: deepseek-chat)
        temperature: LLM temperature (default: 0.7)
        
    Returns:
        LLM's market narrative analysis
    """
    market_data = _get_market_json()
    if market_data == "Market data unavailable.":
        return market_data
    
    agent = Agent(model=model, temperature=temperature)
    return agent.ask(market_data)


def narrate_market_with_instructions(
    model: str = "deepseek-reasoner",
    temperature: float = 0.1,
) -> str:
    """Generate market narrative using LLM with NARRATIVE_INSTRUCTIONS as system prompt.
    
    Args:
        model: LLM model to use (default: deepseek-reasoner)
        temperature: LLM temperature (default: 0.1)
        
    Returns:
        LLM's market narrative analysis
    """
    from narrative_instructions import NARRATIVE_INSTRUCTIONS
    
    market_data = _get_market_json()
    if not market_data or market_data == "Market data unavailable.":
        return market_data
    
    llm = ChatDeepSeek(model=model, temperature=temperature)
    agent_exec = create_agent(
        llm,
        tools=MARKET_DATA_TOOLS,
        system_prompt=NARRATIVE_INSTRUCTIONS,
        debug=False,
    )
    
    response = agent_exec.invoke({"input": market_data})
    messages = response.get('messages', [])
    for msg in reversed(messages):
        if hasattr(msg, 'content') and msg.content and isinstance(msg.content, str):
            return msg.content
    
    return response.get('output', str(response))


