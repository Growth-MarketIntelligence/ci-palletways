import pytest
from app.models import Competitor, Event, IntelligenceTopic, Market, Source
from app.services.strategy_engine import synthesize_competitor_strategy
from app.core.config import settings

@pytest.fixture
def setup_strategy_data(db):
    market = db.query(Market).filter_by(country_code="GB").first()
    if not market:
        market = Market(name="United Kingdom", country_code="GB")
        db.add(market)
    
    comp = db.query(Competitor).filter_by(canonical_name="TestCompStrategy").first()
    if not comp:
        comp = Competitor(name="TestCompStrategy", canonical_name="TestCompStrategy")
        db.add(comp)
    
    net_topic = db.query(IntelligenceTopic).filter_by(code="NETWORK_GEOGRAPHIC_EXPANSION").first()
    if not net_topic:
        net_topic = IntelligenceTopic(code="NETWORK_GEOGRAPHIC_EXPANSION", name="Network")
        db.add(net_topic)
        
    strat_topic = db.query(IntelligenceTopic).filter_by(code="STRATEGY_MP").first()
    if not strat_topic:
        strat_topic = IntelligenceTopic(code="STRATEGY_MP", name="Strategy")
        db.add(strat_topic)
        
    db.commit()
    return {"competitor": comp, "net_topic": net_topic, "strat_topic": strat_topic}

def test_strategy_independence(db, setup_strategy_data, monkeypatch):
    """
    Proves that Strategy Synthesis works successfully even when Network Events are 0,
    as long as Direct Strategy Events are present.
    """
    comp = setup_strategy_data["competitor"]
    net_topic = setup_strategy_data["net_topic"]
    strat_topic = setup_strategy_data["strat_topic"]
    
    # 1. Guarantee Network Events = 0
    net_events_count = db.query(Event).filter(
        Event.competitor_id == comp.id, 
        Event.topic_id == net_topic.id
    ).count()
    assert net_events_count == 0
    
    # 2. Add one Direct Strategy Event
    strat_event = Event(
        competitor_id=comp.id,
        topic_id=strat_topic.id,
        event_type="COMMERCIAL_STRATEGY",
        title="Direct Strategy Testing",
        description="This event came directly from Strategy Collection pipeline, skipping Network."
    )
    db.add(strat_event)
    db.commit()
    
    # 3. Mock the AI Provider to return an insight grounded in the Strategy Event
    def mock_synth(self, events_json_str, competitor_name):
        return [{
            "strategy_category": "COMMERCIAL_STRATEGY",
            "strategy_theme": "Direct Independence",
            "assessment": "The competitor is demonstrating independent capability.",
            "interpretation": "Verified strategy extraction independence.",
            "confidence": 0.99,
            "supporting_event_ids": [str(strat_event.id)]
        }]
        
    from app.services.ai_provider.mock_provider import MockProvider
    monkeypatch.setattr(settings, "ai_provider", "mock")
    monkeypatch.setattr(MockProvider, "synthesize_strategy", mock_synth)
    
    # 4. Run Synthesis
    insights = synthesize_competitor_strategy(db, str(comp.id))
    
    # 5. Assert Success
    assert len(insights) == 1
    assert insights[0].strategy_category == "COMMERCIAL_STRATEGY"
    assert insights[0].strategy_theme == "Direct Independence"
    assert len(insights[0].events) == 1
    assert insights[0].events[0].event_id == strat_event.id
