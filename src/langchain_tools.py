# ============================================================================
# LangChain Tool Definitions
# ============================================================================


from utils import _data_cache
from utils import _get_market_json


from langchain_core.tools import tool


@tool
def get_market_data_tool() -> str:
    """Retrieve current market data for all configured financial instruments.
    Returns formatted data including price, change, and volatility metrics.
    Use this when the user asks for market conditions or current market state.
    """
    return _get_market_json()


@tool
def refresh_data_tool() -> str:
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
    refresh_data_tool,
]