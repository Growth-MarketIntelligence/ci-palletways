from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models import Event, Signal, SignalEvent

def get_utc_now():
    return datetime.now(timezone.utc)

def generate_network_signals(db: Session, competitor_id: str):
    """
    Simple rule-based signal generator.
    If there are 2 or more un-signaled expansion/depot events in the last 30 days,
    generate a signal.
    """
    thirty_days_ago = get_utc_now().date() - timedelta(days=30)
    
    # Get the Network topic
    from app.models import IntelligenceTopic
    network_topic = db.query(IntelligenceTopic).filter_by(code="NETWORK_GEOGRAPHIC_EXPANSION").first()
    if not network_topic:
        return None

    recent_events = db.query(Event).filter(
        Event.competitor_id == competitor_id,
        Event.topic_id == network_topic.id
    ).all()
    
    # Filter for events not already in a signal
    unsignaled = []
    for ev in recent_events:
        has_signal = db.query(SignalEvent).filter(SignalEvent.event_id == ev.id).first()
        if not has_signal:
            unsignaled.append(ev)
            
    # Group by event_type
    grouped_events = {}
    for ev in unsignaled:
        if ev.event_type not in grouped_events:
            grouped_events[ev.event_type] = []
        grouped_events[ev.event_type].append(ev)

    signals_created = []
    from app.services.network_signal_synthesizer import synthesize_signal
    from app.models import Competitor
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    competitor_name = competitor.name if competitor else "Competitor"

    for event_type, events_group in grouped_events.items():
        if len(events_group) >= 1:
            synthesis = synthesize_signal(competitor_name, events_group)
            
            signal = Signal(
                competitor_id=competitor_id,
                topic_id=network_topic.id,
                title=synthesis["title"],
                description=synthesis["description"],
                signal_type="NETWORK_ACTIVITY",
                confidence=0.8,
                detected_at=get_utc_now()
            )
            db.add(signal)
            db.flush()
            
            for ev in events_group:
                se = SignalEvent(signal_id=signal.id, event_id=ev.id)
                db.add(se)
                
            signals_created.append(signal)
            
    if signals_created:
        db.commit()
        return signals_created[0] # Return one of them just to signify success to caller
        
    return None
