import type { Agent, AgentCreate, RunRecord, ModelInfo, ToolInfo, Stats, NotificationConfig, NotificationResponse } from '../types';

const BASE = (import.meta.env.VITE_API_URL as string) || '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.detail || err.error || 'Request failed');
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Agents
export const listAgents = () => request<Agent[]>('/agents');
export const getAgent = (id: string) => request<Agent>(`/agents/${id}`);
export const createAgent = (data: AgentCreate) =>
  request<Agent>('/agents', { method: 'POST', body: JSON.stringify(data) });
export const updateAgent = (id: string, data: Partial<AgentCreate>) =>
  request<Agent>(`/agents/${id}`, { method: 'PUT', body: JSON.stringify(data) });
export const deleteAgent = (id: string) =>
  request<void>(`/agents/${id}`, { method: 'DELETE' });
export const getAgentCode = (id: string) =>
  request<{ code: string | null; explainer: string | null; file_path: string }>(`/agents/${id}/code`);

// Runs
export const triggerRun = (agentId: string, inputData?: Record<string, unknown>) =>
  request<{ status: string }>(`/agents/${agentId}/run`, {
    method: 'POST',
    body: JSON.stringify(inputData ? { input_data: inputData } : {}),
  });
export const listRuns = (agentId: string) => request<RunRecord[]>(`/agents/${agentId}/runs`);
export const getRun = (id: string) => request<RunRecord>(`/runs/${id}`);
export const recentRuns = () => request<RunRecord[]>('/runs/recent');

// Models
export const listModels = () => request<{ models: ModelInfo[] }>('/models');
export const checkOllama = () => request<{ reachable: boolean }>('/models/ollama/status');

// Tools
export const listTools = () => request<{ tools: ToolInfo[] }>('/tools');

// Settings
export const getSettings = () => request<Record<string, string>>('/settings');
export const updateSettings = (data: Record<string, string>) =>
  request<{ status: string }>('/settings', { method: 'PUT', body: JSON.stringify(data) });

// Notifications
export const listNotifications = (agentId: string) =>
  request<NotificationResponse[]>(`/agents/${agentId}/notifications`);
export const createNotification = (agentId: string, data: NotificationConfig) =>
  request<NotificationResponse>(`/agents/${agentId}/notifications`, {
    method: 'POST', body: JSON.stringify(data),
  });
export const deleteNotification = (agentId: string, notifId: string) =>
  request<void>(`/agents/${agentId}/notifications/${notifId}`, { method: 'DELETE' });
export const toggleNotification = (agentId: string, notifId: string) =>
  request<NotificationResponse>(`/agents/${agentId}/notifications/${notifId}/toggle`, { method: 'PUT' });

// Stats
export const getStats = () => request<Stats>('/stats');
