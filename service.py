from flask import request, jsonify
from stockapi import stock_search

countries = ["India 🇮🇳", "United States 🇺🇸", "China 🇨🇳", "Japan 🇯🇵", "Germany 🇩🇪"]

countries_fallback_count = 0


def wrapper_sidebar_news(country=countries[0]):
    global countries_fallback_count
    try:
        countries_fallback_count += 1
        country = request.args.get("news_country") or country
        news_page = int(request.args.get("news_page", 0))
        if countries_fallback_count > 10:
            return None
        return get_sidebar_news(country, news_page)
    except Exception as e:
        if country == countries[4]:
            return None
        else:
            return wrapper_sidebar_news(country=countries[countries.index(country) + 1])


def get_sidebar_news(news_country=countries[0], news_page=0):

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
