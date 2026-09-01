import pytest
import respx
import httpx
from datetime import datetime, timezone, date
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.models import Market, Competitor, CompetitorMarket, IntelligenceTopic, Source, Document, Evidence, Event, Signal, CollectionRun
from app.services.collector import collect_url
from app.services.extractor import extract_network_events
from app.services.signal_generator import generate_network_signals

client = TestClient(app)

def get_utc_now():
    return datetime.now(timezone.utc)

@pytest.fixture
def setup_seed_data(db):
    market = db.query(Market).filter_by(country_code="GB").first()
    if not market:
        market = Market(name="United Kingdom", country_code="GB")
        db.add(market)
    
    comp = db.query(Competitor).filter_by(canonical_name="Palletforce").first()
    if not comp:
        comp = Competitor(name="Palletforce", canonical_name="Palletforce")
        db.add(comp)
    
    topic = db.query(IntelligenceTopic).filter_by(code="NETWORK_GEOGRAPHIC_EXPANSION").first()
    if not topic:
        topic = IntelligenceTopic(code="NETWORK_GEOGRAPHIC_EXPANSION", name="Network")
        db.add(topic)
    db.commit()
    
    cm = db.query(CompetitorMarket).filter_by(competitor_id=comp.id, market_id=market.id).first()
    if not cm:
        cm = CompetitorMarket(competitor_id=comp.id, market_id=market.id)
        db.add(cm)
    
    source = db.query(Source).filter_by(url="https://test.network.com").first()
    if not source:
        source = Source(
            competitor_id=comp.id,
            market_id=market.id,
            topic_id=topic.id,
            source_type="Website",
            name="Network Page",
            url="https://test.network.com",
            domain="test.network.com",
            collection_method="HTTP",
            collection_enabled=True,
            priority=1
        )
        db.add(source)
    db.commit()
    
    return {"market": market, "competitor": comp, "topic": topic, "source": source}

@respx.mock
def test_successful_collection_and_dates(db, setup_seed_data):
    source = setup_seed_data["source"]
    
    # Mock HTTP response
    html = """
    <html>
    <head>
        <title>Our Network</title>
        <meta property="article:published_time" content="2024-03-01T12:00:00Z" />
    </head>
    <body>
        We just opened a new depot in London.
    </body>
    </html>
    """
    respx.get(source.url).mock(return_value=httpx.Response(200, text=html, headers={"content-type": "text/html"}))
    
    run = CollectionRun(source_id=source.id, started_at=get_utc_now(), status="RUNNING")
    db.add(run)
    db.commit()
    doc, status, links = collect_url(db, str(source.id), source.url, run)
    assert doc is not None
    assert doc.title == "Our Network"
    assert doc.source_published_at is not None
    assert doc.source_published_at.year == 2024
    assert doc.source_published_at.month == 3
    assert doc.collected_at is not None

@respx.mock
def test_unchanged_source_deduplication(db, setup_seed_data):
    source = setup_seed_data["source"]
    
    html = "<html><body>Same Content</body></html>"
    respx.get(source.url).mock(return_value=httpx.Response(200, text=html))
    
    run1 = CollectionRun(source_id=source.id, started_at=get_utc_now(), status="RUNNING")
    db.add(run1)
    db.commit()
    doc1, status1, links1 = collect_url(db, str(source.id), source.url, run1)
    
    run2 = CollectionRun(source_id=source.id, started_at=get_utc_now(), status="RUNNING")
    db.add(run2)
    db.commit()
    doc2, status2, links2 = collect_url(db, str(source.id), source.url, run2)
    
    assert doc1 is not None
    assert doc2 is not None
    assert status2 == "UNCHANGED"
    assert doc1.id == doc2.id  # Should return the same document

@respx.mock
def test_changed_source_historical_preservation(db, setup_seed_data):
    source = setup_seed_data["source"]
    
    html1 = "<html><body>Old Content</body></html>"
    html2 = "<html><body>New Content</body></html>"
    
    # We use a route to return different responses based on calls
    route = respx.get(source.url)
    route.side_effect = [
        httpx.Response(200, text=html1),
        httpx.Response(200, text=html2)
    ]
    
    run1 = CollectionRun(source_id=source.id, started_at=get_utc_now(), status="RUNNING")
    db.add(run1)
    db.commit()
    doc1, status1, links1 = collect_url(db, str(source.id), source.url, run1)
    
    run2 = CollectionRun(source_id=source.id, started_at=get_utc_now(), status="RUNNING")
    db.add(run2)
    db.commit()
    doc2, status2, links2 = collect_url(db, str(source.id), source.url, run2)
    
    assert doc1 is not None
    assert doc2 is not None
    assert status2 == "CHANGED"
    
    assert doc1.id != doc2.id  # Should create a new document

