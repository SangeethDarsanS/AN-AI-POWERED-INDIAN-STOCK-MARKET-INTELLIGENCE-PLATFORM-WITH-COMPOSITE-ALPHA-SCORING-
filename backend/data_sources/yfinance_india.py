import yfinance as yf
import pandas as pd
from typing import Optional


class YFinanceIndia:
    def _get_yf_ticker(self, ticker: str, exchange: str = "NSE") -> str:
        ticker = ticker.upper().strip()
        if ticker.endswith(".NS") or ticker.endswith(".BO"):
            return ticker
        suffix = ".NS" if exchange.upper() == "NSE" else ".BO"
        return ticker + suffix

    # ------------------------------------------------------------------ #
    #  Normalisation helpers                                               #
    # ------------------------------------------------------------------ #

    def _normalize_de(self, raw) -> Optional[float]:
        """
        yfinance returns debtToEquity for .NS tickers in percentage form
        (e.g. 6.675 for a 0.067 ratio).  Divide by 100 to get the ratio.
        For banks/NBFCs the returned value can be 700-1200 (i.e. 7-12× ratio
        after dividing by 100), which is still realistic.
        """
        if raw is None:
            return None
        try:
            v = float(raw)
            if v < 0:
                return None
            return round(v / 100, 4)
        except (TypeError, ValueError):
            return None

    def _normalize_yield(self, raw) -> Optional[float]:
        """
        yfinance inconsistently returns dividendYield as:
          • decimal form: 0.0075 → 0.75 %  (most non-Indian stocks)
          • percent form:  0.88  → 0.88 %  (some Indian NSE stocks)
        Heuristic: if raw > 0.5, treat as already a percentage.
        """
        if raw is None or raw == 0:
            return None
        try:
            v = float(raw)
            if v <= 0:
                return None
            if v > 0.5:
                return round(v, 2)       # already in % form
            return round(v * 100, 2)     # decimal form → multiply
        except (TypeError, ValueError):
            return None

    def _safe_pct(self, raw, cap: float = 1000.0) -> Optional[float]:
        """Convert a decimal ratio to % (e.g. 0.15 → 15.0), with sanity cap."""
        if raw is None:
            return None
        try:
            v = float(raw) * 100.0
            if v == 0:
                return None
            return round(min(v, cap), 2)
        except (TypeError, ValueError):
            return None

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def get_stock_info(self, ticker: str, exchange: str = "NSE") -> dict:
        yf_ticker = self._get_yf_ticker(ticker, exchange)
        try:
            stock = yf.Ticker(yf_ticker)
            info = stock.info or {}

            return {
                "ticker": ticker,
                "yf_ticker": yf_ticker,
                "company_name": info.get("longName", ticker),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice") or None,
                "previous_close": info.get("previousClose") or None,
                "change_percent": info.get("regularMarketChangePercent") or None,
                "market_cap": info.get("marketCap") or None,
                "pe_ratio": info.get("trailingPE") or info.get("forwardPE") or None,
                "pb_ratio": info.get("priceToBook") or None,
                "eps": info.get("trailingEps") or info.get("forwardEps") or None,
                # ROE: yfinance often returns None for Indian NSE stocks;
                # compute_roe() fills in from financial statements
                "roe": self._safe_pct(info.get("returnOnEquity")),
                "debt_equity": self._normalize_de(info.get("debtToEquity")),
                "dividend_yield": self._normalize_yield(info.get("dividendYield")),
                # Growth: yfinance returns as decimal fractions
                "revenue_growth": self._safe_pct(info.get("revenueGrowth")),
                "earnings_growth": self._safe_pct(info.get("earningsGrowth")),
                "gross_margins": self._safe_pct(info.get("grossMargins")),
                "profit_margins": self._safe_pct(info.get("profitMargins")),
                "52w_high": info.get("fiftyTwoWeekHigh") or None,
                "52w_low": info.get("fiftyTwoWeekLow") or None,
                "volume": info.get("volume") or 0,
                "avg_volume": info.get("averageVolume") or 0,
                "beta": info.get("beta") or None,
                "currency": info.get("currency", "INR"),
            }
        except Exception as e:
            return {"ticker": ticker, "yf_ticker": yf_ticker, "error": str(e)}

    def get_historical_data(self, ticker: str, exchange: str = "NSE", period: str = "1y") -> pd.DataFrame:
        yf_ticker = self._get_yf_ticker(ticker, exchange)
        try:
            stock = yf.Ticker(yf_ticker)
            df = stock.history(period=period)
            return df
        except Exception:
            return pd.DataFrame()

    def get_financials(self, ticker: str, exchange: str = "NSE") -> dict:
        yf_ticker = self._get_yf_ticker(ticker, exchange)
        try:
            stock = yf.Ticker(yf_ticker)
            result = {}
            try:
                result["income_stmt"] = stock.income_stmt.to_dict() if stock.income_stmt is not None else {}
            except Exception:
                result["income_stmt"] = {}
            try:
                result["balance_sheet"] = stock.balance_sheet.to_dict() if stock.balance_sheet is not None else {}
            except Exception:
                result["balance_sheet"] = {}
            try:
                result["cashflow"] = stock.cashflow.to_dict() if stock.cashflow is not None else {}
            except Exception:
                result["cashflow"] = {}
            return result
        except Exception as e:
            return {"error": str(e)}

    def compute_roce(self, ticker: str, exchange: str = "NSE") -> Optional[float]:
        """
        ROCE = EBIT / Capital Employed × 100
        Capital Employed = Total Assets − Current Liabilities
        """
        yf_ticker = self._get_yf_ticker(ticker, exchange)
        try:
            stock = yf.Ticker(yf_ticker)
            income = stock.income_stmt
            balance = stock.balance_sheet
            if income is None or balance is None or income.empty or balance.empty:
                return None

            ebit = None
            for label in ["EBIT", "Operating Income", "Pretax Income"]:
                if label in income.index:
                    val = income.loc[label].iloc[0]
                    if val is not None and not pd.isna(val):
                        ebit = float(val)
                        break

            total_assets = None
            for label in ["Total Assets"]:
                if label in balance.index:
                    val = balance.loc[label].iloc[0]
                    if val is not None and not pd.isna(val):
                        total_assets = float(val)
                        break

            current_liabilities = None
            for label in ["Current Liabilities", "Total Current Liabilities"]:
                if label in balance.index:
                    val = balance.loc[label].iloc[0]
                    if val is not None and not pd.isna(val):
                        current_liabilities = float(val)
                        break

            if ebit is not None and total_assets is not None and current_liabilities is not None:
                capital_employed = total_assets - current_liabilities
                if capital_employed > 0:
                    return round((ebit / capital_employed) * 100, 2)
        except Exception:
            pass
        return None

    def compute_roe(self, ticker: str, exchange: str = "NSE") -> Optional[float]:
        """
        ROE = Net Income / Total Stockholders Equity × 100
        Fallback when yfinance `info.returnOnEquity` is None.
        """
        yf_ticker = self._get_yf_ticker(ticker, exchange)
        try:
            stock = yf.Ticker(yf_ticker)
            income = stock.income_stmt
            balance = stock.balance_sheet
            if income is None or balance is None or income.empty or balance.empty:
                return None

            net_income = None
            for label in ["Net Income", "Net Income Common Stockholders", "Net Income Applicable To Common Shares"]:
                if label in income.index:
                    val = income.loc[label].iloc[0]
                    if val is not None and not pd.isna(val):
                        net_income = float(val)
                        break

            equity = None
            for label in ["Stockholders Equity", "Total Equity", "Common Stock Equity",
                          "Total Stockholder Equity"]:
                if label in balance.index:
                    val = balance.loc[label].iloc[0]
                    if val is not None and not pd.isna(val):
                        equity = float(val)
                        break

            if net_income is not None and equity is not None and equity != 0:
                return round((net_income / equity) * 100, 2)
        except Exception:
            pass
        return None

    def get_multiple_stocks(self, tickers: list[str], exchange: str = "NSE") -> list[dict]:
        results = []
        for ticker in tickers:
            try:
                info = self.get_stock_info(ticker, exchange)
                results.append(info)
            except Exception:
                pass
        return results
