import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.database import get_db
from backend.models.agent import AgentCreate, AgentResponse, AgentUpdate

router = APIRouter(prefix="/api/agents", tags=["agents"])


def _row_to_response(row) -> AgentResponse:
    return AgentResponse(
        id=row["id"],
        name=row["name"],
        model=row["model"],
        provider=row["provider"],
        system_prompt=row["system_prompt"],
        user_prompt_template=row["user_prompt_template"],
        tools=json.loads(row["tools_json"]),
        schedule=row["schedule"],
        is_active=bool(row["is_active"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.post("", status_code=201)
async def create_agent(body: AgentCreate) -> AgentResponse:
    db = await get_db()
    agent_id = uuid.uuid4().hex[:12]
    now = datetime.now(timezone.utc).isoformat()

    try:
        await db.execute(
            """INSERT INTO agents (id, name, model, provider, system_prompt,
               user_prompt_template, tools_json, schedule, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                agent_id,
                body.name,
                body.model,
                body.provider,
                body.system_prompt,
                body.user_prompt_template,
                json.dumps(body.tools),
                body.schedule,
                now,
                now,
            ),
        )
        await db.commit()
    except Exception as e:
        if "UNIQUE" in str(e):
            raise HTTPException(409, f"Agent named '{body.name}' already exists")
        raise

    # Generate agent file and explainer
    from backend.services.codegen import generate_agent_file
    from backend.services.explainer import generate_explainer

    row = await db.execute_fetchall(
        "SELECT * FROM agents WHERE id = ?", (agent_id,)
    )
    agent = _row_to_response(row[0])

    try:
        file_path = generate_agent_file(agent)
        generate_explainer(agent)
        agent.file_path = file_path
    except Exception:
        pass  # Don't fail the API call if file generation fails

    return agent


@router.get("")
async def list_agents() -> list[AgentResponse]:
    db = await get_db()
    rows = await db.execute_fetchall("SELECT * FROM agents ORDER BY created_at DESC")
    return [_row_to_response(r) for r in rows]


@router.get("/{agent_id}")
async def get_agent(agent_id: str) -> AgentResponse:
    db = await get_db()
    rows = await db.execute_fetchall("SELECT * FROM agents WHERE id = ?", (agent_id,))
    if not rows:
        raise HTTPException(404, "Agent not found")
    return _row_to_response(rows[0])


@router.put("/{agent_id}")
async def update_agent(agent_id: str, body: AgentUpdate) -> AgentResponse:
    db = await get_db()
    rows = await db.execute_fetchall("SELECT * FROM agents WHERE id = ?", (agent_id,))
    if not rows:
        raise HTTPException(404, "Agent not found")

    updates = body.model_dump(exclude_unset=True)
    if not updates:
        return _row_to_response(rows[0])

    if "tools" in updates:
        updates["tools_json"] = json.dumps(updates.pop("tools"))

    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [agent_id]
    await db.execute(f"UPDATE agents SET {set_clause} WHERE id = ?", values)
    await db.commit()

    rows = await db.execute_fetchall("SELECT * FROM agents WHERE id = ?", (agent_id,))
    agent = _row_to_response(rows[0])

    # Regenerate files
    from backend.services.codegen import generate_agent_file
    from backend.services.explainer import generate_explainer

    try:
        file_path = generate_agent_file(agent)
        generate_explainer(agent)
        agent.file_path = file_path
    except Exception:
        pass

    return agent


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str) -> None:
    db = await get_db()
    rows = await db.execute_fetchall("SELECT * FROM agents WHERE id = ?", (agent_id,))
    if not rows:
        raise HTTPException(404, "Agent not found")

    agent = _row_to_response(rows[0])

    # Remove generated files
    from backend.services.codegen import remove_agent_file
    from backend.services.explainer import remove_explainer

    try:
        remove_agent_file(agent)
        remove_explainer(agent)
    except Exception:
        pass

    await db.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
    await db.commit()


@router.get("/{agent_id}/code")
async def get_agent_code(agent_id: str) -> dict:
    db = await get_db()
    rows = await db.execute_fetchall("SELECT * FROM agents WHERE id = ?", (agent_id,))
    if not rows:
        raise HTTPException(404, "Agent not found")

    agent = _row_to_response(rows[0])

    from backend.services.codegen import get_agent_file_path
    from backend.services.explainer import get_explainer_path

    code_path = get_agent_file_path(agent)
    explainer_path = get_explainer_path(agent)

    code = code_path.read_text() if code_path.exists() else None
    explainer = explainer_path.read_text() if explainer_path.exists() else None

    return {"code": code, "explainer": explainer, "file_path": str(code_path)}
