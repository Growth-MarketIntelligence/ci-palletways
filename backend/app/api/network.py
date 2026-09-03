from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.models import Event, Evidence, Document, Competitor, Signal, SignalEvent, CollectionRun

router = APIRouter()

@router.get("/status")
def get_network_status(db: Session = Depends(get_db)):
    """
    Returns the collection status so the UI can distinguish between
    'pipeline has not run' and 'pipeline ran but found 0 events'.
    """
    from sqlalchemy import func
    
    total_runs = db.query(CollectionRun).count()
    failed_runs = db.query(CollectionRun).filter(CollectionRun.status == "FAILED").count()
    total_docs = db.query(Document).count()
    
    stats = db.query(
        func.sum(CollectionRun.items_found).label("found"),
        func.sum(CollectionRun.items_new).label("new"),
        func.sum(CollectionRun.items_updated).label("updated"),
        func.sum(CollectionRun.items_duplicate).label("duplicate"),
        func.sum(CollectionRun.items_failed).label("failed")
    ).first()
    
    return {
        "total_collection_runs": total_runs,
        "failed_collection_runs": failed_runs,
        "total_documents": total_docs,
        "urls_discovered": stats.found if stats and stats.found else 0,
        "new_documents": stats.new if stats and stats.new else 0,
        "changed_documents": stats.updated if stats and stats.updated else 0,
        "unchanged_documents": stats.duplicate if stats and stats.duplicate else 0,
        "failed_urls": stats.failed if stats and stats.failed else 0,
        "has_run": total_runs > 0
    }

@router.get("/events")
def get_network_events(
    competitor_id: Optional[str] = None,
    event_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Event, Evidence, Document, Competitor).join(
        Evidence, Event.evidence_id == Evidence.id
    ).join(
        Document, Evidence.document_id == Document.id
    ).join(
        Competitor, Event.competitor_id == Competitor.id
    ).filter(
        Event.topic.has(code="NETWORK_GEOGRAPHIC_EXPANSION")
    )
    
    if competitor_id:
        query = query.filter(Event.competitor_id == competitor_id)
        
    if event_type:
        query = query.filter(Event.event_type == event_type)
        
    # Coalesce the dates for filtering
    effective_date = func.coalesce(
        cast(Event.event_date, Date),
        cast(Document.source_updated_at, Date),
        cast(Document.source_published_at, Date),
        cast(Document.collected_at, Date)
    )
    
    if start_date:
        query = query.filter(effective_date >= start_date)
    if end_date:
        query = query.filter(effective_date <= end_date)
        
    query = query.order_by(effective_date.desc())
    
    results = query.all()
    
    response = []
    for evt, evid, doc, comp in results:
        response.append({
            "id": evt.id,
            "competitor_name": comp.canonical_name,
            "event_type": evt.event_type,
            "description": evt.description,
            "location": evt.location,
            "event_date": evt.event_date,
            "evidence_excerpt": evid.text_excerpt,
            "confidence": evt.confidence,
            "source_url": doc.url,
            "source_published_at": doc.source_published_at,
            "source_updated_at": doc.source_updated_at,
            "collected_at": doc.collected_at
        })
        
    return response

@router.get("/signals")
def get_network_signals(db: Session = Depends(get_db)):
    query = db.query(Signal, Competitor).join(
        Competitor, Signal.competitor_id == Competitor.id
    ).filter(
        Signal.topic.has(code="NETWORK_GEOGRAPHIC_EXPANSION")
    ).order_by(Signal.detected_at.desc())
    
    results = query.all()
    
    response = []
    for sig, comp in results:
        # Get linked events and their source docs
        events_with_docs = db.query(Event, Document).join(
            SignalEvent, Event.id == SignalEvent.event_id
        ).outerjoin(
            Evidence, Event.evidence_id == Evidence.id
        ).outerjoin(
            Document, Evidence.document_id == Document.id
        ).filter(SignalEvent.signal_id == sig.id).all()
        
        citations = []
        for evt, doc in events_with_docs:
            if doc and doc.url and doc.url not in citations:
                citations.append(doc.url)
        
        response.append({
            "id": sig.id,
            "title": sig.title,
            "summary": sig.description,
            "competitor_name": comp.canonical_name,
            "generated_at": sig.detected_at,
            "event_count": len(events_with_docs),
            "citations": citations
        })
        
    return response

@router.get("/summary")
def get_network_summary(
    start_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        Competitor.canonical_name,
        Event.event_type,
        func.count(Event.id).label("count")
    ).join(
        Competitor, Event.competitor_id == Competitor.id
    ).filter(
        Event.topic.has(code="NETWORK_GEOGRAPHIC_EXPANSION")
    )
    
    if start_date:
        query = query.join(
            Evidence, Event.evidence_id == Evidence.id
        ).join(
            Document, Evidence.document_id == Document.id
        )
        effective_date = func.coalesce(
            cast(Event.event_date, Date),
            cast(Document.source_updated_at, Date),
            cast(Document.source_published_at, Date),
            cast(Document.collected_at, Date)
        )
        query = query.filter(effective_date >= start_date)
        
    query = query.group_by(Competitor.canonical_name, Event.event_type)
    
    results = query.all()
    
    summary = {}
    for comp_name, evt_type, count in results:
        if comp_name not in summary:
            summary[comp_name] = {}
        summary[comp_name][evt_type] = count
        
    return summary
