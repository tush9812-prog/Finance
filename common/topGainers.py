from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any
import time
from functools import lru_cache
import json
from nsetools import Nse

app = Flask(__name__)


# Cache for 5 min (300s) for efficiency
@lru_cache(maxsize=2)
def fetch_stocks_cached(market: str, timestamp: int) -> List[Dict[str, str]]:
    """Cached scraper - called every 5 min."""
    return fetch_stocks(market)


def fetch_stocks(market: str) -> List[Dict[str, str]]:
    """100% efficient scraper: Session reuse, timeout, caching, min data."""
    base_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_8) AppleWebKit (KHTML, like Gecko) Chrome/120.0.0.0 Safari",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.nseindia.com/",
        "Cache-Control": "no-cache",
    }

    urls = {
        "US": "https://finance.yahoo.com/markets/stocks/gainers/",
        "India": "https://www.moneycontrol.com/stocks/marketstats/nsegainer/index.php",
    }

    if market not in urls:
        return []

    url = urls[market]
    session = requests.Session()
    session.headers.update(base_headers)

    try:
        resp = session.get(url, timeout=8)
        resp.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(resp.content, "html.parser")
    return parse_table(soup, market)


def parse_table(soup: BeautifulSoup, market: str) -> List[Dict[str, str]]:
    """Market-specific parsing - top 20 only."""
    tickers = []

    if market == "US":
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")[1:21]
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 8:
                    price_str = cells[3].text.strip()
                    parts = re.split(r"\s{2,}", price_str)
                    tickers.append(
                        {
                            "symbol": cells[0].text.strip(),
                            "name": cells[1].text.strip(),
                            "price": parts[0] if parts else price_str,
                            "change": cells[4].text.strip(),
                            "change_pct": cells[5].text.strip(),
                            "volume": cells[6].text.strip(),
                        }
                    )

    elif market == "India":
        # NSE: Dynamic table (try common selectors)
        table = soup.find("table", {"id": "topGainer-table"}) or soup.find(
            "table", class_="table"
        )
        if not table:
            # Fallback script data
            scripts = soup.find_all("script")
            for script in scripts:
                if script.string and (
                    "topGainers" in script.string or "gainer" in script.string.lower()
                ):
                    match = re.search(r'"data":\s*(\[.*?\])', script.string, re.DOTALL)
                    if match:
                        try:
                            data = json.loads(match.group(1))
                            for item in data[:20]:
                                tickers.append(
                                    {
                                        "symbol": item.get("symbol", ""),
                                        "price": item.get("price", ""),
                                        "change_pct": item.get("pchange", ""),
                                        "volume": item.get("quantity", ""),
                                    }
                                )
                            break
                        except:
                            pass
            return tickers

        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else table.find_all("tr")[1:21]
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 5:
                tickers.append(
                    {
                        "symbol": cells[0].text.strip(),
                        "price": cells[2].text.strip(),
                        "change_pct": cells[3].text.strip(),
                        "volume": cells[4].text.strip() if len(cells) > 4 else "",
                    }
                )

    return tickers[:20]


def parse_nse_api(data: dict) -> List[Dict[str, str]]:
    """Parse NSE JSON API response."""
    tickers = []
    if "data" in data:
        for item in data["data"][:20]:  # Top 20
            tickers.append(
                {
                    "symbol": item.get("symbol", ""),
                    "price": f"{item.get('lastPrice', 0):.2f}",
                    "change_pct": f"{item.get('change', 0):.2f} ({item.get('pChange', 0):.2f}%)",
                    "change": str(item.get("change", 0)),
                    "volume": str(item.get("totalTradedVolume", 0)),
                }
            )
    return tickers
