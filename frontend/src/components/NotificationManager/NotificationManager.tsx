import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listNotifications, createNotification, deleteNotification, toggleNotification } from '../../api/client';
import { Plus, Trash2, Bell, BellOff, Mail, Send, MessageCircle } from 'lucide-react';
import type { NotificationConfig } from '../../types';

interface Props {
  agentId: string;
}

const CHANNELS = [
  { id: 'email', label: 'Email', icon: Mail },
  { id: 'telegram', label: 'Telegram', icon: Send },
  { id: 'whatsapp', label: 'WhatsApp', icon: MessageCircle },
];

const CHANNEL_FIELDS: Record<string, { key: string; label: string; type: string }[]> = {
  email: [
    { key: 'smtp_host', label: 'SMTP Host', type: 'text' },
    { key: 'smtp_port', label: 'SMTP Port', type: 'number' },
    { key: 'smtp_user', label: 'SMTP Username', type: 'text' },
    { key: 'smtp_pass', label: 'SMTP Password', type: 'password' },
    { key: 'to_email', label: 'Recipient Email', type: 'email' },
  ],
  telegram: [
    { key: 'telegram_bot_token', label: 'Bot Token', type: 'password' },
    { key: 'telegram_chat_id', label: 'Chat ID', type: 'text' },
  ],
  whatsapp: [
    { key: 'twilio_account_sid', label: 'Twilio Account SID', type: 'text' },
    { key: 'twilio_auth_token', label: 'Twilio Auth Token', type: 'password' },
    { key: 'twilio_from_number', label: 'From Number (with +)', type: 'text' },
    { key: 'whatsapp_to_number', label: 'To Number (with +)', type: 'text' },
  ],
};

export function NotificationManager({ agentId }: Props) {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [selectedChannel, setSelectedChannel] = useState('email');
  const [formData, setFormData] = useState<Record<string, string>>({});

  const { data: notifications } = useQuery({
    queryKey: ['notifications', agentId],
    queryFn: () => listNotifications(agentId),
  });

  const createMutation = useMutation({
    mutationFn: (data: NotificationConfig) => createNotification(agentId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications', agentId] });
      setShowForm(false);
      setFormData({});
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (notifId: string) => deleteNotification(agentId, notifId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications', agentId] }),
  });

  const toggleMutation = useMutation({
    mutationFn: (notifId: string) => toggleNotification(agentId, notifId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications', agentId] }),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      channel: selectedChannel,
      is_active: true,
      ...formData,
    } as NotificationConfig);
  };

  const channelIcon = (ch: string) => {
    const c = CHANNELS.find(c => c.id === ch);
    if (!c) return null;
    const Icon = c.icon;
    return <Icon size={14} />;
  };

  return (
    <div className="notification-manager">
      <div className="run-monitor-header">
        <h3>Notifications</h3>
        <button onClick={() => setShowForm(!showForm)}>
          <Plus size={14} /> Add Channel
        </button>
      </div>

      {showForm && (
        <form className="notification-form" onSubmit={handleSubmit}>
          <div className="channel-selector">
            {CHANNELS.map((ch) => (
              <button
                key={ch.id}
                type="button"
                className={`channel-btn ${selectedChannel === ch.id ? 'active' : ''}`}
                onClick={() => { setSelectedChannel(ch.id); setFormData({}); }}
              >
                <ch.icon size={16} /> {ch.label}
              </button>
            ))}
          </div>

          {CHANNEL_FIELDS[selectedChannel]?.map((field) => (
            <div className="form-group" key={field.key}>
              <label>{field.label}</label>
              <input
                type={field.type}
                value={formData[field.key] || ''}
                onChange={(e) => setFormData(f => ({ ...f, [field.key]: e.target.value }))}
                required
              />
            </div>
          ))}

          <div className="form-actions">
            <button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Adding...' : 'Add Notification'}
            </button>
            <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {notifications && notifications.length > 0 ? (
        <div className="notification-list">
          {notifications.map((n) => (
            <div key={n.id} className="notification-item">
              <div className="notification-info">
                {channelIcon(n.channel)}
                <span className="notification-channel">{n.channel}</span>
                {n.channel === 'email' && n.config.to_email && (
                  <span className="notification-detail">{n.config.to_email}</span>
                )}
                {n.channel === 'telegram' && n.config.telegram_chat_id && (
                  <span className="notification-detail">Chat: {n.config.telegram_chat_id}</span>
                )}
                {n.channel === 'whatsapp' && n.config.whatsapp_to_number && (
                  <span className="notification-detail">{n.config.whatsapp_to_number}</span>
                )}
              </div>
              <div className="notification-actions">
                <button
                  className="btn-icon"
                  title={n.is_active ? 'Disable' : 'Enable'}
                  onClick={() => toggleMutation.mutate(n.id)}
                >
                  {n.is_active ? <Bell size={14} /> : <BellOff size={14} />}
                </button>
                <button
                  className="btn-icon btn-danger"
                  title="Remove"
                  onClick={() => deleteMutation.mutate(n.id)}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : !showForm ? (
        <div className="empty-state" style={{ padding: '20px' }}>
          No notifications configured. Agent output stays in the dashboard only.
        </div>
      ) : null}
    </div>
  );
}
