import pandas as pd
import numpy as np
from typing import Optional


class TechnicalIndicators:
    def compute_rsi(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        if len(prices) < period + 1:
            return None
        delta = prices.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return round(float(rsi.iloc[-1]), 2) if not rsi.empty else None

    def compute_macd(self, prices: pd.Series) -> dict:
        if len(prices) < 26:
            return {"macd": None, "signal": None, "histogram": None, "crossover": "NEUTRAL"}
        ema12 = prices.ewm(span=12, adjust=False).mean()
        ema26 = prices.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line

        crossover = "NEUTRAL"
        if len(macd_line) >= 2:
            if macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2]:
                crossover = "BULLISH_CROSSOVER"
            elif macd_line.iloc[-1] < signal_line.iloc[-1] and macd_line.iloc[-2] >= signal_line.iloc[-2]:
                crossover = "BEARISH_CROSSOVER"
            elif macd_line.iloc[-1] > signal_line.iloc[-1]:
                crossover = "BULLISH"
            elif macd_line.iloc[-1] < signal_line.iloc[-1]:
                crossover = "BEARISH"

        return {
            "macd": round(float(macd_line.iloc[-1]), 4),
            "signal": round(float(signal_line.iloc[-1]), 4),
            "histogram": round(float(histogram.iloc[-1]), 4),
            "crossover": crossover,
        }

    def compute_bollinger_bands(self, prices: pd.Series, period: int = 20) -> dict:
        if len(prices) < period:
            return {"upper": None, "middle": None, "lower": None, "position": "MIDDLE", "bandwidth": None}
        sma = prices.rolling(period).mean()
        std = prices.rolling(period).std()
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        current = prices.iloc[-1]
        u = upper.iloc[-1]
        l = lower.iloc[-1]
        m = sma.iloc[-1]
        bandwidth = round(float((u - l) / m * 100), 2) if m != 0 else None
        position = "MIDDLE"
        if current >= u * 0.98:
            position = "UPPER"
        elif current <= l * 1.02:
            position = "LOWER"
        return {
            "upper": round(float(u), 2),
            "middle": round(float(m), 2),
            "lower": round(float(l), 2),
            "position": position,
            "bandwidth": bandwidth,
        }

    def compute_moving_averages(self, df: pd.DataFrame) -> dict:
        closes = df["Close"]
        current = float(closes.iloc[-1])
        result = {
            "current": round(current, 2),
            "sma50": None, "sma200": None,
            "ema9": None, "ema20": None, "ema21": None, "ema50": None, "ema200": None,
            "above_50dma": False, "above_200dma": False,
            "golden_cross": False, "death_cross": False,
        }
        if len(closes) >= 9:
            result["ema9"] = round(float(closes.ewm(span=9, adjust=False).mean().iloc[-1]), 2)
        if len(closes) >= 20:
            result["ema20"] = round(float(closes.ewm(span=20, adjust=False).mean().iloc[-1]), 2)
        if len(closes) >= 21:
            result["ema21"] = round(float(closes.ewm(span=21, adjust=False).mean().iloc[-1]), 2)
        if len(closes) >= 50:
            sma50 = float(closes.rolling(50).mean().iloc[-1])
            ema50 = float(closes.ewm(span=50, adjust=False).mean().iloc[-1])
            result["sma50"] = round(sma50, 2)
            result["ema50"] = round(ema50, 2)
            result["above_50dma"] = current > sma50
        if len(closes) >= 200:
            sma200 = float(closes.rolling(200).mean().iloc[-1])
            ema200 = float(closes.ewm(span=200, adjust=False).mean().iloc[-1])
            result["sma200"] = round(sma200, 2)
            result["ema200"] = round(ema200, 2)
            result["above_200dma"] = current > sma200
            if result["sma50"]:
                result["golden_cross"] = result["sma50"] > sma200
                result["death_cross"] = result["sma50"] < sma200
        return result

    def compute_support_resistance(self, df: pd.DataFrame) -> dict:
        if len(df) < 20:
            return {"support": None, "resistance": None}
        # Use rolling 20-bar pivots for more accurate S/R
        highs = df["High"].rolling(20).max()
        lows = df["Low"].rolling(20).min()
        # Recent 20 sessions
        recent_support = round(float(lows.iloc[-20:].min()), 2)
        recent_resistance = round(float(highs.iloc[-20:].max()), 2)
        return {
            "support": recent_support,
            "resistance": recent_resistance,
        }

    def compute_adx(self, df: pd.DataFrame, period: int = 14) -> Optional[float]:
        if len(df) < period + 1:
            return None
        high = df["High"]
        low = df["Low"]
        close = df["Close"]
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)
        atr = tr.ewm(span=period, adjust=False).mean()
        plus_dm = high.diff()
        minus_dm = low.diff().abs()
        plus_dm = plus_dm.where((plus_dm > 0) & (plus_dm > minus_dm), 0.0)
        minus_dm_calc = minus_dm.where((minus_dm > 0) & (minus_dm > high.diff().abs()), 0.0)
        plus_di = 100 * plus_dm.ewm(span=period, adjust=False).mean() / atr
        minus_di = 100 * minus_dm_calc.ewm(span=period, adjust=False).mean() / atr
        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
        adx = dx.ewm(span=period, adjust=False).mean()
        return round(float(adx.iloc[-1]), 2) if not adx.empty else None

    def compute_volume_signal(self, df: pd.DataFrame) -> str:
        if len(df) < 20:
            return "AVERAGE"
        avg_vol = df["Volume"].rolling(20).mean().iloc[-1]
        current_vol = df["Volume"].iloc[-1]
        if current_vol > avg_vol * 1.5:
            return "ABOVE_AVERAGE"
        elif current_vol < avg_vol * 0.5:
            return "BELOW_AVERAGE"
        return "AVERAGE"

    def compute_supertrend(self, df: pd.DataFrame, period: int = 7, multiplier: float = 3.0) -> str:
        if len(df) < period + 1:
            return "NEUTRAL"
        try:
            high = df["High"]
            low = df["Low"]
            close = df["Close"]
            hl2 = (high + low) / 2
            tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
            atr = tr.ewm(span=period, adjust=False).mean()
            upperband = hl2 + (multiplier * atr)
            lowerband = hl2 - (multiplier * atr)
            current_price = float(close.iloc[-1])
            if current_price > float(lowerband.iloc[-1]):
                return "BUY"
            elif current_price < float(upperband.iloc[-1]):
                return "SELL"
            return "NEUTRAL"
        except Exception:
            return "NEUTRAL"

    def compute_all(self, df: pd.DataFrame) -> dict:
        if df.empty:
            return {}
        closes = df["Close"]
        rsi = self.compute_rsi(closes)
        macd = self.compute_macd(closes)
        bb = self.compute_bollinger_bands(closes)
        mas = self.compute_moving_averages(df)
        sr = self.compute_support_resistance(df)
        adx = self.compute_adx(df)
        volume_signal = self.compute_volume_signal(df)
        supertrend = self.compute_supertrend(df)
        return {
            "current_price": round(float(closes.iloc[-1]), 2),
            "rsi": rsi,
            "macd": macd,
            "bollinger_bands": bb,
            "moving_averages": mas,
            "support": sr["support"],
            "resistance": sr["resistance"],
            "adx": adx,
            "volume_signal": volume_signal,
            "supertrend": supertrend,
        }
