from flask import request, jsonify
from stockapi import stock_search

countries = ["India 🇮🇳", "United States 🇺🇸", "China 🇨🇳", "Japan 🇯🇵", "Germany 🇩🇪"]


def get_sidebar_news():
    news_country = request.args.get("news_country") or countries[0]
    news_page = int(request.args.get("news_page", 0))
    news_per_page = 2

    info = stock_search(news_country)
    news = list(info["news"])

    total_news = len(news)
    if total_news == 0:
        return jsonify({"news": [], "total": 0})

    max_page = (total_news - 1) // news_per_page

    # 🔥 Wrap-around logic
    if news_page < 0:
        news_page = max_page
    elif news_page > max_page:
        news_page = 0
    if news_page > max_page:
        news_page = news_page - max_page
    # print("news page", news_page, max_page)
    start = news_page * news_per_page
    end = start + news_per_page
    # print("start", start, end)
    sliced_news = news[start:end]

    return sliced_news, news_country, total_news, news_page
