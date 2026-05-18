import os
import json
import anthropic
from models.analysis import FundamentalResult
from data_sources.yfinance_india import YFinanceIndia
from utils.prompt_builder import build_fundamental_prompt


class FundamentalAgent:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None
        self.yf = YFinanceIndia()

    def analyze(self, ticker: str, exchange: str = "NSE") -> FundamentalResult:
        info = self.yf.get_stock_info(ticker, exchange)

        # Compute ROCE and fallback ROE from financial statements
        roce = None
        try:
            roce = self.yf.compute_roce(ticker, exchange)
        except Exception:
            pass

        # Fill ROE from financial statements if yfinance info didn't provide it
        roe = info.get("roe")
        if roe is None:
            try:
                roe = self.yf.compute_roe(ticker, exchange)
            except Exception:
                pass

        financial_data = {
            "ticker": ticker,
            "exchange": exchange,
            "company_name": info.get("company_name", ticker),
            "current_price": info.get("current_price"),
            "market_cap": info.get("market_cap"),
            "pe_ratio": info.get("pe_ratio"),
            "pb_ratio": info.get("pb_ratio"),
            "eps": info.get("eps"),
            "roe": roe,
            "roce": roce,
            "debt_equity": info.get("debt_equity"),
            "revenue_growth_yoy": info.get("revenue_growth"),
            "earnings_growth": info.get("earnings_growth"),
            "gross_margins": info.get("gross_margins"),
            "net_profit_margin": info.get("profit_margins"),
            "dividend_yield": info.get("dividend_yield"),
            "52w_high": info.get("52w_high"),
            "52w_low": info.get("52w_low"),
        }

        # Shared result kwargs used by both AI and fallback paths
        common_fields = dict(
            ticker=ticker,
            exchange=exchange,
            pe_ratio=financial_data.get("pe_ratio"),
            pb_ratio=financial_data.get("pb_ratio"),
            eps=financial_data.get("eps"),
            market_cap=financial_data.get("market_cap"),
            current_price=financial_data.get("current_price"),
            week52_high=financial_data.get("52w_high"),
            week52_low=financial_data.get("52w_low"),
            roe=roe,
            roce=roce,
            debt_equity=financial_data.get("debt_equity"),
            revenue_growth_yoy=financial_data.get("revenue_growth_yoy"),
            net_profit_growth=financial_data.get("earnings_growth"),
            gross_margins=financial_data.get("gross_margins"),
            net_profit_margin=financial_data.get("net_profit_margin"),
            dividend_yield=financial_data.get("dividend_yield"),
            # promoter_holding and fii_trend are not available from yfinance
            promoter_holding=None,
            fii_trend="UNKNOWN",
        )

        # Try AI analysis
        if self.client:
            try:
                prompt = build_fundamental_prompt(ticker, financial_data)
                response = self.client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                text = response.content[0].text.strip()
                # Clean markdown code fences if present
                if "```" in text:
                    parts = text.split("```")
                    for part in parts:
                        stripped = part.strip()
                        if stripped.startswith("json"):
                            stripped = stripped[4:].strip()
                        if stripped.startswith("{"):
                            text = stripped
                            break
                ai_result = json.loads(text)
                return FundamentalResult(
                    **common_fields,
                    fundamental_score=ai_result.get("fundamental_score", 50),
                    verdict=ai_result.get("verdict", "MODERATE"),
                    summary=ai_result.get("summary", ""),
                    flags=ai_result.get("flags", []),
                )
            except Exception:
                pass

        # Fallback heuristic scoring
        score = self._heuristic_score(financial_data)
        verdict = "STRONG" if score >= 70 else "MODERATE" if score >= 40 else "WEAK"
        return FundamentalResult(
            **common_fields,
            fundamental_score=score,
            verdict=verdict,
            summary=f"{ticker} fundamental analysis based on available market data.",
            flags=[],
        )

    def _heuristic_score(self, data: dict) -> int:
        score = 40  # base
        roe = data.get("roe")
        if roe is not None:
            if roe > 20: score += 20
            elif roe > 15: score += 15
            elif roe > 10: score += 8

        roce = data.get("roce")
        if roce is not None:
            if roce > 20: score += 10
            elif roce > 12: score += 6

        de = data.get("debt_equity")
        if de is not None:
            if de < 0.3: score += 20
            elif de < 0.5: score += 15
            elif de < 1.0: score += 8
            elif de > 3.0: score -= 15

        pe = data.get("pe_ratio")
        if pe is not None and pe > 0:
            if pe < 15: score += 15
            elif pe < 25: score += 10
            elif pe < 40: score += 5
            elif pe > 60: score -= 10

        rev_growth = data.get("revenue_growth_yoy")
        if rev_growth is not None:
            if rev_growth > 20: score += 15
            elif rev_growth > 10: score += 10
            elif rev_growth > 0: score += 5
            elif rev_growth < -10: score -= 10

        margin = data.get("net_profit_margin")
        if margin is not None:
            if margin > 20: score += 10
            elif margin > 10: score += 5

        return max(0, min(100, score))
