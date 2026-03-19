import json
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.database import get_db

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


async def _run_scheduled_agent(agent_id: str) -> None:
    from backend.services.runner import run_agent
    logger.info(f"Scheduled run for agent {agent_id}")
    await run_agent(agent_id)


def add_job(agent_id: str, cron_expression: str) -> None:
    scheduler = get_scheduler()
    # Remove existing job if any
    remove_job(agent_id)

    parts = cron_expression.split()
    if len(parts) == 5:
        trigger = CronTrigger(
            minute=parts[0],
            hour=parts[1],
            day=parts[2],
            month=parts[3],
            day_of_week=parts[4],
        )
    else:
        logger.warning(f"Invalid cron expression: {cron_expression}")
        return

    scheduler.add_job(
        _run_scheduled_agent,
        trigger=trigger,
        args=[agent_id],
        id=f"agent_{agent_id}",
        replace_existing=True,
    )
    logger.info(f"Scheduled agent {agent_id} with cron: {cron_expression}")


def remove_job(agent_id: str) -> None:
    scheduler = get_scheduler()
    job_id = f"agent_{agent_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)


async def load_all_schedules() -> None:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT id, schedule FROM agents WHERE schedule IS NOT NULL AND is_active = 1"
    )
    for row in rows:
        add_job(row["id"], row["schedule"])
    logger.info(f"Loaded {len(rows)} scheduled agents")


def list_jobs() -> list[dict]:
    scheduler = get_scheduler()
    return [
        {
            "id": job.id,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
        }
        for job in scheduler.get_jobs()
    ]
