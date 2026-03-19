import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listRuns, triggerRun } from '../../api/client';
import { Play, ChevronDown, ChevronUp } from 'lucide-react';

interface Props {
  agentId: string;
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    success: 'badge-success',
    error: 'badge-error',
    running: 'badge-running',
    pending: 'badge-pending',
  };
  return <span className={`status-badge ${colors[status] || ''}`}>{status}</span>;
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

function formatCost(cost: number): string {
  if (cost === 0) return 'Free';
  if (cost < 0) return '?';
  return `$${cost.toFixed(4)}`;
}

export function RunMonitor({ agentId }: Props) {
  const queryClient = useQueryClient();
  const [expandedRun, setExpandedRun] = useState<string | null>(null);

  const { data: runs, isLoading } = useQuery({
    queryKey: ['runs', agentId],
    queryFn: () => listRuns(agentId),
    refetchInterval: 5000,
  });

  const runMutation = useMutation({
    mutationFn: () => triggerRun(agentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['runs', agentId] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  return (
    <div className="run-monitor">
      <div className="run-monitor-header">
        <h3>Run History</h3>
        <button onClick={() => runMutation.mutate()} disabled={runMutation.isPending}>
          <Play size={14} /> {runMutation.isPending ? 'Starting...' : 'Run Now'}
        </button>
      </div>

      {isLoading && <div className="loading">Loading runs...</div>}

      {runs && runs.length === 0 && (
        <div className="empty-state">No runs yet. Click "Run Now" to start.</div>
      )}

      {runs && runs.length > 0 && (
        <table className="runs-table">
          <thead>
            <tr>
              <th></th>
              <th>Time</th>
              <th>Status</th>
              <th>Latency</th>
              <th>Tokens</th>
              <th>Cost</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <>
                <tr key={run.id} onClick={() => setExpandedRun(expandedRun === run.id ? null : run.id)} className="run-row">
                  <td>
                    {expandedRun === run.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </td>
                  <td>{run.started_at ? new Date(run.started_at).toLocaleString() : '-'}</td>
                  <td><StatusBadge status={run.status} /></td>
                  <td>{formatDuration(run.latency_ms)}</td>
                  <td>{run.tokens_in + run.tokens_out > 0 ? `${run.tokens_in}/${run.tokens_out}` : '-'}</td>
                  <td>{formatCost(run.cost_estimate)}</td>
                </tr>
                {expandedRun === run.id && (
                  <tr key={`${run.id}-detail`} className="run-detail">
                    <td colSpan={6}>
                      {run.error && <div className="run-error"><strong>Error:</strong> {run.error}</div>}
                      {run.output_data && (
                        <div className="run-output">
                          <strong>Output:</strong>
                          <pre>{run.output_data}</pre>
                        </div>
                      )}
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
