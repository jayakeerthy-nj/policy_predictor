from app.models.schemas import PolicyParseResponse
from app.services.prediction_service import PredictionService


def test_prediction_returns_all_domains():
    parsed = PolicyParseResponse(
        policy_type="monetary",
        sectors=["markets", "inflation"],
        variables=["repo rate", "inflation"],
        direction="decrease",
        intensity="low",
        confidence=0.7,
        method="rule_engine",
    )
    vector = {
        "policy_direction": -1.0,
        "policy_intensity": 0.3,
        "policy_confidence": 0.7,
        "inflation_pressure": 0.5,
    }
    output = PredictionService().predict(parsed, vector)
    assert len(output.impacts) == 5
    assert all(i.feature_importance for i in output.impacts)

