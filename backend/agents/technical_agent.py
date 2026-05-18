import os
import json
import anthropic
from models.analysis import TechnicalResult
from data_sources.yfinance_india import YFinanceIndia
from utils.indicators import TechnicalIndicators
from utils.prompt_builder import build_technical_prompt


class TechnicalAgent:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None
        self.yf = YFinanceIndia()
        self.indicators = TechnicalIndicators()

    def analyze(self, ticker: str, exchange: str = "NSE") -> TechnicalResult:
        # Use 1y (≈252 trading days) so that 200 DMA, golden/death cross can be computed
        df = self.yf.get_historical_data(ticker, exchange, period="1y")

        if df.empty:
            return TechnicalResult(
                ticker=ticker,
                technical_score=50,
                trend="NEUTRAL",
                summary="No historical price data available for this ticker.",
            )

        ind = self.indicators.compute_all(df)
        macd_data = ind.get("macd", {})
        mas = ind.get("moving_averages", {})
        bb = ind.get("bollinger_bands", {})

        # Common fields shared by AI and fallback paths
        common_fields = dict(
            ticker=ticker,
            timeframe="1D",
            current_price=ind.get("current_price"),
            rsi=ind.get("rsi"),
            moving_averages=mas,
            bollinger_bands=bb,
            adx=ind.get("adx"),
            support=ind.get("support"),
            resistance=ind.get("resistance"),
            volume_signal=ind.get("volume_signal", "AVERAGE"),
            supertrend=ind.get("supertrend", "NEUTRAL"),
            macd_line=macd_data.get("macd"),
            macd_hist=macd_data.get("histogram"),
        )

        # Try AI analysis
        if self.client:
            try:
                prompt = build_technical_prompt(ticker, ind)
                response = self.client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                text = response.content[0].text.strip()
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
                return TechnicalResult(
                    **common_fields,
                    technical_score=ai_result.get("technical_score", 50),
                    trend=ai_result.get("trend", "NEUTRAL"),
                    macd_signal=ai_result.get("macd_signal", macd_data.get("crossover", "NEUTRAL")),
                    summary=ai_result.get("summary", ""),
                    chart_patterns=ai_result.get("chart_patterns", []),
                )
            except Exception:
                pass

        # Fallback heuristic
        score = self._heuristic_score(ind)
        trend = "BULLISH" if score >= 60 else "BEARISH" if score <= 40 else "NEUTRAL"
        return TechnicalResult(
            **common_fields,
            technical_score=score,
            trend=trend,
            macd_signal=macd_data.get("crossover", "NEUTRAL"),
            summary=f"{ticker} is showing {trend.lower()} technical signals.",
            chart_patterns=[],
        )

    def _heuristic_score(self, ind: dict) -> int:
        score = 50
        rsi = ind.get("rsi")
        if rsi is not None:
            if 40 <= rsi <= 60: score += 10
            elif 30 <= rsi < 40 or 60 < rsi <= 70: score += 5
            elif rsi < 30: score += 15  # oversold — potential bullish opportunity
            elif rsi > 70: score -= 10  # overbought

        macd = ind.get("macd", {})
        crossover = macd.get("crossover", "NEUTRAL")
        if crossover == "BULLISH_CROSSOVER": score += 20
        elif crossover == "BEARISH_CROSSOVER": score -= 20
        elif crossover == "BULLISH": score += 10
        elif crossover == "BEARISH": score -= 10

        mas = ind.get("moving_averages", {})
        if mas.get("above_200dma"): score += 15
        if mas.get("above_50dma"): score += 10
        if mas.get("golden_cross"): score += 10
        if mas.get("death_cross"): score -= 10

        adx = ind.get("adx")
        if adx is not None:
            if adx > 25: score += 5   # strong trend present

        if ind.get("volume_signal") == "ABOVE_AVERAGE": score += 5
        if ind.get("supertrend") == "BUY": score += 10
        elif ind.get("supertrend") == "SELL": score -= 10

        return max(0, min(100, score))
