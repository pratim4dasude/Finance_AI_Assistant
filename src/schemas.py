from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


# AgentName = Literal[
#     "portfolio_health",
#     "market_research",
#     "investment_strategy",
#     "financial_calculator",
#     "risk_analysis",
#     "recommendations",
#     "predictive_analysis",
#     "support",
# ]

AgentName = Literal[
    "portfolio_health",
    "market_research",
    "investment_strategy",
    "financial_planning",
    "financial_calculator",
    "risk_analysis",
    "risk_assessment",
    "recommendations",
    "product_recommendation",
    "predictive_analysis",
    "support",
    "customer_support",
    "general_query",
]

class UserContext(BaseModel):
    user_id: str
    risk_profile: Optional[str] = None
    kyc_status: Optional[str] = None
    base_currency: Optional[str] = "USD"
    portfolio: List[Dict[str, Any]] = Field(default_factory=list)


class ChatRequest(BaseModel):
    session_id: str
    query: str
    user_context: UserContext


class SafetyResult(BaseModel):
    allowed: bool
    category: Optional[str] = None
    response: Optional[str] = None


class ClassificationResult(BaseModel):
    intent: str
    agent: AgentName
    entities: Dict[str, Any] = Field(default_factory=dict)
    safety_verdict: str = "safe"
    confidence: float = 0.0


class AgentResponse(BaseModel):
    agent: str
    intent: str
    data: Dict[str, Any]