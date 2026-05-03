import json

from src.agents.llm_agent import LLMFinanceAgent
from src.agents.portfolio_health import PortfolioHealthAgent


class RecommendationsAgent(LLMFinanceAgent):
    def __init__(self):
        super().__init__(
            name="recommendations",
            system_prompt="""
You are Valura AI's recommendations agent.

Your job:
- For portfolio strategy questions, use computed portfolio analysis.
- For product recommendation questions, recommend suitable products/funds without claiming guarantees.
- Never give reckless financial advice.
- Avoid guaranteed-return language.
- Be clear, beginner-friendly, and structured.
Return JSON only.
""",
        )

    def run(self, query, user_context, intent, classification=None):
        is_product_recommendation = (
            classification
            and classification.agent == "product_recommendation"
        ) or intent == "product_recommendation"

        portfolio_analysis = None

        if not is_product_recommendation:
            portfolio_agent = PortfolioHealthAgent()
            portfolio_analysis = portfolio_agent.run(
                query="Analyze portfolio before recommendation",
                user_context=user_context,
                intent="portfolio_health_check",
                classification=classification,
            )["data"]

        if not self.client:
            return {
                "agent": self.name,
                "intent": intent,
                "data": {
                    "message": "OPENAI_API_KEY is missing. Add it in .env file.",
                    "portfolio_analysis": portfolio_analysis,
                    "fallback": True,
                },
            }

        if is_product_recommendation:
            prompt = self._product_prompt(query, user_context)
        else:
            prompt = self._portfolio_prompt(query, portfolio_analysis)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1000,
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
                    "message": "Recommendation agent failed while generating response.",
                    "portfolio_analysis": portfolio_analysis,
                },
            }

    def _portfolio_prompt(self, query, portfolio_analysis):
        return f"""
User query:
{query}

Computed portfolio analysis:
{json.dumps(portfolio_analysis, indent=2)}

Use the computed portfolio values, weights, risk flags, and observations.
Do not say portfolio value is 0 unless portfolio_analysis says it is 0.

Return JSON only with this structure:
{{
  "summary": "short useful answer",
  "portfolio_snapshot": {{
    "total_value": null,
    "top_holding": null,
    "top_holding_weight_pct": null,
    "top_3_weight_pct": null,
    "risk_flag": null
  }},
  "analysis": [],
  "recommendations": [],
  "risks": [],
  "next_steps": [],
  "disclaimer": "This is educational information, not financial advice."
}}
"""

    def _product_prompt(self, query, user_context):
        return f"""
User query:
{query}

User profile:
{{
  "risk_profile": "{user_context.risk_profile}",
  "base_currency": "{user_context.base_currency}"
}}

This is a product recommendation request.
Do not say the portfolio has no holdings.
Recommend suitable product categories or examples based on the query and risk profile.
Do not claim guaranteed returns.
Mention that the user should compare expense ratio, liquidity, dividend yield, and tax treatment.

Return JSON only with this structure:
{{
  "summary": "short useful answer",
  "recommendations": [],
  "analysis": [],
  "risks": [],
  "next_steps": [],
  "disclaimer": "This is educational information, not financial advice."
}}
"""