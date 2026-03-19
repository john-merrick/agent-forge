.PHONY: install dev dev-backend dev-frontend build

install:
	uv venv
	uv pip install fastapi uvicorn pydantic pydantic-settings aiosqlite jinja2 apscheduler httpx python-dotenv
	cd frontend && npm install

dev-backend:
	.venv/bin/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

dev:
	@echo "Run in two terminals:"
	@echo "  make dev-backend"
	@echo "  make dev-frontend"

build:
	cd frontend && npm run build
