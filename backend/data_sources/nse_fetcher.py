import yfinance as yf
from typing import Optional

NIFTY50_TICKERS = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK",
    "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "TITAN",
    "NESTLEIND", "WIPRO", "ULTRACEMCO", "TECHM", "POWERGRID",
    "HCLTECH", "SUNPHARMA", "BAJFINANCE", "ADANIENT", "ONGC",
    "NTPC", "JSWSTEEL", "TATACONSUM", "TATAMOTORS", "M&M",
]

INDEX_MAP = {
    "nifty50": "^NSEI",
    "sensex": "^BSESN",
    "bank_nifty": "^NSEBANK",
    "india_vix": "^INDIAVIX",
}


class NSEFetcher:
    def get_market_overview(self) -> dict:
        result = {}
        for key, symbol in INDEX_MAP.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info or {}
                price = info.get("regularMarketPrice") or info.get("previousClose") or 0.0
                prev_close = info.get("previousClose") or price
                change = price - prev_close
                change_pct = (change / prev_close * 100) if prev_close else 0.0

                hist = ticker.history(period="2d")
                if not hist.empty and len(hist) >= 1:
                    price = float(hist["Close"].iloc[-1])
                    if len(hist) >= 2:
                        prev_close = float(hist["Close"].iloc[-2])
                        change = price - prev_close
                        change_pct = (change / prev_close * 100) if prev_close else 0.0

                result[key] = {
                    "name": self._index_name(key),
                    "value": round(price, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_pct, 2),
                }
            except Exception as e:
                result[key] = {
                    "name": self._index_name(key),
                    "value": 0.0,
                    "change": 0.0,
                    "change_percent": 0.0,
                }
        return result

    def _index_name(self, key: str) -> str:
        names = {
            "nifty50": "NIFTY 50",
            "sensex": "SENSEX",
            "bank_nifty": "BANK NIFTY",
            "india_vix": "INDIA VIX",
        }
        return names.get(key, key.upper())

    def get_top_gainers(self, exchange: str = "NSE", limit: int = 10) -> list[dict]:
        stocks = self._fetch_stock_changes(exchange)
        gainers = sorted(stocks, key=lambda x: x["change_percent"], reverse=True)
        return gainers[:limit]

    def get_top_losers(self, exchange: str = "NSE", limit: int = 10) -> list[dict]:
        stocks = self._fetch_stock_changes(exchange)
        losers = sorted(stocks, key=lambda x: x["change_percent"])
        return losers[:limit]

    def _fetch_stock_changes(self, exchange: str = "NSE") -> list[dict]:
        suffix = ".NS" if exchange.upper() == "NSE" else ".BO"
        results = []
        for ticker in NIFTY50_TICKERS[:20]:  # Limit to avoid timeout
            try:
                stock = yf.Ticker(ticker + suffix)
                hist = stock.history(period="2d")
                if len(hist) >= 2:
                    price = float(hist["Close"].iloc[-1])
                    prev = float(hist["Close"].iloc[-2])
                    change = price - prev
                    change_pct = (change / prev * 100) if prev else 0.0
                    info = stock.info or {}
                    results.append({
                        "ticker": ticker,
                        "company_name": info.get("longName", ticker),
                        "price": round(price, 2),
                        "change": round(change, 2),
                        "change_percent": round(change_pct, 2),
                        "volume": info.get("volume") or 0,
                    })
            except Exception:
                continue
        return results
