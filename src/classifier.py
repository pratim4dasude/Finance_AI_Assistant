# import json
# import os
# from typing import List, Dict, Any
# from openai import OpenAI
#
# from src.schemas import ClassificationResult
#
#
# SYSTEM_PROMPT = """
# You are the intent classifier for Valura AI.
#
# Return only valid JSON.
#
# Schema:
# {
#   "intent": "string",
#   "agent": "portfolio_health | market_research | investment_strategy | financial_calculator | risk_analysis | recommendations | predictive_analysis | support",
#   "entities": {
#     "tickers": [],
#     "amount": null,
#     "time_period": null,
#     "topics": []
#   },
#   "safety_verdict": "safe | caution | harmful",
#   "confidence": 0.0
# }
#
# Rules:
# - Portfolio review, diversification, health check, performance, concentration risk => portfolio_health.
# - Market/news/company research => market_research.
# - Allocation planning or investment strategy => investment_strategy.
# - Numeric calculations, CAGR, SIP, retirement math => financial_calculator.
# - Risk-only questions => risk_analysis.
# - Suggestions or next moves => recommendations.
# - Forecasting/prediction => predictive_analysis.
# - Account/help/product support => support.
# - Resolve follow-ups using conversation history.
# """
#
#
# class IntentClassifier:
#     def __init__(self, model: str | None = None):
#         self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
#         self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
#
#     def classify(
#         self,
#         query: str,
#         history: List[Dict[str, str]] | None = None,
#     ) -> ClassificationResult:
#         if not self.client:
#             return self._fallback_classify(query)
#
#         try:
#             messages = [{"role": "system", "content": SYSTEM_PROMPT}]
#
#             for turn in history or []:
#                 messages.append(turn)
#
#             messages.append({"role": "user", "content": query})
#
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 temperature=0,
#                 max_tokens=400,
#             )
#
#             raw = response.choices[0].message.content
#             data = json.loads(raw)
#             return ClassificationResult(**data)
#
#         except Exception:
#             return self._fallback_classify(query)
#
#     def _fallback_classify(self, query: str) -> ClassificationResult:
#         q = query.lower()
#
#         if any(x in q for x in ["portfolio", "health", "diversified", "diversification", "doing"]):
#             agent = "portfolio_health"
#             intent = "portfolio_health_check"
#         elif any(x in q for x in ["calculate", "cagr", "return", "sip"]):
#             agent = "financial_calculator"
#             intent = "financial_calculation"
#         elif any(x in q for x in ["news", "research", "market", "stock"]):
#             agent = "market_research"
#             intent = "market_research"
#         else:
#             agent = "support"
#             intent = "general_support"
#
#         return ClassificationResult(
#             intent=intent,
#             agent=agent,
#             entities={},
#             safety_verdict="safe",
#             confidence=0.4,
#         )


import json
import os
from typing import List, Dict
from openai import OpenAI

from src.schemas import ClassificationResult


SYSTEM_PROMPT = """
You are the intent classifier for Valura AI, a wealth-management AI microservice.

Return ONLY valid JSON. No markdown. No explanation.

Schema:
{
  "intent": "string",
  "agent": "portfolio_health | market_research | investment_strategy | financial_calculator | risk_analysis | recommendations | predictive_analysis | support",
  "entities": {
    "tickers": [],
    "amount": null,
    "time_period": null,
    "topics": []
  },
  "safety_verdict": "safe | caution | harmful",
  "confidence": 0.0
}

Routing rules:
- Portfolio health, performance, holdings summary, diversification, concentration risk => portfolio_health
- Market news, stock/company research, sector research => market_research
- Goal planning, asset allocation, investment plan, long-term strategy => investment_strategy
- CAGR, SIP, returns, percentages, retirement calculation, allocation math => financial_calculator
- Risk, volatility, drawdown, downside, exposure, loss protection => risk_analysis
- Rebalance, next move, what should I do, improve portfolio, buy/sell/hold suggestion => recommendations
- Forecast, prediction, expected movement, future price => predictive_analysis
- App help, account issue, general product support => support

Important:
- If the user asks "Should I rebalance?" route to recommendations.
- If the user asks "Is my portfolio risky?" route to risk_analysis.
- If the user asks "How is my portfolio doing?" route to portfolio_health.
- Use conversation history to understand follow-up questions.
"""


class IntentClassifier:
    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def classify(
        self,
        query: str,
        history: List[Dict[str, str]] | None = None,
    ) -> ClassificationResult:
        if not self.client:
            return self._fallback_classify(query)

        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            for turn in history or []:
                role = turn.get("role", "user")
                content = turn.get("content", "")
                if role in ["user", "assistant"] and content:
                    messages.append({"role": role, "content": content})

            messages.append({"role": "user", "content": query})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0,
                max_tokens=500,
            )

            raw = response.choices[0].message.content.strip()

            if raw.startswith("```"):
                raw = raw.replace("```json", "").replace("```", "").strip()

            data = json.loads(raw)

            return ClassificationResult(
                intent=data.get("intent", "general_support"),
                agent=data.get("agent", "support"),
                entities=data.get("entities", {}),
                safety_verdict=data.get("safety_verdict", "safe"),
                confidence=float(data.get("confidence", 0.7)),
            )

        except Exception as e:
            print("Classifier error:", str(e))
            return self._fallback_classify(query)

    def _fallback_classify(self, query: str) -> ClassificationResult:
        q = query.lower()

        if any(x in q for x in ["rebalance", "next move", "what should i do", "improve", "suggest", "recommend"]):
            agent = "recommendations"
            intent = "portfolio_recommendation"

        elif any(x in q for x in ["risk", "risky", "volatility", "drawdown", "loss", "exposure"]):
            agent = "risk_analysis"
            intent = "risk_analysis"

        elif any(x in q for x in ["calculate", "cagr", "sip", "return", "percentage", "retirement"]):
            agent = "financial_calculator"
            intent = "financial_calculation"

        elif any(x in q for x in ["news", "research", "market", "stock", "company", "sector"]):
            agent = "market_research"
            intent = "market_research"

        elif any(x in q for x in ["forecast", "predict", "prediction", "future price", "expected"]):
            agent = "predictive_analysis"
            intent = "prediction_request"

        elif any(x in q for x in ["strategy", "plan", "allocation", "goal", "long term"]):
            agent = "investment_strategy"
            intent = "investment_strategy"

        elif any(x in q for x in ["portfolio", "health", "diversified", "diversification", "doing", "performance"]):
            agent = "portfolio_health"
            intent = "portfolio_health_check"

        else:
            agent = "support"
            intent = "general_support"

        return ClassificationResult(
            intent=intent,
            agent=agent,
            entities={
                "tickers": [],
                "amount": None,
                "time_period": None,
                "topics": [],
            },
            safety_verdict="safe",
            confidence=0.4,
        )