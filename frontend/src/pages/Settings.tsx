import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getSettings, updateSettings, checkOllama } from '../api/client';

export function SettingsPage() {
  const queryClient = useQueryClient();
  const { data: settings } = useQuery({ queryKey: ['settings'], queryFn: getSettings });
  const { data: ollamaStatus } = useQuery({ queryKey: ['ollama-status'], queryFn: checkOllama });

  const [apiKey, setApiKey] = useState('');
  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (settings) {
      setApiKey(settings.openrouter_api_key || '');
      setOllamaUrl(settings.ollama_base_url || 'http://localhost:11434');
    }
  }, [settings]);

  const mutation = useMutation({
    mutationFn: (data: Record<string, string>) => updateSettings(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      queryClient.invalidateQueries({ queryKey: ['models'] });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    },
  });

  const handleSave = () => {
    mutation.mutate({
      openrouter_api_key: apiKey,
      ollama_base_url: ollamaUrl,
    });
  };

  return (
    <div className="settings-page">
      <h1>Settings</h1>

      <div className="settings-section">
        <h2>Ollama</h2>
        <div className="form-group">
          <label>Base URL</label>
          <input
            type="text"
            value={ollamaUrl}
            onChange={(e) => setOllamaUrl(e.target.value)}
          />
          <div className={`status-indicator ${ollamaStatus?.reachable ? 'connected' : 'disconnected'}`}>
            {ollamaStatus?.reachable ? 'Connected' : 'Not running'}
          </div>
        </div>
      </div>

      <div className="settings-section">
        <h2>OpenRouter</h2>
        <div className="form-group">
          <label>API Key</label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="sk-or-..."
          />
          {settings?.openrouter_api_key_masked && (
            <div className="current-key">Current: {settings.openrouter_api_key_masked}</div>
          )}
        </div>
      </div>

      <button onClick={handleSave} disabled={mutation.isPending}>
        {saved ? 'Saved!' : mutation.isPending ? 'Saving...' : 'Save Settings'}
      </button>
    </div>
  );
}
