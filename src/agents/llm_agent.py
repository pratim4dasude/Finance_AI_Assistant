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

        portfolio = user_context.model_dump()

        prompt = f"""
User query:
{query}

User context:
{json.dumps(portfolio, indent=2)}

Classification:
{classification.model_dump_json() if classification else "{}"}

Return JSON only with this structure:
{{
  "summary": "short useful answer",
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
                    "message": "Agent failed while generating response.",
                },
            }