# from agents.portfolio_health import PortfolioHealthAgent
# from agents.stud_agent import StubAgent
#
# class AgentRouter:
#     def __init__(self):
#         self.portfolio_agent = PortfolioHealthAgent()
#
#     def route(self, query, user_context, classification):
#         if classification.agent == "portfolio_health":
#             return self.portfolio_agent.run(
#                 query=query,
#                 user_context=user_context,
#                 intent=classification.intent,
#             )
#
#         return StubAgent(classification.agent).run(
#             query=query,
#             user_context=user_context,
#             classification=classification,
#         )

# from src.agents.portfolio_health import PortfolioHealthAgent
# from src.agents.stud_agent import StubAgent
# from src.agents.recommedation import RecommendationsAgent
# from src.agents.risk_analysis import RiskAnalysisAgent
# from src.agents.market_reaserch import MarketResearchAgent
# from src.agents.finance_calculator import FinancialCalculatorAgent
#
#
# class AgentRouter:
#     def __init__(self):
#         self.agents = {
#             "portfolio_health": PortfolioHealthAgent(),
#             "recommendations": RecommendationsAgent(),
#             "risk_analysis": RiskAnalysisAgent(),
#             "market_research": MarketResearchAgent(),
#             "financial_calculator": FinancialCalculatorAgent(),
#         }
#
#     def route(self, query, user_context, classification):
#         agent = self.agents.get(classification.agent)
#
#         if agent:
#             return agent.run(
#                 query=query,
#                 user_context=user_context,
#                 intent=classification.intent,
#                 classification=classification,
#             )
#
#         return StubAgent(classification.agent).run(
#             query=query,
#             user_context=user_context,
#             classification=classification,
#         )

from src.agents.portfolio_health import PortfolioHealthAgent
from src.agents.stud_agent import StubAgent
from src.agents.recommedation import RecommendationsAgent
from src.agents.risk_analysis import RiskAnalysisAgent
from src.agents.market_reaserch import MarketResearchAgent
from src.agents.finance_calculator import FinancialCalculatorAgent


class AgentRouter:
    def __init__(self):
        self.agents = {
            "portfolio_health": PortfolioHealthAgent(),
            "recommendations": RecommendationsAgent(),
            "risk_analysis": RiskAnalysisAgent(),
            "market_research": MarketResearchAgent(),
            "financial_calculator": FinancialCalculatorAgent(),
        }

        self.aliases = {
            "risk_assessment": "risk_analysis",
            "product_recommendation": "recommendations",
            "customer_support": "support",
            "financial_planning": "recommendations",
            "investment_strategy": "recommendations",
            "general_query": "support",
        }

    def route(self, query, user_context, classification):
        agent_name = self.aliases.get(classification.agent, classification.agent)
        agent = self.agents.get(agent_name)

        if agent:
            return agent.run(
                query=query,
                user_context=user_context,
                intent=classification.intent,
                classification=classification,
            )

        return StubAgent(classification.agent).run(
            query=query,
            user_context=user_context,
            classification=classification,
        )