from pydantic import BaseModel
from typing import Optional


class StockInfo(BaseModel):
    ticker: str
    company_name: str = ""
    exchange: str = "NSE"
    sector: str = ""
    current_price: float = 0.0
    change_percent: float = 0.0


class AnalysisRequest(BaseModel):
    ticker: str
    exchange: str = "NSE"


class IndexData(BaseModel):
    name: str
    value: float
    change: float
    change_percent: float


class MarketOverview(BaseModel):
    nifty50: IndexData
    sensex: IndexData
    bank_nifty: IndexData
    india_vix: IndexData
