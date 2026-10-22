# Rwanda Sector Data Aggregator

An automated data collection and processing platform designed to improve access to structured sector-level information in Rwanda.

The platform combines web scraping, data validation, deduplication, change detection, and scheduled collection to transform publicly available information into structured records accessible through a REST API.

## Project Overview

Publicly available information is often distributed across multiple websites and published in inconsistent formats. This project explores how automated data engineering pipelines can collect, standardize, and maintain sector records with minimal manual intervention.

The system uses TypeScript for data extraction, Python for backend processing, FastAPI for API access, and SQLite for persistent storage.

## Technology Stack

| Layer | Technologies |
|---|---|
| Data extraction | TypeScript, Node.js, Cheerio, Playwright |
| Data processing | Data sanitization, SHA-256 hashing |
| Backend | Python, FastAPI, Pydantic |
| Database | SQLite, SQLAlchemy |
| Scheduling | APScheduler |
| Testing | Pytest, Jest |
| Frontend | Next.js (integration pending) |

## System Architecture

```text
Public Data Sources
        |
        v
TypeScript Collection Pipeline
        |
        +-- Cheerio: Static HTML
        |
        +-- Playwright: JavaScript-rendered HTML
        |
        v
Record Extraction
        |
        v
Sanitization and Validation
        |
        v
SHA-256 Fingerprinting
        |
        v
Deduplication
        |
        v
FastAPI Ingestion Endpoint
        |
        v
SQLAlchemy + SQLite
        |
        +-- Sector Records
        |
        +-- Change History
        |
        +-- Collection Logs
        |
        v
REST API
```

## Features

### Data Collection

- Extracts structured records from supported HTML sources using Cheerio.
- Uses Playwright to render JavaScript-driven websites before extraction.
- Supports configurable source-specific rendering methods.
- Includes retry handling for temporary HTTP failures.

### Data Processing

- Sanitizes extracted text.
- Generates deterministic SHA-256 fingerprints.
- Detects duplicate and changed records.
- Validates incoming records before storage.

### Backend and Database

- Provides REST endpoints for record ingestion and retrieval.
- Stores records in SQLite using SQLAlchemy.
- Maintains fingerprint-based change history.
- Protects ingestion using API-key authentication.

### Automated Collection

- Uses APScheduler for interval-based collection.
- Supports configurable public data sources.
- Records collection status, timestamps, counts, and errors.
- Exposes collection monitoring endpoints.
- Keeps automatic scheduling disabled by default until sources are validated.

## Project Structure

```text
sector-rwanda-pipeline/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── database.py
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── pipeline/
│   ├── src/
│   │   ├── index.ts
│   │   ├── scraper.ts
│   │   ├── playwright_scraper.ts
│   │   └── processor.ts
│   ├── fixtures/
│   ├── tests/
│   └── package.json
├── frontend/
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js and npm
- uv
- Chromium for Playwright

### 1. Clone the repository

```bash
git clone <repository-url>
cd sector-rwanda-pipeline
```

### 2. Set up the backend

```bash
cd backend
uv venv
uv pip install --python .venv/bin/python -r requirements.txt
```

### 3. Start FastAPI

```bash
export INGESTION_API_KEY="replace-with-a-secure-key"
export ENABLE_COLLECTION_SCHEDULER="false"

.venv/bin/python -m uvicorn app.main:app --reload
```

The API is available at:

- `http://127.0.0.1:8000`
- Swagger documentation: `http://127.0.0.1:8000/docs`

### 4. Set up the scraping pipeline

In another terminal:

```bash
cd pipeline
npm install
npx playwright install chromium
```

### 5. Run a local fixture

```bash
npm run run -- --fixture fixtures/demo.html
```

To ingest the fixture into the running backend:

```bash
export INGESTION_API_KEY="replace-with-a-secure-key"
npm run run -- --fixture fixtures/demo.html --ingest
```

Use the same API key in both terminals.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API health |
| GET | `/records` | Retrieve sector records |
| GET | `/records/{record_id}` | Retrieve a specific record |
| GET | `/records/{record_id}/changes` | View record change history |
| POST | `/records/ingest` | Ingest processed records |
| GET | `/collections/sources` | List configured collection sources |
| GET | `/collections/runs` | Retrieve collection execution history |
| POST | `/collections/run` | Trigger collection manually |

Ingestion and collection-management endpoints require an `X-API-Key` header.

## Source Configuration

Collection sources are configured through a JSON file referenced by `COLLECTION_SOURCES_FILE`.

Each source defines a name, URL, and renderer.

Example configuration format:

```json
[
  {
    "name": "Approved Static Source",
    "url": "https://example.org/static",
    "renderer": "cheerio"
  },
  {
    "name": "Approved Dynamic Source",
    "url": "https://example.org/dynamic",
    "renderer": "playwright"
  }
]
```

These URLs illustrate the configuration format only. They are not production data sources.

Supported renderers are `cheerio` and `playwright`. The default renderer is `cheerio`.

Actual sources must be verified for access permissions, extraction compatibility, and data quality before scheduled collection is enabled.

## Automated Scheduling

The backend supports interval-based scheduling using APScheduler.

Configuration variables:

| Variable | Purpose |
|---|---|
| `INGESTION_API_KEY` | Protects ingestion and collection endpoints |
| `API_URL` | Backend URL used by the scraping pipeline |
| `COLLECTION_SOURCES_FILE` | Path to the source configuration file |
| `ENABLE_COLLECTION_SCHEDULER` | Enables or disables scheduled collection |
| `COLLECTION_INTERVAL_HOURS` | Interval between collection runs |
| `DATABASE_URL` | Database connection string |

Scheduling is disabled by default.

In deployment, the scheduler should run in one designated process to prevent duplicate executions.

## Testing

### Backend

```bash
cd backend
.venv/bin/python -m pytest -v
```

### TypeScript

```bash
cd pipeline
npm run typecheck
npm test
```

Tests cover record validation, ingestion, deduplication, change tracking, API authentication, and source configuration.

Additional scheduler execution, Playwright browser, and network-security tests are planned.

## Current Limitations

- The HTML extractor expects a specific record structure and requires source-specific adaptation.
- Playwright renders JavaScript pages but does not automatically extract arbitrary website layouts.
- CSV, JSON, and PDF ingestion are not yet implemented.
- Real public-data sources have not yet been verified for production collection.
- Scheduled collection should remain disabled until outbound network safeguards and execution tests are completed.
- SQLite is suitable for local development; a production deployment may require a more scalable database.
- The frontend has not yet been integrated with the API.

## Roadmap

- Validate and integrate real Rwanda public-data sources.
- Add source-specific extraction configurations.
- Support CSV, JSON, and PDF datasets.
- Expand automated collection and security tests.
- Implement frontend analytics and search.
- Add deployment configuration and monitoring.

## Project Status

**Active development**

The scraping pipeline, FastAPI ingestion, SQLite storage, change tracking, and initial automated collection components have been implemented. Production source integration, scheduler hardening, and frontend integration remain in progress.
