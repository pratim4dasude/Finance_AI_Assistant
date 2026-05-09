
from src.schemas import UserContext
from src.market_data import get_latest_price

DISCLAIMER = (
    "This is not investment advice. It is an educational portfolio health summary. "
    "Please consult a licensed financial advisor before making investment decisions."
)


class PortfolioHealthAgent:
    name = "portfolio_health"

    def run(self, query: str, user_context: UserContext, intent: str, classification=None):
        portfolio = user_context.portfolio or []

        if not portfolio:
            return {
                "agent": self.name,
                "intent": intent,
                "data": {
                    "status": "empty_portfolio",
                    "portfolio_value": 0,
                    "number_of_positions": 0,
                    "concentration_risk": {
                        "top_position_pct": 0,
                        "top_3_positions_pct": 0,
                        "flag": "none",
                    },
                    "performance": {
                        "total_return_pct": None,
                        "annualized_return_pct": None,
                    },
                    "benchmark_comparison": {
                        "benchmark": self._benchmark(user_context.base_currency),
                        "portfolio_return_pct": None,
                        "benchmark_return_pct": None,
                        "alpha_pct": None,
                    },
                    "positions": [],
                    "observations": [
                        {
                            "severity": "info",
                            "text": "You do not have holdings yet. Start with goals, time horizon, emergency fund, and risk comfort before choosing instruments.",
                        }
                    ],
                    "disclaimer": DISCLAIMER,
                },
            }

        positions = []

        for holding in portfolio:
            enriched = self._enrich_holding(holding)
            positions.append(enriched)

        total_value = sum(position["market_value"] for position in positions)

        for position in positions:
            if total_value > 0:
                position["weight_pct"] = round(
                    position["market_value"] / total_value * 100,
                    2,
                )
            else:
                position["weight_pct"] = 0

        positions.sort(key=lambda x: x["weight_pct"], reverse=True)

        top_position_pct = positions[0]["weight_pct"] if positions else 0
        top_3_positions_pct = round(
            sum(position["weight_pct"] for position in positions[:3]),
            2,
        )

        if top_position_pct >= 50 or top_3_positions_pct >= 75:
            flag = "high"
        elif top_position_pct >= 30 or top_3_positions_pct >= 60:
            flag = "medium"
        else:
            flag = "low"

        observations = self._build_observations(
            flag=flag,
            positions=positions,
            top_position_pct=top_position_pct,
        )

        return {
            "agent": self.name,
            "intent": intent,
            "data": {
                "portfolio_value": round(total_value, 2),
                "number_of_positions": len(positions),
                "concentration_risk": {
                    "top_position_pct": top_position_pct,
                    "top_3_positions_pct": top_3_positions_pct,
                    "flag": flag,
                },
                "performance": {
                    "total_return_pct": self._weighted_return(positions),
                    "annualized_return_pct": None,
                },
                "benchmark_comparison": {
                    "benchmark": self._benchmark(user_context.base_currency),
                    "portfolio_return_pct": self._weighted_return(positions),
                    "benchmark_return_pct": None,
                    "alpha_pct": None,
                },
                "positions": positions,
                "observations": observations,
                "disclaimer": DISCLAIMER,
            },
        }

    def _enrich_holding(self, holding: dict) -> dict:
        ticker = holding.get("ticker") or holding.get("symbol")
        quantity = float(holding.get("quantity", 0) or 0)

        latest_price = get_latest_price(ticker) if ticker else None

        avg_cost = holding.get("avg_cost") or holding.get("avg_price")

        if latest_price is not None:
            price_used = float(latest_price)
            price_source = "yfinance"
        elif holding.get("market_value") is not None and quantity > 0:
            price_used = float(holding.get("market_value") or 0) / quantity
            price_source = "provided_market_value"
        else:
            price_used = float(
                holding.get("avg_price", holding.get("avg_cost", holding.get("price", 0))) or 0
            )
            price_source = "avg_cost_fallback"

        market_value = quantity * price_used

        unrealized_return_pct = None
        if avg_cost is not None and latest_price is not None:
            avg_cost_float = float(avg_cost)
            if avg_cost_float > 0:
                unrealized_return_pct = round(
                    ((latest_price - avg_cost_float) / avg_cost_float) * 100,
                    2,
                )

        return {
            "ticker": ticker,
            "name": holding.get("name", ticker),
            "exchange": holding.get("exchange"),
            "quantity": quantity,
            "avg_cost": float(avg_cost) if avg_cost is not None else None,
            "latest_price": round(latest_price, 2) if latest_price is not None else None,
            "price_used": round(price_used, 2),
            "price_source": price_source,
            "market_value": round(market_value, 2),
            "weight_pct": 0,
            "unrealized_return_pct": unrealized_return_pct,
            "currency": holding.get("currency"),
        }

    def _weighted_return(self, positions: list[dict]):
        weighted_return = 0
        valid_weight = 0

        for position in positions:
            if position.get("unrealized_return_pct") is not None:
                weighted_return += (
                    position["weight_pct"] * position["unrealized_return_pct"]
                )
                valid_weight += position["weight_pct"]

        if valid_weight == 0:
            return None

        return round(weighted_return / valid_weight, 2)

    def _build_observations(self, flag: str, positions: list[dict], top_position_pct: float):
        if not positions:
            return []

        if flag == "high":
            return [
                {
                    "severity": "warning",
                    "text": f"{top_position_pct}% of your portfolio is in {positions[0]['ticker']}. That is highly concentrated.",
                }
            ]

        if flag == "medium":
            return [
                {
                    "severity": "warning",
                    "text": f"Your top holding is {top_position_pct}% of the portfolio. Consider whether this matches your risk comfort.",
                }
            ]

        return [
            {
                "severity": "info",
                "text": "Your portfolio does not appear heavily concentrated in one position.",
            }
        ]

    def _benchmark(self, currency: str | None):
        if currency == "INR":
            return "NIFTY 50"
        if currency == "EUR":
            return "STOXX Europe 600"
        return "S&P 500"



















