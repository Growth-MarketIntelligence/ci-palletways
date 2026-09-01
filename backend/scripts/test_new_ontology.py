import asyncio
import logging
from app.services.ai_provider import get_ai_provider

logging.basicConfig(level=logging.INFO)

def test_extraction():
    provider = get_ai_provider()
    
    text = """
    Palletline expands its infrastructure today by opening a massive new 50,000 square foot depot in Manchester, 
    adding 20 new EV trucks to its fleet, and securing Smith Haulage as a new partner. This multi-million 
    pound investment aims to boost throughput by 30%.
    """
    print(f"Testing extraction on {provider.provider_name} ({provider.model_name})...")
    events = provider.extract_network_events(text, "Palletline")
    
    import json
    print(json.dumps(events, indent=2))

if __name__ == "__main__":
    test_extraction()
