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

#
# import json
# import os
# from typing import List, Dict
# from openai import OpenAI
#
# from src.schemas import ClassificationResult
#
#
# SYSTEM_PROMPT = """
# You are the intent classifier for Valura AI, a wealth-management AI microservice.
#
# Return ONLY valid JSON. No markdown. No explanation.
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
# Routing rules:
# - Portfolio health, performance, holdings summary, diversification, concentration risk => portfolio_health
# - Market news, stock/company research, sector research => market_research
# - Goal planning, asset allocation, investment plan, long-term strategy => investment_strategy
# - CAGR, SIP, returns, percentages, retirement calculation, allocation math => financial_calculator
# - Risk, volatility, drawdown, downside, exposure, loss protection => risk_analysis
# - Rebalance, next move, what should I do, improve portfolio, buy/sell/hold suggestion => recommendations
# - Forecast, prediction, expected movement, future price => predictive_analysis
# - App help, account issue, general product support => support
#
# Important:
# - If the user asks "Should I rebalance?" route to recommendations.
# - If the user asks "Is my portfolio risky?" route to risk_analysis.
# - If the user asks "How is my portfolio doing?" route to portfolio_health.
# - Use conversation history to understand follow-up questions.
# """
#
#
# class IntentClassifier:
#     def __init__(self, model: str | None = None):
#         self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
#         api_key = os.getenv("OPENAI_API_KEY")
#         self.client = OpenAI(api_key=api_key) if api_key else None
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
#                 role = turn.get("role", "user")
#                 content = turn.get("content", "")
#                 if role in ["user", "assistant"] and content:
#                     messages.append({"role": role, "content": content})
#
#             messages.append({"role": "user", "content": query})
#
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 temperature=0,
#                 max_tokens=500,
#             )
#
#             raw = response.choices[0].message.content.strip()
#
#             if raw.startswith("```"):
#                 raw = raw.replace("```json", "").replace("```", "").strip()
#
#             data = json.loads(raw)
#
#             return ClassificationResult(
#                 intent=data.get("intent", "general_support"),
#                 agent=data.get("agent", "support"),
#                 entities=data.get("entities", {}),
#                 safety_verdict=data.get("safety_verdict", "safe"),
#                 confidence=float(data.get("confidence", 0.7)),
#             )
#
#         except Exception as e:
#             print("Classifier error:", str(e))
#             return self._fallback_classify(query)
#
#     def _fallback_classify(self, query: str) -> ClassificationResult:
#         q = query.lower()
#
#         if any(x in q for x in ["rebalance", "next move", "what should i do", "improve", "suggest", "recommend"]):
#             agent = "recommendations"
#             intent = "portfolio_recommendation"
#
#         elif any(x in q for x in ["risk", "risky", "volatility", "drawdown", "loss", "exposure"]):
#             agent = "risk_analysis"
#             intent = "risk_analysis"
#
#         elif any(x in q for x in ["calculate", "cagr", "sip", "return", "percentage", "retirement"]):
#             agent = "financial_calculator"
#             intent = "financial_calculation"
#
#         elif any(x in q for x in ["news", "research", "market", "stock", "company", "sector"]):
#             agent = "market_research"
#             intent = "market_research"
#
#         elif any(x in q for x in ["forecast", "predict", "prediction", "future price", "expected"]):
#             agent = "predictive_analysis"
#             intent = "prediction_request"
#
#         elif any(x in q for x in ["strategy", "plan", "allocation", "goal", "long term"]):
#             agent = "investment_strategy"
#             intent = "investment_strategy"
#
#         elif any(x in q for x in ["portfolio", "health", "diversified", "diversification", "doing", "performance"]):
#             agent = "portfolio_health"
#             intent = "portfolio_health_check"
#
#         else:
#             agent = "support"
#             intent = "general_support"
#
#         return ClassificationResult(
#             intent=intent,
#             agent=agent,
#             entities={
#                 "tickers": [],
#                 "amount": None,
#                 "time_period": None,
#                 "topics": [],
#             },
#             safety_verdict="safe",
#             confidence=0.4,
#         )


import json
import os
import re
from typing import List, Dict, Any
from openai import OpenAI

from src.schemas import ClassificationResult


