import os
import json
import anthropic
from data_sources.nse_fetcher import NSEFetcher
from data_sources.yfinance_india import YFinanceIndia
from data_sources.news_fetcher import NewsFetcher

SYSTEM_PROMPT = """You are "Artha", an expert AI financial advisor specializing exclusively in the Indian stock market (NSE and BSE).

CRITICAL FORMATTING RULES — follow these exactly:
1. Write in plain text only. No markdown. No asterisks, no hashes, no dashes for bullets, no pipes for tables, no bold, no italic, no headers.
2. Use short plain paragraphs separated by a blank line.
3. When you have a list of stocks (top gainers, top losers, or any stock list from tool results), output it ONLY as a special block in this exact format and nothing else for the list:
   STOCKS_DATA::[{"ticker":"X","company":"Y","price":0.0,"change":0.0,"change_percent":0.0}]::END_STOCKS_DATA
   Replace the JSON array with the actual data from the tool. Do not wrap it in markdown. Do not add any other symbols around it.
4. After the STOCKS_DATA block you may add a brief plain-text comment (1-2 sentences, no markdown).
5. For disclaimers write them as a plain sentence at the end.

Your personality:
- Knowledgeable, concise, and helpful
- Speak in simple English, occasionally use Hindi financial terms like Dhandho, Bazaar, Nivesh
- Never give guaranteed return promises (SEBI compliance)
- Keep answers short and factual

You have access to real-time tools to fetch live market data.
Always ground your answers in fresh data. If data is unavailable, say so clearly.
Never hallucinate stock prices or financial data."""

TOOLS = [
    {
        "name": "get_top_gainers",
        "description": "Fetch top gaining stocks on NSE or BSE for today",
        "input_schema": {
            "type": "object",
            "properties": {
                "exchange": {"type": "string", "enum": ["NSE", "BSE"], "description": "Stock exchange"},
                "limit": {"type": "integer", "description": "Number of stocks to return", "default": 10}
            },
            "required": ["exchange"]
        }
    },
    {
        "name": "get_top_losers",
        "description": "Fetch top losing stocks on NSE or BSE for today",
        "input_schema": {
            "type": "object",
            "properties": {
                "exchange": {"type": "string", "enum": ["NSE", "BSE"]},
                "limit": {"type": "integer", "default": 10}
            },
            "required": ["exchange"]
        }
    },
    {
        "name": "get_market_overview",
        "description": "Get current levels of NIFTY 50, SENSEX, BANK NIFTY, INDIA VIX",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_stock_info",
        "description": "Get current price and basic info for an Indian stock",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "NSE symbol e.g. RELIANCE, INFY, TCS"},
                "exchange": {"type": "string", "enum": ["NSE", "BSE"], "default": "NSE"}
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_news",
        "description": "Fetch latest news articles for a given Indian stock",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "limit": {"type": "integer", "default": 5}
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_sector_performance",
        "description": "Get today's performance data for Indian market sectors like IT, Banking, Pharma",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector": {"type": "string", "description": "e.g. IT, Banking, Pharma, Auto, FMCG"}
            },
            "required": ["sector"]
        }
    },
]

SECTOR_INDICES = {
    "IT": "^CNXIT",
    "BANK": "^NSEBANK",
    "BANKING": "^NSEBANK",
    "PHARMA": "^CNXPHARMA",
    "AUTO": "^CNXAUTO",
    "FMCG": "^CNXFMCG",
    "METAL": "^CNXMETAL",
    "ENERGY": "^CNXENERGY",
    "REALTY": "^CNXREALTY",
    "INFRA": "^CNXINFRA",
}


class ChatbotAgent:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None
        self.nse = NSEFetcher()
        self.yf = YFinanceIndia()
        self.news = NewsFetcher()

    def chat(self, message: str, history: list[dict] = []) -> dict:
        if not self.client:
            return {
                "response": "I'm sorry, the AI service is not configured. Please set ANTHROPIC_API_KEY.",
                "session_id": "",
                "tool_calls_made": [],
            }

        messages = list(history) + [{"role": "user", "content": message}]
        tool_calls_made = []

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )

            # Handle tool use loop
            while response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        tool_calls_made.append(tool_name)
                        result = self._execute_tool(tool_name, tool_input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, default=str),
                        })

                messages = messages + [
                    {"role": "assistant", "content": response.content},
                    {"role": "user", "content": tool_results},
                ]
                response = self.client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=2048,
                    system=SYSTEM_PROMPT,
                    tools=TOOLS,
                    messages=messages,
                )

            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text

            return {
                "response": final_text,
                "tool_calls_made": tool_calls_made,
            }

        except Exception as e:
            return {
                "response": f"I encountered an error: {str(e)}. Please try again.",
                "tool_calls_made": tool_calls_made,
            }

    def _execute_tool(self, name: str, inputs: dict) -> dict:
        try:
            if name == "get_top_gainers":
                return {"gainers": self.nse.get_top_gainers(inputs.get("exchange", "NSE"), inputs.get("limit", 10))}
            elif name == "get_top_losers":
                return {"losers": self.nse.get_top_losers(inputs.get("exchange", "NSE"), inputs.get("limit", 10))}
            elif name == "get_market_overview":
                return self.nse.get_market_overview()
            elif name == "get_stock_info":
                return self.yf.get_stock_info(inputs["ticker"], inputs.get("exchange", "NSE"))
            elif name == "get_news":
                articles = self.news.fetch_news(inputs["ticker"], limit=inputs.get("limit", 5))
                return {"articles": articles}
            elif name == "get_sector_performance":
                sector = inputs.get("sector", "").upper()
                symbol = SECTOR_INDICES.get(sector, "^NSEI")
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                if len(hist) >= 2:
                    price = float(hist["Close"].iloc[-1])
                    prev = float(hist["Close"].iloc[-2])
                    change_pct = round((price - prev) / prev * 100, 2)
                    return {"sector": sector, "price": round(price, 2), "change_percent": change_pct}
                return {"sector": sector, "error": "Data unavailable"}
        except Exception as e:
            return {"error": str(e)}
        return {}
