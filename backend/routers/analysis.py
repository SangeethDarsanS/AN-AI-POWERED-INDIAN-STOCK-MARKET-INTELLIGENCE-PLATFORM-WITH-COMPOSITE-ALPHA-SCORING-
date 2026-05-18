from fastapi import APIRouter, HTTPException
from models.stock import AnalysisRequest
from models.analysis import (
    FundamentalResult, TechnicalResult, SentimentResult,
    FullAnalysisResult, SMDResult,
)
from agents.fundamental_agent import FundamentalAgent
from agents.technical_agent import TechnicalAgent
from agents.news_sentiment_agent import NewsSentimentAgent
from agents.dhandho_score_agent import DhandhoScoreAgent
from agents.sentiment_momentum_agent import SentimentMomentumAgent
from db.database import cache_set, cache_get, save_sentiment_history

router = APIRouter()

fundamental_agent = FundamentalAgent()
technical_agent = TechnicalAgent()
sentiment_agent = NewsSentimentAgent()
dhandho_agent = DhandhoScoreAgent()
smd_agent = SentimentMomentumAgent()


@router.post("/fundamental", response_model=FundamentalResult)
async def run_fundamental(req: AnalysisRequest):
    try:
        result = fundamental_agent.analyze(req.ticker, req.exchange)
        cache_set(f"fundamental:{req.ticker}", result.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/technical", response_model=TechnicalResult)
async def run_technical(req: AnalysisRequest):
    try:
        result = technical_agent.analyze(req.ticker, req.exchange)
        cache_set(f"technical:{req.ticker}", result.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment", response_model=SentimentResult)
async def run_sentiment(req: AnalysisRequest):
    try:
        result = sentiment_agent.analyze(req.ticker, exchange=req.exchange)
        cache_set(f"sentiment:{req.ticker}", result.model_dump())
        # Persist daily snapshot for SMD computation
        save_sentiment_history(
            ticker=req.ticker.upper(),
            score=result.sentiment_score,
            overall=result.overall_sentiment,
            articles=result.articles_analyzed,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full")
async def run_full_analysis(req: AnalysisRequest):
    try:
        fundamental = fundamental_agent.analyze(req.ticker, req.exchange)
        technical = technical_agent.analyze(req.ticker, req.exchange)
        sentiment = sentiment_agent.analyze(req.ticker, exchange=req.exchange)
        dhandho = dhandho_agent.compute(req.ticker, fundamental, technical, sentiment)

        # Persist daily snapshot for SMD computation
        save_sentiment_history(
            ticker=req.ticker.upper(),
            score=sentiment.sentiment_score,
            overall=sentiment.overall_sentiment,
            articles=sentiment.articles_analyzed,
        )

        result = FullAnalysisResult(
            ticker=req.ticker,
            exchange=req.exchange,
            fundamental=fundamental,
            technical=technical,
            sentiment=sentiment,
            dhandho=dhandho,
        )
        cache_set(f"full:{req.ticker}", result.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/smd/{ticker}", response_model=SMDResult)
async def get_smd(ticker: str):
    """
    Sentiment Momentum Divergence (SMD) for a ticker.

    Computes EMA(3) and EMA(14) of daily sentiment scores stored in the DB,
    then returns SMD = EMA3 − EMA14 along with signal classification and
    full history for charting.

    Requires prior /sentiment or /full calls to have seeded the history.
    """
    try:
        result = smd_agent.compute(ticker.upper())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cached/{ticker}")
async def get_cached(ticker: str):
    result = cache_get(f"full:{ticker.upper()}")
    if not result:
        raise HTTPException(status_code=404, detail=f"No cached analysis for {ticker}")
    return result
