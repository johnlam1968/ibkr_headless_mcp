import json
from fastmcp import FastMCP
from llm_foundation import (
    get_market_data, 
    analyze_market,
    narrate_market_with_instructions
)

server = FastMCP("market-analysis-server")

@server.tool()
async def list_market_tools() -> str:
    """List available market analysis tools"""
    return "Available: get_market_data, analyze_market, narrate_market"

@server.tool()
async def get_market_snapshot() -> str:
    """Get current market snapshot"""
    try:
        return json.dumps(get_market_data(), indent=2)
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def analyze_question(question: str) -> str:
    """Analyze market question with AI"""
    try:
        return analyze_market(question)
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def generate_narrative() -> str:
    """Generate detailed market narrative analysis"""
    try:
        return narrate_market_with_instructions()
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    server.run()

# to run the server from command line:
# cd /home/john/CodingProjects/llm_public && PYTHONPATH=./src python src/mcp_server.py