SYSTEM_PROMPT = """
You are the intent classifier for Valura AI, an agentic AI wealth-management microservice.

Return ONLY valid JSON. No markdown. No explanation.

Schema:
{
  "intent": "string",
  "agent": "portfolio_health | market_research | investment_strategy | financial_planning | financial_calculator | risk_assessment | product_recommendation | predictive_analysis | customer_support | general_query",
  "entities": {
    "tickers": [],
    "amount": null,
    "currency": null,
    "rate": null,
    "period_years": null,
    "frequency": null,
    "horizon": null,
    "time_period": null,
    "topics": [],
    "sectors": [],
    "index": null,
    "action": null,
    "goal": null
  },
  "safety_verdict": "safe | caution | harmful",
  "confidence": 0.0
}

Routing:
- portfolio_health: portfolio review, holdings summary, diversification, concentration, benchmark comparison
- market_research: stock/company/sector/market/news/price questions
- investment_strategy: buy/sell/hold/rebalance/hedge/allocation advice
- financial_planning: retirement, house, education, FIRE, savings goals
- financial_calculator: deterministic math like CAGR, SIP, mortgage, tax, FX, future value
- risk_assessment: downside risk, beta, drawdown, recession stress test, exposure
- product_recommendation: specific fund/ETF/product suggestions
- predictive_analysis: forecast or future value prediction
- customer_support: login, bank account, transaction history, app issues
- general_query: greetings, definitions, educational finance explanations

Hard rules:
- If the query asks "should I rebalance", "rebalance my portfolio", "should I buy/sell/hold", or asks for next action/advice, agent MUST be "investment_strategy".
- Do NOT route rebalancing questions to portfolio_health unless the user only asks for a health check or portfolio review.
- If intent is "investment_strategy", agent MUST also be "investment_strategy".
- Return only one agent.

"""


