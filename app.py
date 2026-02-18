from flask import Flask, jsonify, render_template, request
from stockapi import stock_get, stock_search, stock_indices
from flask_socketio import SocketIO, emit
from stockstrending import stocks_trending
from webSocketForPriceStream import stock_webSocket
import yfinance as yf

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
countries = ["India 🇮🇳", "United States 🇺🇸", "China 🇨🇳", "Japan 🇯🇵", "Germany 🇩🇪"]


@app.route("/stock/<symbol>")
def get_single_stock_price(symbol):
    stock = stock_get(symbol)
    return render_template("stock.html", symbol=symbol, stock=stock, show_table=False)


@app.route("/api/search/<symbol>", methods=["GET"])
def search_stock(symbol):
    results = stock_search(symbol)

    # return jsonify({"symbol": symbol, "results": results})


@app.route("/")
def index():
    selected_country = request.args.get("country", countries[0])
    # News
    news_country = request.args.get("news_country", countries[0])
    info = stock_search(news_country)
    news = list(info["news"])
    news_page = min(request.args.get("news_page", 0, type=int), len(news))
    news_per_page = 2

    # Most active stocks
    trending_stocks = stocks_trending()

    # stock_indices()
    return render_template(
        "base.html",
        countries=countries,
        news=news,
        news_country=news_country,
        news_page=news_page,
        news_per_page=news_per_page,
        trending_stocks=trending_stocks,
        show_table=True,
    )


@app.context_processor
def inject_news_context():
    """Auto-injects news vars to ALL templates"""
    news_country = request.args.get("news_country", "United States 🇺🇸")
    try:
        info = stock_search(news_country)
        news = list(info["news"])
    except:
        news = []
    return {
        "countries": countries,
        "news": news,
        "news_country": news_country,
        "news_page": int(request.args.get("news_page", 0)),
        "news_per_page": 2,
    }


@socketio.on("subscribe")
def handle_subscribe(data):
    print("data incomi", data)
    stock_webSocket(data, socketio)


@socketio.on("connect")
def handle_connect():
    emit("status", {"msg": "Connected to live prices"})


if __name__ == "__main__":
    socketio.run(app, debug=True, port=4000)
