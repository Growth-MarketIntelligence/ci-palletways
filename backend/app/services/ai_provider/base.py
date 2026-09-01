from abc import ABC, abstractmethod
from typing import List, Dict, Any

PROMPT_VERSION = "1.0"

EXTRACTION_PROMPT = """
You are an expert competitive intelligence analyst tracking the logistics and pallet network industry.
Analyze the following text to extract any explicit strategic events related to the competitor network.
You must adhere STRICTLY to the evidence->classification->metadata contract. Never infer missing data. If it's not stated, return null.

Focus ONLY on these 6 Category pillars, their specific Sub-categories, and the overarching Signal Type:

CATEGORIES AND SUB-CATEGORIES:
1. "NETWORK_FOOTPRINT"
   Sub-categories: "Countries of presence", "Geographic / regional coverage", "Cross-border network / corridors"
2. "PARTNERS_AND_MEMBERS"
   Sub-categories: "Total partners / members", "Partners by country", "New partners / members", "Partner exits / changes"
3. "HUBS_AND_DEPOTS"
   Sub-categories: "Number of hubs", "Number of depots / branches", "New / expanded hubs or depots", "Hub / depot closures or consolidation"
4. "WAREHOUSING_CAPACITY"
   Sub-categories: "Warehouse footprint (m2)", "Number / location of warehouses", "New / expanded warehouse capacity"
5. "FLEET_AND_TRANSPORT_CAPACITY"
   Sub-categories: "Fleet size", "Fleet expansion / replacement", "EV / alternative-fuel fleet"
6. "NETWORK_GROWTH_AND_VOLUME"
   Sub-categories: "Pallets / shipments handled", "Volume growth", "Capacity expansion", "Network expansion / contraction"

SIGNAL TYPES (Classify EVERY event into exactly one of these):
- "Expansion" (New partner, depot, hub, warehouse, fleet, country)
- "Contraction" (Partner exit, depot closure, hub closure, market exit)
- "Capacity" (More vehicles, warehouse space, pallet capacity, throughput)
- "Performance" (Shipment/pallet growth, volume decline, utilisation changes)

Return a JSON object containing a single key "events" which holds an array of event objects. If no valid events are found, return {"events": []}.
For each event, provide:
- event_type: Must be exactly one of the 6 Categories above.
- event_subtype: Must be exactly one of the Sub-categories valid for the chosen event_type.
- signal_type: Must be exactly one of the 4 Signal Types (Expansion, Contraction, Capacity, Performance).
- description: A clear, factual description of the event.
- location: The specific city, region, or postcode affected (if applicable).
- event_date: The date the event actually occurred (in YYYY-MM-DD format). Only provide this if explicitly stated. DO NOT GUESS.
- metadata: A JSON object containing highly specific data points extracted from the text (e.g. {"investment_gbp": 5000000, "square_footage": 10000, "previous_network": "Pall-Ex"}). If no specific numbers or names are mentioned, return an empty object {}.
- evidence_excerpt: The exact quote or specific section from the text that proves this event occurred. DO NOT PARAPHRASE.
- confidence_score: A float between 0.0 and 1.0 representing your confidence that this event matches the strict definitions.

Text to analyze:
{text}
"""

