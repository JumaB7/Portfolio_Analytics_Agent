# Portfolio Analytics Agent — full project walkthrough

This document records **how this project was built**, the decisions behind it, the code steps in order, how API keys work, and how to run or restart everything locally.

Demo data only — never client or employer data.

---

## 1. Goal

Build a **portfolio-grade, bounded AI data analyst agent**:

- User asks a natural-language sales question  
- Model may only call **allowlisted tools** (no raw SQL from the model)  
- Tools query **synthetic SQL Server demo data**  
- Answer is **grounded** in tool results (or honestly says there is no data)  
- Angular UI for chat, tool activity, and simple charts/tables  

First milestone that unlocked the rest:

> One question → one tool call → grounded answer

---

## 2. Product decisions (locked early)

| Decision | Choice | Why |
| --- | --- | --- |
| Data | Synthetic SQL Server LocalDB (`AnalyticsDemo`) | Safe to demo publicly |
| Backend | Python 3.12+ + FastAPI + Pydantic | Clear API + typed tool contracts |
| Agent | Bounded tool-calling loop, allowlisted tools | Safer and easier to explain in interviews |
| LLM | Provider adapter (OpenAI-compatible) | Can switch providers later |
| Frontend | Angular | Show existing full-stack skills |
| Repo | Separate from Veld Supply / e-comm | Clean portfolio story |
| Build order | FastAPI tool loop first, Angular second | Prove the hard part before UI polish |

**Security rule:** the model never generates or executes raw SQL. It only requests tools like `get_sales_summary`; Python validates arguments and runs fixed read-only queries.

---

## 3. Repository and branches

- Remote: `https://github.com/JumaB7/Portfolio_Analytics_Agent.git`  
- Local path: `C:\Users\OEM\Personal\portfolio_analytics_agent`

| Branch | Role |
| --- | --- |
| `develop` | Integration / day-to-day baseline |
| `release` | Staging |
| `main` | Production |
| `feature/...` | Short-lived work branches |

Feature branches used so far (in order):

1. `feature/demo-db-sales-summary-agent` — demo DB + first tool + chat agent  
2. `feature/category-mom-analytics-tools` — category / MoM / product tools  
3. `feature/angular-chat-ui` — Angular chat front end  
4. `feature/agent-eval-hardening` — eval set, empty-data honesty, clearer LLM errors  

Flow: work on `feature/...` → PR into `develop` → merge → sync local `develop` → next feature branch.

---

## 4. Build steps we followed (chronological)

### Step 0 — Project framing

- Chose the AI Data Analyst Agent use case from the detailed project plan  
- Agreed MVP questions (total sales, top category, MoM change, lowest products, charts later)  
- Agreed not to start with LangChain; start with a direct tool-calling loop  

### Step 1 — FastAPI skeleton

Created on `develop`:

- `pyproject.toml` (FastAPI, Uvicorn, Pydantic, pytest)  
- `app/main.py` — FastAPI app, CORS, `/health` and `/api/health`  
- `app/config.py` — `pydantic-settings` from `.env`  
- `.env.example`, `.gitignore`, README, `tests/test_health.py`  
- Local Python 3.12 venv + editable install  

**Done when:** `GET /health` returned `{"status":"ok", ...}`.

### Step 2 — Synthetic demo database + first tool

- SQLAlchemy models: categories, products, orders, order_items, `demo_meta`  
- LocalDB database name: **`AnalyticsDemo`**  
- Seed script: `python -m scripts.init_demo_db`  
- September 2026 fixed totals for tests: **R 125,000**, 30 orders, 250 units  
- Tool: `get_sales_summary(start_date, end_date)`  
- Direct HTTP check (no LLM): `/api/tools/sales-summary?...`  

**Done when:** tool returned seed totals; empty ranges returned `has_data=false`.

### Step 3 — LLM adapter + bounded chat loop

- `app/agent/provider.py` — OpenAI-compatible Chat Completions client  
- `app/agent/orchestrator.py` — max iterations; allowlist + Pydantic validation  
- `app/agent/prompts.py` — system instructions (today’s date, no inventing numbers)  
- `POST /api/chat` with `{ "message": "..." }`  

Typical one question uses **two** LLM calls:

1. Model requests a tool  
2. Server runs tool  
3. Model writes the final answer from tool JSON  

**Done when:** chat answered “What were our total sales last month?” with September demo totals via `get_sales_summary`.

### Step 4 — More allowlisted tools

Added:

- `get_revenue_by_category`  
- `compare_sales_periods`  
- `get_product_performance` (`sort=highest|lowest`)  

Each got schemas, analytics queries, registry entry, HTTP tool route, tests, and prompt updates.

### Step 5 — Angular chat UI (`web/`)

- Angular 19 app with pnpm  
- Chat page: prompt box, sample questions, answer, tool activity  
- Tool results panel: metric cards + ranking bars  
- Dev proxy: `/api` → `http://127.0.0.1:8000`  
- Chat API extended so each tool activity includes `result` for the UI  

**Done when:** UI at `http://127.0.0.1:4200` could ask questions against the running API.

### Step 6 — Eval + hardening

- Stronger prompts for empty data, greetings, unsupported questions  
- Orchestrator adds an empty-data instruction back to the model when `has_data=false`  
- Friendlier LLM error codes (`llm_quota_exhausted`, `llm_auth_failed`, …)  
- Fixed eval catalog: `app/eval/cases.py` + `docs/EVAL.md` (Fake LLM, no credits)  
- Angular parses structured `{ code, message }` API errors  

