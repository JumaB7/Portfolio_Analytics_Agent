# Portfolio Analytics Agent

Bounded AI data analyst agent over **synthetic e-commerce demo data**.  
Python FastAPI backend with allowlisted tools; Angular UI comes later.

Demo data only — not client or employer data.

## Stack (MVP)

| Part | Choice |
| --- | --- |
| Backend | Python 3.12+, FastAPI, Pydantic |
| Agent | Bounded tool-calling loop, allowlisted tools (no raw SQL from the model) |
| Data | Synthetic SQL Server demo dataset (next milestone) |
| Frontend | Angular + TypeScript (after the API tool loop works) |

## First milestone

One question → one tool call → grounded answer from demo data.

## Local setup

### Requirements

- Python 3.12+
- (Later) SQL Server LocalDB or Express for demo data

### Install

```powershell
cd C:\Users\OEM\Personal\portfolio_analytics_agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
copy .env.example .env
```

### Run the API

```powershell
uvicorn app.main:app --reload --port 8000
```

- Health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- API health: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Tests

```powershell
pytest
```

## Project layout

```
app/
  main.py          # FastAPI app + health routes
  config.py        # environment-based settings
  schemas/         # Pydantic request/response models
tests/
.env.example
pyproject.toml
```

## Branches

| Branch | Role |
| --- | --- |
| `develop` | Day-to-day work |
| `release` | Staging |
| `main` | Production |
