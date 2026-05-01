from fastapi import APIRouter

from app.models.schemas import PolicyParseRequest, PolicyParseResponse
from app.services.policy_parser_service import PolicyParserService

router = APIRouter()
service = PolicyParserService()


@router.post("/parse", response_model=PolicyParseResponse)
def parse_policy(payload: PolicyParseRequest) -> PolicyParseResponse:
    return service.parse(payload.policy_text)

