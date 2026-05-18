# Stocks AI — AI-Powered Indian Stock Market Intelligence Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-24+-2496ED?style=for-the-badge&logo=docker)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql)
![AI Powered](https://img.shields.io/badge/AI-Powered-success?style=for-the-badge)

### Institutional-Grade AI Stock Intelligence for the Indian Equity Market

*A Full-Stack, Multi-Agent, AI-Powered Stock Market Intelligence Platform for NSE & BSE Equities*

</div>

---

## Executive Summary

**Stocks AI** is a full-stack, AI-powered stock market intelligence platform designed exclusively for the **Indian Equity Market**, covering both the **National Stock Exchange (NSE)** and the **Bombay Stock Exchange (BSE)**.

The platform addresses a major challenge faced by Indian retail investors: the lack of access to **institutional-grade stock analysis tools** that combine **fundamental analysis, technical indicators, and market sentiment** into a single decision-making framework.

Unlike conventional stock platforms that provide fragmented analytics, **Stocks AI integrates three independent analytical dimensions** into a unified AI-driven investment intelligence system:

- Fundamental Analysis
- Technical Analysis
- News Sentiment Intelligence

These analytical engines are orchestrated using a **multi-agent AI architecture** powered by **FastAPI**, **React**, **Claude AI**, and **FinBERT**, enabling explainable and actionable stock intelligence.

---

## Problem Statement

Indian retail investors face three major barriers:

### 1. Information Asymmetry

Institutional investors use premium research tools, Bloomberg terminals, proprietary market intelligence, and expert analysts, while retail investors rely on fragmented online resources.

### 2. Analytical Fragmentation

Existing platforms focus on only one dimension:

| Platform | Capability |
|----------|------------|
| Screener | Fundamental Analysis |
| TradingView | Technical Analysis |
| Moneycontrol | Financial News |

No single platform combines **fundamental + technical + sentiment intelligence** into a unified AI verdict.

### 3. Lack of India-Specific Context

Global financial tools fail to understand:

- Promoter pledging
- FII/DII behavior
- SEBI regulations
- Budget impact
- Monsoon sensitivity
- RBI policy influence
- Nifty/Sensex inclusion effects

---

# Key Innovations

## 1. Alpha Score (0–100)

A proprietary **Composite AI Investment Score**.

```text
Alpha Score =
(Fundamental × 40%)
+ (Technical × 35%)
+ (Sentiment × 25%)
+ India-Specific Adjustments
```

### Score Interpretation

| Score | Interpretation |
|--------|---------------|
| 80–100 | Strong Alpha |
| 60–79 | Positive Carry |
| 40–59 | Neutral Bias |
| 20–39 | High Beta Risk |
| 0–19 | Capital At Risk |

### India Context Adjustments

Stocks AI incorporates:

- Promoter pledging analysis
- SEBI risk alerts
- FII activity
- Debt restructuring
- Nifty/Sensex blue-chip status

---

## 2. Sentiment Momentum Divergence (SMD)

**A Novel Financial Signal Proposed in This Project**

SMD applies **EMA crossover logic to sentiment data**.

```text
SMD = EMA(3) - EMA(14)
```

### Signal Logic

| Condition | Signal |
|-----------|--------|
| Above Zero | Bullish |
| Below Zero | Bearish |
| Upward Cross | Bullish Crossover |
| Downward Cross | Bearish Crossover |

This enables **early detection of narrative shifts before price movement occurs**.

---

## 3. Artha — AI Financial Assistant

**Artha** is an AI-powered conversational financial assistant built using **Claude AI**.

### Capabilities

- Market overview
- Stock insights
- Sector performance
- Top gainers & losers
- News intelligence
- Natural language stock queries

### Example Queries

```text
"Should I invest in Reliance now?"
"Show Nifty sector performance"
"What is the market sentiment on Infosys?"
```

---

# System Architecture

```text
                 ┌────────────────────┐
                 │    React Frontend  │
                 │     (UI Layer)     │
                 └─────────┬──────────┘
                           │
                    REST API Calls
                           │
                 ┌─────────▼─────────┐
                 │   FastAPI Backend │
                 │   API Gateway     │
                 └─────────┬─────────┘
                           │
       ┌───────────────────┼────────────────────┐
       │                   │                    │
       ▼                   ▼                    ▼

┌─────────────┐   ┌──────────────┐   ┌──────────────┐
│ Fundamental │   │ Technical AI │   │ Sentiment AI │
│   Agent     │   │    Agent     │   │  (FinBERT)   │
└─────────────┘   └──────────────┘   └──────────────┘
       │                   │                    │
       └───────────────────┼────────────────────┘
                           │
                           ▼
                 ┌────────────────┐
                 │ Alpha Score AI │
                 └────────────────┘
                           │
                           ▼
                   Unified Stock Verdict
```

---

# Core Features

## Fundamental Analysis

### Evaluates

- P/E Ratio
- P/B Ratio
- ROE
- Debt-to-Equity Ratio
- Revenue Growth
- Profit Margin
- EPS Growth
- Dividend Yield

### AI Verdict Types

- Strong
- Moderate
- Weak

---

## Technical Analysis

Computes **10+ Indicators**

| Indicator | Purpose |
|-----------|---------|
| RSI | Momentum |
| MACD | Trend Detection |
| Bollinger Bands | Volatility |
| EMA | Trend |
| SMA | Long-Term Trend |
| ADX | Trend Strength |
| Supertrend | Buy/Sell Signals |
| Volume Trend | Confirmation |
| Support & Resistance | Risk Zones |

---

## News Sentiment Analysis

Powered by **FinBERT**

### Sources

- Economic Times
- Moneycontrol
- Business Standard
- Livemint
- Yahoo Finance

### Sentiment Categories

```text
Positive
Neutral
Negative
```

Confidence-weighted scoring converts sentiment into a **0–100 intelligence score**.

---

# Technology Stack

## Frontend

```text
React 18
Tailwind CSS
Framer Motion
Recharts
Zustand
TanStack Query
Vite
```

## Backend

```text
Python 3.11+
FastAPI
Pydantic
SQLAlchemy
```

## AI Stack

```text
Claude AI
Anthropic API
FinBERT
Transformers
HuggingFace
```

## Data Layer

```text
Yahoo Finance (yfinance)
RSS Feeds
NumPy
Pandas
```

## Database

```text
SQLite (Development)
PostgreSQL (Production)
```

## Deployment

```text
Docker
Docker Compose
```

---

# Project Structure

```bash
Stocks-AI/
│
├── backend/
│   ├── agents/
│   │   ├── fundamental_agent.py
│   │   ├── technical_agent.py
│   │   ├── news_sentiment_agent.py
│   │   ├── sentiment_momentum_agent.py
│   │   ├── alpha_score_agent.py
│   │   └── chatbot_agent.py
│   │
│   ├── routes/
│   ├── utils/
│   ├── models/
│   ├── database/
│   └── main.py
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   └── assets/
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# API Endpoints

## Analysis APIs

```http
POST /api/analysis/fundamental
POST /api/analysis/technical
POST /api/analysis/sentiment
POST /api/analysis/full
GET  /api/analysis/smd/{ticker}
```

## Market APIs

```http
GET /api/market/indices
GET /api/market/gainers
GET /api/market/losers
GET /api/market/sectors
```

## Chat APIs

```http
POST /api/chat/message
GET  /api/chat/history/{session_id}
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/stocks-ai.git

cd stocks-ai
```

## Backend Setup

```bash
cd backend

pip install -r requirements.txt
```

Create `.env`

```env
ANTHROPIC_API_KEY=your_key
DATABASE_URL=sqlite:///stocks.db
```

Run Server

```bash
uvicorn main:app --reload
```

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

# Docker Deployment

```bash
docker-compose up --build
```

---

# Research Contributions

## Alpha Score

A proprietary investment intelligence score combining:

- Fundamental Analysis
- Technical Analysis
- Market Sentiment

## Sentiment Momentum Divergence (SMD)

A novel indicator applying:

```text
EMA crossover logic
to financial sentiment
```

for predictive market intelligence.

---

# Performance Highlights

### Institutional Multi-Dimensional Analysis

✔ Fundamental Intelligence  
✔ Technical Intelligence  
✔ Sentiment Intelligence  
✔ AI Explanations  
✔ Conversational Financial Assistant  
✔ India-Specific Adjustments

---

# Future Scope

- Portfolio management
- AI trade simulation
- Real-time alerts
- Mobile application
- Multi-language support
- Options & derivatives analytics
- Personalized investment recommendations

---

# Contributors

### Project Team

**Esakki Raj**  
**Nithin Ganesh P K**  
**Sangeeth Darsan S**  
**Sanjai Thilak V S**

**Department of Artificial Intelligence & Data Science**  
**Amrita College of Engineering and Technology**  
**Anna University**

---

# Research Impact

This project demonstrates the practical integration of:

- Artificial Intelligence
- Financial Intelligence
- Sentiment Analysis
- Large Language Models
- Explainable AI
- Multi-Agent Systems

for **institutional-grade stock intelligence accessible to retail investors**.

---

# Disclaimer

> Stocks AI is designed for **educational and research purposes only**.  
> This platform **does not constitute financial or investment advice** and is **not SEBI-registered investment advisory software**.

---

<div align="center">

### ⭐ If you found this project valuable, consider starring the repository.

**Stocks AI — AI-Powered Indian Stock Market Intelligence Platform**

</div>