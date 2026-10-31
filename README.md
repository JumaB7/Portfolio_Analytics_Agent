# Portfolio Analytics Agent

Bounded AI data analyst agent over **synthetic e-commerce demo data**.  
Python FastAPI backend with allowlisted tools; Angular UI comes later.

Demo data only — not client or employer data.

## Stack (MVP)

| Part | Choice |
| --- | --- |
| Backend | Python 3.12+, FastAPI, Pydantic |
| Agent | Bounded tool-calling loop, allowlisted tools (no raw SQL from the model) |
| Data | Synthetic SQL Server LocalDB database `AnalyticsDemo` |
| LLM | OpenAI-compatible Chat Completions API (provider adapter) |
| Frontend | Angular + TypeScript (after the API tool loop works) |

## First milestone

One question → one tool call → grounded answer from demo data.

## Allowlisted tools

| Tool | Purpose |
| --- | --- |
| `get_sales_summary` | Total revenue / orders / units for a date range |
| `get_revenue_by_category` | Category ranking by revenue |
| `compare_sales_periods` | Period vs period (e.g. month-over-month) |
| `get_product_performance` | Highest or lowest products by revenue |

## Local setup

### Requirements

- Python 3.12+
- SQL Server LocalDB (`(localdb)\MSSQLLocalDB`)
- ODBC Driver 18 for SQL Server
- An OpenAI API key (or another OpenAI-compatible provider)

### Install

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
copy .env.example .env
```

Edit `.env` and set `LLM_API_KEY`.

### Create and seed demo data

```powershell
python -m scripts.init_demo_db
```

### Run the API

```powershell
uvicorn app.main:app --reload --port 8000
```

### Try the agent (chat)

With the server running:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/chat" `
  -ContentType "application/json" `
  -Body '{"message":"What were our total sales last month?"}'
```

Or use Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) → `POST /api/chat`.

Other useful URLs:

- Health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Sales summary: `/api/tools/sales-summary?start_date=2026-09-01&end_date=2026-09-30`
- Categories: `/api/tools/revenue-by-category?start_date=2026-09-01&end_date=2026-09-30`
- MoM compare: `/api/tools/compare-sales-periods?current_start_date=2026-09-01&current_end_date=2026-09-30&previous_start_date=2026-08-01&previous_end_date=2026-08-31`
- Products: `/api/tools/product-performance?start_date=2026-09-01&end_date=2026-09-30&sort=lowest`

Example chat prompts:

- “What were our total sales last month?”
- “Which product category generated the most revenue last month?”
- “How did sales change compared with the previous month?”
- “Which products have the lowest sales last month?”

### Tests

```powershell
pytest
```

## Project layout

```
app/
  main.py
  config.py
  api/chat.py          # POST /api/chat
  api/tools.py         # direct tool HTTP endpoints
  agent/               # prompts, provider adapter, orchestrator
  db/                  # SQLAlchemy models, session, seed
  services/analytics.py
  tools/               # allowlisted tools + registry
  schemas/
scripts/init_demo_db.py
tests/
```

## Security note

The model never generates or executes raw SQL. It may only call allowlisted tools such as `get_sales_summary`. Tools validate inputs and run fixed read-only queries. Keep `LLM_API_KEY` in `.env` only.

## Branches

| Branch | Role |
| --- | --- |
| `develop` | Day-to-day work |
| `release` | Staging |
| `main` | Production |