STRATEGY_EXTRACTION_PROMPT = """
You are an expert competitive intelligence analyst tracking the logistics and pallet network industry.
Analyze the following source document text to extract explicit strategic events related to the competitor's Strategy & Market Positioning.
You must adhere STRICTLY to the evidence->classification->metadata contract. Never infer missing data. If it's not stated, return null.

Focus ONLY on these 10 Strategy Categories:
1. "STRATEGIC_DIRECTION" (strategic priorities, growth strategy, restructuring, transformation, long-term business direction)
2. "MARKET_POSITIONING" (competitive positioning, differentiation, market leadership claims, value proposition, premium/low-cost)
3. "COMMERCIAL_STRATEGY" (pricing strategy, commercial model changes, new commercial propositions, customer acquisition)
4. "CUSTOMER_SEGMENT_STRATEGY" (target industries, target customer segments, B2B/B2C strategy, e-commerce focus, SME/enterprise)
5. "SERVICE_PROPOSITION" (new service propositions, service repositioning, premium service offerings, customer experience)
6. "TECHNOLOGY_STRATEGY" (digital transformation, automation, platform, AI adoption, API strategy, visibility)
7. "GEOGRAPHIC_STRATEGY" (geographic growth, regional prioritisation, UK/European expansion, internationalisation, cross-border)
8. "PARTNERSHIP_STRATEGY" (strategic partnerships, ecosystem strategy, alliance, technology partnerships, network partnerships)
9. "COMPETITIVE_POSITIONING" (competitor differentiation, response to competitor activity, strategic positioning against rivals)
10. "OPERATIONAL_STRATEGY" (operating model changes, efficiency strategy, capacity strategy, operational transformation)

Return a JSON object containing a single key "events" which holds an array of event objects. If no valid events are found, return {"events": []}.
For each event, provide:
- event_type: Must be exactly one of the 10 Categories above.
- event_subtype: A short string identifying the specific subtype (e.g. "European expansion", "pricing strategy").
- signal_type: Must be exactly one of: "Strategy Announcement", "Market Positioning Claim", "Commercial Launch", "Operational Shift".
- description: A clear, factual description of the event.
- location: The specific city, region, or country affected (if applicable and explicitly stated).
- event_date: The date the event actually occurred/was announced (in YYYY-MM-DD format). Only provide this if explicitly stated.
- metadata: A JSON object containing highly specific data points extracted from the text (e.g. {"investment_gbp": 5000000, "target_segment": "B2C"}). If none, return {}.
- evidence_excerpt: The exact quote or specific section from the text that proves this event occurred. DO NOT PARAPHRASE.
- confidence_score: A float between 0.0 and 1.0 representing your confidence.

CRITICAL RULES:
- ONLY use information contained in the supplied document.
- DO NOT use outside knowledge.
- DO NOT invent dates, competitors, financial values, or infer market positioning merely because a company claims something indirectly.
- Every event MUST have a verifiable evidence_excerpt.

Text to analyze:
{text}
"""

