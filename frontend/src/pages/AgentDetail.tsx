import { useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getAgent } from '../api/client';
import { AgentBuilder } from '../components/AgentBuilder/AgentBuilder';
import { CodeViewer } from '../components/CodeViewer/CodeViewer';
import { RunMonitor } from '../components/RunMonitor/RunMonitor';
import { NotificationManager } from '../components/NotificationManager/NotificationManager';
import { ArrowLeft } from 'lucide-react';

export function AgentDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [tab, setTab] = useState<'overview' | 'code' | 'runs' | 'notifications'>(
    searchParams.get('edit') ? 'overview' : 'runs'
  );
  const [editing, setEditing] = useState(!!searchParams.get('edit'));

  const { data: agent, isLoading } = useQuery({
    queryKey: ['agent', id],
    queryFn: () => getAgent(id!),
    enabled: !!id,
  });

  if (isLoading) return <div className="loading">Loading agent...</div>;
  if (!agent) return <div className="error-message">Agent not found</div>;

  return (
    <div className="agent-detail">
      <div className="agent-detail-header">
        <button className="btn-icon" onClick={() => navigate('/')}>
          <ArrowLeft size={20} />
        </button>
        <h1>{agent.name}</h1>
        <span className={`provider-badge ${agent.provider}`}>{agent.provider}</span>
        <span className="model-name">{agent.model}</span>
      </div>

      <div className="tab-bar">
        <button className={tab === 'overview' ? 'active' : ''} onClick={() => setTab('overview')}>
          Overview
        </button>
        <button className={tab === 'code' ? 'active' : ''} onClick={() => setTab('code')}>
          Code
        </button>
        <button className={tab === 'runs' ? 'active' : ''} onClick={() => setTab('runs')}>
          Runs
        </button>
        <button className={tab === 'notifications' ? 'active' : ''} onClick={() => setTab('notifications')}>
          Notifications
        </button>
      </div>

      <div className="tab-content">
        {tab === 'overview' && (
          editing ? (
            <AgentBuilder
              agent={agent}
              onSaved={() => setEditing(false)}
              onCancel={() => setEditing(false)}
            />
          ) : (
            <div className="agent-overview">
              <div className="overview-section">
                <h3>System Prompt</h3>
                <pre>{agent.system_prompt || '(none)'}</pre>
              </div>
              <div className="overview-section">
                <h3>User Prompt Template</h3>
                <pre>{agent.user_prompt_template || '(none)'}</pre>
              </div>
              {agent.tools.length > 0 && (
                <div className="overview-section">
                  <h3>Tools</h3>
                  <ul>{agent.tools.map((t) => <li key={t}>{t}</li>)}</ul>
                </div>
              )}
              {agent.schedule && (
                <div className="overview-section">
                  <h3>Schedule</h3>
                  <code>{agent.schedule}</code>
                </div>
              )}
              <button onClick={() => setEditing(true)}>Edit Agent</button>
            </div>
          )
        )}
        {tab === 'code' && <CodeViewer agentId={agent.id} />}
        {tab === 'runs' && <RunMonitor agentId={agent.id} />}
        {tab === 'notifications' && <NotificationManager agentId={agent.id} />}
      </div>
    </div>
  );
}
