import json
import logging
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import cast, Date, func

from app.models import Event, Competitor, StrategyInsight, StrategyInsightEvent
from app.services.ai_provider import get_ai_provider

logger = logging.getLogger(__name__)

ALLOWED_STRATEGY_CATEGORIES = {
    "NETWORK_STRATEGY",
    "INFRASTRUCTURE_STRATEGY",
    "COMMERCIAL_STRATEGY",
    "TECHNOLOGY_STRATEGY",
    "GEOGRAPHIC_MARKET_EXPANSION",
    "COMPETITIVE_POSITIONING",
    "OPERATIONAL_POSITIONING"
}

def synthesize_competitor_strategy(db: Session, competitor_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[StrategyInsight]:
    """
    Synthesize strategy insights from Phase 1 Events for a given competitor.
    """
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not comp:
        logger.error(f"Competitor not found: {competitor_id}")
        return []

    # Step 1: Retrieve Events
    from app.models import IntelligenceTopic
    strategy_topic = db.query(IntelligenceTopic).filter_by(code="STRATEGY_MP").first()
    
    query = db.query(Event).filter(Event.competitor_id == competitor_id)
    if strategy_topic:
        query = query.filter(Event.topic_id == strategy_topic.id)
        
    if start_date:
        query = query.filter(cast(Event.event_date, Date) >= start_date)
    if end_date:
        query = query.filter(cast(Event.event_date, Date) <= end_date)
        
    events = query.order_by(Event.event_date.asc().nulls_last()).all()
    
    # We must have Strategy Events to synthesize strategy, or at least some events.
    has_strategy = any(e.topic_id == strategy_topic.id for e in events if strategy_topic)
    if not events:
        logger.info(f"No events available for strategy synthesis for {comp.canonical_name}.")
        return []

    # Step 3: Build Lean Input
    lean_events = []
    for e in events:
        source_type = "DIRECT STRATEGY"
        evt_dict = {
            "id": str(e.id),
            "source_type": source_type,
            "event_type": e.event_type,
            "event_subtype": e.event_subtype,
            "description": e.description,
            "location": e.location
        }
        if e.event_date:
            evt_dict["event_date"] = e.event_date.isoformat()
        if e.event_metadata:
            evt_dict["metadata"] = e.event_metadata
        lean_events.append(evt_dict)

    events_json_str = json.dumps(lean_events)

    # Step 4: Single Batch LLM Call
    try:
        provider = get_ai_provider()
    except Exception as e:
        logger.error(f"Provider configuration error: {e}")
        return []
        
    raw_insights = provider.synthesize_strategy(events_json_str, comp.canonical_name)
    
    created_insights = []
    
    # Validation and Deduplication
    for insight_data in raw_insights:
        cat = insight_data.get("strategy_category")
        if cat not in ALLOWED_STRATEGY_CATEGORIES:
            logger.warning(f"Rejecting insight: invalid category '{cat}'")
            continue
            
        theme = insight_data.get("strategy_theme")
        assessment = insight_data.get("assessment")
        interpretation = insight_data.get("interpretation")
        if not theme or not assessment or not interpretation:
            logger.warning("Rejecting insight: missing required text fields")
            continue
            
        confidence = insight_data.get("confidence")
        if confidence is not None:
            try:
                confidence = float(confidence)
                if not (0.0 <= confidence <= 1.0):
                    confidence = None
            except:
                confidence = None
                
        # Validate event IDs
        supplied_ids = [e["id"] for e in lean_events]
        supporting_ids = insight_data.get("supporting_event_ids", [])
        valid_supporting_ids = [eid for eid in supporting_ids if eid in supplied_ids]
        
        if not valid_supporting_ids:
            logger.warning("Rejecting insight: no valid supporting event IDs provided")
            continue

        # Deduplication
        existing = db.query(StrategyInsight).filter(
            StrategyInsight.competitor_id == competitor_id,
            StrategyInsight.strategy_category == cat,
            StrategyInsight.strategy_theme == theme
        ).first()
        
        if existing:
            # Update dates if needed or skip. Let's just skip to avoid duplicates entirely.
            logger.info(f"Insight '{theme}' already exists. Skipping.")
            continue

        # Step 6: Persist Insight
        insight = StrategyInsight(
            competitor_id=comp.id,
            strategy_category=cat,
            strategy_theme=theme,
            assessment=assessment,
            interpretation=interpretation,
            confidence=confidence,
            period_start=start_date,
            period_end=end_date
        )
        db.add(insight)
        db.flush() # get ID
        
        for eid in valid_supporting_ids:
            mapping = StrategyInsightEvent(
                strategy_insight_id=insight.id,
                event_id=eid
            )
            db.add(mapping)
            
        created_insights.append(insight)

    db.commit()
    for ins in created_insights:
        db.refresh(ins)
        
    return created_insights
