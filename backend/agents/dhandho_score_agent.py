import os
import json
import anthropic
from models.analysis import FundamentalResult, TechnicalResult, SentimentResult, DhandhoResult
from utils.prompt_builder import build_dhandho_prompt

SCORE_BANDS = [
    (80, 100, "Strong Alpha", "#00C853"),
    (60, 79, "Positive Carry", "#2196F3"),
    (40, 59, "Neutral Bias", "#FFB300"),
    (20, 39, "High Beta Risk", "#FF6D00"),
    (0, 19, "Capital At Risk", "#D50000"),
]


class DhandhoScoreAgent:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None

    def compute(
        self,
        ticker: str,
        fundamental: FundamentalResult,
        technical: TechnicalResult,
        sentiment: SentimentResult,
    ) -> DhandhoResult:
        f_score = fundamental.fundamental_score
        t_score = technical.technical_score
        s_score = sentiment.sentiment_score

        base_score = f_score * 0.40 + t_score * 0.35 + s_score * 0.25

        # India context adjustments
        india_context = []
        adjustment = 0

        # Nifty 50 premium (simple check by known tickers)
        nifty50 = [
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "ITC",
            "SBIN", "BHARTIARTL", "KOTAKBANK", "LT", "AXISBANK",
            # Additional Nifty 50 constituents
            "SUNPHARMA", "BAJFINANCE", "WIPRO", "HCLTECH", "TITAN", "NESTLEIND",
            "MARUTI", "ULTRACEMCO", "NTPC", "POWERGRID", "COALINDIA", "ONGC",
            "BPCL", "TATAMOTORS", "TATASTEEL", "ADANIENT", "ADANIPORTS",
            "DIVISLAB", "CIPLA", "DRREDDY", "APOLLOHOSP", "BAJAJFINSV",
            "BAJAJ-AUTO", "EICHERMOT", "HEROMOTOCO", "JSWSTEEL", "HINDALCO",
            "GRASIM", "TECHM", "INDUSINDBK", "BRITANNIA", "ASIANPAINT",
            "LTIM", "SHRIRAMFIN", "TRENT", "BEL", "JIOFIN",
        ]
        if ticker.upper().replace(".NS", "").replace(".BO", "") in nifty50:
            adjustment += 3
            india_context.append({
                "factor": "Nifty 50 Constituent",
                "impact": "+3",
                "reason": "Blue chip stability premium"
            })

        # Debt concern
        if fundamental.debt_equity and fundamental.debt_equity > 3.0:
            adjustment -= 10
            india_context.append({
                "factor": "High Leverage",
                "impact": "-10",
                "reason": "Debt-to-equity ratio exceeds safe threshold for Indian market"
            })

        # Strong fundamentals bonus
        if f_score >= 75:
            india_context.append({
                "factor": "Strong Fundamentals",
                "impact": "+0",
                "reason": "Solid financial health supports long-term wealth creation"
            })

        final_score = round(min(100, max(0, base_score + adjustment)))

        # Determine label and color
        label, color = "Watch & Wait", "#FFB300"
        for low, high, lbl, clr in SCORE_BANDS:
            if low <= final_score <= high:
                label, color = lbl, clr
                break

        # AI one-liner
        one_liner = f"{ticker} shows a balanced risk-reward profile based on composite analysis."
        best_for = ["Long-term investors"]
        risk_factors = ["Market volatility", "Sector headwinds"]

        if self.client:
            try:
                prompt = build_dhandho_prompt(
                    ticker,
                    fundamental.model_dump(),
                    technical.model_dump(),
                    sentiment.model_dump(),
                )
                response = self.client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=512,
                    messages=[{"role": "user", "content": prompt}]
                )
                text = response.content[0].text.strip()
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                ai_result = json.loads(text)
                one_liner = ai_result.get("one_liner", one_liner)
                best_for = ai_result.get("best_for", best_for)
                risk_factors = ai_result.get("risk_factors", risk_factors)
            except Exception:
                pass

        return DhandhoResult(
            ticker=ticker,
            dhandho_score=final_score,
            label=label,
            color=color,
            breakdown={
                "fundamental": f_score,
                "technical": t_score,
                "sentiment": s_score,
                "india_adjustments": adjustment,
            },
            india_context=india_context,
            one_liner=one_liner,
            best_for=best_for,
            risk_factors=risk_factors,
            disclaimer="This score is AI-generated for informational purposes only. Not SEBI-registered investment advice.",
        )
