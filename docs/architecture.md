# Run strategy collection

set PYTHONPATH=. && .\venv\Scripts\python.exe scripts/run_strategy_collection.py



# Palletways Competitive Intelligence Platform - Architecture

## Overview

The Palletways Competitive Intelligence Platform is an AI-powered prototype designed to monitor competitive developments in the logistics market.
This document outlines the foundational structure and the core components built to date. The architecture uses a monolithic approach with a Python FastAPI backend and a Next.js (React) frontend shell. PostgreSQL is used as the primary data store.

### Technology Stack
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic, Pytest.
- **Frontend:** Next.js, React, TailwindCSS, TypeScript.
- **Database:** PostgreSQL (local).
- **AI/LLM:** Google GenAI (Gemini) for data extraction and synthesis.

---

## End-to-End Architecture & Workflow

```text
                              PALLETWAYS CI PLATFORM

                                       │

             ┌─────────────────────────┴─────────────────────────┐

             │                                                   │

             ▼                                                   ▼

      EXTERNAL INTELLIGENCE                              INTERNAL / USER INPUT

             │                                                   │

             │                                      ┌────────────┴───────────┐

             │                                      │                        │

             │                                      ▼                        ▼

             │                              User Questions            Job / Hiring Data

             │                              Documents                  User Feedback

             │                              Search Queries             Analyst Input

             │

             ▼

┌──────────────────────────────────────────────────────────────────────────────┐

│                         COMPETITOR SOURCE LAYER                              │

│                                                                              │

│  Competitor Websites      Newsrooms         Press Releases                  │

│  Investor Relations       Annual Reports    RSS / Atom                      │

│  Sitemaps                 Blogs             Careers / Jobs                   │

│  Regulatory Sources       Industry Sources  Reports / PDFs                  │

│  APIs / Feeds (future)    Social / Reviews (future)                         │

└──────────────────────────────────┬───────────────────────────────────────────┘

                                   │

                                   ▼

┌──────────────────────────────────────────────────────────────────────────────┐

│                         DISCOVERY ENGINE                                     │

│                                                                              │

│  Topic-Aware Discovery                                                       │

│                                                                              │

│  ├── URL scoring                                                             │

│  ├── Anchor-text scoring                                                     │

│  ├── Referrer-context scoring                                                │

│  ├── Sitemap discovery                                                       │

│  ├── RSS / Atom discovery                                                    │

│  ├── Recency scoring                                                         │

│  ├── Topic vocabulary                                                        │

│  ├── Domain restriction                                                      │

│  └── Priority queue                                                          │

│                                                                              │

│  Each intelligence topic can have its own discovery vocabulary.             │

└──────────────────────────────────┬───────────────────────────────────────────┘

                                   │

                                   ▼

┌──────────────────────────────────────────────────────────────────────────────┐

│                           TARGETED CRAWLER                                   │

│                                                                              │

│  robots.txt validation                                                      │

│  Domain restriction                                                         │

│  Crawl depth control                                                        │

│  Page limits                                                                │

│  Priority queue                                                             │

│  URL normalization                                                           │

│  Duplicate URL prevention                                                    │

│  HTTP failure handling                                                       │

│  Retry / backoff                                                             │

│  Change detection                                                           │

└──────────────────────────────────┬───────────────────────────────────────────┘

                                   │

                                   ▼

┌──────────────────────────────────────────────────────────────────────────────┐

│                              COLLECTOR                                       │

│                                                                              │

│  httpx                                                                      │

│  BeautifulSoup                                                              │

│  Readability / boilerplate removal                                          │

│  Main-content extraction                                                    │

│  Title extraction                                                           │

│  Date extraction                                                            │

│  Metadata extraction                                                        │

│  Content hashing                                                            │

│  Deduplication                                                              │

│  Encoding / null-byte sanitization                                          │

└──────────────────────────────────┬───────────────────────────────────────────┘

                                   │

                                   ▼

┌──────────────────────────────────────────────────────────────────────────────┐

│                           DOCUMENT STORE                                     │

│                              PostgreSQL                                      │

│                                                                              │

│  Document                                                                   │

│  ├── URL                                                                     │

│  ├── Source                                                                  │

│  ├── Competitor                                                              │

│  ├── Raw provenance                                                          │

│  ├── Clean content                                                           │

│  ├── Content hash                                                            │

│  ├── Published date                                                          │

│  ├── Updated date                                                            │

│  └── Collected date                                                          │

│                                                                              │

│  Evidence-first provenance foundation                                       │

└──────────────────────────────────┬───────────────────────────────────────────┘

                                   │

                ┌──────────────────┼────────────────────┐

                │                  │                    │

                ▼                  ▼                    ▼

┌──────────────────────┐ ┌──────────────────────┐ ┌────────────────────────┐

│ NETWORK & GEOGRAPHY  │ │ STRATEGY & MARKET    │ │ FUTURE INTELLIGENCE    │

│      LAYER           │ │ POSITIONING LAYER    │ │       TOPICS            │

│                      │ │                      │ │                        │

│ Existing Phase 1    │ │ Existing Phase 2    │ │ Technology             │

│                      │ │                      │ │ Pricing                │

│ Network Expansion   │ │ Direct Strategy      │ │ Customers              │

│ Infrastructure      │ │ Events               │ │ Financial              │

│ Contraction         │ │                      │ │ Sustainability         │

│ Commercial          │ │ Strategy Synthesis   │ │ Leadership             │

│ Innovation           │ │                      │ │ Risk & Regulation      │

└──────────┬───────────┘ └──────────┬───────────┘ └───────────┬────────────┘

           │                        │                         │

           ▼                        ▼                         ▼

      ┌──────────┐             ┌──────────┐              ┌──────────┐

      │ Evidence │             │ Evidence │              │ Evidence │

      └────┬─────┘             └────┬─────┘              └────┬─────┘

           │                        │                         │

           ▼                        ▼                         ▼

      Network Events          Strategy Events             Topic Events

           │                        │                         │

           └────────────────────────┼─────────────────────────┘

                                    │

                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐

│                         INTELLIGENCE EVENT STORE                              │

│                                                                              │

│  Event                                                                       │

│  ├── event_type                                                              │

│  ├── event_subtype                                                           │

│  ├── event_metadata JSONB                                                    │

│  ├── competitor_id                                                           │

│  ├── evidence_id                                                             │

│  ├── event_date                                                              │

│  ├── impact                                                                   │

│  ├── threat_level                                                            │

│  └── recommended_watch                                                       │

│                                                                              │

│  Evidence → Event lineage preserved                                          │

└──────────────────────────────────┬───────────────────────────────────────────┘

                                   │

             ┌─────────────────────┼────────────────────────┐

             │                     │                        │

             ▼                     ▼                        ▼

┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────────┐

│ SIGNAL ENGINE        │ │ PATTERN ENGINE       │ │ TREND ENGINE             │

│                      │ │                      │ │                          │

│ Event significance   │ │ Multi-event patterns │ │ Time-series trends      │

│ Competitor signals   │ │ Repeated behaviour   │ │ Strategic patterns   │

│ Alerts               │ │ Strategic patterns   │ │ Activity velocity       │

│ Risk indicators      │ │ Correlations         │ │ Emerging themes         │

└──────────┬───────────┘ └──────────┬───────────┘ └────────────┬─────────────┘

           │                        │                           │

           └────────────────────────┼───────────────────────────┘

                                    │

                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐

│                      STRATEGY SYNTHESIS ENGINE                               │

│                                                                              │

│  Phase 2 Strategy & Market Positioning                                      │

│                                                                              │

│  Inputs:                                                                     │

│  ├── Direct Strategy Events                                                  │

│  ├── Network & Geography Events                                              │

│  ├── Signals                                                                 │

│  ├── Patterns                                                                │

│  └── Trends                                                                  │

│                                                                              │

│  Outputs:                                                                    │

│  ├── Assessment                                                               │

│  ├── Interpretation                                                          │

│  ├── Impact                                                                   │

│  ├── Threat Level                                                             │

│  └── Recommended Watch                                                       │

└──────────────────────────────────┬───────────────────────────────────────────┘

                                   │

                                   ▼

┌──────────────────────────────────────────────────────────────────────────────┐

│                         KNOWLEDGE LAYER                                      │

│                                                                              │

│                       ┌─────────────────────┐                                │

│                       │ KNOWLEDGE INGESTION │                                │

│                       └──────────┬──────────┘                                │

│                                  │                                           │

│          ┌───────────────────────┼────────────────────────┐                  │

│          │                       │                        │                  │

│          ▼                       ▼                        ▼                  │

│     Documents                Events                   Evidence               │

│     Reports                 Signals                  Insights               │

│     PDFs                    Strategy                 Jobs                   │

│          │                       │                        │                  │

│          └───────────────────────┼────────────────────────┘                  │

│                                  ▼                                           │

│                         Chunking / Cleaning                                  │

│                                  │                                           │

│                                  ▼                                           │

│                         Embedding Generation                                 │

│                                  │                                           │

│                                  ▼                                           │

│                       Vector / Semantic Index                                │

│                                  │                                           │

│                         ┌────────┴────────┐                                  │

│                         │                 │                                  │

│                         ▼                 ▼                                  │

│                   Semantic Search      Metadata                             │

│                                      Filtering                              │

└───────────────────────────────┬──────────────────────────────────────────────┘

                                │

                                ▼

┌──────────────────────────────────────────────────────────────────────────────┐

│                         RAG INTELLIGENCE LAYER                               │

│                                                                              │

│                         Query Processing                                     │

│                              │                                               │

│                              ▼                                               │

│                     Query Understanding                                      │

│                              │                                               │

│               ┌──────────────┼──────────────┐                               │

│               │              │              │                                │

│               ▼              ▼              ▼                                │

│          Keyword Search   Semantic Search  Metadata Filter                   │

│               │              │              │                                │

│               └──────────────┼──────────────┘                               │

│                              ▼                                               │

│                         Hybrid Retrieval                                     │

│                              │                                               │

│                              ▼                                               │

│                           Re-ranking                                         │

│                              │                                               │

│                              ▼                                               │

│                       Evidence Assembly                                      │

│                              │                                               │

│                              ▼                                               │

│                        Context Builder                                       │

│                              │                                               │

│                              ▼                                               │

│                          Groq LLM                                             │

│                              │                                               │

│                              ▼                                               │

│                     Grounded AI Response                                     │

│                                                                              │

│  Rule: RAG answers must be grounded in retrieved evidence.                  │

└──────────────────────────────────┬───────────────────────────────────────────┘

                                   │

                                   ▼

┌──────────────────────────────────────────────────────────────────────────────┐

│                              ASK AI                                          │

│                                                                              │

│  User Question                                                              │

│       │                                                                      │

│       ▼                                                                      │

│  Intent Detection                                                            │

│       │                                                                      │

│       ├── Competitor Question                                                │

│       ├── Network Question                                                   │

│       ├── Strategy Question                                                  │

│       ├── Pricing Question                                                   │

│       ├── Technology Question                                                │

│       ├── Customer Question                                                  │

│       ├── Trend Question                                                     │

│       ├── Comparison Question                                                │

│       └── Executive Question                                                 │

│       │                                                                      │

│       ▼                                                                      │

│  RAG Retrieval                                                               │

│       │                                                                      │

│       ▼                                                                      │

│  Evidence Validation                                                         │

│       │                                                                      │

│       ▼                                                                      │

│  Groq Reasoning                                                              │

│       │                                                                      │

│       ▼                                                                      │

│  Answer + Sources + Confidence + Evidence                                    │

└──────────────────────────────────┬───────────────────────────────────────────┘

                                   │

             ┌─────────────────────┼──────────────────────────┐

             │                     │                          │

             ▼                     ▼                          ▼

┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────────┐

│ JOB INTELLIGENCE     │ │ ML / ANALYTICS       │ │ COMPETITOR PROFILING     │

│                      │ │ ENGINE               │ │                          │

│ Careers pages        │ │                      │ │ Competitor profiles      │

│ Job postings         │ │ Classification       │ │ Capability maps          │

│ Hiring velocity      │ │ Clustering           │ │ Strategy profiles        │

│ New roles            │ │ Anomaly detection    │ │ Network footprint        │

│ Skill demand         │ │ Trend prediction     │ │ Technology profile       │

│ Leadership hiring    │ │ Similarity           │ │ Commercial profile       │

│ Technology hiring    │ │ Topic modelling      │ │                          │

└──────────┬───────────┘ └──────────┬───────────┘ └────────────┬─────────────┘

           │                        │                           │

           └────────────────────────┼───────────────────────────┘

                                    │

                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐

│                         ML INTELLIGENCE LAYER                                │

│                                                                              │

│  Training Data                                                               │

│       ▲                                                                      │

│       │                                                                      │

│  Historical Events + Documents + Evidence + Analyst Labels                  │

│       │                                                                      │

│       ▼                                                                      │

│  Feature Engineering                                                        │

│       │                                                                      │

│       ▼                                                                      │

│  Model Training                                                             │

│       │                                                                      │

│       ├── Event Classification                                               │

│       ├── Topic Classification                                               │

│       ├── Competitor Clustering                                              │

│       ├── Anomaly Detection                                                  │

│       ├── Trend Detection                                                    │

│       └── Similarity / Ranking                                               │

│       │                                                                      │

│       ▼                                                                      │

│  Model Evaluation                                                            │

│       │                                                                      │

│       ▼                                                                      │

│  Model Registry / Versioning                                                 │

│       │                                                                      │

│       ▼                                                                      │

│  Production Inference                                                        │

│                                                                              │

│  IMPORTANT: ML outputs augment intelligence; they do not replace            │

│  evidence-backed extraction.                                                │

└──────────────────────────────────┬───────────────────────────────────────────┘

                                   │

                                   ▼

┌──────────────────────────────────────────────────────────────────────────────┐

│                       EXECUTIVE INTELLIGENCE LAYER                           │

│                                                                              │

│                         EXECUTIVE COCKPIT                                    │

│                                                                              │

│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐                    │

│  │ Competitor     │ │ Strategic      │ │ Network        │                    │

│  │ Overview       │ │ Moves          │ │ Changes        │                    │

│  └────────────────┘ └────────────────┘ └────────────────┘                    │

│                                                                              │

│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐                    │

│  │ Threat Radar   │ │ Market Trends  │ │ Emerging      │                    │

│  │                │ │                │ │ Risks          │                    │

│  └────────────────┘ └────────────────┘ └────────────────┘                    │

│                                                                              │

│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐                    │

│  │ Opportunities  │ │ Recommended    │ │ Executive      │                    │

│  │                │ │ Watch          │ │ Briefing       │                    │

│  └────────────────┘ └────────────────┘ └────────────────┘                    │

└──────────────────────────────────┬───────────────────────────────────────────┘

                                   │

                                   ▼

┌──────────────────────────────────────────────────────────────────────────────┐

│                         ALERTS & BRIEFINGS                                   │

│                                                                              │

│  High-threat event                                                          │

│  Major competitor move                                                      │

│  Network member loss                                                        │

│  New hub / infrastructure investment                                        │

│  Strategic acquisition                                                      │

│  Major technology launch                                                    │

│  Leadership change                                                          │

│  Significant hiring trend                                                   │

│  Emerging market trend                                                      │

│                                                                              │

│  ├── Real-time / event alerts                                               │

│  ├── Daily intelligence digest                                              │

│  ├── Weekly competitor briefing                                             │

│  └── Executive strategic briefing                                           │

└──────────────────────────────────┬───────────────────────────────────────────┘

                                   │

                                   ▼

┌──────────────────────────────────────────────────────────────────────────────┐

│                          NEXT.JS FRONTEND                                    │

│                                                                              │

│  Dashboard                                                                   │

│  │                                                                           │

│  ├── Executive Competitive Cockpit                                          │

│  ├── Network & Geography Intelligence                                       │

│  ├── Strategy & Market Positioning                                           │

│  ├── Services & Proposition                                                 │

│  ├── Pricing & Commercial                                                    │

│  ├── Customers & Verticals                                                   │

│  ├── Technology & Automation                                                 │

│  ├── M&A & Partnerships                                                      │

│  ├── Financial & Investment                                                  │

│  ├── Sustainability & Fleet                                                  │

│  ├── Leadership & Talent                                                     │

│  ├── Brand & Customer Sentiment                                              │

│  ├── Risk & Regulation                                                       │

│  ├── Job Intelligence                                                        │

│  ├── Competitor Profiles                                                      │

│  ├── Market Trends                                                            │

│  ├── Alerts                                                                   │

│  └── Ask AI                                                                  │

│                                                                              │

└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Components and Workflows

Here is a breakdown of what each major code component is for and how it works based on what has been built so far:

### 1. Data Collection (`backend/app/services/crawler.py` & `collector.py`)
- **Purpose:** To discover and fetch intelligence from monitored sources (e.g., competitor websites, news feeds).
- **How it works:** 
  - The `NetworkCrawler` implements a focused crawling strategy. It starts at a seed URL and explores links up to a configured depth.
  - It uses a deterministic scoring engine to prioritize URLs. Scores are increased based on URL paths, anchor text containing topic vocabulary (e.g., "depot", "network"), referrer context (e.g., linked from a "news" page), and document recency.
  - It supports discovering content via HTML links, XML Sitemaps, and RSS feeds.
  - Documents are fetched and deduplicated based on content hashes.

### 2. AI Extraction (`backend/app/services/extractor.py`)
- **Purpose:** To convert unstructured text documents into structured competitive `Events`.
- **How it works:**
  - Uses heuristic pre-filtering to skip documents that lack strategic keywords (like 'partner', 'hub', 'depot').
  - Sends the relevant text to a Google GenAI model to extract structured events.
  - Extracted events are mapped to allowed types (e.g., `NETWORK_FOOTPRINT`, `HUBS_AND_DEPOTS`).
  - Creates an `Evidence` record linking the extracted event directly to the source text for data lineage, then saves the `Event` to the database.

### 3. Strategy Synthesis (`backend/app/services/strategy_engine.py`)
- **Purpose:** To analyze individual extracted events and synthesize them into higher-level strategic insights.
- **How it works:**
  - Retrieves all relevant `Events` (e.g., network expansion events) for a specific competitor within a timeframe.
  - Compiles these events into a lean JSON payload and sends it to the AI provider.
  - The AI model synthesizes the events into `StrategyInsight` records, categorized under themes like `NETWORK_STRATEGY` or `COMMERCIAL_STRATEGY`.
  - Links the generated insights back to the original supporting `Events` via `StrategyInsightEvent` for full traceability.

### 4. API Layer (`backend/app/api/`)
- **Purpose:** To expose the data to the frontend application.
- **How it works:** Contains FastAPI routers (e.g., `network.py`, `strategy.py`) that query the database and serve JSON responses to the frontend.

### 5. Frontend Shell (`frontend/src/app/`)
- **Purpose:** To provide a user interface for analysts to view the collected intelligence.
- **How it works:** Built with Next.js App Router. It contains specific views for different intelligence modules:
  - `/network`: Visualizes the competitor's network footprint and recent expansion events.
  - `/strategy`: Displays the synthesized strategic insights and the underlying evidence.

---

## Database Entities & Relationships

The database is built strictly relationally using UUID primary keys.

1. **Market**: Represents a geographic or economic region (e.g., United Kingdom).
2. **Competitor**: A target company monitored by the system.
3. **CompetitorAlias**: Alternative names or references for a given competitor.
4. **CompetitorMarket**: Join table linking a Competitor to a Market.
5. **IntelligenceTopic**: Represents the core intelligence themes.
6. **Source**: A monitored origin of information (e.g., website, article, API). 
7. **Document**: A piece of collected content from a source. Uses `content_hash` for deduplication.
8. **Evidence**: Specific text excerpt or claim from a Document that supports an Event.
9. **Event**: A structured competitive development extracted from Evidence. Contains the actual real-world `event_date`.
10. **Signal**: Broader patterns derived from multiple events.
11. **StrategyInsight**: AI-synthesized strategic interpretations based on multiple events.
12. **CollectionRun**: Tracks metadata about collection job executions.

### Data Lineage
The core relationships preserve strict evidence lineage:
`Source → Document → Evidence → Event → StrategyInsight`

This ensures that every Insight or Event can be traced back to its raw Document and the original Source, proving provenance.

---

## Date Semantics & Historical Data

One of the most critical aspects of the data model is the strict separation of timestamps. The system does not invent dates and does not silently substitute one date for another.

### Document Date Fields
- **`source_published_at`**: When the *source* states the information was originally published. (Nullable)
- **`source_updated_at`**: When the *source* states the information was last updated. (Nullable)
- **`collected_at`**: When *our system* fetched or observed the information. (Non-nullable)

### Event Date Field
- **`event_date`**: The date the real-world competitive event actually occurred, according to the evidence. (Nullable)

### Historical Data Preservation
Historical changes are preserved rather than overwritten. Deduplication on the `Document` table uses a unique constraint on `(source_id, content_hash)`. If a single URL's contents change over time, a *new* Document record is created rather than overwriting the old one.

---

## Local Development Setup

### Backend (Python)
1. **Prerequisites:** Python 3.11+, PostgreSQL installed and running locally.
2. **Environment Setup:** 
   ```bash
   cd backend
   python -m venv venv
   source venv/Scripts/activate # Windows PowerShell
   pip install -r requirements.txt
   ```
3. **Database Setup:** 
   Create a `.env` file from `.env.example` containing:
   ```ini
   DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/palletways_ci
   TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/palletways_ci_test
   ```
4. **Migrations & Seeding:** 
   ```bash
   alembic upgrade head
   python scripts/seed.py
   ```
5. **Running Pipelines (Examples):**
   ```bash
   # Run strategy collection
   set PYTHONPATH=. && .\venv\Scripts\python.exe scripts/run_strategy_collection.py
   ```
6. **Running the API:**
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend (Next.js)
1. **Prerequisites:** Node.js (LTS).
2. **Installation:**
   ```bash
   cd frontend
   npm install
   ```
3. **Running the App:**
   ```bash
   npm run dev
   ```
   Access `http://localhost:3000`.
