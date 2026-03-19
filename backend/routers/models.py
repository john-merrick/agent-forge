from fastapi import APIRouter

from backend.services.model_registry import list_all_models, check_ollama_status

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("")
async def get_models() -> dict:
    models = await list_all_models()
    return {"models": models}


@router.get("/ollama/status")
async def ollama_status() -> dict:
    reachable = await check_ollama_status()
    return {"reachable": reachable}
