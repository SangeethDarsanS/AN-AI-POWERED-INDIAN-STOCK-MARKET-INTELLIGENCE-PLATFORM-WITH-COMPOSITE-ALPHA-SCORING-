import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, DateTime, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bharatstocks.db")

# SQLite needs special connect args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class StockDB(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), unique=True, index=True)
    company_name = Column(String(200))
    exchange = Column(String(5))
    sector = Column(String(100))
    market_cap_cr = Column(Float)
    nifty50 = Column(Boolean, default=False)
    sensex30 = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalysisCacheDB(Base):
    __tablename__ = "analysis_cache"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), index=True)
    analysis_type = Column(String(20))
    result = Column(JSON)
    dhandho_score = Column(Integer, nullable=True)
    analyzed_at = Column(DateTime, default=datetime.utcnow)


class NewsDB(Base):
    __tablename__ = "stock_news"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), index=True)
    headline = Column(Text)
    source = Column(String(100))
    url = Column(Text)
    sentiment = Column(String(10))
    impact = Column(String(10))
    sentiment_reason = Column(Text)
    published_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)


class SentimentHistoryDB(Base):
    """Stores one sentiment score per ticker per day for SMD computation."""
    __tablename__ = "sentiment_history"
    __table_args__ = (UniqueConstraint("ticker", "date", name="uq_ticker_date"),)

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), index=True)
    date = Column(String(10), index=True)        # YYYY-MM-DD
    sentiment_score = Column(Float)
    overall_sentiment = Column(String(10))
    articles_analyzed = Column(Integer, default=0)
    recorded_at = Column(DateTime, default=datetime.utcnow)


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# In-memory cache fallback
_memory_cache: dict = {}


def cache_set(key: str, value: dict):
    _memory_cache[key] = value


def cache_get(key: str) -> dict | None:
    return _memory_cache.get(key)


# ---------- Sentiment history helpers (used by SMD system) ----------

def save_sentiment_history(ticker: str, score: float, overall: str, articles: int):
    """Upsert today's sentiment score for a ticker (one record per day)."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    db = SessionLocal()
    try:
        existing = (
            db.query(SentimentHistoryDB)
            .filter_by(ticker=ticker, date=today)
            .first()
        )
        if existing:
            existing.sentiment_score = score
            existing.overall_sentiment = overall
            existing.articles_analyzed = articles
            existing.recorded_at = datetime.utcnow()
        else:
            db.add(SentimentHistoryDB(
                ticker=ticker,
                date=today,
                sentiment_score=score,
                overall_sentiment=overall,
                articles_analyzed=articles,
            ))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def get_sentiment_history(ticker: str, days: int = 60) -> list[dict]:
    """Return up to `days` most recent sentiment records for a ticker, oldest first."""
    db = SessionLocal()
    try:
        rows = (
            db.query(SentimentHistoryDB)
            .filter(SentimentHistoryDB.ticker == ticker)
            .order_by(SentimentHistoryDB.date.desc())
            .limit(days)
            .all()
        )
        # Reverse so oldest → newest for EMA computation
        return [
            {
                "date": r.date,
                "sentiment_score": r.sentiment_score,
                "overall_sentiment": r.overall_sentiment,
                "articles_analyzed": r.articles_analyzed,
            }
            for r in reversed(rows)
        ]
    finally:
        db.close()
