from flask import Flask, jsonify, render_template, request
from stockapi import stock_get, stock_search, stock_indices
from flask_socketio import SocketIO, emit
from stockstrending import stocks_trending
from webSocketForPriceStream import stock_webSocket
import yfinance as yf
from datetime import datetime, timezone
from common.helperFunctions import get_sidebar_news, countries
from common.topGainers import fetch_stocks_cached
import time


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


@app.route("/stock/<symbol>")
def get_single_stock_price(symbol):
    stock = stock_get(symbol)
    print("Stock data:", stock["details"].get("info")["symbol"])
    news, news_country, total_news, news_page = get_sidebar_news()
    return render_template(
        "stock.html",
        countries=countries,
        news=news,
        total=total_news,
        page=news_page,
        news_country=news_country,
        symbol=stock["details"].get("info")["symbol"],
        stock=stock,
        show_table=False,
    )


@app.route("/api/search/<symbol>", methods=["GET"])
def search_stock(symbol):
    results = stock_search(symbol)

    # return jsonify({"symbol": symbol, "results": results})


@app.route("/api/news")
def api_news():
    news, news_country, total_news, news_page = get_sidebar_news()

    return jsonify(
        {
            "news": news,
            "total": total_news,
            "page": news_page,
            "news_country": news_country,
        }
    )


@app.route("/")
def index():

    # Most active stocks
    trending_stocks = stocks_trending()

    # stock_indices()
    return render_template(
        "base.html",
        countries=countries,
        trending_stocks=trending_stocks,
        show_table=True,
    )


@app.route("/api/top-gainers/<market>", methods=["GET"])
def top_gainers(market: str):
    """Flask API endpoint for dropdown selection."""
    market = request.args.get("market", "US")
    cache_key = int(time.time() // 8000)  # 5-min cache key
    data = fetch_stocks_cached(market, cache_key)
    return jsonify(
        {
            "market": market,
            "timestamp": time.time(),
            "gainers": data,
            "count": len(data),
        }
    )


@socketio.on("subscribe")
def handle_subscribe(data):
    print("data incomi", data)
    stock_webSocket(data, socketio)


@socketio.on("connect")
def handle_connect():
    emit("status", {"msg": "Connected to live prices"})


@app.template_filter("datetimeformat")
def datetimeformat(value):
    if not value:
        return ""
    return datetime.fromtimestamp(value, timezone.utc).strftime("%b %d, %Y")


if __name__ == "__main__":
    # socketio.run(app, debug=True, port=4000)
    socketio.run(app, debug=False, port=5000)
