# Agent evaluation set

Fixed prompts used to regression-test the bounded portfolio analytics agent.

## How it works

- Cases live in `app/eval/cases.py` (`EVAL_CASES`).
- `tests/test_eval_cases.py` runs each case with a **scripted Fake LLM**.
- No OpenAI credits are spent in CI.
- Tests force `PORTFOLIO_API_BASE_URL=""` so the local seed is used (same projects as PortfolioAPI).

This checks that:

1. Allowlisted tools return grounded showcase metrics (project counts, tech/category mix).
2. Missing projects stay empty (`has_data=false`) and answers do not invent details.
3. Unsupported / greeting turns can complete without tools.
4. Unknown tools are rejected by the backend allowlist.

## Case kinds

| Kind | Meaning |
| --- | --- |
| `tool_grounded` | Expected tool + args; assert key fields from tool result |
| `empty_data` | Tool runs with no match; answer must not invent projects |
| `greeting` | No tool calls |
| `unsupported` | No tool calls; honest refusal |
| `rejected_tool` | Model requests a non-allowlisted tool; backend rejects |

## Running

```powershell
pytest tests/test_eval_cases.py -q
```

When prompts, tools, or seed projects change, update the matching case in `app/eval/cases.py`.
