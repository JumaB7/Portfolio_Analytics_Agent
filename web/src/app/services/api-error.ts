import { HttpErrorResponse } from '@angular/common/http';

export interface ApiErrorBody {
  code?: string;
  message?: string;
}

export function readApiErrorMessage(err: unknown): string {
  if (!(err instanceof HttpErrorResponse)) {
    return 'Request failed. Is the API running on port 8000?';
  }

  const detail = err.error?.detail;

  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  if (detail && typeof detail === 'object') {
    const body = detail as ApiErrorBody;
    if (body.message) {
      return body.code ? `${body.message} (${body.code})` : body.message;
    }
  }

  if (err.status === 0) {
    return 'Could not reach the API. Start uvicorn on port 8000, then retry.';
  }

  if (err.status === 503) {
    return 'The analytics API is unavailable (often a missing LLM key or exhausted credits).';
  }

  if (err.status === 502) {
    return 'The LLM provider failed. Check LLM_API_KEY, LLM_BASE_URL, and provider status.';
  }

  return `Request failed with HTTP ${err.status}.`;
}
