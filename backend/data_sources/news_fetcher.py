import feedparser
import yfinance as yf
from datetime import datetime, timezone

RSS_FEEDS = {
    "Economic Times": "https://economictimes.indiatimes.com/markets/rss.cms",
    "Moneycontrol": "https://www.moneycontrol.com/rss/marketreports.xml",
    "Business Standard": "https://www.business-standard.com/rss/markets-106.rss",
    "Livemint": "https://www.livemint.com/rss/markets",
}


def _fmt_timestamp(ts) -> str:
    """Convert Unix timestamp to readable string."""
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    except Exception:
        return ""


class NewsFetcher:
    def fetch_news(self, ticker: str, company_name: str = "", limit: int = 10) -> list[dict]:
        """
        Fetch news for a stock.
        Priority: yfinance news → RSS filtered → general market RSS fallback
        """
        articles = []

        # --- Source 1: yfinance built-in news (most reliable for Indian stocks) ---
        articles = self._fetch_yfinance_news(ticker, limit)

        # --- Source 2: RSS feeds filtered by ticker/company name ---
        if len(articles) < limit:
            rss_articles = self._fetch_rss_filtered(ticker, company_name, limit - len(articles))
            # deduplicate by headline
            seen = {a["headline"] for a in articles}
            for a in rss_articles:
                if a["headline"] not in seen:
                    articles.append(a)
                    seen.add(a["headline"])

        # --- Source 3: General market news as final fallback ---
        if len(articles) == 0:
            articles = self._fetch_rss_general(limit)

        return articles[:limit]

    def _fetch_yfinance_news(self, ticker: str, limit: int = 10) -> list[dict]:
        """Use yfinance Ticker.news which returns stock-specific news."""
        results = []
        # Try both .NS and .BO suffixes
        for suffix in [".NS", ".BO"]:
            sym = ticker.upper().replace(".NS", "").replace(".BO", "") + suffix
            try:
                stock = yf.Ticker(sym)
                news = stock.news or []
                for item in news[:limit]:
                    content = item.get("content", {}) if isinstance(item.get("content"), dict) else {}
                    # Support both old and new yfinance news schema
                    title = (
                        content.get("title") or
                        item.get("title") or
                        ""
                    )
                    publisher = (
                        content.get("provider", {}).get("displayName") or
                        item.get("publisher") or
                        "Yahoo Finance"
                    )
                    link = (
                        content.get("canonicalUrl", {}).get("url") or
                        item.get("link") or
                        ""
                    )
                    pub_time = (
                        content.get("pubDate") or
                        item.get("providerPublishTime") or
                        ""
                    )
                    if isinstance(pub_time, (int, float)):
                        pub_time = _fmt_timestamp(pub_time)

                    if title:
                        results.append({
                            "headline": title,
                            "source": publisher,
                            "url": link,
                            "published_at": pub_time,
                            "summary": content.get("summary", "")[:200] if content.get("summary") else "",
                        })
                if results:
                    break  # got news from first working suffix
            except Exception:
                continue
        return results

    def _fetch_rss_filtered(self, ticker: str, company_name: str = "", limit: int = 10) -> list[dict]:
        """Search RSS feeds for articles mentioning the ticker or company."""
        clean = ticker.upper().replace(".NS", "").replace(".BO", "")
        search_terms = [clean]
        if company_name:
            words = [w for w in company_name.split() if len(w) > 3]
            search_terms.extend(words[:3])

        articles = []
        for source_name, feed_url in RSS_FEEDS.items():
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:100]:
                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    combined = (title + " " + summary).upper()
                    if any(t.upper() in combined for t in search_terms):
                        published_at = getattr(entry, "published", "") or getattr(entry, "updated", "")
                        articles.append({
                            "headline": title,
                            "source": source_name,
                            "url": entry.get("link", ""),
                            "published_at": published_at,
                            "summary": summary[:200] if summary else "",
                        })
                        if len(articles) >= limit:
                            return articles
            except Exception:
                continue
        return articles

    def _fetch_rss_general(self, limit: int = 10) -> list[dict]:
        """Fallback: return general Indian market news from RSS."""
        articles = []
        for source_name, feed_url in RSS_FEEDS.items():
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:
                    title = entry.get("title", "")
                    if title:
                        articles.append({
                            "headline": title,
                            "source": source_name,
                            "url": entry.get("link", ""),
                            "published_at": getattr(entry, "published", ""),
                            "summary": "",
                        })
            except Exception:
                continue
            if len(articles) >= limit:
                break
        return articles[:limit]

    def fetch_general_market_news(self, limit: int = 10) -> list[dict]:
        return self._fetch_rss_general(limit)
