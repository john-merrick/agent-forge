# Agent Forge

A fully local, browser-accessible platform for building, running, scheduling, and monitoring AI agents.

Build agents with a UI form, run them on demand or on a cron schedule, inspect the generated code, and monitor every run — all from your browser.

## Features

- **Visual Agent Builder** — form-based UI to configure model, prompts, tools, and schedule
- **Code Generation** — every agent produces a standalone, readable Python file saved to disk
- **Auto Explainer** — an `explainer.md` is generated alongside each agent file
- **On-Demand & Scheduled Runs** — trigger agents manually or set a cron schedule
- **Run Monitoring** — token counts, cost estimates, latency, errors, and full output history
- **Model Switching** — seamlessly switch between local Ollama models and OpenRouter cloud models
- **Notifications** — send agent output to Email, Telegram, or WhatsApp
- **Built-in Tools** — web search, file reader, and shell command execution
- **Docker Support** — single-container deployment with multi-stage build

## Quickstart

### Docker (recommended)

```bash
docker compose up -d
```

Open http://localhost:8000.

To use OpenRouter models, pass your API key:

```bash
OPENROUTER_API_KEY=sk-or-... docker compose up -d
```

### Local Development

**Prerequisites:** Python 3.11+, Node.js 18+, [uv](https://docs.astral.sh/uv/)

```bash
# Install dependencies
make install

# Terminal 1 — backend
make dev-backend

# Terminal 2 — frontend
make dev-frontend
```

Backend runs on http://localhost:8000, frontend on http://localhost:5173.

## Architecture

```
agent-forge/
├── backend/                # FastAPI + SQLite + APScheduler
│   ├── routers/            # API endpoints (agents, runs, models, settings, notifications)
│   ├── services/           # codegen, runner, scheduler, notifier, cost, model_registry
│   ├── templates/          # Jinja2 agent template
│   └── tools/              # Built-in tool registry + implementations
├── frontend/               # React + Vite + TypeScript
│   └── src/
│       ├── components/     # AgentBuilder, AgentList, CodeViewer, RunMonitor, NotificationManager
│       └── pages/          # Dashboard, AgentDetail, Settings
├── agents/                 # Generated agent files (gitignored)
├── data/                   # SQLite database (gitignored)
├── Dockerfile
└── docker-compose.yml
```

## How It Works

1. **Create an agent** via the UI — pick a model, write system/user prompts, select tools, set a schedule
2. **Agent Forge generates** a standalone Python file at `agents/{name}.py` and an `agents/{name}_explainer.md`
3. **Run the agent** from the UI or let the scheduler trigger it on cron
4. **The runner** executes the agent as an isolated subprocess, captures structured JSON output (content, token counts, timing)
5. **Results appear** in the run monitor with full metrics
6. **Notifications** are sent to configured channels (email, Telegram, WhatsApp)

### Generated Agents Are Standalone

Every generated agent file can run independently outside the platform:

```bash
# Ollama agent
python agents/my_agent.py

# OpenRouter agent
OPENROUTER_API_KEY=sk-or-... python agents/my_agent.py
```

## Model Providers

| Provider | Setup | Cost |
|----------|-------|------|
| **Ollama** | Install [Ollama](https://ollama.com), pull a model (`ollama pull qwen2.5:14b`) | Free (local) |
| **OpenRouter** | Add your API key in Settings | Per-token pricing |

The platform auto-detects available Ollama models and lists OpenRouter models when an API key is configured.

## Notifications

Each agent can have notification channels that receive the output after every run:

| Channel | Requirements |
|---------|-------------|
| **Email** | SMTP server credentials (Gmail, Fastmail, etc.) |
| **Telegram** | Bot token from [@BotFather](https://t.me/BotFather), chat ID |
| **WhatsApp** | [Twilio](https://www.twilio.com) account SID, auth token, phone numbers |

Configure notifications in the agent detail page under the **Notifications** tab.

## Built-in Tools

| Tool | Description |
|------|-------------|
| `web_search` | Search the web via DuckDuckGo |
| `file_reader` | Read local files (restricted to working directory) |
| `shell_command` | Execute shell commands (30s timeout) |

## API

All endpoints are under `/api`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/agents` | List all agents |
| `POST` | `/api/agents` | Create agent |
| `GET` | `/api/agents/:id` | Get agent |
| `PUT` | `/api/agents/:id` | Update agent |
| `DELETE` | `/api/agents/:id` | Delete agent |
| `GET` | `/api/agents/:id/code` | Get generated code + explainer |
| `POST` | `/api/agents/:id/run` | Trigger a run |
| `GET` | `/api/agents/:id/runs` | Run history |
| `GET` | `/api/agents/:id/notifications` | List notification channels |
| `POST` | `/api/agents/:id/notifications` | Add notification channel |
| `GET` | `/api/models` | List available models |
| `GET` | `/api/tools` | List available tools |
| `GET` | `/api/stats` | Dashboard statistics |
| `GET/PUT` | `/api/settings` | Platform settings |

## Configuration

Environment variables (prefix `AGENT_FORGE_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_FORGE_OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `AGENT_FORGE_OPENROUTER_API_KEY` | _(empty)_ | OpenRouter API key |
| `AGENT_FORGE_DATABASE_PATH` | `data/agent_forge.db` | SQLite database path |
| `AGENT_FORGE_AGENTS_DIR` | `agents` | Directory for generated agent files |
| `AGENT_FORGE_PORT` | `8000` | Server port |

## License

MIT
