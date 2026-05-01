from app.models.schemas import PolicyParseResponse
from app.services.feature_engineering_service import FeatureEngineeringService


def test_feature_vector_has_core_fields():
    parser_output = PolicyParseResponse(
        policy_type="trade",
        sectors=["trade"],
        variables=["inflation"],
        direction="increase",
        intensity="medium",
        confidence=0.8,
        method="rule_engine",
    )
    vector = FeatureEngineeringService().build_feature_vector(
        parsed_policy=parser_output,
        economic_indicators={"gdp": 7.0},
        news_signals={"inflation_pressure": 0.4, "supply_shock": 0.2, "trade_disruption": 0.3},
    )
    assert "policy_intensity" in vector
    assert "gdp" in vector
    assert "inflation_pressure" in vector

