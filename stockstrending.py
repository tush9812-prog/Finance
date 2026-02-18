import requests
from bs4 import BeautifulSoup
import re


def stocks_trending():
    url = "https://finance.yahoo.com/markets/stocks/most-active/"
    headers = {"User-Agent": "Stock"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")
    tickers = []
    if table:
        rows = table.find_all("tr")[1:]  # Skip header
        for row in rows:  # Get first 20
            cells = row.find_all("td")
            if cells:
                # print("cells:", cells[4].get_text())  # Debug: print th
                price_str = cells[3].text.strip()
                parts = re.split(r"\s{2,}", price_str)
                ticker = {
                    "Symbol": cells[0].text.strip(),
                    "Name": cells[1].text.strip(),
                    "Price": parts[0] if parts else price_str,
                    "Change": cells[4].text.strip(),
                    "Change %": cells[5].text.strip(),
                    "Volume": cells[6].text.strip(),
                    "Avg_Volume": cells[7].text.strip(),
                }
                tickers.append(ticker)
    return tickers
