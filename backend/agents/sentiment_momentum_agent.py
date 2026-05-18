"""
Sentiment Momentum Divergence (SMD) Agent
==========================================
Novel indicator proposed for BharatStocks AI research paper.

Concept
-------
Applies EMA-crossover logic (as in MACD for price) to *daily news sentiment scores*
instead of price. The divergence between a fast EMA and a slow EMA of sentiment
acts as an early-warning signal for shifts in market narrative.

    SMD = EMA(3, sentiment) − EMA(14, sentiment)

Signal rules (mirrors MACD crossover interpretation):
  BULLISH_CROSSOVER  — SMD crossed above 0 (short-term narrative accelerating positive)
  BEARISH_CROSSOVER  — SMD crossed below 0 (narrative deteriorating)
  BULLISH            — SMD > +2 (sustained positive sentiment momentum)
  BEARISH            — SMD < −2 (sustained negative sentiment momentum)
  NEUTRAL            — |SMD| ≤ 2 (no directional bias)

Confidence is based on the number of data points available:
  HIGH   ≥ 14 days  (full EMA-14 seed available)
  MEDIUM  7–13 days
  LOW    < 7 days   (estimates only)

Reference
---------
Inspired by Gerald Appel's MACD (1979) applied to NLP sentiment time series.
"""
from typing import Optional
from models.analysis import SMDResult, SMDDataPoint
from db.database import get_sentiment_history

# Threshold below which SMD is considered "near zero" / neutral
_NEUTRAL_BAND = 2.0


def _compute_ema_series(values: list[float], period: int) -> list[Optional[float]]:
    """
    Compute a full EMA series for `values` using the given `period`.

    - If len(values) >= period: seeds with SMA of first `period` values.
    - If len(values) < period : seeds with the first value and applies the
      multiplier from the start (best-effort for sparse data).

    Returns a list of the same length as `values`.
    Positions before the seed index are None.
    """
    n = len(values)
    if n == 0:
        return []

    k = 2.0 / (period + 1)
    result: list[Optional[float]] = [None] * n

    if n >= period:
        seed_idx = period - 1
        result[seed_idx] = sum(values[:period]) / period
        for i in range(seed_idx + 1, n):
            result[i] = values[i] * k + result[i - 1] * (1 - k)
    else:
        # Sparse fallback: seed with first value, apply EMA from index 0
        result[0] = float(values[0])
        for i in range(1, n):
            result[i] = values[i] * k + result[i - 1] * (1 - k)

    return result


def _last_valid(series: list[Optional[float]], fallback: float = 50.0) -> float:
    for v in reversed(series):
        if v is not None:
            return v
    return fallback


def _classify_signal(smd_now: float, smd_prev: Optional[float]) -> str:
    if smd_prev is not None:
        if smd_prev <= 0 and smd_now > 0:
            return "BULLISH_CROSSOVER"
        if smd_prev >= 0 and smd_now < 0:
            return "BEARISH_CROSSOVER"
    if smd_now > _NEUTRAL_BAND:
        return "BULLISH"
    if smd_now < -_NEUTRAL_BAND:
        return "BEARISH"
    return "NEUTRAL"


def _confidence_label(n: int) -> str:
    if n >= 14:
        return "HIGH"
    if n >= 7:
        return "MEDIUM"
    return "LOW"


def _build_interpretation(signal: str, smd: float, n: int) -> str:
    _msgs = {
        "BULLISH_CROSSOVER": (
            f"SMD crossed above zero (SMD = {smd:+.1f}). "
            "Short-term sentiment momentum has turned positive relative to the 14-day baseline — "
            "historically a precursor to positive price action in Indian equities."
        ),
        "BEARISH_CROSSOVER": (
            f"SMD crossed below zero (SMD = {smd:+.1f}). "
            "Sentiment momentum is deteriorating faster than the baseline — "
            "watch for downside pressure in coming sessions."
        ),
        "BULLISH": (
            f"SMD is in sustained positive territory (SMD = {smd:+.1f}). "
            "News flow momentum consistently exceeds the long-term average."
        ),
        "BEARISH": (
            f"SMD is in sustained negative territory (SMD = {smd:+.1f}). "
            "Persistent negative news relative to baseline — elevated risk."
        ),
        "NEUTRAL": (
            f"SMD near zero (SMD = {smd:+.1f}). "
            "No clear directional bias; sentiment momentum is balanced."
        ),
    }
    base = _msgs.get(signal, "")
    if n < 7:
        base += (
            f" [LOW CONFIDENCE — only {n} data point(s) available. "
            "Run daily sentiment analyses to build a reliable SMD signal.]"
        )
    return base


class SentimentMomentumAgent:
    """
    Computes the Sentiment Momentum Divergence (SMD) indicator for a ticker
    using stored daily sentiment history.
    """

    def compute(self, ticker: str) -> SMDResult:
        history = get_sentiment_history(ticker, days=60)

        if not history:
            return SMDResult(
                ticker=ticker,
                signal="NEUTRAL",
                smd_value=0.0,
                ema3=50.0,
                ema14=50.0,
                data_points=0,
                history=[],
                interpretation=(
                    "No sentiment history found. Run /api/analysis/sentiment or "
                    "/api/analysis/full for this ticker at least once to seed the SMD system."
                ),
                confidence="LOW",
            )

        scores = [h["sentiment_score"] for h in history]
        ema3_series = _compute_ema_series(scores, period=3)
        ema14_series = _compute_ema_series(scores, period=14)

        # Build full history series for charting
        data_points_list: list[SMDDataPoint] = []
        for i, h in enumerate(history):
            e3 = ema3_series[i]
            e14 = ema14_series[i]
            smd = round(e3 - e14, 2) if (e3 is not None and e14 is not None) else None
            data_points_list.append(SMDDataPoint(
                date=h["date"],
                sentiment_score=h["sentiment_score"],
                ema3=round(e3, 2) if e3 is not None else None,
                ema14=round(e14, 2) if e14 is not None else None,
                smd=smd,
            ))

        last_e3 = _last_valid(ema3_series)
        last_e14 = _last_valid(ema14_series)
        smd_now = round(last_e3 - last_e14, 2)

        # Previous SMD for crossover detection
        smd_prev: Optional[float] = None
        for dp in reversed(data_points_list[:-1]):
            if dp.smd is not None:
                smd_prev = dp.smd
                break

        signal = _classify_signal(smd_now, smd_prev)
        n = len(history)

        return SMDResult(
            ticker=ticker,
            signal=signal,
            smd_value=smd_now,
            ema3=round(last_e3, 2),
            ema14=round(last_e14, 2),
            data_points=n,
            history=data_points_list,
            interpretation=_build_interpretation(signal, smd_now, n),
            confidence=_confidence_label(n),
        )
