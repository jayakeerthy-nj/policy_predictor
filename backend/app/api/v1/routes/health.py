from fastapi import APIRouter
from sqlalchemy import text

from app.cache.redis_client import redis_health
from app.core.config import settings
from app.models.schemas import HealthResponse
from app.db.session import engine

router = APIRouter()


@router.get("", response_model=HealthResponse)
def health() -> HealthResponse:
    postgres = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        postgres = "degraded"
    gemini = "ok" if settings.gemini_api_key else "not_configured"
    return HealthResponse(
        status="ok" if postgres == "ok" else "degraded",
        postgres=postgres,
        redis=redis_health(),
        gemini=gemini,
    )

