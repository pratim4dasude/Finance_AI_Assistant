
class StubAgent:
    def __init__(self, name: str):
        self.name = name

    def run(self, query, user_context, classification):
        return {
            "agent": self.name,
            "intent": classification.intent,
            "data": {
                "classified_intent": classification.intent,
                "entities": classification.entities,
                "target_agent": classification.agent,
                "message": f"The {self.name} agent is not implemented in this build.",
                "safety_verdict": classification.safety_verdict,
            },
        }