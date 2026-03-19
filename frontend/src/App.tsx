import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Dashboard } from './pages/Dashboard';
import { AgentDetail } from './pages/AgentDetail';
import { SettingsPage } from './pages/Settings';
import { Bot, Settings } from 'lucide-react';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 5000, retry: 1 },
  },
});

function Nav() {
  const location = useLocation();
  return (
    <nav className="sidebar">
      <div className="sidebar-logo">
        <Bot size={24} /> Agent Forge
      </div>
      <div className="sidebar-links">
        <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
          Dashboard
        </Link>
        <Link to="/settings" className={location.pathname === '/settings' ? 'active' : ''}>
          <Settings size={16} /> Settings
        </Link>
      </div>
    </nav>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="app-layout">
          <Nav />
          <main className="app-main">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/agents/:id" element={<AgentDetail />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
