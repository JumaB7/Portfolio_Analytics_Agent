# Agent evaluation set

Fixed prompts used to regression-test the bounded analytics agent.

## How it works

- Cases live in `app/eval/cases.py` (`EVAL_CASES`).
- `tests/test_eval_cases.py` runs each case with a **scripted Fake LLM**.
- No OpenAI credits are spent in CI.

This checks that:

1. The allowlisted tool path returns grounded numbers from `AnalyticsDemo`.
2. Empty periods stay empty (`has_data=false`) and answers do not invent revenue.
3. Unsupported / greeting turns can complete without tools.
4. Unknown tools are rejected by the backend allowlist.

## Case kinds

| Kind | Meaning |
| --- | --- |
| `tool_grounded` | Expected tool + args; assert key fields from tool result |
| `empty_data` | Tool runs on an empty range; answer must not invent totals |
| `greeting` | No tool calls |
| `unsupported` | No tool calls; honest refusal |
| `rejected_tool` | Model requests a non-allowlisted tool; backend rejects |

## Running

```powershell
pytest tests/test_eval_cases.py -q
```

When prompts, tools, or seed totals change, update the matching case in `app/eval/cases.py`.
