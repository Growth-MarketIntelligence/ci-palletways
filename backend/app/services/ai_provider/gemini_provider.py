import json
import logging
from typing import List, Dict, Any
from google import genai
from google.genai import types

from app.core.config import settings
from app.services.ai_provider.base import AIProvider, EXTRACTION_PROMPT

logger = logging.getLogger(__name__)

class GeminiProvider(AIProvider):
    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return settings.gemini_model

    def extract_network_events(self, text: str, competitor_name: str) -> List[Dict[str, Any]]:
        if not settings.gemini_api_key:
            logger.error("GEMINI_API_KEY is not set.")
            return []
            
        try:
            client = genai.Client(api_key=settings.gemini_api_key)
            prompt = EXTRACTION_PROMPT.replace("{text}", text)
            
            import time
            max_retries = 3
            base_delay = 15 # Wait 15 seconds before retrying (6 RPM = 1 every 10s)

            response = None
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        ),
                    )
                    break
                except Exception as api_err:
                    err_str = str(api_err).lower()
                    if "429" in err_str or "rate limit" in err_str or "quota" in err_str:
                        if attempt < max_retries - 1:
                            logger.warning(f"Gemini Rate Limit Exceeded. Waiting {base_delay}s before retry {attempt + 1}/{max_retries}...")
                            time.sleep(base_delay)
                            base_delay *= 2
                            continue
                    raise api_err
            
            try:
                events_data = json.loads(response.text)
                if isinstance(events_data, dict):
                    for key, value in events_data.items():
                        if isinstance(value, list):
                            return value
                    return []
                return events_data
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response as JSON from Gemini: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"AI Extraction failed (Gemini): {e}")
            return []

    def extract_strategy_events(self, text: str, competitor_name: str) -> List[Dict[str, Any]]:
        from app.services.ai_provider.base import STRATEGY_EXTRACTION_PROMPT
        if not settings.gemini_api_key:
            logger.error("GEMINI_API_KEY is not set.")
            return []
            
        try:
            client = genai.Client(api_key=settings.gemini_api_key)
            prompt = STRATEGY_EXTRACTION_PROMPT.replace("{text}", text)
            
            import time
            max_retries = 3
            base_delay = 15

            response = None
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        ),
                    )
                    break
                except Exception as api_err:
                    err_str = str(api_err).lower()
                    if "429" in err_str or "rate limit" in err_str or "quota" in err_str:
                        if attempt < max_retries - 1:
                            logger.warning(f"Gemini Rate Limit Exceeded. Waiting {base_delay}s before retry {attempt + 1}/{max_retries}...")
                            time.sleep(base_delay)
                            base_delay *= 2
                            continue
                    raise api_err
            
            try:
                events_data = json.loads(response.text)
                if isinstance(events_data, dict):
                    for key, value in events_data.items():
                        if isinstance(value, list):
                            return value
                    return []
                return events_data
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response as JSON from Gemini: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"AI Strategy Extraction failed (Gemini): {e}")
            return []

    def synthesize_strategy(self, events_json_str: str, competitor_name: str) -> List[Dict[str, Any]]:
        from app.services.ai_provider.base import STRATEGY_SYNTHESIS_PROMPT
        if not settings.gemini_api_key:
            logger.error("GEMINI_API_KEY is not set.")
            return []
            
        try:
            client = genai.Client(api_key=settings.gemini_api_key)
            prompt = STRATEGY_SYNTHESIS_PROMPT.replace("{competitor_name}", competitor_name).replace("{events_json}", events_json_str)
            
            import time
            max_retries = 3
            base_delay = 15

            response = None
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        ),
                    )
                    break
                except Exception as api_err:
                    err_str = str(api_err).lower()
                    if "429" in err_str or "rate limit" in err_str or "quota" in err_str:
                        if attempt < max_retries - 1:
                            logger.warning(f"Gemini Rate Limit Exceeded. Waiting {base_delay}s before retry {attempt + 1}/{max_retries}...")
                            time.sleep(base_delay)
                            base_delay *= 2
                            continue
                    raise api_err
            
            try:
                insights_data = json.loads(response.text)
                if isinstance(insights_data, dict):
                    for key, value in insights_data.items():
                        if isinstance(value, list):
                            return value
                    return []
                return insights_data
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response as JSON from Gemini strategy synthesis: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"AI Strategy Synthesis failed (Gemini): {e}")
            return []
