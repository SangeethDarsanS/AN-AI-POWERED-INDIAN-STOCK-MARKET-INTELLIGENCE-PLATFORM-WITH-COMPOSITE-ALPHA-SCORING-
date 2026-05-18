from fastapi import APIRouter, HTTPException, Query
from agents.fundamental_agent import FundamentalAgent
from agents.technical_agent import TechnicalAgent
from agents.news_sentiment_agent import NewsSentimentAgent
from agents.dhandho_score_agent import DhandhoScoreAgent

router = APIRouter()

fundamental_agent = FundamentalAgent()
technical_agent = TechnicalAgent()
sentiment_agent = NewsSentimentAgent()
dhandho_agent = DhandhoScoreAgent()

LEADERBOARD_TICKERS = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "KOTAKBANK", "LT", "AXISBANK", "MARUTI", "SUNPHARMA",
]


@router.get("/score/{ticker}")
async def get_dhandho_score(ticker: str, exchange: str = Query("NSE")):
    try:
        ticker = ticker.upper()
        fundamental = fundamental_agent.analyze(ticker, exchange)
        technical = technical_agent.analyze(ticker, exchange)
        sentiment = sentiment_agent.analyze(ticker, exchange=exchange)
        dhandho = dhandho_agent.compute(ticker, fundamental, technical, sentiment)
        return dhandho
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard")
async def get_leaderboard():
    results = []
    for ticker in LEADERBOARD_TICKERS[:5]:  # Limit to 5 to avoid timeout
        try:
            fundamental = fundamental_agent.analyze(ticker, "NSE")
            technical = technical_agent.analyze(ticker, "NSE")
            sentiment = sentiment_agent.analyze(ticker, exchange="NSE")
            dhandho = dhandho_agent.compute(ticker, fundamental, technical, sentiment)
            results.append({
                "ticker": ticker,
                "dhandho_score": dhandho.dhandho_score,
                "label": dhandho.label,
                "color": dhandho.color,
                "one_liner": dhandho.one_liner,
            })
        except Exception:
            pass
    results.sort(key=lambda x: x["dhandho_score"], reverse=True)
    return {"leaderboard": results}


@router.get("/watchlist")
async def get_watchlist_scores(tickers: str = Query(..., description="Comma-separated tickers")):
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    results = []
    for ticker in ticker_list[:10]:
        try:
            fundamental = fundamental_agent.analyze(ticker, "NSE")
            technical = technical_agent.analyze(ticker, "NSE")
            sentiment = sentiment_agent.analyze(ticker, exchange="NSE")
            dhandho = dhandho_agent.compute(ticker, fundamental, technical, sentiment)
            results.append({
                "ticker": ticker,
                "dhandho_score": dhandho.dhandho_score,
                "label": dhandho.label,
                "color": dhandho.color,
            })
        except Exception:
            pass
    return {"watchlist_scores": results}
