from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import analysis, chat, market, dhandho
from db.database import create_tables

create_tables()

app = FastAPI(
    title="BharatStocks AI",
    description="AI-Powered Indian Stock Market Intelligence Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(market.router, prefix="/api/market", tags=["Market"])
app.include_router(dhandho.router, prefix="/api/dhandho", tags=["Dhandho"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "BharatStocks AI"}


@app.get("/")
async def root():
    return {"message": "BharatStocks AI API", "docs": "/docs"}