@respx.mock
def test_http_failure_and_timeouts(db, setup_seed_data):
    source = setup_seed_data["source"]
    
    # 404
    respx.get(source.url).mock(return_value=httpx.Response(404))
    run1 = CollectionRun(source_id=source.id, started_at=get_utc_now(), status="RUNNING")
    db.add(run1)
    db.commit()
    doc1, status1, links1 = collect_url(db, str(source.id), source.url, run1)
    assert doc1 is None
    assert status1 == "FAILED"
    
    # Timeout
    respx.get(source.url).mock(side_effect=httpx.TimeoutException("Timeout"))
    run2 = CollectionRun(source_id=source.id, started_at=get_utc_now(), status="RUNNING")
    db.add(run2)
    db.commit()
    doc2, status2, links2 = collect_url(db, str(source.id), source.url, run2)
    assert doc2 is None
    assert status2 == "FAILED"

def test_valid_ai_event_extraction(db, setup_seed_data, monkeypatch):
    source = setup_seed_data["source"]
    
    # Use mock AI
    monkeypatch.setattr(settings, "ai_provider", "mock")
    
    doc = Document(
        source_id=source.id,
        content_hash="mock_hash",
        text_content="We opened a new depot in London on 2024-03-15.",
        collected_at=get_utc_now()
    )
    db.add(doc)
    db.commit()
    
    events = extract_network_events(db, str(doc.id))
    assert len(events) == 1
    assert events[0].event_type == "HUBS_AND_DEPOTS"
    assert events[0].evidence is not None
    
    # Check event_date behavior
    assert events[0].event_date.year == 2024

def test_invalid_event_rejection(db, setup_seed_data, monkeypatch):
    source = setup_seed_data["source"]
    monkeypatch.setattr(settings, "ai_provider", "mock")
    
    doc = Document(
        source_id=source.id,
        content_hash="mock_hash_2",
        text_content="some text",
        collected_at=get_utc_now()
    )
    db.add(doc)
    db.commit()
    
    # Hack the mock AI to return an invalid type
    def bad_mock(self, *args):
        return [{"event_type": "INVALID_TYPE", "evidence_excerpt": "test", "confidence_score": 1.0}]
    
    from app.services.ai_provider.mock_provider import MockProvider
    monkeypatch.setattr(MockProvider, "extract_network_events", bad_mock)
    
    events = extract_network_events(db, str(doc.id))
    assert len(events) == 0  # Rejected

def test_signal_generation(db, setup_seed_data):
    comp = setup_seed_data["competitor"]
    topic = setup_seed_data["topic"]
    
    # Needs >= 2 events
    sig1 = generate_network_signals(db, str(comp.id))
    assert sig1 is None
    
    # Add events
    ev1 = Event(competitor_id=comp.id, topic_id=topic.id, event_type="NETWORK_FOOTPRINT", title="1")
    ev2 = Event(competitor_id=comp.id, topic_id=topic.id, event_type="HUBS_AND_DEPOTS", title="2")
    db.add_all([ev1, ev2])
    db.commit()
    
    sig2 = generate_network_signals(db, str(comp.id))
    assert sig2 is not None
    assert sig2.title.startswith("Recent Network Growth")

