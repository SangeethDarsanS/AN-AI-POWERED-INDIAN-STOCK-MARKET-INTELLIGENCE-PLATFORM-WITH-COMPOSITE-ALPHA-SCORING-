import json


def build_fundamental_prompt(ticker: str, financial_data: dict) -> str:
    return f"""You are a SEBI-registered equity analyst specializing in Indian markets (NSE/BSE).
Given the following financial data for {ticker}:
{json.dumps(financial_data, indent=2, default=str)}

Analyze and provide a JSON response with exactly this structure:
{{
  "fundamental_score": <integer 0-100>,
  "verdict": "<STRONG|MODERATE|WEAK>",
  "summary": "<2-3 sentence plain-language summary for retail Indian investors mentioning key metrics>",
  "flags": ["<risk flag 1>", "<risk flag 2>"]
}}

Scoring guide (all scores 0-100):
- ROE > 20%: +20 pts; 15-20%: +15 pts; 10-15%: +8 pts
- ROCE > 20%: +10 pts; 12-20%: +6 pts
- Debt/Equity < 0.3: +20 pts; 0.3-0.5: +15 pts; 0.5-1.0: +8 pts; > 3.0: -15 pts
- PE < 15: +15 pts; 15-25: +10 pts; 25-40: +5 pts; > 60: -10 pts
- Revenue growth > 20% YoY: +15 pts; 10-20%: +10 pts; 0-10%: +5 pts; negative: -10 pts
- Net profit margin > 20%: +10 pts; 10-20%: +5 pts
- Gross margin > 50%: strong moat indicator (pharma, software)
- Base score = 40; add/subtract adjustments; clamp to [0, 100]

India-specific context:
- High promoter holding (>50%): generally positive signal
- Pharma/IT sectors: higher PE norms (30-40 PE is normal)
- FMCG: high gross margins (>50%) indicate pricing power
- PSU stocks: may have low PE but political/governance risk

Respond ONLY with valid JSON. No markdown, no extra text."""


def build_technical_prompt(ticker: str, indicators: dict) -> str:
    return f"""You are a technical analyst specializing in NSE/BSE Indian equities.
Given these technical indicators for {ticker}:
{json.dumps(indicators, indent=2, default=str)}

Provide a JSON response with exactly this structure:
{{
  "technical_score": <integer 0-100>,
  "trend": "<BULLISH|BEARISH|NEUTRAL>",
  "macd_signal": "<BULLISH_CROSSOVER|BEARISH_CROSSOVER|BULLISH|BEARISH|NEUTRAL>",
  "summary": "<2-3 sentence technical summary>",
  "chart_patterns": ["<pattern name>"],
  "recommendation": "<BUY|SELL|HOLD|WATCH>"
}}

RSI interpretation: <30 oversold (bullish), >70 overbought (bearish), 40-60 neutral
MACD bullish crossover = bullish signal
Price above 200DMA = long-term bullish
Golden cross (50DMA > 200DMA) = strong bullish

Respond ONLY with valid JSON."""


def build_sentiment_prompt(ticker: str, company_name: str, articles: list) -> str:
    articles_text = json.dumps(articles, indent=2, default=str)
    return f"""You are a financial news analyst for Indian equity markets.
Analyze the following news articles about {ticker} ({company_name}):

{articles_text}

For each article, classify sentiment and provide an overall analysis.
Respond with ONLY this JSON structure:
{{
  "overall_sentiment": "<POSITIVE|NEGATIVE|NEUTRAL>",
  "sentiment_score": <integer 0-100>,
  "positive_count": <int>,
  "negative_count": <int>,
  "neutral_count": <int>,
  "key_themes": ["<theme1>", "<theme2>"],
  "risk_alerts": ["<alert1>"],
  "analyzed_articles": [
    {{
      "headline": "<headline>",
      "source": "<source>",
      "sentiment": "<POSITIVE|NEGATIVE|NEUTRAL>",
      "impact": "<HIGH|MEDIUM|LOW>",
      "reason": "<1 sentence reason from Indian investor perspective>"
    }}
  ]
}}

Focus on material impact on stock price. Ignore irrelevant gossip.
Sentiment score: 70-100 = positive, 40-69 = neutral, 0-39 = negative.
Respond ONLY with valid JSON."""


def build_dhandho_prompt(ticker: str, fundamental: dict, technical: dict, sentiment: dict) -> str:
    base_score = (
        fundamental.get("fundamental_score", 50) * 0.40 +
        technical.get("technical_score", 50) * 0.35 +
        sentiment.get("sentiment_score", 50) * 0.25
    )
    return f"""You are an expert Indian stock market analyst.
Based on this composite analysis for {ticker}:

Fundamental Score: {fundamental.get("fundamental_score", "N/A")}
Technical Score: {technical.get("technical_score", "N/A")}
Sentiment Score: {sentiment.get("sentiment_score", "N/A")}
Base Dhandho Score: {base_score:.1f}

Fundamental Summary: {fundamental.get("summary", "")}
Technical Summary: {technical.get("summary", "")}

Generate a Dhandho Score assessment. Respond with ONLY this JSON:
{{
  "one_liner": "<1 punchy sentence summarizing the investment case for Indian retail investors>",
  "best_for": ["<investor type 1>", "<investor type 2>"],
  "risk_factors": ["<risk 1>", "<risk 2>", "<risk 3>"]
}}

Keep it concise, India-specific, and actionable. Respond ONLY with valid JSON."""
