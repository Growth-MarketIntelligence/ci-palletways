import pytest
from app.services.network_signal_synthesizer import synthesize_signal

class MockEvent:
    def __init__(self, event_type, location, signal_type, event_subtype=None):
        self.event_type = event_type
        self.location = location
        self.signal_type = signal_type
        self.event_subtype = event_subtype

def test_multiple_expansion_events():
    events = [
        MockEvent("HUBS_AND_DEPOTS", "Manchester", "Expansion"),
        MockEvent("HUBS_AND_DEPOTS", "Leeds", "Expansion")
    ]
    result = synthesize_signal("Pall-Ex", events)
    assert "Across Leeds and Manchester" in result["title"]
    assert "new depot activity" in result["description"]
    assert "Expansion" in result["title"]
    assert "expanded its network" in result["description"]

def test_expansion_and_partnership():
    events = [
        MockEvent("HUBS_AND_DEPOTS", "Birmingham", "Expansion"),
        MockEvent("PARTNERS_AND_MEMBERS", "Birmingham", "Expansion")
    ]
    result = synthesize_signal("Palletforce", events)
    assert "Hub and Depot Expansion in Birmingham" in result["title"]
    assert "Palletforce expanded its network with new depot activity and partner additions in Birmingham." == result["description"].strip()

def test_network_contraction():
    events = [
        MockEvent("HUBS_AND_DEPOTS", "Bristol", "Contraction", "Hub / depot closures or consolidation"),
        MockEvent("PARTNERS_AND_MEMBERS", "Bristol", "Contraction", "Partner exits / changes")
    ]
    result = synthesize_signal("Fortec", events)
    assert "Hub and Depot Contraction in Bristol" in result["title"]
    assert "Fortec reduced its network presence following depot changes and partner changes in Bristol." == result["description"].strip()

def test_missing_location():
    events = [
        MockEvent("NETWORK_FOOTPRINT", None, "Expansion")
    ]
    result = synthesize_signal("Palletline", events)
    assert "Geographic Expansion" in result["title"]
    assert " in " not in result["title"]
    assert "Palletline expanded its network with geographic expansion." == result["description"].strip()
