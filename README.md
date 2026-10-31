# Portfolio Analytics Agent

Bounded AI assistant over **portfolio site content** (about, skills, experience, projects, contact, dashboard KPIs) shared with JumariPortfolio.

Python FastAPI backend with allowlisted tools; site-wide FAB in PortfolioWebApp (path-based `/api/agent`). The standalone `web/` app remains for isolated demos.

Demo / showcase data only — not client or employer data.

**Walkthrough:** [docs/PROJECT_WALKTHROUGH.md](docs/PROJECT_WALKTHROUGH.md)  
**Eval catalog:** [docs/EVAL.md](docs/EVAL.md)

## Stack

| Part | Choice |
| --- | --- |
| Backend | Python 3.12+, FastAPI, Pydantic |
| Agent | Bounded tool-calling loop, allowlisted tools (no raw SQL from the model) |
| Data | `GET /api/dashboard/analytics` on PortfolioAPI (local seed fallback) |
| LLM | OpenAI-compatible Chat Completions API |
| Hosted UI | PortfolioWebApp FAB (all pages) → `/api/agent/*` |

## Efficiency defaults

| Setting | Default | Effect |
| --- | --- | --- |
| `AGENT_RULE_ROUTER` | `true` | Common prompts answered with **0 LLM calls** |
| `AGENT_TEMPLATE_ANSWERS` | `true` | After a tool runs, Python writes the answer (**no second LLM call**) |

## Allowlisted tools

| Tool | Purpose |
| --- | --- |
| `get_owner_profile` | Who Jumari is |
| `get_skills` | Skills section |
| `get_experience` | Work / education |
| `get_contact` | Public email |
| `get_portfolio_summary` | Project KPI overview |
| `list_projects` | Filter projects |
| `get_technology_usage` | Technology mix |
| `get_category_distribution` | Category mix |
| `get_project_detail` | One project by id or name |

## First-time setup

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
copy .env.example .env
```

Edit `.env`:

```env
LLM_API_KEY=sk-your-real-key-here
PORTFOLIO_API_BASE_URL=http://127.0.0.1:5157
```

Leave `PORTFOLIO_API_BASE_URL` empty to force the built-in seed (same projects as the API seed).

## Startup with JumariPortfolio (recommended)

Three processes, one browser origin (`http://localhost:4200`):

1. **PortfolioAPI** (5157) — serves `/api/dashboard/analytics`
2. **Agent API** (8000) — reads that dataset (or seed)
3. **PortfolioWebApp** (4200) — proxies `/api` → 5157 and `/api/agent` → 8000/api

```powershell
# Terminal A — PortfolioAPI
cd C:\Users\OEM\Personal\portfolio\JumariPortfolio\PortfolioAPI
dotnet run

# Terminal B — Agent
cd C:\Users\OEM\Personal\portfolio_analytics_agent
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000

# Terminal C — Portfolio web
cd C:\Users\OEM\Personal\portfolio\JumariPortfolio\PortfolioWebApp
pnpm start
```

Open http://localhost:4200 and use the chat FAB (or `/?agent=1`).

Sample prompts:

- “Who is Jumari?”
- “What are the skills?”
- “Where has Jumari worked?”
- “Tell me about Veld Supply”

## Standalone agent API

```powershell
uvicorn app.main:app --reload --port 8000
```

- Health: http://127.0.0.1:8000/health
- Chat: `POST http://127.0.0.1:8000/api/chat`
- Tools: http://127.0.0.1:8000/api/tools

## Tests

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent
.\.venv\Scripts\Activate.ps1
pytest
```

## Security note

The model never generates or executes raw SQL. It may only call allowlisted tools. Keep `LLM_API_KEY` in `.env` only — never in the Angular app or git.

## Branches

| Branch | Role |
| --- | --- |
| `feature/portfolio-dashboard-data` | Portfolio dataset tools + PortfolioAPI client |
| `develop` | Day-to-day work |
| `release` | Staging |
| `main` | Production |
