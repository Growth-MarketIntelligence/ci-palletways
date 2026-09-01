import json
import logging
import httpx
from typing import List, Dict, Any

from app.core.config import settings
from app.services.ai_provider.base import AIProvider, EXTRACTION_PROMPT, STRATEGY_EXTRACTION_PROMPT, STRATEGY_SYNTHESIS_PROMPT

logger = logging.getLogger(__name__)

class OllamaProvider(AIProvider):
    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return settings.ollama_model

    def extract_network_events(self, text: str, competitor_name: str) -> List[Dict[str, Any]]:
        if not settings.ollama_model:
            logger.error("OLLAMA_MODEL is not set. Cannot use OllamaProvider.")
            return []
            
        try:
            prompt = EXTRACTION_PROMPT.replace("{text}", text)
            url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.0,
                    "top_p": 0.1,
                    "num_ctx": 8192
                }
            }
            
            with httpx.Client(timeout=900.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                response_text = result.get("response", "")
                
                try:
                    events_data = json.loads(response_text)
                    if isinstance(events_data, dict):
                        # Some models might return a dict like {"events": [...]} instead of an array
                        for key, value in events_data.items():
                            if isinstance(value, list):
                                return value
                        return []
                    return events_data
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse AI response as JSON from Ollama: {response_text}")
                    return []
                    
        except httpx.HTTPError as e:
            logger.error(f"AI Extraction failed (Ollama HTTP Error): {e}")
            return []
        except Exception as e:
            logger.error(f"AI Extraction failed (Ollama): {e}")
            return []

    def extract_strategy_events(self, text: str, competitor_name: str) -> List[Dict[str, Any]]:
        if not settings.ollama_model:
            logger.error("OLLAMA_MODEL is not set. Cannot use OllamaProvider.")
            return []
            
        try:
            prompt = STRATEGY_EXTRACTION_PROMPT.replace("{text}", text)
            url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.0,
                    "top_p": 0.1,
                    "num_ctx": 8192
                }
            }
            
            with httpx.Client(timeout=900.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                response_text = result.get("response", "")
                
                try:
                    events_data = json.loads(response_text)
                    if isinstance(events_data, dict):
                        for key, value in events_data.items():
                            if isinstance(value, list):
                                return value
                        return []
                    return events_data
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse AI response as JSON from Ollama: {response_text}")
                    return []
                    
        except httpx.HTTPError as e:
            logger.error(f"AI Strategy Extraction failed (Ollama HTTP Error): {e}")
            return []
        except Exception as e:
            logger.error(f"AI Strategy Extraction failed (Ollama): {e}")
            return []

    def synthesize_strategy(self, events_json_str: str, competitor_name: str) -> List[Dict[str, Any]]:
        if not settings.ollama_model:
            logger.error("OLLAMA_MODEL is not set. Cannot use OllamaProvider.")
            return []
            
        try:
            prompt = STRATEGY_SYNTHESIS_PROMPT.replace("{competitor_name}", competitor_name).replace("{events_json}", events_json_str)
            url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.3,
                    "num_ctx": 8192
                }
            }
            
            with httpx.Client(timeout=900.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                response_text = result.get("response", "")
                
                try:
                    insights_data = json.loads(response_text)
                    if isinstance(insights_data, dict):
                        for key, value in insights_data.items():
                            if isinstance(value, list):
                                return value
                        return []
                    return insights_data
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse AI response as JSON from Ollama: {response_text}")
                    return []
                    
        except httpx.HTTPError as e:
            logger.error(f"AI Strategy Synthesis failed (Ollama HTTP Error): {e}")
            return []
        except Exception as e:
            logger.error(f"AI Strategy Synthesis failed (Ollama): {e}")
            return []
