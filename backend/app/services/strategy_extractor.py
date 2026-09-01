import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import uuid

from app.models import Document, Evidence, Event, Competitor
from app.services.ai_provider import get_ai_provider
from app.services.ai_provider.base import PROMPT_VERSION

logger = logging.getLogger(__name__)

ALLOWED_STRATEGY_TYPES = {
    "STRATEGIC_DIRECTION",
    "MARKET_POSITIONING",
    "COMMERCIAL_STRATEGY",
    "CUSTOMER_SEGMENT_STRATEGY",
    "SERVICE_PROPOSITION",
    "TECHNOLOGY_STRATEGY",
    "GEOGRAPHIC_STRATEGY",
    "PARTNERSHIP_STRATEGY",
    "COMPETITIVE_POSITIONING",
    "OPERATIONAL_STRATEGY"
}

def extract_strategy_events(db: Session, document_id: str, strategy_topic_id: uuid.UUID, ai_context: Optional[str] = None) -> List[Event]:
    """
    Creates Evidence from a Document and runs AI extraction to generate Strategy Events.
    If ai_context is provided (e.g., diff text), it uses that instead of the full document.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc or not doc.text_content:
        return []
        
    comp = db.query(Competitor).filter(Competitor.id == doc.source.competitor_id).first()
    
    if not comp:
        logger.error(f"Extraction failed: Document {document_id} has a missing Competitor.")
        return []

    # Heuristic Pre-Filtering
    content_to_analyze = ai_context if ai_context else doc.text_content
    content_to_analyze_lower = content_to_analyze.lower()
    
    strategic_keywords = [
        "strategy", "strategic", "growth", "positioning", "competitor", 
        "advantage", "proposition", "investment", "transformation", "leadership", 
        "partner", "expansion", "commercial", "digital", "technology", "europe", 
        "acquisition", "revenue", "b2b", "b2c", "e-commerce"
    ]
    if not any(keyword in content_to_analyze_lower for keyword in strategic_keywords):
        logger.info(f"Skipping Document {document_id}: No strategic keywords found (Heuristic Pre-Filter).")
        return []

    # Aggressive Truncation for Rate Limits
    content_to_analyze = content_to_analyze[:3500]

    try:
        provider = get_ai_provider()
    except Exception as e:
        logger.error(f"Provider configuration error: {e}")
        return []

    raw_events = provider.extract_strategy_events(content_to_analyze, comp.canonical_name)
    model_used = provider.model_name
        
    created_events = []
    
    for e_data in raw_events:
        event_type = e_data.get("event_type")
        if event_type not in ALLOWED_STRATEGY_TYPES:
            logger.warning(f"Rejecting unsupported strategy event type: {event_type}")
            continue
            
        evidence_excerpt = e_data.get("evidence_excerpt")
        if not evidence_excerpt or evidence_excerpt == "null" or evidence_excerpt == "":
            logger.warning(f"Rejecting event missing evidence_excerpt: {event_type}")
            continue
            
        # Create Evidence first
        evidence = Evidence(
            document_id=doc.id,
            claim=e_data.get("description", "Extracted automatically"),
            text_excerpt=evidence_excerpt,
            location_reference=e_data.get("location")
        )
        db.add(evidence)
        db.flush() # get ID
        
        # Parse event date if provided
        event_date_val = None
        if e_data.get("event_date"):
            try:
                dt = datetime.strptime(e_data["event_date"], "%Y-%m-%d")
                event_date_val = dt.date()
            except ValueError:
                pass
                
        # Create Event grounded in Evidence
        event = Event(
            evidence_id=evidence.id,
            competitor_id=comp.id,
            topic_id=strategy_topic_id,
            event_type=event_type,
            event_subtype=e_data.get("event_subtype"),
            signal_type=e_data.get("signal_type"),
            title=f"{e_data.get('event_subtype', event_type)} - {e_data.get('location', 'Global/General')}",
            description=e_data.get("description", ""),
            event_metadata=e_data.get("metadata"),
            event_date=event_date_val,
            location=e_data.get("location"),
            confidence=e_data.get("confidence_score", 0.5),
            extraction_model=model_used,
            extraction_prompt_version=PROMPT_VERSION
        )
        db.add(event)
        created_events.append(event)
        
    db.commit()
    for ev in created_events:
        db.refresh(ev)
        
    return created_events
