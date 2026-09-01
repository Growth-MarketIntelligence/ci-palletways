import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import Competitor, Event, IntelligenceTopic
from app.services.strategy_engine import synthesize_competitor_strategy

def main():
    db: Session = SessionLocal()
    try:
        print("=== STRATEGY INTELLIGENCE PIPELINE ===")
        competitors = db.query(Competitor).all()
        strategy_topic = db.query(IntelligenceTopic).filter_by(code="STRATEGY_MP").first()
        network_topic = db.query(IntelligenceTopic).filter_by(code="NETWORK_GEOGRAPHIC_EXPANSION").first()
        
        for comp in competitors:
            print(f"\nCompetitor: {comp.canonical_name}")
            
            strat_events = db.query(Event).filter(Event.competitor_id == comp.id, Event.topic_id == strategy_topic.id).count() if strategy_topic else 0
            net_events = db.query(Event).filter(Event.competitor_id == comp.id, Event.topic_id == network_topic.id).count() if network_topic else 0
            
            print(f"Direct Strategy Events: {strat_events}")
            print(f"Network Context Events: {net_events}")
            
            if strat_events == 0 and net_events == 0:
                print("No events available for strategy synthesis.")
                continue
                
            try:
                insights = synthesize_competitor_strategy(db, str(comp.id))
                print("AI synthesis: SUCCESS")
                print(f"Strategy Insights: {len(insights)}\n")
                
                for insight in insights:
                    print(f"{insight.strategy_category}")
                    print(f"  {insight.strategy_theme}")
                    print(f"  Supporting Events: {len(insight.events)}\n")
                    
            except Exception as e:
                print(f"AI synthesis: FAILED - {e}")
                
        print("======================================")
    finally:
        db.close()

if __name__ == "__main__":
    main()
