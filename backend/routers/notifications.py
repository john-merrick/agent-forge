import json
import uuid

from fastapi import APIRouter, HTTPException

from backend.database import get_db
from backend.models.notification import NotificationConfig, NotificationResponse

router = APIRouter(prefix="/api/agents", tags=["notifications"])


def _row_to_response(row) -> NotificationResponse:
    config = json.loads(row["config_json"])
    # Mask sensitive fields in response
    masked = {}
    for k, v in config.items():
        if any(s in k for s in ["pass", "token", "auth", "sid"]) and v:
            masked[k] = v[:4] + "..." + v[-4:] if len(str(v)) > 8 else "***"
        else:
            masked[k] = v
    return NotificationResponse(
        id=row["id"],
        agent_id=row["agent_id"],
        channel=row["channel"],
        config=masked,
        is_active=bool(row["is_active"]),
    )


@router.get("/{agent_id}/notifications")
async def list_notifications(agent_id: str) -> list[NotificationResponse]:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT * FROM notifications WHERE agent_id = ?", (agent_id,)
    )
    return [_row_to_response(r) for r in rows]


@router.post("/{agent_id}/notifications", status_code=201)
async def create_notification(agent_id: str, body: NotificationConfig) -> NotificationResponse:
    db = await get_db()

    # Verify agent exists
    agent_rows = await db.execute_fetchall("SELECT id FROM agents WHERE id = ?", (agent_id,))
    if not agent_rows:
        raise HTTPException(404, "Agent not found")

    notif_id = uuid.uuid4().hex[:12]
    config_data = body.model_dump(exclude={"channel", "is_active"})
    # Only store non-empty config values
    config_data = {k: v for k, v in config_data.items() if v}

    await db.execute(
        "INSERT INTO notifications (id, agent_id, channel, config_json, is_active) VALUES (?, ?, ?, ?, ?)",
        (notif_id, agent_id, body.channel, json.dumps(config_data), int(body.is_active)),
    )
    await db.commit()

    rows = await db.execute_fetchall("SELECT * FROM notifications WHERE id = ?", (notif_id,))
    return _row_to_response(rows[0])


@router.delete("/{agent_id}/notifications/{notif_id}", status_code=204)
async def delete_notification(agent_id: str, notif_id: str) -> None:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT id FROM notifications WHERE id = ? AND agent_id = ?", (notif_id, agent_id)
    )
    if not rows:
        raise HTTPException(404, "Notification not found")
    await db.execute("DELETE FROM notifications WHERE id = ?", (notif_id,))
    await db.commit()


@router.put("/{agent_id}/notifications/{notif_id}/toggle")
async def toggle_notification(agent_id: str, notif_id: str) -> NotificationResponse:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT * FROM notifications WHERE id = ? AND agent_id = ?", (notif_id, agent_id)
    )
    if not rows:
        raise HTTPException(404, "Notification not found")

    new_state = 0 if rows[0]["is_active"] else 1
    await db.execute("UPDATE notifications SET is_active = ? WHERE id = ?", (new_state, notif_id))
    await db.commit()

    rows = await db.execute_fetchall("SELECT * FROM notifications WHERE id = ?", (notif_id,))
    return _row_to_response(rows[0])
