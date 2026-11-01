/** Sample prompts shown on the chat page — keep aligned with allowlisted agent tools. */
export const SAMPLE_PROMPTS = [
  'Who is Jumari?',
  'What are the skills?',
  'Where has Jumari worked?',
  'Tell me about Veld Supply',
] as const;

export type SamplePrompt = (typeof SAMPLE_PROMPTS)[number];
