import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone

from backend.config import settings
from backend.database import get_db
from backend.services.codegen import get_agent_file_path
from backend.services.cost import estimate_cost


async def run_agent(agent_id: str, input_data: dict | None = None) -> dict:
    db = await get_db()
    rows = await db.execute_fetchall("SELECT * FROM agents WHERE id = ?", (agent_id,))
    if not rows:
        return {"error": "Agent not found"}

    agent = rows[0]
    run_id = uuid.uuid4().hex[:12]
    started_at = datetime.now(timezone.utc).isoformat()

    await db.execute(
        "INSERT INTO runs (id, agent_id, status, started_at, input_data) VALUES (?, ?, ?, ?, ?)",
        (run_id, agent_id, "running", started_at, json.dumps(input_data) if input_data else None),
    )
    await db.commit()

    # Resolve agent file
    from backend.models.agent import AgentResponse

    agent_resp = AgentResponse(
        id=agent["id"],
        name=agent["name"],
        model=agent["model"],
        provider=agent["provider"],
        system_prompt=agent["system_prompt"],
        user_prompt_template=agent["user_prompt_template"],
        tools=json.loads(agent["tools_json"]),
        schedule=agent["schedule"],
        is_active=bool(agent["is_active"]),
        created_at=agent["created_at"],
        updated_at=agent["updated_at"],
    )

    file_path = get_agent_file_path(agent_resp)
    if not file_path.exists():
        await _finish_run(db, run_id, "error", started_at, error="Agent file not found")
        return {"error": "Agent file not found", "run_id": run_id}

    # Build environment
    env = os.environ.copy()
    if agent["provider"] == "openrouter":
        # Get API key from settings table
        key_rows = await db.execute_fetchall(
            "SELECT value FROM settings WHERE key = 'openrouter_api_key'"
        )
        if key_rows:
            env["OPENROUTER_API_KEY"] = key_rows[0]["value"]
        elif settings.openrouter_api_key:
            env["OPENROUTER_API_KEY"] = settings.openrouter_api_key

    env["OLLAMA_BASE_URL"] = settings.ollama_base_url

    if input_data:
        env["AGENT_INPUT"] = json.dumps(input_data)

    # Run as subprocess
    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, str(file_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)

        output = stdout.decode().strip()
        error_output = stderr.decode().strip()

        # Try to parse structured output
        tokens_in = 0
        tokens_out = 0
        try:
            result = json.loads(output)
            tokens_in = result.get("tokens_in", 0)
            tokens_out = result.get("tokens_out", 0)
        except (json.JSONDecodeError, TypeError):
            pass

        cost = estimate_cost(agent["model"], agent["provider"], tokens_in, tokens_out)

        if proc.returncode == 0:
            await _finish_run(
                db, run_id, "success", started_at,
                output=output, tokens_in=tokens_in, tokens_out=tokens_out, cost=cost,
            )
            run_data = {"status": "success", "output_data": output,
                        "tokens_in": tokens_in, "tokens_out": tokens_out,
                        "latency_ms": 0}
        else:
            await _finish_run(
                db, run_id, "error", started_at,
                output=output, error=error_output or f"Exit code {proc.returncode}",
                tokens_in=tokens_in, tokens_out=tokens_out, cost=cost,
            )
            run_data = {"status": "error", "output_data": output,
                        "error": error_output, "tokens_in": tokens_in,
                        "tokens_out": tokens_out, "latency_ms": 0}

        # Send notifications
        from backend.services.notifier import send_notifications
        await send_notifications(agent_id, agent["name"], run_data)

    except asyncio.TimeoutError:
        proc.kill()
        await _finish_run(db, run_id, "error", started_at, error="Timeout after 120s")

    except Exception as e:
        await _finish_run(db, run_id, "error", started_at, error=str(e))

    return {"run_id": run_id}


async def _finish_run(
    db, run_id: str, status: str, started_at: str,
    output: str | None = None, error: str | None = None,
    tokens_in: int = 0, tokens_out: int = 0, cost: float = 0.0,
) -> None:
    completed_at = datetime.now(timezone.utc).isoformat()
    started = datetime.fromisoformat(started_at)
    completed = datetime.fromisoformat(completed_at)
    latency_ms = int((completed - started).total_seconds() * 1000)

    await db.execute(
        """UPDATE runs SET status=?, completed_at=?, output_data=?, error=?,
           tokens_in=?, tokens_out=?, cost_estimate=?, latency_ms=?
           WHERE id=?""",
        (status, completed_at, output, error, tokens_in, tokens_out, cost, latency_ms, run_id),
    )
    await db.commit()
