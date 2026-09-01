from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import List

from app.core.database import get_db
from app.models import Market, Competitor, IntelligenceTopic
from app.core.config import settings
from app.api import network, strategy

app = FastAPI(title="Palletways CI Prototype", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(network.router, prefix="/network", tags=["Network Insights"])
app.include_router(strategy.router, prefix="/strategy", tags=["Strategy Insights"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/markets")
def get_markets(db: Session = Depends(get_db)):
    markets = db.query(Market).all()
    return [{"id": m.id, "name": m.name, "country_code": m.country_code} for m in markets]

@app.get("/competitors")
def get_competitors(db: Session = Depends(get_db)):
    competitors = db.query(Competitor).all()
    return [{"id": c.id, "name": c.name, "canonical_name": c.canonical_name} for c in competitors]

@app.get("/intelligence-topics")
def get_intelligence_topics(db: Session = Depends(get_db)):
    topics = db.query(IntelligenceTopic).all()
    return [{"id": t.id, "code": t.code, "name": t.name} for t in topics]
