import pytest
import respx
import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.services.ai_provider.factory import get_ai_provider
from app.services.ai_provider.gemini_provider import GeminiProvider
from app.services.ai_provider.ollama_provider import OllamaProvider
from app.services.ai_provider.mock_provider import MockProvider
from app.services.ai_provider.base import AIProvider

def test_provider_factory_gemini(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "gemini")
    provider = get_ai_provider()
    assert isinstance(provider, GeminiProvider)
    assert provider.provider_name == "gemini"
    assert provider.model_name == settings.gemini_model

def test_provider_factory_ollama(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "ollama")
    monkeypatch.setattr(settings, "ollama_model", "test-model")
    provider = get_ai_provider()
    assert isinstance(provider, OllamaProvider)
    assert provider.provider_name == "ollama"
    assert provider.model_name == "test-model"

def test_provider_factory_mock(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "mock")
    provider = get_ai_provider()
    assert isinstance(provider, MockProvider)
    assert provider.provider_name == "mock"
    assert provider.model_name == "mock"

def test_provider_factory_invalid(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "invalid")
    with pytest.raises(ValueError, match="Invalid AI_PROVIDER configuration"):
        get_ai_provider()

@respx.mock
def test_ollama_provider_unavailable(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "ollama")
    monkeypatch.setattr(settings, "ollama_model", "test-model")
    monkeypatch.setattr(settings, "ollama_base_url", "http://test-ollama:11434")
    
    # Mock connection error
    respx.post("http://test-ollama:11434/api/generate").mock(side_effect=httpx.ConnectError("Connection refused"))
    
    provider = get_ai_provider()
    events = provider.extract_network_events("Some text", "TestComp")
    assert events == []  # Fails gracefully without fabricating data

def test_gemini_provider_no_key(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "gemini")
    monkeypatch.setattr(settings, "gemini_api_key", "")
    
    provider = get_ai_provider()
    events = provider.extract_network_events("Some text", "TestComp")
    assert events == []  # Gracefully fails without API key

def test_mock_provider_deterministic():
    provider = MockProvider()
    events = provider.extract_network_events("We opened a new depot in London on 2024-03-15.", "TestComp")
    assert len(events) == 1
    assert events[0]["event_type"] == "HUBS_AND_DEPOTS"
    assert events[0]["location"] == "Mock Location"
    assert events[0]["event_date"] == "2024-01-01"
