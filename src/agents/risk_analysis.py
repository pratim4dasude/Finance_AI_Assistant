import json

from src.agents.llm_agent import LLMFinanceAgent
from src.agents.portfolio_health import PortfolioHealthAgent


class RiskAnalysisAgent(LLMFinanceAgent):
    def __init__(self):
        super().__init__(
            name="risk_analysis",
            system_prompt="""
                You are Finance AI's risk analysis agent.
                
                Your job:
                - Use computed portfolio data (NOT guesses).
                - Detect concentration risk.
                - Explain downside risk clearly.
                - Highlight volatility and drawdown exposure.
                - Suggest simple risk controls.
                - Never assume portfolio value is 0 unless given.
                
                Return JSON only.
            """,
        )

    def run(self, query, user_context, intent, classification=None):

        portfolio_agent = PortfolioHealthAgent()

        portfolio_analysis = portfolio_agent.run(
            query="analyze portfolio for risk",
            user_context=user_context,
            intent="portfolio_health_check",
        )["data"]

        # If no OpenAI key → fallback
        if not self.client:
            return {
                "agent": self.name,
                "intent": intent,
                "data": {
                    "message": "OPENAI_API_KEY missing",
                    "portfolio_analysis": portfolio_analysis,
                },
            }


        prompt = f"""
User query:
{query}

Portfolio analysis:
{json.dumps(portfolio_analysis, indent=2)}

Based on this, explain downside risk.

Return JSON:
{{
  "summary": "",
  "portfolio_snapshot": {{
    "total_value": null,
    "top_holding": null,
    "top_holding_weight_pct": null,
    "top_3_weight_pct": null,
    "risk_flag": null
  }},
  "analysis": [],
  "risks": [],
  "recommendations": [],
  "next_steps": [],
  "disclaimer": "This is educational information, not financial advice."
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=900,
            )

            raw = response.choices[0].message.content.strip()

            if raw.startswith("```"):
                raw = raw.replace("```json", "").replace("```", "").strip()

            data = json.loads(raw)

            return {
                "agent": self.name,
                "intent": intent,
                "data": data,
            }

        except Exception as e:
            return {
                "agent": self.name,
                "intent": intent,
                "data": {
                    "error": str(e),
                    "portfolio_analysis": portfolio_analysis,
                },
            }