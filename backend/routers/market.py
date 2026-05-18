from fastapi import APIRouter, Query
from data_sources.nse_fetcher import NSEFetcher

router = APIRouter()
nse = NSEFetcher()

STRATEGY_STOCKS = {
    "consistent_compounders": [
        "TCS", "INFY", "HINDUNILVR", "PIDILITIND", "NESTLEIND",
        "TITAN", "ASIANPAINT", "BAJFINANCE", "HDFCBANK", "BRITANNIA",
        "DIVISLAB", "DRREDDY", "SUNPHARMA",
    ],
    "momentum_kings": [
        "RELIANCE", "BAJFINANCE", "TATAMOTORS", "ZOMATO", "IRCTC",
        "TRENT", "DMART", "PERSISTENT", "COFORGE", "LTIM",
        "KPITTECH", "BHARTIARTL",
    ],
    "high_roe": [
        "BAJFINANCE", "TITAN", "NESTLEIND", "HINDUNILVR", "PIDILITIND",
        "ASIANPAINT", "TCS", "INFY", "DRREDDY", "HDFCBANK",
        "KOTAK", "SUNPHARMA",
    ],
    "small_cap_rockets": [
        "DEEPAKNTR", "PIIND", "KPITTECH", "AAVAS", "CHOLAFIN",
        "MUTHOOTFIN", "CANFINHOME", "IDFCFIRSTB", "AUBANK", "FEDERALBNK",
        "TORNTPHARM", "APLLTD",
    ],
    "fii_darlings": [
        "ICICIBANK", "HDFCBANK", "INFY", "TCS", "RELIANCE",
        "BAJFINANCE", "AXISBANK", "TECHM", "LT", "BHARTIARTL",
        "WIPRO", "HCLTECH",
    ],
    "dividend_aristocrats": [
        "ITC", "COALINDIA", "ONGC", "POWERGRID", "NTPC",
        "BPCL", "HINDUNILVR", "TCS", "INFY", "SBIN",
        "IOC", "GAIL",
    ],
}


@router.get("/indices")
async def get_indices():
    return nse.get_market_overview()


@router.get("/gainers")
async def get_gainers(exchange: str = Query("NSE"), limit: int = Query(10)):
    return nse.get_top_gainers(exchange, limit)


@router.get("/losers")
async def get_losers(exchange: str = Query("NSE"), limit: int = Query(10)):
    return nse.get_top_losers(exchange, limit)


@router.get("/sectors")
async def get_sectors():
    import yfinance as yf
    sectors = {
        "IT": "^CNXIT",
        "Banking": "^NSEBANK",
        "Pharma": "^CNXPHARMA",
        "Auto": "^CNXAUTO",
        "FMCG": "^CNXFMCG",
        "Metal": "^CNXMETAL",
        "Energy": "^CNXENERGY",
        "Realty": "^CNXREALTY",
    }
    result = []
    for name, symbol in sectors.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                price = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2])
                change_pct = round((price - prev) / prev * 100, 2)
                result.append({"sector": name, "change_percent": change_pct, "price": round(price, 2)})
            else:
                result.append({"sector": name, "change_percent": 0.0, "price": 0.0})
        except Exception:
            result.append({"sector": name, "change_percent": 0.0, "price": 0.0})
    return result


@router.get("/screener/{strategy_id}")
async def screener(strategy_id: str):
    import yfinance as yf
    from concurrent.futures import ThreadPoolExecutor
    import asyncio

    symbols = STRATEGY_STOCKS.get(strategy_id, [])
    if not symbols:
        return {"strategy_id": strategy_id, "stocks": []}

    def fetch_one(symbol):
        try:
            t = yf.Ticker(f"{symbol}.NS")
            info = t.info
            hist = t.history(period="5d")
            if hist.empty:
                return None
            price = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else price
            change_pct = round((price - prev) / prev * 100, 2)
            mkcap = info.get("marketCap", 0)
            roe_raw = info.get("returnOnEquity")
            de_raw = info.get("debtToEquity")
            return {
                "ticker": symbol,
                "company_name": info.get("longName") or info.get("shortName") or symbol,
                "price": round(price, 2),
                "change_pct": change_pct,
                "market_cap_cr": round(mkcap / 1e7, 0) if mkcap else None,
                "pe_ratio": round(info.get("trailingPE", 0), 1) if info.get("trailingPE") else None,
                "roe": round(roe_raw * 100, 1) if roe_raw else None,
                "debt_equity": round(de_raw / 100, 2) if de_raw else None,
                "revenue_growth": round(info.get("revenueGrowth", 0) * 100, 1) if info.get("revenueGrowth") else None,
                "sector": info.get("sector", ""),
            }
        except Exception:
            return None

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=6) as executor:
        results = await asyncio.gather(
            *[loop.run_in_executor(executor, fetch_one, s) for s in symbols]
        )

    stocks = [r for r in results if r is not None]
    # Sort by market cap descending
    stocks.sort(key=lambda x: x.get("market_cap_cr") or 0, reverse=True)
    return {"strategy_id": strategy_id, "stocks": stocks}


@router.get("/ipo-calendar")
async def get_ipo_calendar():
    return {
        "upcoming_ipos": [
            {
                "company": "Upcoming IPO Data",
                "open_date": "Check NSE/BSE website",
                "price_band": "N/A",
                "lot_size": "N/A",
                "note": "Real-time IPO data requires NSE/BSE subscription"
            }
        ]
    }


@router.get("/earnings-calendar")
async def get_earnings_calendar():
    return {
        "upcoming_results": [
            {
                "company": "Earnings Calendar",
                "result_date": "Check NSE/BSE website",
                "note": "Real-time earnings calendar requires NSE/BSE subscription"
            }
        ]
    }
