from src.schemas import UserContext

DISCLAIMER = (
    "This is not investment advice. It is an educational portfolio health summary. "
    "Please consult a licensed financial advisor before making investment decisions."
)


class PortfolioHealthAgent:
    name = "portfolio_health"

    def run(self, query: str, user_context: UserContext, intent: str):
        portfolio = user_context.portfolio or []

        if not portfolio:
            return {
                "agent": self.name,
                "intent": intent,
                "data": {
                    "status": "empty_portfolio",
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
                    "observations": [
                        {
                            "severity": "info",
                            "text": "You do not have holdings yet. Start with goals, time horizon, emergency fund, and risk comfort before choosing instruments.",
                        },
                        {
                            "severity": "info",
                            "text": "A beginner-friendly first allocation usually avoids concentration and uses diversified funds or baskets.",
                        },
                    ],
                    "disclaimer": DISCLAIMER,
                },
            }

        total_value = sum(float(h.get("market_value", 0)) for h in portfolio)

        positions = []
        for h in portfolio:
            value = float(h.get("market_value", 0))
            pct = (value / total_value * 100) if total_value > 0 else 0
            positions.append(
                {
                    "ticker": h.get("ticker"),
                    "name": h.get("name", h.get("ticker")),
                    "market_value": value,
                    "weight_pct": round(pct, 2),
                    "return_pct": h.get("return_pct"),
                }
            )

        positions.sort(key=lambda x: x["weight_pct"], reverse=True)

        top_position_pct = positions[0]["weight_pct"]
        top_3_positions_pct = round(sum(p["weight_pct"] for p in positions[:3]), 2)

        if top_position_pct >= 50 or top_3_positions_pct >= 75:
            flag = "high"
        elif top_position_pct >= 30 or top_3_positions_pct >= 60:
            flag = "medium"
        else:
            flag = "low"

        weighted_return = 0
        valid_return_weight = 0

        for p in positions:
            if p["return_pct"] is not None:
                weighted_return += p["weight_pct"] * float(p["return_pct"])
                valid_return_weight += p["weight_pct"]

        total_return_pct = (
            round(weighted_return / valid_return_weight, 2)
            if valid_return_weight > 0
            else None
        )

        benchmark = self._benchmark(user_context.base_currency)
        benchmark_return_pct = None
        alpha_pct = None

        observations = []

        if flag == "high":
            observations.append(
                {
                    "severity": "warning",
                    "text": f"{top_position_pct}% of your portfolio is in {positions[0]['ticker']}. That is highly concentrated.",
                }
            )
        elif flag == "medium":
            observations.append(
                {
                    "severity": "warning",
                    "text": f"Your top holding is {top_position_pct}% of the portfolio. Consider whether this matches your risk comfort.",
                }
            )
        else:
            observations.append(
                {
                    "severity": "info",
                    "text": "Your portfolio does not appear heavily concentrated in one position.",
                }
            )

        if total_return_pct is not None:
            observations.append(
                {
                    "severity": "info",
                    "text": f"Your weighted portfolio return is approximately {total_return_pct}%. Compare this against a relevant benchmark before judging performance.",
                }
            )

        return {
            "agent": self.name,
            "intent": intent,
            "data": {
                "concentration_risk": {
                    "top_position_pct": top_position_pct,
                    "top_3_positions_pct": top_3_positions_pct,
                    "flag": flag,
                },
                "performance": {
                    "total_return_pct": total_return_pct,
                    "annualized_return_pct": None,
                },
                "benchmark_comparison": {
                    "benchmark": benchmark,
                    "portfolio_return_pct": total_return_pct,
                    "benchmark_return_pct": benchmark_return_pct,
                    "alpha_pct": alpha_pct,
                },
                "positions": positions,
                "observations": observations[:2],
                "disclaimer": DISCLAIMER,
            },
        }

    def _benchmark(self, currency: str | None):
        if currency == "INR":
            return "NIFTY 50"
        if currency == "EUR":
            return "STOXX Europe 600"
        return "S&P 500"