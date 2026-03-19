import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { listAgents, getStats } from '../api/client';
import { AgentList } from '../components/AgentList/AgentList';
import { AgentBuilder } from '../components/AgentBuilder/AgentBuilder';
import { Plus, Zap, DollarSign, AlertTriangle, Bot } from 'lucide-react';

export function Dashboard() {
  const [showBuilder, setShowBuilder] = useState(false);
  const { data: agents, isLoading } = useQuery({ queryKey: ['agents'], queryFn: listAgents });
  const { data: stats } = useQuery({ queryKey: ['stats'], queryFn: getStats, refetchInterval: 10000 });

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Agent Forge</h1>
        <button className="btn-primary" onClick={() => setShowBuilder(!showBuilder)}>
          <Plus size={16} /> New Agent
        </button>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <Bot size={20} />
            <div>
              <div className="stat-value">{stats.total_agents}</div>
              <div className="stat-label">Agents</div>
            </div>
          </div>
          <div className="stat-card">
            <Zap size={20} />
            <div>
              <div className="stat-value">{stats.runs_today}</div>
              <div className="stat-label">Runs Today</div>
            </div>
          </div>
          <div className="stat-card">
            <DollarSign size={20} />
            <div>
              <div className="stat-value">${stats.cost_today.toFixed(4)}</div>
              <div className="stat-label">Cost Today</div>
            </div>
          </div>
          <div className="stat-card">
            <AlertTriangle size={20} />
            <div>
              <div className="stat-value">{stats.errors_today}</div>
              <div className="stat-label">Errors Today</div>
            </div>
          </div>
        </div>
      )}

      {showBuilder && (
        <AgentBuilder
          onSaved={() => setShowBuilder(false)}
          onCancel={() => setShowBuilder(false)}
        />
      )}

      {isLoading ? (
        <div className="loading">Loading agents...</div>
      ) : (
        <AgentList agents={agents ?? []} />
      )}
    </div>
  );
}
