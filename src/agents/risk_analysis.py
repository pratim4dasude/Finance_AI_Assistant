from src.agents.llm_agent import LLMFinanceAgent


class RiskAnalysisAgent(LLMFinanceAgent):
    def __init__(self):
        super().__init__(
            name="risk_analysis",
            system_prompt="""
You are Valura AI's risk analysis agent.

Your job:
- Detect concentration risk.
- Explain volatility, drawdown, downside exposure.
- Highlight behavioral risks.
- Suggest risk controls.
- Use simple language for novice investors.
""",
        )