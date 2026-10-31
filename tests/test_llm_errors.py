from app.agent.errors import classify_llm_http_error


def test_classify_quota_exhausted() -> None:
    body = (
        '{"error":{"message":"You have no credits remaining.",'
        '"type":"insufficient_quota","code":"credit_balance_exhausted"}}'
    )
    err = classify_llm_http_error(429, body)
    assert err.code == "llm_quota_exhausted"
    assert "credits" in err.message.lower()


def test_classify_auth_failed() -> None:
    err = classify_llm_http_error(401, '{"error":{"message":"Invalid API key"}}')
    assert err.code == "llm_auth_failed"


def test_classify_server_error() -> None:
    err = classify_llm_http_error(503, "upstream unavailable")
    assert err.code == "llm_unavailable"
