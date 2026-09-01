import uuid
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import Source, Competitor, IntelligenceTopic, Market

def register_sources(db: Session):
    topic = db.query(IntelligenceTopic).filter(IntelligenceTopic.code == "NETWORK_GEOGRAPHIC_EXPANSION").first()
    market = db.query(Market).filter(Market.country_code == "GB").first()
    
    if not topic or not market:
        print("Required seed data (Topic or Market) missing. Run seed.py first.")
        return

    # Define verified URLs
    sources_data = [
        {
            "comp_name": "Palletforce",
            "url": "https://www.palletforce.com",
            "name": "Palletforce"
        },
        {
            "comp_name": "Pall-Ex",
            "url": "https://pallexlogistics.co.uk",
            "name": "Pall-Ex"
        },
        {
            "comp_name": "Palletline",
            "url": "https://www.palletline.co.uk",
            "name": "Palletline"
        },
        {
            "comp_name": "Fortec Distribution",
            "url": "https://www.fortec-distribution.com",
            "name": "Fortec Distribution"
        }
    ]

    for data in sources_data:
        comp = db.query(Competitor).filter(Competitor.canonical_name == data["comp_name"]).first()
        if not comp:
            print(f"Competitor {data['comp_name']} not found. Skipping.")
            continue
            
        existing_source = db.query(Source).filter(Source.url == data["url"], Source.competitor_id == comp.id).first()
        if not existing_source:
            source = Source(
                competitor_id=comp.id,
                market_id=market.id,
                topic_id=topic.id,
                source_type="Website",
                name=data["name"],
                url=data["url"],
                domain=data["url"].split("/")[2],
                collection_method="HTTP",
                collection_enabled=True,
                priority=1
            )
            db.add(source)
            print(f"Registered source: {data['name']}")
        else:
            print(f"Source already registered: {data['name']}")
            
    db.commit()

if __name__ == "__main__":
    db = SessionLocal()
    try:
        register_sources(db)
    finally:
        db.close()
