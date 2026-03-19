import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { deleteAgent, triggerRun } from '../../api/client';
import { Play, Trash2, Edit, Clock } from 'lucide-react';
import type { Agent } from '../../types';

interface Props {
  agents: Agent[];
}

export function AgentList({ agents }: Props) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const runMutation = useMutation({
    mutationFn: (id: string) => triggerRun(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['stats'] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteAgent(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['agents'] }),
  });

  if (agents.length === 0) {
    return <div className="empty-state">No agents yet. Create your first one!</div>;
  }

  return (
    <div className="agent-list">
      {agents.map((agent) => (
        <div key={agent.id} className="agent-card" onClick={() => navigate(`/agents/${agent.id}`)}>
          <div className="agent-card-header">
            <h3>{agent.name}</h3>
            <span className={`provider-badge ${agent.provider}`}>{agent.provider}</span>
          </div>
          <div className="agent-card-meta">
            <span className="model-name">{agent.model}</span>
            {agent.schedule && (
              <span className="schedule-badge">
                <Clock size={12} /> {agent.schedule}
              </span>
            )}
          </div>
          <div className="agent-card-actions" onClick={(e) => e.stopPropagation()}>
            <button
              className="btn-icon"
              title="Run now"
              onClick={() => runMutation.mutate(agent.id)}
              disabled={runMutation.isPending}
            >
              <Play size={16} />
            </button>
            <button
              className="btn-icon"
              title="Edit"
              onClick={() => navigate(`/agents/${agent.id}?edit=1`)}
            >
              <Edit size={16} />
            </button>
            <button
              className="btn-icon btn-danger"
              title="Delete"
              onClick={() => {
                if (confirm(`Delete agent "${agent.name}"?`)) {
                  deleteMutation.mutate(agent.id);
                }
              }}
            >
              <Trash2 size={16} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
