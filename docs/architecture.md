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

```mermaid
graph TD
    %% Define Styles
    classDef frontend fill:#0ea5e9,stroke:#0284c7,stroke-width:2px,color:#fff;
    classDef api fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff;
    classDef services fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff;
    classDef data fill:#6366f1,stroke:#4f46e5,stroke-width:2px,color:#fff;
    classDef external fill:#64748b,stroke:#475569,stroke-width:2px,color:#fff;

    %% External Sources
    subgraph External_Sources["External Sources"]
        Websites["Competitor Websites"]:::external
        News["News & RSS Feeds"]:::external
        LLM["Google GenAI API"]:::external
    end

    %% Data Pipeline (Services)
    subgraph Data_Pipeline["Backend - Data Pipeline"]
        Crawler["Crawler / Collector"]:::services
        Extractor["AI Extractor"]:::services
        StrategyEngine["Strategy Engine"]:::services
        
        Crawler -->|Fetches raw HTML/XML| Websites
        Crawler -->|Fetches Feeds| News
        Crawler -->|Saves Raw Documents| DB_Docs[("Raw Documents")]:::data
        
        DB_Docs -->|Feeds Text to| Extractor
        Extractor <-->|Prompts for Event Extraction| LLM
        Extractor -->|Saves Extracted Events| DB_Events[("Events & Evidence")]:::data
        
        DB_Events -->|Feeds Events to| StrategyEngine
        StrategyEngine <-->|Prompts for Synthesis| LLM
        StrategyEngine -->|Saves Strategic Insights| DB_Insights[("Strategy Insights")]:::data
    end

    %% Database
    subgraph Database["PostgreSQL Database"]
        DB_Docs
        DB_Events
        DB_Insights
        DB_Core[("Core Entities: Competitors, Markets, Topics")]:::data
    end

    %% API Layer
    subgraph API_Layer["Backend - FastAPI"]
        NetworkAPI["Network API Router"]:::api
        StrategyAPI["Strategy API Router"]:::api
        
        DB_Events -.->|Queried by| NetworkAPI
        DB_Insights -.->|Queried by| StrategyAPI
        DB_Core -.->|Queried by| NetworkAPI
        DB_Core -.->|Queried by| StrategyAPI
    end

    %% Frontend Shell
    subgraph Frontend["Frontend - Next.js Shell"]
        UI_Network["Network UI /network"]:::frontend
        UI_Strategy["Strategy UI /strategy"]:::frontend
        
        NetworkAPI -->|JSON Response| UI_Network
        StrategyAPI -->|JSON Response| UI_Strategy
    end
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
