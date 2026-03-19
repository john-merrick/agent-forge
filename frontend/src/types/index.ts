export interface Agent {
  id: string;
  name: string;
  model: string;
  provider: string;
  system_prompt: string;
  user_prompt_template: string;
  tools: string[];
  schedule: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  file_path?: string;
}

export interface AgentCreate {
  name: string;
  model: string;
  provider: string;
  system_prompt: string;
  user_prompt_template: string;
  tools: string[];
  schedule: string | null;
}

export interface RunRecord {
  id: string;
  agent_id: string;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  input_data: string | null;
  output_data: string | null;
  tokens_in: number;
  tokens_out: number;
  cost_estimate: number;
  latency_ms: number;
  error: string | null;
}

export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  context_length: number | null;
  pricing: { input?: number; output?: number };
}

export interface ToolInfo {
  name: string;
  description: string;
  parameters: Record<string, unknown>;
}

export interface Stats {
  total_agents: number;
  total_runs: number;
  runs_today: number;
  cost_today: number;
  errors_today: number;
}

export interface NotificationConfig {
  channel: string;
  is_active: boolean;
  smtp_host?: string;
  smtp_port?: number;
  smtp_user?: string;
  smtp_pass?: string;
  to_email?: string;
  telegram_bot_token?: string;
  telegram_chat_id?: string;
  twilio_account_sid?: string;
  twilio_auth_token?: string;
  twilio_from_number?: string;
  whatsapp_to_number?: string;
}

export interface NotificationResponse {
  id: string;
  agent_id: string;
  channel: string;
  config: Record<string, string>;
  is_active: boolean;
}
