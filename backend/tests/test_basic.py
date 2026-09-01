import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from app.models import Market, Competitor, CompetitorMarket, IntelligenceTopic, Source, Document, Evidence, Event, Signal, SignalEvent

def get_utc_now():
    return datetime.now(timezone.utc)

def test_create_market_and_competitor(db):
    market = Market(name="United Kingdom", country_code="GB")
    db.add(market)
    
    competitor = Competitor(name="Palletforce", canonical_name="Palletforce")
    db.add(competitor)
    db.commit()
    
    assert market.id is not None
    assert competitor.id is not None

def test_intelligence_topic_code_unique(db):
    topic1 = IntelligenceTopic(code="NETWORK_GEOGRAPHIC_EXPANSION", name="Network")
    db.add(topic1)
    db.commit()
    
    topic2 = IntelligenceTopic(code="NETWORK_GEOGRAPHIC_EXPANSION", name="Another Network")
    db.add(topic2)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()

def test_competitor_market_unique(db):
    market = Market(name="United Kingdom", country_code="GB")
    competitor = Competitor(name="Pall-Ex", canonical_name="Pall-Ex")
    db.add(market)
    db.add(competitor)
    db.commit()
    
    cm1 = CompetitorMarket(competitor_id=competitor.id, market_id=market.id)
    db.add(cm1)
    db.commit()
    
    cm2 = CompetitorMarket(competitor_id=competitor.id, market_id=market.id)
    db.add(cm2)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()

def test_source_document_deduplication(db):
    topic = IntelligenceTopic(code="TEST_TOPIC", name="Test")
    db.add(topic)
    db.commit()

    source = Source(topic_id=topic.id, source_type="Website", name="Test Source")
    db.add(source)
    db.commit()
    
    collected_time = get_utc_now()
    doc1 = Document(source_id=source.id, content_hash="hash123", collected_at=collected_time)
    db.add(doc1)
    db.commit()
    
    doc2 = Document(source_id=source.id, content_hash="hash123", collected_at=collected_time)
    db.add(doc2)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    
    # Different hash should work
    doc3 = Document(source_id=source.id, content_hash="hash456", collected_at=collected_time)
    db.add(doc3)
    db.commit()
    assert doc3.id is not None

def test_dates_separation_in_document(db):
    source = Source(source_type="Website", name="Test Date Source")
    db.add(source)
    db.commit()
    
    dt_pub = get_utc_now()
    dt_upd = get_utc_now()
    dt_col = get_utc_now()
    
    doc = Document(
        source_id=source.id, 
        content_hash="hash_dates", 
        source_published_at=dt_pub,
        source_updated_at=dt_upd,
        collected_at=dt_col
    )
    db.add(doc)
    db.commit()
    
    assert doc.source_published_at == dt_pub
    assert doc.source_updated_at == dt_upd
    assert doc.collected_at == dt_col

def test_event_has_only_event_date_and_relationships(db):
    competitor = Competitor(name="Test Comp", canonical_name="Test Comp")
    topic = IntelligenceTopic(code="TEST_EVENT_TOPIC", name="Event Test")
    db.add(competitor)
    db.add(topic)
    db.commit()
    
    event_dt = get_utc_now()
    event = Event(
        competitor_id=competitor.id,
        topic_id=topic.id,
        event_type="Expansion",
        title="New Depot",
        event_date=event_dt
    )
    db.add(event)
    db.commit()
    
    assert event.event_date == event_dt
    assert not hasattr(event, "source_published_at")
    assert not hasattr(event, "source_updated_at")
    assert not hasattr(event, "collected_at")
