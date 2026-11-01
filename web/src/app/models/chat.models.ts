/** Allowlisted tool outcome from the agent API. */
export enum ToolStatus {
  Ok = 'ok',
  Error = 'error',
  Rejected = 'rejected',
}

/** How the final answer text was produced. */
export enum AnswerSource {
  Router = 'router',
  Template = 'template',
  Llm = 'llm',
}

export interface ToolActivity {
  tool_name: string;
  status: ToolStatus;
  detail?: string;
  arguments?: Record<string, unknown>;
  result?: Record<string, unknown>;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  answer: string;
  tool_activity: ToolActivity[];
  model: string;
  iterations: number;
  llm_calls?: number;
  answer_source?: AnswerSource;
  is_demo_dataset?: boolean;
}

export interface ChatTurn {
  id: string;
  question: string;
  response?: ChatResponse;
  error?: string;
  loading: boolean;
}
