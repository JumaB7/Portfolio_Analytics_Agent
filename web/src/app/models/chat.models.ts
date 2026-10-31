export type ToolStatus = 'ok' | 'error' | 'rejected';

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

export type AnswerSource = 'router' | 'template' | 'llm';

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
