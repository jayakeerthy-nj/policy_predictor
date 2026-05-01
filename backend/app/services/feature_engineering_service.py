from statistics import mean

from app.models.schemas import PolicyParseResponse


class FeatureEngineeringService:
    def build_feature_vector(
        self,
        parsed_policy: PolicyParseResponse,
        economic_indicators: dict[str, float],
        news_signals: dict[str, float],
        overrides: dict[str, float] | None = None,
    ) -> dict[str, float]:
        intensity_map = {"low": 0.3, "medium": 0.6, "high": 1.0}
        direction_map = {"increase": 1.0, "decrease": -1.0, "neutral": 0.0}

        feature_vector: dict[str, float] = {
            "policy_direction": direction_map[parsed_policy.direction],
            "policy_intensity": intensity_map[parsed_policy.intensity],
            "policy_confidence": parsed_policy.confidence,
            "sector_count": float(len(parsed_policy.sectors)),
            "variable_count": float(len(parsed_policy.variables)),
            "macro_mean": mean(economic_indicators.values()) if economic_indicators else 0.0,
        }
        feature_vector.update(economic_indicators)
        feature_vector.update(news_signals)
        if overrides:
            feature_vector.update(overrides)
        return feature_vector

