import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { getAgentCode } from '../../api/client';
import { Copy, Check, FileText, Code } from 'lucide-react';

interface Props {
  agentId: string;
}

export function CodeViewer({ agentId }: Props) {
  const [tab, setTab] = useState<'code' | 'explainer'>('code');
  const [copied, setCopied] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['agent-code', agentId],
    queryFn: () => getAgentCode(agentId),
  });

  const handleCopy = async () => {
    const text = tab === 'code' ? data?.code : data?.explainer;
    if (text) {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (isLoading) return <div className="loading">Loading code...</div>;
  if (!data?.code) return <div className="empty-state">No code generated yet.</div>;

  return (
    <div className="code-viewer">
      <div className="code-viewer-header">
        <div className="code-tabs">
          <button className={tab === 'code' ? 'active' : ''} onClick={() => setTab('code')}>
            <Code size={14} /> Agent Code
          </button>
          <button className={tab === 'explainer' ? 'active' : ''} onClick={() => setTab('explainer')}>
            <FileText size={14} /> Explainer
          </button>
        </div>
        <div className="code-actions">
          <span className="file-path">{data.file_path}</span>
          <button className="btn-icon" onClick={handleCopy} title="Copy to clipboard">
            {copied ? <Check size={14} /> : <Copy size={14} />}
          </button>
        </div>
      </div>
      {tab === 'code' ? (
        <SyntaxHighlighter language="python" style={vscDarkPlus} showLineNumbers>
          {data.code}
        </SyntaxHighlighter>
      ) : (
        <div className="explainer-content">
          <pre>{data.explainer || 'No explainer generated.'}</pre>
        </div>
      )}
    </div>
  );
}
