import re
from src.agents.llm_agent import LLMFinanceAgent


class FinancialCalculatorAgent(LLMFinanceAgent):
    def __init__(self):
        super().__init__(
            name="financial_calculator",
            system_prompt="""
You are Valura AI's financial calculator agent.

Your job:
- Solve financial calculations accurately.
- Prefer exact math when possible.
- If unsure, explain assumptions clearly.
- Return structured JSON only.
""",
        )

    def run(self, query, user_context, intent, classification=None):
        q = query.lower()


        sip_result = self._try_sip_calculation(q)
        if sip_result:
            return {
                "agent": self.name,
                "intent": intent,
                "data": sip_result,
            }


        lump_sum_result = self._try_lump_sum(q)
        if lump_sum_result:
            return {
                "agent": self.name,
                "intent": intent,
                "data": lump_sum_result,
            }


        return super().run(query, user_context, intent, classification)

    #  SIP
    def _try_sip_calculation(self, q: str):
        if "monthly" not in q:
            return None

        amount = self._extract_number(q, r"(\d+(?:,\d+)*)\s*(monthly|per month)")
        years = self._extract_number(q, r"(\d+)\s*years?")
        rate = self._extract_rate(q)

        if not amount or not years or not rate:
            return None

        amount = float(amount.replace(",", ""))
        years = int(years)
        rate = float(rate)

        monthly_rate = rate / 12
        months = years * 12

        fv = amount * (((1 + monthly_rate) ** months - 1) / monthly_rate)

        return {
            "calculation_type": "monthly_sip",
            "inputs": {
                "monthly_amount": amount,
                "years": years,
                "annual_rate_pct": rate * 100,
            },
            "result": {
                "future_value": round(fv, 2),
                "total_invested": amount * months,
                "gain": round(fv - (amount * months), 2),
            },
            "summary": f"Investing {amount} monthly for {years} years at {rate*100:.1f}% gives approx {fv:,.2f}.",
            "disclaimer": "This is educational information, not financial advice.",
        }

    #  Lump sum
    def _try_lump_sum(self, q: str):
        if "monthly" in q:
            return None

        amount = self._extract_number(q, r"(?:invest|value of)\s*(\d+(?:,\d+)*)")
        years = self._extract_number(q, r"(\d+)\s*years?")
        rate = self._extract_rate(q)

        if not amount or not years or not rate:
            return None

        amount = float(amount.replace(",", ""))
        years = int(years)
        rate = float(rate)

        fv = amount * ((1 + rate) ** years)

        return {
            "calculation_type": "lump_sum",
            "inputs": {
                "principal": amount,
                "years": years,
                "annual_rate_pct": rate * 100,
            },
            "result": {
                "future_value": round(fv, 2),
                "gain": round(fv - amount, 2),
            },
            "summary": f"{amount} invested for {years} years at {rate*100:.1f}% grows to {fv:,.2f}.",
            "disclaimer": "This is educational information, not financial advice.",
        }

    # Helper
    def _extract_number(self, text, pattern):
        match = re.search(pattern, text)
        return match.group(1) if match else None

    def _extract_rate(self, text):
        match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
        if match:
            return float(match.group(1)) / 100
        return None