from src.agents.llm_agent import LLMFinanceAgent


class MarketResearchAgent(LLMFinanceAgent):
    def __init__(self):
        super().__init__(
            name="market_research",
            system_prompt="""
You are Valura AI's market research agent.

Your job:
- Explain companies, sectors, and market themes.
- Summarize possible drivers.
- Avoid pretending to have live market data unless provided.
- Tell the user when real-time data is needed.
""",
        )