from typing import List, Dict, Any

def format_list_to_english(items: List[str], max_items: int = 3, suffix: str = "locations") -> str:
    """Formats a list of strings into 'A, B and C' format, truncating if too long."""
    if not items:
        return ""
    items = sorted(list(set(items)))
    if len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]} and {items[1]}"
    elif len(items) > max_items:
        remaining = len(items) - max_items
        return ", ".join(items[:max_items]) + f" and {remaining} other {suffix}"
    else:
        return ", ".join(items[:-1]) + f" and {items[-1]}"

def synthesize_signal(competitor_name: str, events: List[Any]) -> Dict[str, str]:
    """
    Deterministically synthesize a signal title and description from a list of structured events.
    """
    if not events:
        return {
            "title": f"{competitor_name} Network Activity",
            "description": "Detected network activity."
        }

    # Extract distinct locations and map event_types to human-readable strings
    locations = set()
    
    # Try to map actual subtype or type to specific actions
    activity_phrases = set()
    signal_types = set()
    
    for ev in events:
        # handle both ORM objects and dicts
        location = getattr(ev, 'location', None) or (ev.get('location') if isinstance(ev, dict) else None)
        event_type = getattr(ev, 'event_type', None) or (ev.get('event_type') if isinstance(ev, dict) else None)
        event_subtype = getattr(ev, 'event_subtype', None) or (ev.get('event_subtype') if isinstance(ev, dict) else None)
        signal_type = getattr(ev, 'signal_type', None) or (ev.get('signal_type') if isinstance(ev, dict) else None)
        
        if location and str(location).strip() and str(location).strip().lower() not in ["null", "none", "unknown"]:
            locations.add(str(location).strip())
            
        # Parse activity
        activity = None
        if event_type == "PARTNERS_AND_MEMBERS":
            activity = "partner additions" if signal_type == "Expansion" else "partner changes"
        elif event_type == "HUBS_AND_DEPOTS":
            activity = "new depot activity" if signal_type == "Expansion" else "depot changes"
        elif event_type == "NETWORK_FOOTPRINT":
            activity = "geographic expansion" if signal_type == "Expansion" else "network footprint changes"
        elif event_type == "WAREHOUSING_CAPACITY":
            activity = "warehousing capacity adjustments"
        elif event_type == "FLEET_AND_TRANSPORT_CAPACITY":
            activity = "fleet and transport changes"
        elif event_type == "NETWORK_GROWTH_AND_VOLUME":
            activity = "network volume growth" if signal_type == "Expansion" else "network volume changes"
            
        if not activity and event_subtype:
            activity = str(event_subtype).lower()
        elif not activity and event_type:
            activity = str(event_type).replace("_", " ").lower()
            
        if activity:
            activity_phrases.add(activity)
            
        if signal_type:
            signal_types.add(str(signal_type).title())

    location_str = format_list_to_english(list(locations), max_items=3, suffix="locations")
    
    # Determine primary direction
    direction = "Activity"
    if "Expansion" in signal_types and "Contraction" not in signal_types:
        direction = "Expansion"
    elif "Contraction" in signal_types and "Expansion" not in signal_types:
        direction = "Contraction"
    elif "Expansion" in signal_types and "Contraction" in signal_types:
        direction = "Changes"
    elif "Capacity" in signal_types:
        direction = "Capacity Adjustments"
        
    # Determine the topic string from the first event's type (they are grouped by type)
    first_ev = events[0]
    base_type = getattr(first_ev, 'event_type', None) or (first_ev.get('event_type') if isinstance(first_ev, dict) else None)
    
    type_names = {
        "PARTNERS_AND_MEMBERS": "Partner",
        "HUBS_AND_DEPOTS": "Hub and Depot",
        "NETWORK_FOOTPRINT": "Geographic",
        "WAREHOUSING_CAPACITY": "Warehousing",
        "FLEET_AND_TRANSPORT_CAPACITY": "Fleet",
        "NETWORK_GROWTH_AND_VOLUME": "Volume"
    }
    topic_str = type_names.get(base_type, "Network") if base_type else "Network"
    
    # Build Title
    title = f"{topic_str} {direction}"
    if location_str:
        if len(locations) == 1:
            title += f" in {location_str}"
        else:
            title += f" Across {location_str}"
        
    # Keep title concise - if location_str is too long, trim it
    if len(title) > 80:
        title = f"{topic_str} {direction} across multiple locations"
        
    title = f"{competitor_name} {title}"
    
    # Build Description
    activities_str = format_list_to_english(list(activity_phrases), max_items=3, suffix="activities")
    if not activities_str:
        activities_str = "network activity"
        
    if direction == "Expansion":
        desc = f"{competitor_name} expanded its network with {activities_str}"
    elif direction == "Contraction":
        desc = f"{competitor_name} reduced its network presence following {activities_str}"
    else:
        desc = f"{competitor_name} experienced {activities_str}"
        
    if location_str:
        desc += f" in {location_str}."
    else:
        desc += "."

    return {
        "title": title,
        "description": desc
    }