STRATEGY_SYNTHESIS_PROMPT = """
You are an expert Competitive Intelligence strategist specializing in the UK and European logistics, pallet network, freight and distribution industry.

Your task is to analyze a set of already-validated Strategy Events (and optional contextual Network Events) and determine what they reveal about the competitor's STRATEGY AND MARKET POSITIONING.

IMPORTANT:
The foundational event extraction has already established the factual events.
You are NOT performing event extraction.
You are NOT discovering new facts.
You are NOT validating the source material.

Your job is to synthesize strategic meaning from the supplied factual events.

==================================================
CORE PRINCIPLE
==================================================

The foundational event extraction answers:

"What happened?"

This Strategy Intelligence layer answers:

"What do these developments indicate about the competitor's strategic direction, priorities, capabilities, competitive positioning and market approach?"

Strategy Events are the direct, primary source of intelligence. Network Events are supplementary context.
Only use the supplied Strategy and contextual Network events.

==================================================
CRITICAL EVIDENCE RULES
==================================================

1. ONLY use information contained in the supplied events.

2. DO NOT use outside knowledge about the competitor, industry, competitors, market share, financial performance, strategy or history.

3. DO NOT invent:
   - strategic initiatives
   - business objectives
   - market share
   - revenue
   - investment amounts
   - customer numbers
   - competitors
   - motivations
   - future plans
   - dates
   - geographic expansion not present in the events

4. Strategic interpretation is allowed, but it MUST be logically supported by one or more supplied events.

5. Clearly distinguish:
   - ASSESSMENT = what the supplied events factually demonstrate.
   - INTERPRETATION = what the pattern reasonably indicates strategically.

6. Do not convert a single ordinary operational event into a major strategic conclusion.

7. Prefer recurring patterns across multiple events.

8. A single event may support an insight when it represents a strategically significant development, such as:
   - major infrastructure investment
   - significant acquisition
   - major technology deployment
   - significant geographic expansion
   - major service proposition change
   - clear competitive movement

9. Do not manufacture multiple strategic insights simply to increase output.

10. If the supplied events do not provide sufficient evidence for a meaningful strategic conclusion, return:
{"insights": []}

11. The exact event IDs supplied in the input MUST be used when creating supporting_event_ids.

12. NEVER invent, modify, abbreviate or hallucinate event IDs.

==================================================
WHAT STRATEGY SYNTHESIS SHOULD LOOK FOR
==================================================

Look for PATTERNS across the events.

Examples of useful strategic patterns include:

- repeated network expansion into particular regions
- repeated recruitment of new members
- movement from one network model toward another
- repeated infrastructure investment
- increasing operational capacity
- increasing automation
- movement toward B2C services
- movement toward technology-enabled customer experience
- cross-border expansion
- service differentiation
- geographic concentration
- defensive strengthening of existing territories
- aggressive competitive positioning
- operational efficiency initiatives
- capability building
- combination of network, infrastructure and commercial actions
- changes that collectively indicate a shift in market positioning

Do NOT assume that an observed action automatically proves the competitor's intention.

Use language appropriate to the evidence.

For example:

GOOD:
"The repeated addition of regional members indicates a focus on strengthening network coverage."

TOO STRONG:
"The competitor's strategy is to dominate the UK pallet market."

The second statement is unsupported unless the supplied events explicitly establish it.

==================================================
STRATEGY CATEGORIES
==================================================

Every insight MUST use exactly ONE of the following categories:

1. NETWORK_STRATEGY

Use when events indicate how the competitor is building, defending, restructuring or strengthening its network.

Possible themes:
- Regional Network Expansion
- Network Density
- Member Recruitment
- Territory Strengthening
- Network Consolidation
- Network Capacity Growth
- Network Resilience

2. INFRASTRUCTURE_STRATEGY

Use when events indicate strategic investment in physical infrastructure or operational assets.

Possible themes:
- Hub Expansion
- Capacity Expansion
- Infrastructure Modernisation
- Automation Investment
- Regional Hub Strategy
- Operational Scalability

3. COMMERCIAL_STRATEGY

Use when events indicate how the competitor is developing its customer proposition or commercial model.

Possible themes:
- Service Differentiation
- B2B Growth
- B2C Expansion
- Cross-Border Proposition
- Customer Proposition Development
- Service-Level Differentiation

4. TECHNOLOGY_STRATEGY

Use when events indicate strategic development of technology or digital capabilities.

Possible themes:
- Customer Visibility
- Digital Platform Development
- API Strategy
- Automation
- Digital Customer Experience
- Technology-Enabled Operations

5. GEOGRAPHIC_MARKET_EXPANSION

Use when events demonstrate expansion into new geographic markets, territories or countries.

Possible themes:
- Regional Market Expansion
- UK Geographic Expansion
- European Expansion
- Cross-Border Growth
- Territory Penetration
- New Market Entry

6. COMPETITIVE_POSITIONING

Use when events reveal how the competitor is strengthening, differentiating or defending its position relative to the competitive environment.

Possible themes:
- Competitive Differentiation
- Market Position Strengthening
- Capability-Based Differentiation
- Competitive Expansion
- Territory Defence
- Service-Based Differentiation

IMPORTANT:
Do not mention a rival competitor in the interpretation unless that rival is explicitly present in the supplied Network & Operational events.

7. OPERATIONAL_POSITIONING

Use when events indicate the operational model or capabilities through which the competitor appears to be competing.

Possible themes:
- Capacity-Led Positioning
- Efficiency-Led Positioning
- Service-Led Positioning
- Network-Density Positioning
- Asset-Led Positioning
- Scalable Operations
- Operational Resilience

==================================================
STRATEGIC REASONING RULES
==================================================

Use the following reasoning hierarchy:

EVENTS
   ↓
OBSERVED PATTERN
   ↓
STRATEGIC ASSESSMENT
   ↓
STRATEGIC INTERPRETATION

Do NOT jump directly from:

EVENT → STRATEGIC CONCLUSION

unless the event itself is sufficiently significant.

For example:

Event 1:
New member joins in Yorkshire.

Event 2:
Another member joins in North West England.

Event 3:
Another member expands coverage in another region.

Reasonable synthesis:

"The competitor is repeatedly adding regional members, indicating a strategy focused on increasing geographic network coverage and density."

Do NOT claim:

"The competitor is pursuing a national market-share acquisition strategy."

unless the supplied events explicitly support that conclusion.

==================================================
ASSESSMENT VS INTERPRETATION
==================================================

ASSESSMENT should answer:

"What are the supplied events showing?"

Example:

"Palletforce added multiple regional network members covering areas across Yorkshire, the North West and Bristol."

INTERPRETATION should answer:

"What does this pattern indicate strategically?"

Example:

"The repeated member additions indicate a network-density strategy focused on strengthening regional coverage through additional partner capacity."

The interpretation MUST remain proportional to the evidence.

==================================================
CONFIDENCE
==================================================

Confidence represents how strongly the supplied Network & Operational events support the strategic interpretation.

Use:

0.90 - 1.00
Strong repeated evidence or highly significant strategic development.

0.75 - 0.89
Clear evidence with a strong strategic pattern.

0.60 - 0.74
Reasonable strategic interpretation but limited evidence.

Below 0.60
Generally do not create an insight unless the event is unusually significant.

Confidence is NOT permission to invent facts.

==================================================
INSIGHT CONSOLIDATION
==================================================

Consolidate related events into a single strategic insight where appropriate.

For example, five separate member additions should generally NOT produce five separate strategy insights.

They may support one insight such as:

NETWORK_STRATEGY
"Regional Network Expansion"

supported by all relevant Event IDs.

Create separate insights only when the events demonstrate genuinely different strategic dimensions.

For example:

Network member expansion
+
Hub investment
+
Customer technology deployment

may support separate insights under:

NETWORK_STRATEGY
INFRASTRUCTURE_STRATEGY
TECHNOLOGY_STRATEGY

if the evidence independently supports each conclusion.

==================================================
SUPPORTING EVENT REQUIREMENT
==================================================

Every Strategy Insight MUST contain:

supporting_event_ids

These must be the exact IDs of the Network & Operational events that support the insight.

The backend will validate these IDs.

Do not create an insight with fabricated or unknown Event IDs.

==================================================
OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

The response MUST contain exactly one top-level key:

{
  "insights": [...]
}

If there is insufficient evidence:

{
  "insights": []
}

Each insight MUST contain:

{
  "strategy_category": "...",
  "strategy_theme": "...",
  "assessment": "...",
  "interpretation": "...",
  "confidence": 0.0,
  "supporting_event_ids": ["event-id-1", "event-id-2"]
}

Rules:

- strategy_category MUST be one of the seven allowed categories.
- strategy_theme must be concise and meaningful.
- assessment must remain factual.
- interpretation must provide strategic meaning.
- confidence must be between 0.0 and 1.0.
- supporting_event_ids must contain exact supplied Event IDs.
- No additional JSON fields.
- No markdown.
- No commentary outside the JSON.

==================================================
COMPETITOR
==================================================

Competitor:
{competitor_name}

==================================================
PHASE 1 & 2 EVENTS
==================================================

The following events have already been extracted and validated.
Events are categorized as either DIRECT STRATEGY or CONTEXTUAL NETWORK.

Analyze ONLY these events:

{events_json}

==================================================
FINAL INSTRUCTION
==================================================

Think like a competitive intelligence strategist, not an event extractor.

Do not ask:
"What happened in each event?"

Ask:

"What recurring pattern do these events reveal?"

"What capability is the competitor building?"

"What market position is the competitor strengthening?"

"What strategic direction is becoming visible?"

"What does the evidence support — and what does it NOT support?"

Only return strategic insights that are directly grounded in the supplied evidence.
"""

class AIProvider(ABC):
    @abstractmethod
    def extract_network_events(self, text: str, competitor_name: str) -> List[Dict[str, Any]]:
        """
        Extracts network events from the given text based on standard extraction rules.
        Returns a list of dictionaries matching the extraction schema.
        Returns an empty list on failure or if no events are found.
        """
        pass

    @abstractmethod
    def extract_strategy_events(self, text: str, competitor_name: str) -> List[Dict[str, Any]]:
        """
        Extracts Strategy & Market Positioning events from the given text based on independent strategy extraction rules.
        Returns a list of dictionaries matching the extraction schema.
        Returns an empty list on failure or if no events are found.
        """
        pass

    @abstractmethod
    def synthesize_strategy(self, events_json_str: str, competitor_name: str) -> List[Dict[str, Any]]:
        """
        Synthesizes high-level strategy insights from a JSON string of Network & Operational events.
        Returns a list of dictionaries matching the strategy insight schema.
        Returns an empty list on failure or if no insights are found.
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the name of the provider."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the name of the model being used."""
        pass
