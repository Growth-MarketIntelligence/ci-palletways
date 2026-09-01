from typing import List, Dict, Any
from app.services.ai_provider.base import AIProvider

class MockProvider(AIProvider):
    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return "mock"

    def extract_network_events(self, text: str, competitor_name: str) -> List[Dict[str, Any]]:
        """Mock implementation for automated tests."""
        events = []
        text_lower = text.lower()
        if "new depot" in text_lower or "opened" in text_lower:
            events.append({
                "event_type": "HUBS_AND_DEPOTS",
                "description": f"{competitor_name} opened a new depot based on mock detection.",
                "location": "Mock Location",
                "event_date": "2024-01-01",
                "evidence_excerpt": "new depot opened",
                "confidence_score": 0.95
            })
        elif "expand" in text_lower:
            events.append({
                "event_type": "NETWORK_FOOTPRINT",
                "description": f"{competitor_name} expanded its network.",
                "location": "Mock Region",
                "event_date": None,
                "evidence_excerpt": "expanded coverage",
                "confidence_score": 0.8
            })
        return events

    def extract_strategy_events(self, text: str, competitor_name: str) -> List[Dict[str, Any]]:
        return []

    def synthesize_strategy(self, events_json_str: str, competitor_name: str) -> List[Dict[str, Any]]:
        return [
            {
                "strategy_category": "NETWORK_STRATEGY",
                "strategy_theme": "Mock Expansion",
                "assessment": f"Mock assessment for {competitor_name}",
                "interpretation": "Mock interpretation",
                "confidence": 0.9,
                "supporting_event_ids": []
            }
        ]
