from fastapi import APIRouter

from app.connectors.newsapi_connector import NewsAPIConnector
from app.connectors.worldbank_connector import WorldBankConnector
from app.models.schemas import ScenarioRequest, ScenarioResponse
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.policy_parser_service import PolicyParserService
from app.services.prediction_service import PredictionService
from app.services.scenario_service import ScenarioService
from app.utils.news_signal_extractor import aggregate_news_signals, extract_news_signals
from app.utils.normalization import summarize_latest_indicators

router = APIRouter()
policy_parser = PolicyParserService()
feature_service = FeatureEngineeringService()
prediction_service = PredictionService()
scenario_service = ScenarioService()


@router.post("/simulate", response_model=ScenarioResponse)
def simulate_scenario(payload: ScenarioRequest) -> ScenarioResponse:
    country = payload.country.strip() or "India"
    parsed = policy_parser.parse(payload.policy_text)
    # Fetch real indicators instead of hardcoded static values
    indicators_raw = WorldBankConnector().fetch(start_date=None, end_date=None)
    indicators = summarize_latest_indicators(indicators_raw)
    news_raw = NewsAPIConnector().fetch(start_date=None, end_date=None)
    news_signals = aggregate_news_signals(extract_news_signals(news_raw))
    vector = feature_service.build_feature_vector(
        parsed_policy=parsed,
        economic_indicators=indicators,
        news_signals=news_signals,
        overrides=payload.context_overrides if hasattr(payload, "context_overrides") else None,
    )
    prediction = prediction_service.predict(parsed, vector, country=country)
    return scenario_service.simulate(prediction, shock_factor=payload.shock_factor, country=country)


