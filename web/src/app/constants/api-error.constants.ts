/** Fixed user-facing copy for known HTTP failure modes. */
export const API_ERROR_BY_STATUS: Record<number, string> = {
  0: 'Could not reach the API. Start uvicorn on port 8000, then retry.',
  502: 'The LLM provider failed. Check LLM_API_KEY, LLM_BASE_URL, and provider status.',
  503: 'The analytics API is unavailable (often a missing LLM key or exhausted credits).',
};

export const API_ERROR_UNKNOWN =
  'Request failed. Is the API running on port 8000?';
