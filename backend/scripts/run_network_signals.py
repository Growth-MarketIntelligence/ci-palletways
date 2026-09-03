from app.core.database import SessionLocal
from app.models import Competitor, Source, IntelligenceTopic
from app.services.signal_generator import generate_network_signals

def run_signals_only():
    db = SessionLocal()
    try:
        topic = db.query(IntelligenceTopic).filter_by(code="NETWORK_GEOGRAPHIC_EXPANSION").first()
        sources = db.query(Source).filter_by(topic_id=topic.id).all() if topic else []
        
        print("Network Signal Generation Run\n-----------------------------")
        
        # Keep track of competitors to avoid running multiple times per competitor
        processed_competitors = set()
        
        for source in sources:
            competitor_id = str(source.competitor_id)
            if competitor_id in processed_competitors:
                continue
                
            processed_competitors.add(competitor_id)
            print(f"\nGenerating signals for: {source.name}")
            
            signal = generate_network_signals(db, competitor_id)
            if signal:
                print(f"Created Signal: {signal.title}")
                print(f"Description: {signal.description}")
            else:
                print("No new signals generated.")
                
        print("\n-----------------------------")
        print("Signal generation complete.")
    finally:
        db.close()

if __name__ == "__main__":
    run_signals_only()
