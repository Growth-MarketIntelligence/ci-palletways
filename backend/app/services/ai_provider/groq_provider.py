import json
import logging
from typing import List, Dict, Any
from groq import Groq

from app.core.config import settings
from app.services.ai_provider.base import AIProvider, EXTRACTION_PROMPT

logger = logging.getLogger(__name__)

class GroqProvider(AIProvider):
    @property
    def provider_name(self) -> str:
        return "groq"

    @property
    def model_name(self) -> str:
        return settings.groq_model

    def extract_network_events(self, text: str, competitor_name: str) -> List[Dict[str, Any]]:
        if not settings.groq_api_key:
            logger.error("GROQ_API_KEY is not set.")
            return []
            
        try:
            client = Groq(api_key=settings.groq_api_key)
            prompt = EXTRACTION_PROMPT.replace("{text}", text)
            
            import time
            max_retries = 3
            base_delay = 20 # Wait 20 seconds before retrying

            completion = None
            for attempt in range(max_retries):
                try:
                    completion = client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that strictly outputs JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.0,
                        response_format={"type": "json_object"}
                    )
                    break
                except Exception as api_err:
                    err_str = str(api_err).lower()
                    if "429" in err_str or "rate limit" in err_str:
                        if attempt < max_retries - 1:
                            logger.warning(f"Groq Rate Limit Exceeded. Waiting {base_delay}s before retry {attempt + 1}/{max_retries}...")
                            time.sleep(base_delay)
                            base_delay *= 2
                            continue
                    raise api_err
            
            response_text = completion.choices[0].message.content
            
            try:
                events_data = json.loads(response_text)
                if isinstance(events_data, dict):
                    # Llama 3 often returns {"events": [...]} when forced to output JSON objects
                    for key, value in events_data.items():
                        if isinstance(value, list):
                            return value
                    return []
                return events_data
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response as JSON from Groq: {response_text}")
                return []
                
        except Exception as e:
            logger.error(f"AI Extraction failed (Groq): {e}")
            return []

    def extract_strategy_events(self, text: str, competitor_name: str) -> List[Dict[str, Any]]:
        from app.services.ai_provider.base import STRATEGY_EXTRACTION_PROMPT
        if not settings.groq_api_key:
            logger.error("GROQ_API_KEY is not set.")
            return []
            
        try:
            client = Groq(api_key=settings.groq_api_key)
            prompt = STRATEGY_EXTRACTION_PROMPT.replace("{text}", text)
            
            import time
            max_retries = 3
            base_delay = 20

            completion = None
            for attempt in range(max_retries):
                try:
                    completion = client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": "You are a competitive intelligence analyst. You must strictly output JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.0,
                        response_format={"type": "json_object"}
                    )
                    break
                except Exception as api_err:
                    err_str = str(api_err).lower()
                    if "429" in err_str or "rate limit" in err_str:
                        if attempt < max_retries - 1:
                            logger.warning(f"Groq Rate Limit Exceeded. Waiting {base_delay}s before retry {attempt + 1}/{max_retries}...")
                            time.sleep(base_delay)
                            base_delay *= 2
                            continue
                    raise api_err
            
            response_text = completion.choices[0].message.content
            
            try:
                events_data = json.loads(response_text)
                if isinstance(events_data, dict):
                    for key, value in events_data.items():
                        if isinstance(value, list):
                            return value
                    return []
                return events_data
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response as JSON from Groq: {response_text}")
                return []
                
        except Exception as e:
            logger.error(f"AI Strategy Extraction failed (Groq): {e}")
            return []

    def synthesize_strategy(self, events_json_str: str, competitor_name: str) -> List[Dict[str, Any]]:
        from app.services.ai_provider.base import STRATEGY_SYNTHESIS_PROMPT
        if not settings.groq_api_key:
            logger.error("GROQ_API_KEY is not set.")
            return []
            
        try:
            client = Groq(api_key=settings.groq_api_key)
            prompt = STRATEGY_SYNTHESIS_PROMPT.replace("{competitor_name}", competitor_name).replace("{events_json}", events_json_str)
            
            import time
            max_retries = 3
            base_delay = 20

            completion = None
            for attempt in range(max_retries):
                try:
                    completion = client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": "You are a strategic competitive intelligence analyst. You must strictly output JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.0,
                        response_format={"type": "json_object"}
                    )
                    break
                except Exception as api_err:
                    err_str = str(api_err).lower()
                    if "429" in err_str or "rate limit" in err_str:
                        if attempt < max_retries - 1:
                            logger.warning(f"Groq Rate Limit Exceeded. Waiting {base_delay}s before retry {attempt + 1}/{max_retries}...")
                            time.sleep(base_delay)
                            base_delay *= 2
                            continue
                    raise api_err
            
            response_text = completion.choices[0].message.content
            
            try:
                insights_data = json.loads(response_text)
                if isinstance(insights_data, dict):
                    for key, value in insights_data.items():
                        if isinstance(value, list):
                            return value
                    return []
                return insights_data
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response as JSON from Groq strategy synthesis: {response_text}")
                return []
                
        except Exception as e:
            logger.error(f"AI Strategy Synthesis failed (Groq): {e}")
            return []
