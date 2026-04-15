from fastapi import APIRouter

router = APIRouter(tags=["status"])


@router.get("/status")
async def status():
    return {"engine": "idle"}
