from flask import Flask, jsonify, render_template, request
from stockapi import stock_get, stock_search, stock_indices
from flask_socketio import SocketIO, emit
from stockstrending import stocks_trending
from webSocketForPriceStream import stock_webSocket
from datetime import datetime, timezone
from service import get_sidebar_news, countries
from common.topGainers import fetch_stocks_cached
import time
from flask_caching import Cache

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


cache = Cache(app, config={"CACHE_TYPE": "simple"})


@cache.cached(timeout=1800, query_string=True)
@app.route("/stock/<symbol>")
def get_single_stock_price(symbol):
    stock = stock_get(symbol)
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


@cache.cached(timeout=1800, query_string=True)
@app.route("/api/search/<symbol>", methods=["GET"])
def search_stock(symbol):
    results = stock_search(symbol)

    # return jsonify({"symbol": symbol, "results": results})


@cache.cached(timeout=1800, query_string=True)
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


@cache.cached(timeout=1800, query_string=True)
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


@cache.cached(timeout=1800, query_string=True)
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


@cache.cached(timeout=1800, query_string=True)
@socketio.on("subscribe")
def handle_subscribe(data):
    print("data incomi", data)
    stock_webSocket(data, socketio)


@cache.cached(timeout=1800, query_string=True)
@socketio.on("connect")
def handle_connect():
    emit("status", {"msg": "Connected to live prices"})


@app.template_filter("datetimeformat")
def datetimeformat(value):
    if not value:
        return ""
    return datetime.fromtimestamp(value, timezone.utc).strftime("%b %d, %Y")


@app.route("/health", methods=["GET"])  # Or '/ping'
def health():
    print("Health check at", datetime.now())
    return "", 200


if __name__ == "__main__":
    # socketio.run(app, debug=True, port=4000)
    socketio.run(app, debug=True, port=4000)
