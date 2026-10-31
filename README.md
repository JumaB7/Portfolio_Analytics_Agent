# Portfolio Analytics Agent

Bounded AI data analyst agent over **synthetic e-commerce demo data**.  
Python FastAPI backend with allowlisted tools; Angular chat UI in `web/`.

Demo data only — not client or employer data.

**Full history of how we built this:** [docs/PROJECT_WALKTHROUGH.md](docs/PROJECT_WALKTHROUGH.md)  
**Eval catalog:** [docs/EVAL.md](docs/EVAL.md)

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

## Efficiency defaults

| Setting | Default | Effect |
| --- | --- | --- |
| `AGENT_RULE_ROUTER` | `true` | Common demo prompts answered with **0 LLM calls** |
| `AGENT_TEMPLATE_ANSWERS` | `true` | After a tool runs, Python writes the answer (**no second LLM call**) |

Sample prompts in the UI typically use the rule router (free). Ambiguous wording still uses the LLM once to choose a tool, then a template for the final text.

## Allowlisted tools

| Tool | Purpose |
| --- | --- |
| `get_sales_summary` | Total revenue / orders / units for a date range |
| `get_revenue_by_category` | Category ranking by revenue |
| `compare_sales_periods` | Period vs period (e.g. month-over-month) |
| `get_product_performance` | Highest or lowest products by revenue |

## Requirements

- Python 3.12+
- Node.js 20+ and pnpm
- SQL Server LocalDB (`(localdb)\MSSQLLocalDB`)
- ODBC Driver 18 for SQL Server
- An OpenAI API key (or another OpenAI-compatible provider) for chat only

## First-time setup

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
copy .env.example .env
```

### API keys (`.env`)

Edit `.env` (never commit this file):

```env
LLM_API_KEY=sk-your-real-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

Notes:

- The key stays on the **server** only. The Angular app never sees it.
- Tool endpoints and most tests work **without** a key.
- `POST /api/chat` needs a valid key and provider credits.
- After any `.env` change, **restart the API** (see below).

### Seed demo data

```powershell
python -m scripts.init_demo_db
```

Creates LocalDB database `AnalyticsDemo` and loads synthetic e-commerce rows.

### Install the Angular app (once)

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent\web
pnpm install
```

## Startup (every day)

Use **two terminals**.

### Terminal 1 — API

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

Leave this running. Useful URLs:

- Health: http://127.0.0.1:8000/health  
- Swagger: http://127.0.0.1:8000/docs  
- Chat API: `POST http://127.0.0.1:8000/api/chat`

### Terminal 2 — Angular UI

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent\web
pnpm start
```

Open http://127.0.0.1:4200  
The UI proxies `/api` to `http://127.0.0.1:8000`.

## Restart the API

Do this after changing `.env` (API key, model, base URL), or if chat errors look stale.

1. Focus the uvicorn terminal.
2. Stop it with `Ctrl+C`.
3. Start again:

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

`--reload` watches **Python code** changes. It does **not** reliably reload environment variables from `.env`, so a full restart is required after secret/config edits.

## Restart the Angular UI

1. Focus the `pnpm start` terminal.
2. `Ctrl+C`.
3. Start again:

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent\web
pnpm start
```

If the UI fails with missing `main.ts` / `tsconfig` resolve errors while files actually exist:

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent\web
# stop pnpm start first
Remove-Item .angular -Recurse -Force -ErrorAction SilentlyContinue
pnpm start
```

## Try it

### In the browser UI

Open http://127.0.0.1:4200 and use a sample prompt, or ask:

- “What were our total sales last month?”
- “Which product category generated the most revenue last month?”
- “How did sales change compared with the previous month?”
- “Which products have the lowest sales last month?”

### Via PowerShell (API only)

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/chat" `
  -ContentType "application/json" `
  -Body '{"message":"What were our total sales last month?"}'
```

### Tool check without an LLM

http://127.0.0.1:8000/api/tools/sales-summary?start_date=2026-09-01&end_date=2026-09-30

## Tests

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent
.\.venv\Scripts\Activate.ps1
pytest
```

```powershell
cd web
pnpm build
```

## Project layout

```
app/                   # FastAPI + agent + tools
app/eval/              # Fixed eval prompt catalog
web/                   # Angular chat UI
docs/PROJECT_WALKTHROUGH.md
docs/EVAL.md
scripts/init_demo_db.py
tests/
```

## Security note

The model never generates or executes raw SQL. It may only call allowlisted tools. Tools validate inputs and run fixed read-only queries. Keep `LLM_API_KEY` in `.env` only — never in the Angular app or git.

## Branches

| Branch | Role |
| --- | --- |
| `develop` | Day-to-day work |
| `release` | Staging |
| `main` | Production |
