from fastapi import APIRouter

from backend.database import get_db

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("")
async def get_settings() -> dict:
    db = await get_db()
    rows = await db.execute_fetchall("SELECT key, value FROM settings")
    result = {row["key"]: row["value"] for row in rows}
    # Mask API key in response
    if "openrouter_api_key" in result and result["openrouter_api_key"]:
        key = result["openrouter_api_key"]
        result["openrouter_api_key_masked"] = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
    return result


@router.put("")
async def update_settings(body: dict) -> dict:
    db = await get_db()
    for key, value in body.items():
        await db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?",
            (key, str(value), str(value)),
        )
    await db.commit()

    # Update runtime config if API key changed
    if "openrouter_api_key" in body:
        from backend.config import settings
        settings.openrouter_api_key = body["openrouter_api_key"]

    return {"status": "ok"}