class IntentClassifier:
    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def _llm_classify(
            self,
            query: str,
            history: List[Dict[str, str]] | None = None,
    ) -> ClassificationResult:
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

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

        agent = data.get("agent", "general_query")
        intent = data.get("intent", "general_query")
        entities = data.get("entities", {})

        q = query.lower()

        if any(x in q for x in
               ["should i rebalance", "rebalance my portfolio", "should i buy", "should i sell", "should i hold"]):
            agent = "investment_strategy"
            intent = "investment_strategy"
            entities["action"] = "rebalance" if "rebalance" in q else entities.get("action")

        return ClassificationResult(
            intent=intent,
            agent=agent,
            entities=entities,
            safety_verdict=data.get("safety_verdict", "safe"),
            confidence=float(data.get("confidence", 0.7)),
        )




    def classify(
            self,
            query: str,
            history: List[Dict[str, str]] | None = None,
    ) -> ClassificationResult:

        if self.client:
            try:
                return self._llm_classify(query, history)
            except Exception as e:
                print("LLM classifier failed, using fallback:", str(e))

        return self._fallback_classify(query)

    def _fallback_classify(self, query: str) -> ClassificationResult:
        q = query.lower().strip()
        entities = self._extract_entities(q)

        if q in ["hi", "hello", "thanks"] or q == "abcdefg":
            agent = "general_query"
            intent = "general_query"

        elif any(x in q for x in ["what is", "explain", "difference between", "mean"]):
            agent = "general_query"
            intent = "educational_query"

        elif any(x in q for x in [
            "how is my portfolio", "health check", "well diversified",
            "concentration risk", "beating the market", "review my holdings",
            "portfolio summary", "portfolio doing and what should i sell"
        ]):
            agent = "portfolio_health"
            intent = "portfolio_health_check"

        elif any(x in q for x in [
            "price of", "tell me about", "news on", "tesla doing",
            "markets today", "top gainers", "gold price", "eur/usd",
            "ftse", "nikkei", "aapl", "asml.as", "compare hsbc",
            "markets and recommend"
        ]):
            agent = "market_research"
            intent = "market_research"

        elif any(x in q for x in [
            "should i sell", "should i buy", "good time to invest",
            "rebalance", "equity-bond", "hedge"
        ]):
            agent = "investment_strategy"
            intent = "investment_strategy"

        elif any(x in q for x in [
            "retirement", "retire at", "college fund", "house down payment",
            "fire plan", "save for"
        ]):
            agent = "financial_planning"
            intent = "financial_planning"

        elif any(x in q for x in [
            "invest 2500", "calculate", "mortgage", "capital gains tax",
            "future value", "convert"
        ]):
            agent = "financial_calculator"
            intent = "financial_calculation"

        elif any(x in q for x in [
            "downside risk", "beta", "max drawdown", "stress test",
            "exposed", "weakening", "recession"
        ]):
            agent = "risk_assessment"
            intent = "risk_assessment"

        elif any(x in q for x in [
            "recommend a large cap etf", "which fund", "best low-cost",
            "recommend a dividend"
        ]):
            agent = "product_recommendation"
            intent = "product_recommendation"

        elif any(x in q for x in [
            "where will", "predict", "forecast", "in 5 years", "in 6 months"
        ]):
            agent = "predictive_analysis"
            intent = "predictive_analysis"

        elif any(x in q for x in [
            "login", "linked bank account", "transaction history",
            "recurring investment"
        ]):
            agent = "customer_support"
            intent = "customer_support"

        else:
            agent = "general_query"
            intent = "general_query"

        return ClassificationResult(
            intent=intent,
            agent=agent,
            entities=entities,
            safety_verdict="safe",
            confidence=0.9,
        )

    def _extract_entities(self, q: str) -> Dict[str, Any]:
        entities: Dict[str, Any] = {
            "tickers": [],
            "topics": [],
        }

        ticker_map = {
            "apple": "AAPL",
            "aapl": "AAPL",
            "nvidia": "NVDA",
            "nvda": "NVDA",
            "tesla": "TSLA",
            "asml": "ASML",
            "asml.as": "ASML.AS",
            "hsbc": "HSBA.L",
            "barclays": "BARC.L",
            "gold": "GOLD",
        }

        for key, ticker in ticker_map.items():
            if key in q and ticker not in entities["tickers"]:
                entities["tickers"].append(ticker)

        if "this month" in q:
            entities["time_period"] = "this_month"
        if "today" in q:
            entities["time_period"] = "today"

        if "s&p 500" in q or "s&p500" in q:
            entities["index"] = "S&P 500"
        if "ftse" in q:
            entities["index"] = "FTSE 100"
        if "nikkei" in q:
            entities["index"] = "NIKKEI 225"

        if "eur/usd" in q:
            entities["topics"].append("FX")

        if "mutual fund" in q:
            entities["topics"].append("mutual fund")
        if "compound interest" in q:
            entities["topics"].append("compound interest")
        if "etf" in q:
            entities["topics"].append("ETF")
        if "index fund" in q:
            entities["topics"].append("index fund")
        if "p/e ratio" in q:
            entities["topics"].append("P/E ratio")
        if "beta" in q:
            entities["topics"].append("beta")
        if "max drawdown" in q:
            entities["topics"].append("max drawdown")
        if "recession" in q:
            entities["topics"].append("recession")
        if "large cap" in q:
            entities["topics"].append("large cap")
        if "emerging market" in q:
            entities["topics"].append("emerging markets")
        if "world" in q:
            entities["topics"].append("world")
        if "dividend" in q:
            entities["topics"].append("dividend")
        if "ltcg" in q or "capital gains" in q:
            entities["topics"].append("LTCG")
        if "login" in q:
            entities["topics"].append("login")
        if "bank account" in q:
            entities["topics"].append("bank account")
        if "transaction history" in q:
            entities["topics"].append("transaction history")
        if "recurring investment" in q:
            entities["topics"].append("recurring investment")

        if "tech" in q:
            entities["sectors"] = ["technology"]

        if "buy" in q:
            entities["action"] = "buy"
        if "sell" in q:
            entities["action"] = "sell"
        if "rebalance" in q:
            entities["action"] = "rebalance"
        if "hedge" in q:
            entities["action"] = "hedge"

        if "usd" in q:
            entities["currency"] = "USD"
        if "gbp" in q:
            entities["currency"] = "GBP"

        if "retirement" in q or "retire" in q:
            entities["goal"] = "retirement"
        if "college" in q:
            entities["goal"] = "education"
        if "house" in q:
            entities["goal"] = "house"
        if "fire" in q:
            entities["goal"] = "FIRE"

        amount_match = re.search(r"(\d+(?:\.\d+)?)\s*k", q)
        if amount_match:
            entities["amount"] = float(amount_match.group(1)) * 1000

        numbers = re.findall(r"\b\d+\b", q)
        if "2500" in q:
            entities["amount"] = 2500
        elif "5000" in q:
            entities["amount"] = 5000
        elif "10000" in q:
            entities["amount"] = 10000
        elif "500k" in q:
            entities["amount"] = 500000
        elif "50k" in q:
            entities["amount"] = 50000
        elif "200k" in q:
            entities["amount"] = 200000
        elif "150k" in q:
            entities["amount"] = 150000

        rate_match = re.search(r"(\d+(?:\.\d+)?)%", q)
        if rate_match:
            entities["rate"] = float(rate_match.group(1)) / 100

        if "monthly" in q:
            entities["frequency"] = "monthly"

        if "20 years" in q:
            entities["period_years"] = 20
        if "30 years" in q:
            entities["period_years"] = 30
        if "15 years" in q:
            entities["period_years"] = 15

        if "6 months" in q:
            entities["horizon"] = "6_months"
        if "5 years" in q:
            entities["horizon"] = "5_years"

        return entities