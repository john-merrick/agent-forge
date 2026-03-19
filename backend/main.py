import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.database import get_db, close_db
from backend.routers import agents, models, notifications, runs, settings
from backend.services.scheduler import get_scheduler, load_all_schedules

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await get_db()
    logger.info("Database initialized")

    scheduler = get_scheduler()
    await load_all_schedules()
    scheduler.start()
    logger.info("Scheduler started")

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    await close_db()
    logger.info("Shutdown complete")


app = FastAPI(title="Agent Forge", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router)
app.include_router(models.router)
app.include_router(notifications.router)
app.include_router(runs.router)
app.include_router(settings.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/tools")
async def list_tools():
    from backend.tools.registry import list_tools
    return {"tools": list_tools()}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# Serve frontend static files in production (Docker)
_static_dir = Path(__file__).parent.parent / "frontend" / "dist"
if _static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(_static_dir / "assets")), name="static")

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        # Serve the file if it exists, otherwise return index.html (SPA routing)
        file = _static_dir / path
        if file.is_file():
            return FileResponse(str(file))
        return FileResponse(str(_static_dir / "index.html"))
