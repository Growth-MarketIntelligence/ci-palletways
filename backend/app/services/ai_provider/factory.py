from app.core.config import settings
from app.services.ai_provider.base import AIProvider
from app.services.ai_provider.gemini_provider import GeminiProvider
from app.services.ai_provider.ollama_provider import OllamaProvider
from app.services.ai_provider.mock_provider import MockProvider
from app.services.ai_provider.groq_provider import GroqProvider

def get_ai_provider() -> AIProvider:
    provider_type = settings.ai_provider.lower()
    
    if provider_type == "gemini":
        return GeminiProvider()
    elif provider_type == "groq":
        return GroqProvider()
    elif provider_type == "ollama":
        return OllamaProvider()
    elif provider_type == "mock":
        return MockProvider()
    else:
        raise ValueError(f"Invalid AI_PROVIDER configuration: '{provider_type}'. Supported values are 'gemini', 'ollama', 'mock'.")
