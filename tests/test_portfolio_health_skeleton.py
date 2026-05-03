"""
Skeleton test for the Portfolio Health agent.

Wire your agent import and remove the skip decorators.
"""
import pytest
from src.agents.portfolio_health import PortfolioHealthAgent
from src.schemas import UserContext

def run(user, llm=None):
    agent = PortfolioHealthAgent()

    user_context = UserContext(
        user_id=user.get("user_id", user.get("id", "test_user")),
        risk_profile=user.get("risk_profile"),
        kyc_status=user.get("kyc_status"),
        base_currency=user.get("base_currency", "USD"),
        portfolio=user.get("portfolio", user.get("positions", [])),
    )

    result = agent.run(
        query="Check portfolio health",
        user_context=user_context,
        intent="portfolio_health_check",
    )

    return result["data"]

# @pytest.mark.skip(reason="Stub — wire up your agent import below and remove this decorator")
def test_portfolio_health_does_not_crash_on_empty_portfolio(load_user, mock_llm):
    """
    user_004 has no positions. Agent must not crash.
    """
    # from src.agents.portfolio_health import run  # noqa: ERA001

    user = load_user("usr_004")
    response = run(user, llm=mock_llm)  # noqa: F821

    assert response is not None
    assert "disclaimer" in response


# @pytest.mark.skip(reason="Stub — wire up your agent import below and remove this decorator")
def test_portfolio_health_flags_concentration(load_user, mock_llm):
    """
    user_003 has ~60% in NVDA. Agent must surface this.
    """
    user = load_user("usr_003")
    response = run(user, llm=mock_llm)  # noqa: F821

    assert response["concentration_risk"]["flag"] in {"high", "warning"}


# @pytest.mark.skip(reason="Stub — wire up your agent import below and remove this decorator")
def test_portfolio_health_includes_disclaimer(load_user, mock_llm):
    user = load_user("usr_001")
    response = run(user, llm=mock_llm)  # noqa: F821
    assert response["disclaimer"]
    assert "not investment advice" in response["disclaimer"].lower()
