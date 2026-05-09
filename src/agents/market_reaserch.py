from src.market_data import get_latest_price
class MarketResearchAgent:
    name = "market_research"
    def run(self, query, user_context, intent, classification=None):
        entities = classification.entities if classification else {}
        tickers = entities.get("tickers", [])

        # fallback ticker extraction if classifier misses it
        q = query.lower()
        fallback_map = {
            "apple": "AAPL",
            "aapl": "AAPL",
            "nvidia": "NVDA",
            "nvda": "NVDA",
            "tesla": "TSLA",
            "tsla": "TSLA",
            "asml": "ASML",
        }

        for word, ticker in fallback_map.items():
            if word in q and ticker not in tickers:
                tickers.append(ticker)

        if not tickers:
            return {
                "agent": self.name,
                "intent": intent,
                "data": {
                    "message": "No ticker was found in the query.",
                    "query": query,
                    "disclaimer": "This is educational information, not financial advice.",
                },
            }

        results = []

        for ticker in tickers:
            price = get_latest_price(ticker)

            results.append(
                {
                    "ticker": ticker,
                    "latest_price": round(price, 2) if price is not None else None,
                    "price_source": "yfinance" if price is not None else "unavailable",
                }
            )

        return {
            "agent": self.name,
            "intent": intent,
            "data": {
                "summary": f"Fetched latest available market data for {', '.join(tickers)}.",
                "results": results,
                "disclaimer": "This is educational information, not financial advice.",
            },
        }