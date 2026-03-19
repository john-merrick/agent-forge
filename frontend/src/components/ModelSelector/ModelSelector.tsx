import { useQuery } from '@tanstack/react-query';
import { listModels, checkOllama } from '../../api/client';

interface Props {
  value: string;
  provider: string;
  onChange: (model: string, provider: string) => void;
}

export function ModelSelector({ value, onChange }: Props) {
  const { data, isLoading } = useQuery({ queryKey: ['models'], queryFn: listModels });
  const { data: ollamaStatus } = useQuery({ queryKey: ['ollama-status'], queryFn: checkOllama });

  const models = data?.models ?? [];
  const ollamaModels = models.filter((m) => m.provider === 'ollama');
  const openrouterModels = models.filter((m) => m.provider === 'openrouter');

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = models.find((m) => m.id === e.target.value);
    if (selected) onChange(selected.id, selected.provider);
  };

  return (
    <div className="model-selector">
      <label>Model</label>
      {!ollamaStatus?.reachable && (
        <div className="warning">Ollama not running — only OpenRouter models available</div>
      )}
      <select value={value} onChange={handleChange} disabled={isLoading}>
        <option value="">Select a model...</option>
        {ollamaModels.length > 0 && (
          <optgroup label="Ollama (Local)">
            {ollamaModels.map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </optgroup>
        )}
        {openrouterModels.length > 0 && (
          <optgroup label="OpenRouter (Cloud)">
            {openrouterModels.map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </optgroup>
        )}
      </select>
      {isLoading && <span className="loading-text">Loading models...</span>}
    </div>
  );
}
