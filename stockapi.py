import yfinance as yf


def stock_get(stock, period="max", interval="1d"):
    try:
        ticker = yf.Ticker(stock)
        history = ticker.history(period=period, interval=interval)

        if history is None or history.empty:
            return {
                "details": {"price": [], "info": {}},
                "chart_data": {
                    "labels": [],
                    "open": [],
                    "high": [],
                    "low": [],
                    "close": [],
                },
            }
        # print("history:", history)
        info = ticker.info
        details = {"price": history.to_dict("records"), "info": info}
        chart_data = {
            "labels": [str(date.date()) for date in history.index],
            "open": history["Open"].tolist(),
            "high": history["High"].tolist(),
            "low": history["Low"].tolist(),
            "close": history["Close"].tolist(),
        }
        # print("Sample labels with time:", chart_data["labels"][:400])
        # print("details", details.get("info", {}))
        return {"details": details, "chart_data": chart_data}
    except Exception as e:
        print("Yahoo error:", e)

        return {
            "details": {"price": [], "info": {}},
            "chart_data": {
                "labels": [],
                "open": [],
                "high": [],
                "low": [],
                "close": [],
            },
        }


# print(get_stock_info("AAPL", "1mo"))


def stock_search(symbol):
    # print("Searching for:", symbol)
    results = yf.Search(symbol)
    # print("results:", results.quotes)
    results = {
        "quotes": results.quotes,
        "news": results.news,
        "research": results.research,
        "lists": results.lists,
        "nav": results.nav,
    }
    return results


def stock_indices():
    indices = {
        "Americas": [
            [
                "VIX",
                "US Dollar",
                "IBOVESPA",
                "S&P 500",
                "Dow Jones",
                "Nasdaq",
                "Russell 2000",
                "S&P/TSX Composite",
            ],
        ],
        "Asia": [
            "Nikkei 225",
            "Hang Seng",
            "Shanghai Composite",
            "KOSPI",
            "Sensex",
            "Nifty 50",
            "ASX 200",
            "Jakarta Composite",
        ],
        "Europe": [
            "FTSE",
            "FTSE 100",
            "CAC 40",
            "DAX",
            "British Pound",
            "Euro Stoxx 50",
            "MSCI Europe",
            "Euronext 100",
        ],
    }
    us = yf.Market("ASIA")
    print("US Market Status:", us.status)  # Dict: open/high/low
    print("US Summary:", us.summary)  # DataFrame preview
    # print("US Overview:", us.overview)
    # indices = yf.Tickers("^GSPC ^DJI ^IXIC ^RUT ^FTSE ^N225 ^HSI")
    # return indices.tickers
