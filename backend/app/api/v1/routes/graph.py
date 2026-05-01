from fastapi import APIRouter

from app.models.schemas import DependencyGraphResponse
from app.services.dependency_graph_service import DependencyGraphService
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.policy_parser_service import PolicyParserService
from app.services.prediction_service import PredictionService

router = APIRouter()
graph_service = DependencyGraphService()
policy_parser = PolicyParserService()
feature_service = FeatureEngineeringService()
prediction_service = PredictionService()


@router.get("/dependencies", response_model=DependencyGraphResponse)
def get_dependencies() -> DependencyGraphResponse:
    parsed = policy_parser.parse("Increase tariff on strategic imports by 10 percent.")
    vector = feature_service.build_feature_vector(
        parsed_policy=parsed,
        economic_indicators={"gdp": 6.8, "inflation": 5.1, "repo_rate": 6.5},
        news_signals={"inflation_pressure": 0.4, "supply_shock": 0.2, "trade_disruption": 0.5},
    )
    prediction = prediction_service.predict(parsed, vector, country="India")
    return graph_service.build_response(prediction.impacts)

