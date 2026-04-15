from fastapi import APIRouter

router = APIRouter(tags=["admin"])


@router.get("/admin/echo")
async def admin_echo():
    return {"ok": True}
