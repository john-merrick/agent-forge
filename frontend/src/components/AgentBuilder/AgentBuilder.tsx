import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createAgent, updateAgent, listTools } from '../../api/client';
import { ModelSelector } from '../ModelSelector/ModelSelector';
import type { Agent, AgentCreate } from '../../types';

interface Props {
  agent?: Agent;
  onSaved?: () => void;
  onCancel?: () => void;
}

const SCHEDULE_PRESETS = [
  { label: 'Manual only', value: '' },
  { label: 'Every 5 minutes', value: '*/5 * * * *' },
  { label: 'Every hour', value: '0 * * * *' },
  { label: 'Daily at 9am', value: '0 9 * * *' },
  { label: 'Weekly Monday 9am', value: '0 9 * * 1' },
  { label: 'Custom', value: 'custom' },
];

export function AgentBuilder({ agent, onSaved, onCancel }: Props) {
  const queryClient = useQueryClient();
  const { data: toolsData } = useQuery({ queryKey: ['tools'], queryFn: listTools });

  const [form, setForm] = useState<AgentCreate>({
    name: agent?.name ?? '',
    model: agent?.model ?? '',
    provider: agent?.provider ?? 'ollama',
    system_prompt: agent?.system_prompt ?? '',
    user_prompt_template: agent?.user_prompt_template ?? '',
    tools: agent?.tools ?? [],
    schedule: agent?.schedule ?? null,
  });
  const [schedulePreset, setSchedulePreset] = useState(
    agent?.schedule ? (SCHEDULE_PRESETS.find(p => p.value === agent.schedule) ? agent.schedule : 'custom') : ''
  );
  const [customCron, setCustomCron] = useState(agent?.schedule ?? '');
  const [error, setError] = useState('');

  const mutation = useMutation({
    mutationFn: (data: AgentCreate) =>
      agent ? updateAgent(agent.id, data) : createAgent(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
      onSaved?.();
    },
    onError: (err: Error) => setError(err.message),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    const schedule = schedulePreset === 'custom' ? customCron : (schedulePreset || null);
    mutation.mutate({ ...form, schedule });
  };

  const toggleTool = (name: string) => {
    setForm((f) => ({
      ...f,
      tools: f.tools.includes(name)
        ? f.tools.filter((t) => t !== name)
        : [...f.tools, name],
    }));
  };

  return (
    <form className="agent-builder" onSubmit={handleSubmit}>
      <h2>{agent ? 'Edit Agent' : 'Create Agent'}</h2>

      {error && <div className="error-message">{error}</div>}

      <div className="form-group">
        <label>Name</label>
        <input
          type="text"
          value={form.name}
          onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          placeholder="my-research-agent"
          required
        />
      </div>

      <ModelSelector
        value={form.model}
        provider={form.provider}
        onChange={(model, provider) => setForm((f) => ({ ...f, model, provider }))}
      />

      <div className="form-group">
        <label>System Prompt</label>
        <textarea
          value={form.system_prompt}
          onChange={(e) => setForm((f) => ({ ...f, system_prompt: e.target.value }))}
          rows={4}
          placeholder="You are a helpful assistant that..."
        />
      </div>

      <div className="form-group">
        <label>User Prompt Template</label>
        <textarea
          value={form.user_prompt_template}
          onChange={(e) => setForm((f) => ({ ...f, user_prompt_template: e.target.value }))}
          rows={4}
          placeholder='Use {{input}} for dynamic input'
        />
      </div>

      <div className="form-group">
        <label>Tools</label>
        <div className="tools-grid">
          {(toolsData?.tools ?? []).map((tool) => (
            <label key={tool.name} className="tool-checkbox">
              <input
                type="checkbox"
                checked={form.tools.includes(tool.name)}
                onChange={() => toggleTool(tool.name)}
              />
              <span className="tool-name">{tool.name}</span>
              <span className="tool-desc">{tool.description}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Schedule</label>
        <select
          value={schedulePreset}
          onChange={(e) => {
            setSchedulePreset(e.target.value);
            if (e.target.value !== 'custom') setCustomCron('');
          }}
        >
          {SCHEDULE_PRESETS.map((p) => (
            <option key={p.value} value={p.value}>{p.label}</option>
          ))}
        </select>
        {schedulePreset === 'custom' && (
          <input
            type="text"
            value={customCron}
            onChange={(e) => setCustomCron(e.target.value)}
            placeholder="*/30 * * * *"
            className="cron-input"
          />
        )}
      </div>

      <div className="form-actions">
        <button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? 'Saving...' : agent ? 'Update Agent' : 'Create Agent'}
        </button>
        {onCancel && (
          <button type="button" onClick={onCancel} className="btn-secondary">
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
