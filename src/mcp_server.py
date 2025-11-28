import json
from fastmcp import FastMCP
from using_external_llm import (
    analyze_market,
    narrate_market_with_instructions
)
from utils import get_market_data

server = FastMCP("market-analysis-server")

@server.tool()
async def list_market_tools() -> str:
    """List available market analysis tools"""
    return "Available: get_market_data, get_custom_prompt, analyze_market with external LLM, narrate_market with external LLM"

@server.tool()
async def get_custom_prompt() -> str:
    """Get the user's custom prompt instructions for market analysis"""
    from settings import NARRATIVE_INSTRUCTIONS
    return NARRATIVE_INSTRUCTIONS

@server.tool()
async def get_market_snapshot() -> str:
    """Get current market snapshot to serve as context, no analysis"""
    try:
        return json.dumps(get_market_data(), indent=2)
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def analyze_question(question: str) -> str:
    """Analyze market question with with an external LLM, then serve context"""
    try:
        return analyze_market(question)
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def generate_narrative() -> str:
    """Generate detailed market narrative analysis with an external LLM, then serve context"""
    try:
        return narrate_market_with_instructions()
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    server.run()

# to run the server from command line:
# cd /home/john/CodingProjects/llm_public && PYTHONPATH=./src python src/mcp_server.py