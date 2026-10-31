# Portfolio Analytics Agent

Bounded AI data analyst agent over **synthetic e-commerce demo data**.  
Python FastAPI backend with allowlisted tools; Angular chat UI in `web/`.

Demo data only — not client or employer data.

## Stack (MVP)

| Part | Choice |
| --- | --- |
| Backend | Python 3.12+, FastAPI, Pydantic |
| Agent | Bounded tool-calling loop, allowlisted tools (no raw SQL from the model) |
| Data | Synthetic SQL Server LocalDB database `AnalyticsDemo` |
| LLM | OpenAI-compatible Chat Completions API (provider adapter) |
| Frontend | Angular 19 + TypeScript (`web/`) |

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
- Node.js 20+ and pnpm
- SQL Server LocalDB (`(localdb)\MSSQLLocalDB`)
- ODBC Driver 18 for SQL Server
- An OpenAI API key (or another OpenAI-compatible provider)

### Install API

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

### Run the Angular UI

In a second terminal:

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent\web
pnpm install
pnpm start
```

Open [http://127.0.0.1:4200](http://127.0.0.1:4200). The dev server proxies `/api` to `http://127.0.0.1:8000`.

### Try the agent via API

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/chat" `
  -ContentType "application/json" `
  -Body '{"message":"What were our total sales last month?"}'
```

Or use Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) → `POST /api/chat`.

Example chat prompts:

- “What were our total sales last month?”
- “Which product category generated the most revenue last month?”
- “How did sales change compared with the previous month?”
- “Which products have the lowest sales last month?”

### Tests

```powershell
pytest
```

```powershell
cd web
pnpm build
```

## Project layout

```
app/                   # FastAPI + agent + tools
web/                   # Angular chat UI
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
