from fastapi import APIRouter

from app.connectors.newsapi_connector import NewsAPIConnector
from app.connectors.worldbank_connector import WorldBankConnector
from app.models.schemas import ImpactPredictionRequest, ImpactPredictionResponse
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.policy_parser_service import PolicyParserService
from app.services.prediction_service import PredictionService
from app.utils.news_signal_extractor import aggregate_news_signals, extract_news_signals
from app.utils.normalization import summarize_latest_indicators

router = APIRouter()
policy_parser = PolicyParserService()
feature_service = FeatureEngineeringService()
prediction_service = PredictionService()


@router.post("/impact", response_model=ImpactPredictionResponse)
def predict_policy_impact(payload: ImpactPredictionRequest) -> ImpactPredictionResponse:
    country = payload.country.strip() or "India"
    parsed = policy_parser.parse(payload.policy_text)
    indicators_raw = WorldBankConnector().fetch(start_date=None, end_date=None)
    indicators = summarize_latest_indicators(indicators_raw)
    news_raw = NewsAPIConnector().fetch(start_date=None, end_date=None)
    news_signals = aggregate_news_signals(extract_news_signals(news_raw))
    vector = feature_service.build_feature_vector(
        parsed_policy=parsed,
        economic_indicators=indicators,
        news_signals=news_signals,
        overrides=payload.context_overrides,
    )
    return prediction_service.predict(parsed_policy=parsed, feature_vector=vector, country=country)

