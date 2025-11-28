"""
LangChain foundation for multi-LLM support with market data context.

This module provides:
- LangChain Tool definitions for market data queries
- Multi-LLM provider instantiation (DeepSeek, OpenAI, etc.)
- Agent creation and invocation with market data context
- Direct IBKR client integration via web_api_client
"""


from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek

from langchain_agent import Agent
from langchain_tools import MARKET_DATA_TOOLS
from utils import _get_market_json
from web_api_client import get_conids



# ============================================================================
# Using external LLMs for market analysis
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
    from settings import NARRATIVE_INSTRUCTIONS
    
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


