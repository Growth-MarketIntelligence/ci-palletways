from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from collections import defaultdict

from app.core.database import get_db
from app.models import StrategyInsight, StrategyInsightEvent, Event, Competitor
from app.services.strategy_engine import synthesize_competitor_strategy

router = APIRouter()

@router.get("/insights")
def get_strategy_insights(
    competitor_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(StrategyInsight, Competitor).join(
        Competitor, StrategyInsight.competitor_id == Competitor.id
    )
    
    if competitor_id:
        query = query.filter(StrategyInsight.competitor_id == competitor_id)
        
    results = query.order_by(StrategyInsight.created_at.desc()).all()
    
    response = []
    for insight, comp in results:
        # Get supporting events with source URLs
        supporting_events = []
        for se in insight.events:
            ev = se.event
            url = None
            source_name = None
            if ev and ev.evidence and ev.evidence.document and ev.evidence.document.source:
                url = ev.evidence.document.source.url
                source_name = ev.evidence.document.source.name
            
            supporting_events.append({
                "id": str(ev.id) if ev else str(se.event_id),
                "url": url,
                "source_name": source_name,
                "description": ev.description if ev else None,
                "event_type": ev.event_type if ev else None,
                "event_subtype": ev.event_subtype if ev else None,
                "location": ev.location if ev else None,
                "event_date": ev.event_date.isoformat() if ev and ev.event_date else None
            })
        
        response.append({
            "id": str(insight.id),
            "competitor_name": comp.canonical_name,
            "competitor_id": str(comp.id),
            "strategy_category": insight.strategy_category,
            "strategy_theme": insight.strategy_theme,
            "assessment": insight.assessment,
            "interpretation": insight.interpretation,
            "confidence": insight.confidence,
            "period_start": insight.period_start,
            "period_end": insight.period_end,
            "supporting_events": supporting_events,
            "created_at": insight.created_at
        })
        
    return response


@router.get("/profile/{competitor_id}")
def get_strategy_profile(competitor_id: str, db: Session = Depends(get_db)):
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
        
    insights = db.query(StrategyInsight).filter(StrategyInsight.competitor_id == competitor_id).all()
    
    grouped_insights = defaultdict(list)
    for insight in insights:
        supporting_events = []
        for se in insight.events:
            ev = se.event
            url = None
            source_name = None
            if ev and ev.evidence and ev.evidence.document and ev.evidence.document.source:
                url = ev.evidence.document.source.url
                source_name = ev.evidence.document.source.name
            
            supporting_events.append({
                "id": str(ev.id) if ev else str(se.event_id),
                "url": url,
                "source_name": source_name,
                "description": ev.description if ev else None,
                "event_type": ev.event_type if ev else None,
                "event_subtype": ev.event_subtype if ev else None,
                "location": ev.location if ev else None,
                "event_date": ev.event_date.isoformat() if ev and ev.event_date else None
            })
            
        grouped_insights[insight.strategy_category].append({
            "id": str(insight.id),
            "strategy_theme": insight.strategy_theme,
            "assessment": insight.assessment,
            "interpretation": insight.interpretation,
            "confidence": insight.confidence,
            "supporting_events": supporting_events,
            "created_at": insight.created_at
        })
        
    return {
        "competitor_id": str(comp.id),
        "competitor_name": comp.canonical_name,
        "strategy_profile": grouped_insights
    }


@router.post("/analyze/{competitor_id}")
def trigger_strategy_analysis(
    competitor_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
        
    insights = synthesize_competitor_strategy(db, competitor_id, start_date, end_date)
    
    return {
        "message": f"Strategy synthesis completed for {comp.canonical_name}",
        "insights_generated": len(insights)
    }
