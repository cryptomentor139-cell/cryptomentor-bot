from fastapi import FastAPI

from app.api.routes_admin import router as admin_router
from app.api.routes_health import router as health_router
from app.api.routes_pairs import router as pairs_router
from app.api.routes_status import router as status_router
from app.api.routes_trades import router as trades_router
from app.utils.logging import configure_logging

configure_logging()

app = FastAPI(title="SMC Trading Engine", version="0.1.0")
app.include_router(health_router)
app.include_router(pairs_router)
app.include_router(status_router)
app.include_router(trades_router)
app.include_router(admin_router)
