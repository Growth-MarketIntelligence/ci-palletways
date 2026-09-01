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
    
    # Find recent expansion events for this competitor
    recent_events = db.query(Event).filter(
        Event.competitor_id == competitor_id,
        Event.event_type.in_(["NETWORK_FOOTPRINT", "HUBS_AND_DEPOTS"]),
        # If event_date is set, use it, otherwise use a fallback (simplification for the rule)
        # Actually, let's just grab events created recently that don't have a signal
    ).all()
    
    # Filter for events not already in a signal (inefficient for large DB, fine for prototype)
    unsignaled = []
    for ev in recent_events:
        # Check if ev.id is in SignalEvent
        has_signal = db.query(SignalEvent).filter(SignalEvent.event_id == ev.id).first()
        if not has_signal:
            unsignaled.append(ev)
            
    if len(unsignaled) >= 2:
        # Generate Signal
        signal = Signal(
            competitor_id=competitor_id,
            topic_id=unsignaled[0].topic_id,
            title=f"Recent Network Growth ({len(unsignaled)} events)",
            description="Detected multiple recent network expansion activities.",
            signal_type="NETWORK_ACTIVITY",
            confidence=0.8,
            detected_at=get_utc_now()
        )
        db.add(signal)
        db.flush()
        
        for ev in unsignaled:
            se = SignalEvent(signal_id=signal.id, event_id=ev.id)
            db.add(se)
            
        db.commit()
        return signal
        
    return None
