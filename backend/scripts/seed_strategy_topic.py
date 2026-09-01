from app.core.database import SessionLocal
from app.models import IntelligenceTopic
from sqlalchemy.orm import Session
import uuid

def seed_strategy_topic(db: Session):
    code = "STRATEGY_MP"
    existing = db.query(IntelligenceTopic).filter(IntelligenceTopic.code == code).first()
    
    vocabulary = {
        "strategic_direction": [
            "growth", "expansion", "strategy", "strategic", "investment", "transformation", 
            "leadership", "market growth", "growth strategy", "business strategy", 
            "strategic priorities", "restructuring", "transformation programmes", 
            "strategic initiatives", "long-term business direction", "strategic objectives"
        ],
        "market_positioning": [
            "positioning", "proposition", "value proposition", "differentiation", 
            "competitive advantage", "market position", "market leadership", 
            "customer value", "premium service", "competitive positioning", 
            "market leadership claims", "premium/low-cost positioning", 
            "service differentiation", "network positioning"
        ],
        "commercial": [
            "pricing", "pricing strategy", "tariff", "rates", "service launch", 
            "customer segment", "B2B", "B2C", "e-commerce", "home delivery", 
            "commercial model changes", "new commercial propositions", 
            "customer acquisition strategy", "revenue-growth initiatives", 
            "sector targeting", "contract strategy"
        ],
        "customer_segments": [
            "target industries", "target customer segments", "B2B/B2C strategy", 
            "e-commerce focus", "SME/enterprise focus", "vertical expansion"
        ],
        "services": [
            "new service propositions", "service repositioning", "delivery proposition changes", 
            "premium service offerings", "customer experience strategy"
        ],
        "technology": [
            "digital", "digital transformation", "technology", "API", "platform", 
            "portal", "automation", "AI", "artificial intelligence", "visibility", 
            "tracking", "EPOD", "automation strategy", "platform strategy", 
            "AI adoption", "API strategy", "visibility strategy", "technology partnerships"
        ],
        "geography": [
            "Europe", "European", "international", "cross-border", "Ireland", 
            "export", "new market", "market entry", "regional growth", 
            "geographic growth strategy", "regional prioritisation", 
            "UK expansion strategy", "European strategy", "internationalisation"
        ],
        "partnerships": [
            "partnership", "strategic partnership", "alliance", "collaboration", 
            "technology partner", "logistics partner", "European partner", 
            "strategic partnerships", "ecosystem strategy", "alliance strategy", 
            "network partnerships"
        ],
        "competitive_positioning": [
            "competitor differentiation", "market leadership positioning", 
            "response to competitor activity", "strategic positioning against rival networks"
        ],
        "operations": [
            "operating model changes", "efficiency strategy", "capacity strategy", 
            "service model optimisation", "operational transformation"
        ]
    }

    if existing:
        print(f"Topic {code} already exists, updating vocabulary...")
        existing.topic_vocabulary = vocabulary
        existing.name = "Strategy & Market Positioning"
        existing.description = "Independent layer for capturing strategic, commercial, geographic, and market positioning intelligence directly from source websites."
    else:
        print(f"Creating new topic {code}...")
        topic = IntelligenceTopic(
            code=code,
            name="Strategy & Market Positioning",
            description="Independent layer for capturing strategic, commercial, geographic, and market positioning intelligence directly from source websites.",
            topic_vocabulary=vocabulary,
            status="active"
        )
        db.add(topic)
        
    db.commit()
    print("Seed complete.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_strategy_topic(db)
    finally:
        db.close()
