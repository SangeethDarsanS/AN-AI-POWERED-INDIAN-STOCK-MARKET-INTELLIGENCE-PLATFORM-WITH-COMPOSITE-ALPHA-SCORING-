"""
News Sentiment Agent — powered by FinBERT (ProsusAI/finbert).

Runs entirely locally. No external AI API calls required.
FinBERT is a BERT model fine-tuned on financial texts (Malo et al., 2014).
"""
from transformers import pipeline
from models.analysis import SentimentResult
from data_sources.news_fetcher import NewsFetcher
from data_sources.yfinance_india import YFinanceIndia


VERDICT_MAP = {
    "POSITIVE": {
        "label": "POSITIVE",
        "color": "#00C853",
        "icon": "trending_up",
        "message": "Recent news flow is predominantly positive. Strong operational momentum detected.",
    },
    "NEGATIVE": {
        "label": "NEGATIVE",
        "color": "#D50000",
        "icon": "trending_down",
        "message": "Recent news flow is concerning. Exercise caution and monitor closely.",
    },
    "NEUTRAL": {
        "label": "NEUTRAL",
        "color": "#757575",
        "icon": "trending_flat",
        "message": "News sentiment is mixed. No strong directional signal from recent news.",
    },
}

# Keyword maps for lightweight theme + risk extraction
_THEME_MAP = {
    "Earnings & Results": [
        "profit", "revenue", "earnings", "results", "quarterly",
        "q1", "q2", "q3", "q4", "annual report", "net income",
    ],
    "Regulatory & Compliance": [
        "sebi", "rbi", "compliance", "regulatory", "penalty",
        "notice", "investigation", "nse action", "bse action",
    ],
    "Expansion & Growth": [
        "expansion", "capacity", "new plant", "acquisition",
        "merger", "deal", "launch", "order win", "new contract",
    ],
    "Debt & Funding": [
        "debt", "loan", "fundraise", "ipo", "fpo",
        "ncd", "bond", "credit rating", "rights issue",
    ],
    "Management Changes": [
        "ceo", "cfo", "managing director", "resignation",
        "appointed", "board change", "new chairman",
    ],
    "Dividends & Buyback": [
        "dividend", "buyback", "bonus shares", "stock split",
    ],
}

_RISK_KEYWORDS = [
    "fraud", "scam", "penalty", "sebi notice", "downgrade", "net loss",
    "write-off", "insolvency", "default", "investigation", "fir", "raid",
    "profit warning", "guidance cut", "margin pressure", "debt default",
]


def _extract_themes(headlines: list[str]) -> list[str]:
    text = " ".join(headlines).lower()
    return [theme for theme, kws in _THEME_MAP.items() if any(k in text for k in kws)]


def _extract_risk_alerts(headlines: list[str]) -> list[str]:
    text = " ".join(headlines).lower()
    return [kw.title() for kw in _RISK_KEYWORDS if kw in text]


def _impact_from_confidence(score: float) -> str:
    if score >= 0.85:
        return "HIGH"
    if score >= 0.65:
        return "MEDIUM"
    return "LOW"


class NewsSentimentAgent:
    """
    Uses ProsusAI/finbert for per-headline sentiment classification.
    The pipeline is loaded once at class level to avoid reloading on every request.
    """
    _finbert = None

    def __init__(self):
        if NewsSentimentAgent._finbert is None:
            NewsSentimentAgent._finbert = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                truncation=True,
                max_length=512,
            )
        self.news_fetcher = NewsFetcher()
        self.yf = YFinanceIndia()

    def analyze(self, ticker: str, company_name: str = "", exchange: str = "NSE") -> SentimentResult:
        clean_ticker = ticker.replace(".NS", "").replace(".BO", "")

        if not company_name:
            try:
                info = self.yf.get_stock_info(clean_ticker, exchange)
                company_name = info.get("company_name", "")
            except Exception:
                pass

        articles = self.news_fetcher.fetch_news(clean_ticker, company_name, limit=10)

        if not articles:
            return SentimentResult(
                ticker=clean_ticker,
                articles_analyzed=0,
                overall_sentiment="NEUTRAL",
                sentiment_score=50,
                summary="No recent news articles found for this stock.",
                dialog_verdict=VERDICT_MAP["NEUTRAL"],
            )

        headlines = [a["headline"] for a in articles]

        # Batch inference — FinBERT returns {"label": "positive/negative/neutral", "score": float}
        raw_results = self._finbert(headlines)

        numeric_scores: list[float] = []
        top_news: list[dict] = []
        counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}

        for article, res in zip(articles, raw_results):
            label = res["label"].upper()
            confidence = res["score"]
            counts[label] += 1

            # Map to 0–100 scale: positive → above 50, negative → below 50
            if label == "POSITIVE":
                article_score = 50.0 + confidence * 50.0
            elif label == "NEGATIVE":
                article_score = 50.0 - confidence * 50.0
            else:
                article_score = 50.0
            numeric_scores.append(article_score)

            top_news.append({
                "headline": article["headline"],
                "source": article["source"],
                "sentiment": label,
                "impact": _impact_from_confidence(confidence),
                "reason": f"FinBERT financial sentiment — {label.lower()} ({confidence:.0%} confidence)",
                "url": article.get("url", ""),
                "published_at": article.get("published_at", ""),
            })

        sentiment_score = int(round(sum(numeric_scores) / len(numeric_scores)))

        if sentiment_score >= 60:
            overall = "POSITIVE"
        elif sentiment_score <= 40:
            overall = "NEGATIVE"
        else:
            overall = "NEUTRAL"

        return SentimentResult(
            ticker=clean_ticker,
            articles_analyzed=len(articles),
            overall_sentiment=overall,
            sentiment_score=sentiment_score,
            positive_count=counts["POSITIVE"],
            negative_count=counts["NEGATIVE"],
            neutral_count=counts["NEUTRAL"],
            top_news=top_news[:5],
            key_themes=_extract_themes(headlines),
            risk_alerts=_extract_risk_alerts(headlines),
            dialog_verdict=VERDICT_MAP.get(overall, VERDICT_MAP["NEUTRAL"]),
        )