def test_api_time_filtering(db, setup_seed_data):
    comp = setup_seed_data["competitor"]
    topic = setup_seed_data["topic"]
    
    from app.core.database import get_db
    app.dependency_overrides[get_db] = lambda: db
    
    # Insert some data with specific dates
    ev = Event(
        competitor_id=comp.id, 
        topic_id=topic.id, 
        event_type="HUBS_AND_DEPOTS", 
        title="API Test",
        event_date=date(2024, 5, 1)
    )
    # create dummy doc just in case
    doc = Document(source_id=setup_seed_data["source"].id, content_hash="api_test", collected_at=get_utc_now())
    db.add(doc)
    db.commit()

    evid = Evidence(
        document_id=doc.id,
        claim="Test",
        text_excerpt="Test"
    )
    
    evid.document_id = doc.id
    db.add(evid)
    db.commit()
    
    ev.evidence_id = evid.id
    db.add(ev)
    db.commit()
    
    # Test filtering
    response = client.get(f"/network/events?start_date=2024-04-01&end_date=2024-06-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    
    # app.dependency_overrides.clear()
    
    response2 = client.get(f"/network/events?start_date=2024-06-01")
    data2 = response2.json()
    # Shouldn't find the May 1st event
    assert len(data2) == 0

def test_real_ai_extraction(db, setup_seed_data, monkeypatch):
    from app.core.config import settings
    if not settings.gemini_api_key:
        import pytest
        pytest.skip("Skipping real AI extraction test because GEMINI_API_KEY is not set.")
        
    source = setup_seed_data["source"]
    comp = setup_seed_data["competitor"]
    
    text = "We are very excited to announce that Fortec Distribution opened a brand new physical depot in Manchester on September 15th 2024. This will significantly increase our capacity in the North West."
    
    monkeypatch.setattr(settings, "ai_provider", "gemini")
    
    doc = Document(source_id=source.id, content_hash="real_ai_test_hash", text_content=text, collected_at=get_utc_now())
    db.add(doc)
    db.commit()
    
    events = extract_network_events(db, str(doc.id))
    
    # We should have one event
    assert len(events) == 1
    ev = events[0]
    
    assert ev.extraction_model == "gemini-3.6-flash"
    assert ev.event_type == "HUBS_AND_DEPOTS"
    assert ev.location is not None and "Manchester" in ev.location
    assert ev.event_date is not None
    assert ev.event_date.year == 2024
    assert ev.event_date.month == 9
    assert ev.event_date.day == 15
    assert ev.evidence is not None
    assert "depot in Manchester on September 15th 2024" in ev.evidence.text_excerpt

def test_extraction_without_competitor_market_mapping(db, setup_seed_data, monkeypatch):
    """
    Regression test proving that Network extraction does not depend on an unused
    CompetitorMarket relationship. It must reach the AI provider and create events,
    even with a NULL event_date.
    """
    source = setup_seed_data["source"]
    comp = setup_seed_data["competitor"]
    
    # Remove the CompetitorMarket mapping to simulate the bug scenario
    db.query(CompetitorMarket).filter(CompetitorMarket.competitor_id == comp.id).delete()
    db.commit()
    
    # Verify the test conditions
    assert db.query(Competitor).filter_by(id=comp.id).first() is not None
    assert db.query(CompetitorMarket).filter_by(competitor_id=comp.id).first() is None
    
    monkeypatch.setattr(settings, "ai_provider", "mock")
    
    # Hack the mock AI to return a valid event without a date
    def stateless_mock(self, *args):
        return [{"event_type": "NETWORK_FOOTPRINT", "description": "Expanded network", "evidence_excerpt": "Test", "confidence_score": 1.0, "location": "Test Loc", "event_date": None}]
    
    from app.services.ai_provider.mock_provider import MockProvider
    monkeypatch.setattr(MockProvider, "extract_network_events", stateless_mock)
    
    doc = Document(
        source_id=source.id,
        content_hash="regression_no_market",
        text_content="We expanded our network.",
        collected_at=get_utc_now()
    )
    db.add(doc)
    db.commit()
    
    events = extract_network_events(db, str(doc.id))
    
    assert len(events) == 1
    ev = events[0]
    assert ev.event_type == "NETWORK_FOOTPRINT"
    assert ev.event_date is None
    assert ev.evidence is not None

def test_extraction_missing_competitor(db, setup_seed_data, monkeypatch, caplog):
    """
    Proves that a missing Competitor does not silently return [] (which looks like AI found nothing).
    It must explicitly log an error.
    """
    import logging
    source = setup_seed_data["source"]
    comp = setup_seed_data["competitor"]
    
    # Delete the competitor
    db.query(CompetitorMarket).filter(CompetitorMarket.competitor_id == comp.id).delete()
    db.query(Source).filter(Source.competitor_id == comp.id).update({"competitor_id": None})
    db.query(Competitor).filter(Competitor.id == comp.id).delete()
    db.commit()
    
    doc = Document(
        source_id=source.id,
        content_hash="missing_comp",
        text_content="some text",
        collected_at=get_utc_now()
    )
    db.add(doc)
    db.commit()
    
    with caplog.at_level(logging.ERROR):
        events = extract_network_events(db, str(doc.id))
        
    assert len(events) == 0
    assert "Extraction failed" in caplog.text
    assert "missing Competitor" in caplog.text

