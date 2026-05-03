import yfinance as yf


def get_latest_price(ticker: str):
    try:
        stock = yf.Ticker(ticker)

        # Fast path
        if hasattr(stock, "fast_info") and stock.fast_info:
            price = stock.fast_info.get("last_price")
            if price:
                return float(price)

        # Fallback
        hist = stock.history(period="5d")
        if hist is not None and not hist.empty:
            return float(hist["Close"].dropna().iloc[-1])

    except Exception:
        return None

    return None