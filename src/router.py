from agents.portfolio_health import PortfolioHealthAgent
from agents.stud_agent import StubAgent

class AgentRouter:
    def __init__(self):
        self.portfolio_agent = PortfolioHealthAgent()

    def route(self, query, user_context, classification):
        if classification.agent == "portfolio_health":
            return self.portfolio_agent.run(
                query=query,
                user_context=user_context,
                intent=classification.intent,
            )

        return StubAgent(classification.agent).run(
            query=query,
            user_context=user_context,
            classification=classification,
        )