### Step 7 — Efficiency (templated answers + rule router)

- `AGENT_TEMPLATE_ANSWERS=true`: after tools succeed, Python renders the answer (skips 2nd LLM call)  
- `AGENT_RULE_ROUTER=true`: common demo prompts / greetings / obvious unsupported questions run with **0 LLM calls**  
- Chat response includes `llm_calls` and `answer_source` (`router` | `template` | `llm`)  
- Routed sample questions work even without `LLM_API_KEY`  

---

## 5. API keys and secrets

### What you need

| Secret | Where | Purpose |
| --- | --- | --- |
| `LLM_API_KEY` | `.env` only (never commit) | Auth to OpenAI or another OpenAI-compatible provider |
| `LLM_BASE_URL` | `.env` | Default `https://api.openai.com/v1` |
| `LLM_MODEL` | `.env` | Default `gpt-4o-mini` |

Optional later: `DATABASE_URL` if you leave LocalDB defaults.

### Setup

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent
copy .env.example .env
notepad .env
```

Set at least:

```env
LLM_API_KEY=sk-your-real-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

### Important behaviours

- The **browser never** receives the API key. Only the FastAPI server calls the LLM.  
- If `LLM_API_KEY` is missing → `POST /api/chat` returns **503** (`llm_not_configured`).  
- If OpenAI has no credits → **429** mapped to a clear “credits / quota” message.  
- Tool-only endpoints (`/api/tools/...`) and unit/eval tests **do not** need an LLM key.  
- Billing: `gpt-4o-mini` is charged per token; one chat question is usually ~2 model calls and typically costs well under a cent.

### After changing `.env`

**Restart the API** (uvicorn does not always reload env vars reliably). See README “Restart the API”.

---

## 6. Architecture (current)

```
Angular (web/)  --POST /api/chat-->  FastAPI
                                       │
                                       ├─ Agent orchestrator (bounded loop)
                                       ├─ OpenAI-compatible provider
                                       ├─ Tool registry (allowlist + Pydantic)
                                       └─ Analytics service → SQL Server LocalDB AnalyticsDemo
```

Allowlisted tools:

| Tool | Purpose |
| --- | --- |
| `get_sales_summary` | Total revenue / orders / units |
| `get_revenue_by_category` | Category ranking |
| `compare_sales_periods` | Period vs period |
| `get_product_performance` | Highest/lowest products |

---

## 7. Key code map

| Path | Role |
| --- | --- |
| `app/main.py` | FastAPI app + routers |
| `app/config.py` | Settings from `.env` |
| `app/api/chat.py` | `POST /api/chat` |
| `app/api/tools.py` | Direct tool HTTP endpoints |
| `app/agent/orchestrator.py` | Bounded tool loop |
| `app/agent/provider.py` | LLM HTTP adapter |
| `app/agent/prompts.py` | System prompt |
| `app/agent/errors.py` | Friendly LLM error codes |
| `app/tools/*.py` | Allowlisted tool entrypoints |
| `app/tools/registry.py` | Allowlist + OpenAI tool schemas |
| `app/services/analytics.py` | Read-only SQL aggregations |
| `app/db/seed.py` | Create/seed `AnalyticsDemo` |
| `app/eval/cases.py` | Fixed eval prompts |
| `web/src/app/components/chat-page/` | Chat UI |
| `web/proxy.conf.json` | Proxy `/api` to port 8000 |
| `scripts/init_demo_db.py` | CLI seed entrypoint |

---

## 8. Startup and daily commands

Full copy-paste startup lives in the root **README**. Summary:

1. Activate venv  
2. Ensure `.env` has `LLM_API_KEY`  
3. Seed DB once (or after reset): `python -m scripts.init_demo_db`  
4. Start API: `uvicorn app.main:app --reload --port 8000`  
5. Start UI: `cd web` → `pnpm start`  
6. Open `http://127.0.0.1:4200`  

Health check: `http://127.0.0.1:8000/health`  
Swagger: `http://127.0.0.1:8000/docs`

### Restart API (required after `.env` changes)

1. Focus the uvicorn terminal  
2. `Ctrl+C`  
3. Start again:

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

### Restart Angular UI

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent\web
# Ctrl+C if already running
pnpm start
```

If the UI shows odd resolve errors (`main.ts` / `tsconfig.app.json`), stop the server, delete `web/.angular`, and run `pnpm start` again.

---

## 9. How we verified along the way

| Check | How |
| --- | --- |
| API alive | Browser `GET /health` |
| Tool without LLM | `/api/tools/sales-summary?start_date=2026-09-01&end_date=2026-09-30` |
| Chat with LLM | `Invoke-RestMethod` to `/api/chat` or Swagger |
| Automated | `pytest` (includes eval cases) |
| UI build | `cd web; pnpm build` |

Known good chat result for “total sales last month” (with “today” in Oct 2026): September demo **ZAR 125,000.00**, tool `get_sales_summary`, `is_demo_dataset: true`.

---

## 10. What is intentionally not done yet

- Public cloud deploy  
- Conversation persistence / multi-turn memory  
- LangChain / LangGraph  
- Monthly revenue series tool + richer charts  
- Production reverse proxy packaging  

Suggested next themes after hardening merges: portfolio polish (diagrams, recording), then deploy.

---

## 11. Related docs

- Root [README.md](../README.md) — setup, startup, restart  
- [EVAL.md](./EVAL.md) — evaluation catalog behaviour  
