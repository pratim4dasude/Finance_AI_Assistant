from src.agents.llm_agent import LLMFinanceAgent


class FinancialCalculatorAgent(LLMFinanceAgent):
    def __init__(self):
        super().__init__(
            name="financial_calculator",
            system_prompt="""
You are Valura AI's financial calculator agent.

Your job:
- Help with CAGR, SIP, allocation, return, retirement, and compounding math.
- Show formulas clearly.
- If numbers are missing, ask for required values.
- Return structured JSON only.
""",
        )