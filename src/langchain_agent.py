from langchain_tools import MARKET_DATA_TOOLS


from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek


from typing import Any


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