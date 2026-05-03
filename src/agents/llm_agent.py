# import json
# import os
# from openai import OpenAI
#
#
# class LLMFinanceAgent:
#     def __init__(self, name: str, system_prompt: str):
#         self.name = name
#         self.system_prompt = system_prompt
#         api_key = os.getenv("OPENAI_API_KEY")
#         self.client = OpenAI(api_key=api_key) if api_key else None
#         self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
#
#     def run(self, query, user_context, intent, classification=None):
#         if not self.client:
#             return {
#                 "agent": self.name,
#                 "intent": intent,
#                 "data": {
#                     "message": "OPENAI_API_KEY is missing. Add it in .env file.",
#                     "fallback": True,
#                 },
#             }
#
#         portfolio = user_context.model_dump()
#
#         prompt = f"""
# User query:
# {query}
#
# User context:
# {json.dumps(portfolio, indent=2)}
#
# Classification:
# {classification.model_dump_json() if classification else "{}"}
#
# Return JSON only with this structure:
# {{
#   "summary": "short useful answer",
#   "analysis": [],
#   "recommendations": [],
#   "risks": [],
#   "next_steps": [],
#   "disclaimer": "This is educational information, not financial advice."
# }}
# """
#
#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {"role": "system", "content": self.system_prompt},
#                     {"role": "user", "content": prompt},
#                 ],
#                 temperature=0.3,
#                 max_tokens=900,
#             )
#
#             raw = response.choices[0].message.content.strip()
#
#             if raw.startswith("```"):
#                 raw = raw.replace("```json", "").replace("```", "").strip()
#
#             data = json.loads(raw)
#
#             return {
#                 "agent": self.name,
#                 "intent": intent,
#                 "data": data,
#             }
#
#         except Exception as e:
#             return {
#                 "agent": self.name,
#                 "intent": intent,
#                 "data": {
#                     "error": str(e),
#                     "message": "Agent failed while generating response.",
#                 },
#             }

import json
import os
from openai import OpenAI


class LLMFinanceAgent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def enrich_portfolio(self, user_context):
        context = user_context.model_dump()
        portfolio = context.get("portfolio", [])

        enriched = []
        total_value = 0

        for holding in portfolio:
            quantity = float(holding.get("quantity", 0) or 0)
            avg_price = float(holding.get("avg_price", 0) or 0)
            market_value = float(
                holding.get("market_value", quantity * avg_price) or 0
            )

            item = {
                **holding,
                "symbol": holding.get("symbol") or holding.get("ticker"),
                "market_value": round(market_value, 2),
            }

            enriched.append(item)
            total_value += market_value

        for item in enriched:
            item["weight_pct"] = round(
                (item["market_value"] / total_value * 100), 2
            ) if total_value > 0 else 0

        context["portfolio"] = enriched
        context["portfolio_summary"] = {
            "total_value": round(total_value, 2),
            "number_of_holdings": len(enriched),
            "top_holding": max(enriched, key=lambda x: x["weight_pct"]) if enriched else None,
            "top_3_weight_pct": round(
                sum(sorted([x["weight_pct"] for x in enriched], reverse=True)[:3]), 2
            ),
        }

        return context

    def run(self, query, user_context, intent, classification=None):
        if not self.client:
            return {
                "agent": self.name,
                "intent": intent,
                "data": {
                    "message": "OPENAI_API_KEY is missing. Add it in .env file.",
                    "fallback": True,
                },
            }

        portfolio_context = self.enrich_portfolio(user_context)

        prompt = f"""
User query:
{query}

Enriched user context with calculated portfolio weights:
{json.dumps(portfolio_context, indent=2)}

Classification:
{classification.model_dump_json() if classification else "{}"}

Use the calculated market_value and weight_pct in your answer.
Mention exact allocation percentages when relevant.

Return JSON only with this structure:
{{
  "summary": "short useful answer",
  "portfolio_snapshot": {{
    "total_value": null,
    "top_holding": null,
    "top_holding_weight_pct": null,
    "top_3_weight_pct": null
  }},
  "analysis": [],
  "recommendations": [],
  "risks": [],
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
                temperature=0.3,
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
                    "message": "Agent failed while generating response.",
                },
            }