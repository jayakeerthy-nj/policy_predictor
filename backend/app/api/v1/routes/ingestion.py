from fastapi import APIRouter

from app.models.schemas import IngestionRunRequest, IngestionRunResponse
from app.services.ingestion_service import IngestionService

router = APIRouter()
service = IngestionService()


@router.post("/run", response_model=IngestionRunResponse)
def run_ingestion(payload: IngestionRunRequest) -> IngestionRunResponse:
    return service.run(payload)

