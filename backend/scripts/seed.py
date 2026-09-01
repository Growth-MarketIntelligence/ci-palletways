import asyncio
import uuid
import sys
import os

# Add parent directory to sys.path to resolve 'app' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.models import Market, Competitor, IntelligenceTopic

def seed_data(db: Session):
    # Ensure tables are created (just in case, though alembic should be used)
    # Base.metadata.create_all(bind=engine)
    
    # 1. Market
    market_uk = db.query(Market).filter(Market.country_code == 'GB').first()
    if not market_uk:
        market_uk = Market(name="United Kingdom", country_code="GB")
        db.add(market_uk)
        db.commit()
        db.refresh(market_uk)
    
    # 2. Competitors
    competitors_data = [
        {"name": "Palletforce", "canonical_name": "Palletforce"},
        {"name": "Pall-Ex", "canonical_name": "Pall-Ex"},
        {"name": "Palletline", "canonical_name": "Palletline"},
        {"name": "Fortec Distribution", "canonical_name": "Fortec Distribution"}
    ]
    
    for comp_data in competitors_data:
        comp = db.query(Competitor).filter(Competitor.canonical_name == comp_data["canonical_name"]).first()
        if not comp:
            comp = Competitor(**comp_data)
            db.add(comp)
    db.commit()

    # 3. Intelligence Topics
    topics_data = [
        {"code": "STRATEGY_MARKET_POSITIONING", "name": "Strategy & Market Positioning"},
        {
            "code": "NETWORK_GEOGRAPHIC_EXPANSION", 
            "name": "Network & Geographic Expansion",
            "topic_vocabulary": {
                "core": ["network", "depot", "hub", "branch", "location", "coverage"],
                "expansion": ["expand", "expansion", "grow", "growth", "strengthen", "increase", "extend", "new"],
                "membership": ["join", "joins", "joined", "member", "membership", "partner", "appointed"],
                "geographic": ["postcode", "region", "territory", "area"]
            }
        },
        {"code": "PRICING_COMMERCIAL", "name": "Pricing & Commercial Moves"},
        {"code": "SERVICES_CUSTOMER_PROPOSITION", "name": "Services & Customer Proposition"},
        {"code": "CUSTOMERS_VERTICALS_MARKET_WINS", "name": "Customers, Verticals & Market Wins"},
        {"code": "TECHNOLOGY_AUTOMATION", "name": "Technology & Automation"},
        {"code": "M_AND_A_PARTNERSHIPS_NETWORK_ALLIANCES", "name": "M&A, Partnerships & Network Alliances"},
        {"code": "FINANCIALS_INVESTMENT_CAPACITY", "name": "Financials, Revenue, Investment & Capacity"},
        {"code": "LEADERSHIP_TALENT_ORGANISATION", "name": "Leadership, Talent & Organisation"},
        {"code": "MARKET_REGULATORY_ESG_REPUTATION", "name": "Market, Regulatory, ESG & Reputation"}
    ]

    for topic_data in topics_data:
        topic = db.query(IntelligenceTopic).filter(IntelligenceTopic.code == topic_data["code"]).first()
        if not topic:
            topic = IntelligenceTopic(**topic_data)
            db.add(topic)
        else:
            if "topic_vocabulary" in topic_data:
                topic.topic_vocabulary = topic_data["topic_vocabulary"]
            db.add(topic)
    db.commit()

    print("Seed complete.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
