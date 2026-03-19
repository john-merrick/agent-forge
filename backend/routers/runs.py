import asyncio

from fastapi import APIRouter, HTTPException

from backend.database import get_db
from backend.models.run import RunRecord, RunTrigger

router = APIRouter(prefix="/api", tags=["runs"])


def _row_to_record(row) -> RunRecord:
    return RunRecord(
        id=row["id"],
        agent_id=row["agent_id"],
        status=row["status"],
        started_at=row["started_at"],
        completed_at=row["completed_at"],
        input_data=row["input_data"],
        output_data=row["output_data"],
        tokens_in=row["tokens_in"],
        tokens_out=row["tokens_out"],
        cost_estimate=row["cost_estimate"],
        latency_ms=row["latency_ms"],
        error=row["error"],
    )


@router.post("/agents/{agent_id}/run", status_code=202)
async def trigger_run(agent_id: str, body: RunTrigger | None = None) -> dict:
    db = await get_db()
    rows = await db.execute_fetchall("SELECT id FROM agents WHERE id = ?", (agent_id,))
    if not rows:
        raise HTTPException(404, "Agent not found")

    from backend.services.runner import run_agent

    input_data = body.input_data if body else None
    # Run in background so the API returns immediately
    task = asyncio.create_task(run_agent(agent_id, input_data))

    # Get the run ID from the task once the record is created
    # For now, return a pending status
    return {"status": "accepted", "agent_id": agent_id}


@router.get("/agents/{agent_id}/runs")
async def list_runs(agent_id: str, limit: int = 50, offset: int = 0) -> list[RunRecord]:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT * FROM runs WHERE agent_id = ? ORDER BY started_at DESC LIMIT ? OFFSET ?",
        (agent_id, limit, offset),
    )
    return [_row_to_record(r) for r in rows]


@router.get("/runs/recent")
async def recent_runs(limit: int = 20) -> list[RunRecord]:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT * FROM runs ORDER BY started_at DESC LIMIT ?", (limit,)
    )
    return [_row_to_record(r) for r in rows]


@router.get("/runs/{run_id}")
async def get_run(run_id: str) -> RunRecord:
    db = await get_db()
    rows = await db.execute_fetchall("SELECT * FROM runs WHERE id = ?", (run_id,))
    if not rows:
        raise HTTPException(404, "Run not found")
    return _row_to_record(rows[0])


@router.get("/stats")
async def get_stats() -> dict:
    db = await get_db()

    agent_count = await db.execute_fetchall("SELECT COUNT(*) as c FROM agents")
    total_runs = await db.execute_fetchall("SELECT COUNT(*) as c FROM runs")
    today_runs = await db.execute_fetchall(
        "SELECT COUNT(*) as c FROM runs WHERE started_at >= date('now')"
    )
    today_cost = await db.execute_fetchall(
        "SELECT COALESCE(SUM(cost_estimate), 0) as c FROM runs WHERE started_at >= date('now')"
    )
    error_runs = await db.execute_fetchall(
        "SELECT COUNT(*) as c FROM runs WHERE status = 'error' AND started_at >= date('now')"
    )

    return {
        "total_agents": agent_count[0]["c"],
        "total_runs": total_runs[0]["c"],
        "runs_today": today_runs[0]["c"],
        "cost_today": round(today_cost[0]["c"], 4),
        "errors_today": error_runs[0]["c"],
    }
