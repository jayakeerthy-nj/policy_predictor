from fastapi import APIRouter

from app.api.v1.routes.graph import router as graph_router
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.ingestion import router as ingestion_router
from app.api.v1.routes.policy import router as policy_router
from app.api.v1.routes.prediction import router as prediction_router
from app.api.v1.routes.scenario import router as scenario_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(ingestion_router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(policy_router, prefix="/policy", tags=["policy"])
api_router.include_router(prediction_router, prefix="/prediction", tags=["prediction"])
api_router.include_router(scenario_router, prefix="/scenario", tags=["scenario"])
api_router.include_router(graph_router, prefix="/graph", tags=["graph"])

