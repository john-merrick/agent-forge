# Stage 1: Build frontend
FROM node:22-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Production image
FROM python:3.13-slim
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    pydantic \
    pydantic-settings \
    aiosqlite \
    jinja2 \
    apscheduler \
    httpx \
    python-dotenv

# Copy backend
COPY backend/ backend/

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist frontend/dist

# Create directories for runtime data
RUN mkdir -p agents data

# Expose port
EXPOSE 8000

# Environment defaults — Ollama uses host.docker.internal to reach host machine
ENV AGENT_FORGE_OLLAMA_BASE_URL=http://host.docker.internal:11434
ENV AGENT_FORGE_DATABASE_PATH=data/agent_forge.db
ENV AGENT_FORGE_AGENTS_DIR=agents

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
