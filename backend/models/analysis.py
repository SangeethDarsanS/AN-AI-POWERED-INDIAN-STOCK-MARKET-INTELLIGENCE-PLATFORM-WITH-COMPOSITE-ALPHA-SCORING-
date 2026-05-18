from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class FundamentalResult(BaseModel):
    ticker: str
    exchange: str = "NSE"
    fundamental_score: int = 0
    verdict: str = "MODERATE"
    # Valuation
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    eps: Optional[float] = None
    market_cap: Optional[int] = None
    current_price: Optional[float] = None
    week52_high: Optional[float] = None
    week52_low: Optional[float] = None
    # Returns
    roe: Optional[float] = None
    roce: Optional[float] = None
    # Leverage
    debt_equity: Optional[float] = None
    # Holdings
    promoter_holding: Optional[float] = None
    fii_trend: str = "UNKNOWN"
    # Growth
    revenue_growth_yoy: Optional[float] = None
    net_profit_growth: Optional[float] = None
    # Margins
    gross_margins: Optional[float] = None
    net_profit_margin: Optional[float] = None
    # Income
    dividend_yield: Optional[float] = None
    # Narrative
    summary: str = ""
    flags: List[str] = []


class MovingAverages(BaseModel):
    sma50: Optional[float] = None
    sma200: Optional[float] = None
    ema9: Optional[float] = None
    ema20: Optional[float] = None
    ema21: Optional[float] = None
    ema50: Optional[float] = None
    ema200: Optional[float] = None
    above_50dma: bool = False
    above_200dma: bool = False
    golden_cross: bool = False


class TechnicalResult(BaseModel):
    ticker: str
    timeframe: str = "1D"
    technical_score: int = 0
    trend: str = "NEUTRAL"
    current_price: Optional[float] = None
    rsi: Optional[float] = None
    macd_signal: str = "NEUTRAL"
    macd_line: Optional[float] = None
    macd_hist: Optional[float] = None
    moving_averages: Dict[str, Any] = {}
    bollinger_bands: Dict[str, Any] = {}
    adx: Optional[float] = None
    support: Optional[float] = None
    resistance: Optional[float] = None
    volume_signal: str = "AVERAGE"
    supertrend: str = "NEUTRAL"
    summary: str = ""
    chart_patterns: List[str] = []


class NewsItem(BaseModel):
    headline: str
    source: str
    sentiment: str = "NEUTRAL"
    impact: str = "LOW"
    reason: str = ""
    url: str = ""
    published_at: str = ""


class DialogVerdict(BaseModel):
    label: str
    color: str
    icon: str
    message: str


class SentimentResult(BaseModel):
    ticker: str
    articles_analyzed: int = 0
    overall_sentiment: str = "NEUTRAL"
    sentiment_score: int = 50
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    top_news: List[Dict[str, Any]] = []
    key_themes: List[str] = []
    risk_alerts: List[str] = []
    dialog_verdict: Dict[str, Any] = {}


class IndiaContext(BaseModel):
    factor: str
    impact: str
    reason: str


class DhandhoResult(BaseModel):
    ticker: str
    dhandho_score: int = 0
    label: str = "Watch & Wait"
    color: str = "#FFB300"
    breakdown: Dict[str, Any] = {}
    india_context: List[Dict[str, Any]] = []
    one_liner: str = ""
    best_for: List[str] = []
    risk_factors: List[str] = []
    disclaimer: str = "This score is AI-generated for informational purposes only. Not SEBI-registered investment advice."


class FullAnalysisResult(BaseModel):
    ticker: str
    exchange: str
    fundamental: FundamentalResult
    technical: TechnicalResult
    sentiment: SentimentResult
    dhandho: DhandhoResult


# ---- Sentiment Momentum Divergence (SMD) models ----

class SMDDataPoint(BaseModel):
    """One day's data point in the SMD series."""
    date: str
    sentiment_score: float
    ema3: Optional[float] = None
    ema14: Optional[float] = None
    smd: Optional[float] = None


class SMDResult(BaseModel):
    """
    Sentiment Momentum Divergence result.
    SMD = EMA(3) − EMA(14) of daily sentiment scores.
    Analogous to MACD but applied to news sentiment instead of price.
    """
    ticker: str
    signal: str                  # BULLISH_CROSSOVER | BEARISH_CROSSOVER | BULLISH | BEARISH | NEUTRAL
    smd_value: float             # Latest SMD value
    ema3: float                  # Latest 3-day EMA of sentiment
    ema14: float                 # Latest 14-day EMA of sentiment
    data_points: int             # Number of historical records used
    history: List[SMDDataPoint] = []
    interpretation: str          # Human-readable explanation
    confidence: str              # HIGH (≥14 pts) | MEDIUM (≥7 pts) | LOW (<7 pts)
