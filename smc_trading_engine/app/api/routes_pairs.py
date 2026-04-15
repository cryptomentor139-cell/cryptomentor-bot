from fastapi import APIRouter

from app.config.pairs import DEFAULT_PAIRS

router = APIRouter(tags=["pairs"])


@router.get("/pairs")
async def pairs():
    return {"pairs": DEFAULT_PAIRS}
