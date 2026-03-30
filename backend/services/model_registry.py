import httpx

from backend.config import settings


async def check_ollama_status() -> bool:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{settings.ollama_base_url}/api/tags")
            return r.status_code == 200
    except Exception:
        return False


async def list_ollama_models() -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{settings.ollama_base_url}/api/tags")
            r.raise_for_status()
            data = r.json()
            return [
                {
                    "id": m["name"],
                    "name": m["name"],
                    "provider": "ollama",
                    "context_length": None,
                    "pricing": {"input": 0, "output": 0},
                }
                for m in data.get("models", [])
            ]
    except Exception:
        return []


async def list_openrouter_models() -> list[dict]:
    if not settings.openrouter_api_key:
        return []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
            )
            r.raise_for_status()
            data = r.json()
            return [
                {
                    "id": m["id"],
                    "name": m.get("name", m["id"]),
                    "provider": "openrouter",
                    "context_length": m.get("context_length"),
                    "pricing": m.get("pricing", {}),
                }
                for m in data.get("data", [])
            ]
    except Exception:
        return []


async def list_litellm_models() -> list[dict]:
    """List models available through the LiteLLM proxy."""
    if not settings.litellm_api_key:
        return []
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(
                f"{settings.litellm_base_url}/models",
                headers={"Authorization": f"Bearer {settings.litellm_api_key}"},
            )
            r.raise_for_status()
            data = r.json()
            return [
                {
                    "id": m["id"],
                    "name": m["id"],
                    "provider": "litellm",
                    "context_length": None,
                    "pricing": {},
                }
                for m in data.get("data", [])
            ]
    except Exception:
        return []


async def list_all_models() -> list[dict]:
    litellm = await list_litellm_models()
    # If LiteLLM is configured, it already proxies both cloud + Ollama models
    if litellm:
        return litellm
    # Fallback: list directly from providers
    ollama = await list_ollama_models()
    openrouter = await list_openrouter_models()
    return ollama + openrouter
