from app.core.database import SessionLocal
from app.models import Event, IntelligenceTopic, StrategyInsight

db = SessionLocal()
topic = db.query(IntelligenceTopic).filter_by(code='STRATEGY_MP').first()
print('Strategy Topic:', bool(topic))
if topic:
    print('Strategy Events:', db.query(Event).filter(Event.topic_id==topic.id).count())
print('Strategy Insights:', db.query(StrategyInsight).count())
