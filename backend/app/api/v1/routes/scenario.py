from fastapi import APIRouter

from app.models.schemas import ScenarioRequest, ScenarioResponse
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.policy_parser_service import PolicyParserService
from app.services.prediction_service import PredictionService
from app.services.scenario_service import ScenarioService

router = APIRouter()
policy_parser = PolicyParserService()
feature_service = FeatureEngineeringService()
prediction_service = PredictionService()
scenario_service = ScenarioService()


@router.post("/simulate", response_model=ScenarioResponse)
def simulate_scenario(payload: ScenarioRequest) -> ScenarioResponse:
    country = payload.country.strip() or "India"
    parsed = policy_parser.parse(payload.policy_text)
    vector = feature_service.build_feature_vector(
        parsed_policy=parsed,
        economic_indicators={"gdp": 6.8, "inflation": 5.1, "repo_rate": 6.5},
        news_signals={"inflation_pressure": 0.35, "supply_shock": 0.25, "trade_disruption": 0.45},
    )
    prediction = prediction_service.predict(parsed, vector, country=country)
    return scenario_service.simulate(prediction, shock_factor=payload.shock_factor, country=country)

