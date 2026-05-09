import json

from src.agents.llm_agent import LLMFinanceAgent


class SupportAgent(LLMFinanceAgent):
    def __init__(self):
        super().__init__(
            name="customer_support",
            system_prompt="""
                You are Finance AI's customer support agent.
                
                Help users with login, account, linked bank, transaction history, and app usage issues.
                Do not include investment, portfolio, risk, or financial advice fields.
                Return JSON only.
            """,
        )

    def run(self, query, user_context, intent, classification=None):
        if not self.client:
            return {
                "agent": self.name,
                "intent": intent,
                "data": {
                    "summary": "I can help with account support, but OPENAI_API_KEY is missing.",
                    "steps": [],
                    "escalation": "Contact Valura support for account-specific help.",
                    "disclaimer": "For account-specific help, contact Valura support.",
                },
            }

        prompt = f"""
User support issue:
{query}

Return JSON only with this exact structure:
{{
  "summary": "short support answer",
  "steps": [],
  "escalation": "when the user should contact Valura support",
  "disclaimer": "For account-specific help, contact Valura support."
}}

Do not include portfolio_snapshot, analysis, recommendations, risks, or investment disclaimer.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=600,
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
                    "message": "Support agent failed while generating response.",
                },
            }