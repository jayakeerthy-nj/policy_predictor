from statistics import mean

from app.models.schemas import PolicyParseResponse

# Typical scale (approximate real-world range) for each economic indicator.
# Used to normalise raw values from WorldBank/news into the [-1, 1] ballpark
# that the model was trained on.  Values larger than these scales are clipped.
_INDICATOR_SCALES: dict[str, float] = {
    "gdp": 10.0,            # GDP growth rate: typically -5% to +10%
    "inflation": 10.0,      # Inflation rate: typically 0% to 10%
    "unemployment": 20.0,   # Unemployment: typically 2% to 20%
    "repo_rate": 10.0,      # Repo/policy rate: typically 2% to 10%
    "inflation_pressure": 1.0,   # Already normalised signal [0,1]
    "supply_shock": 1.0,         # Already normalised signal [0,1]
    "trade_disruption": 1.0,     # Already normalised signal [0,1]
}
_DEFAULT_SCALE = 10.0  # Fallback for any unknown numeric indicator


def _normalise(indicator: str, value: float) -> float:
    """Scale a raw indicator value to roughly the [-1, 1] range."""
    scale = _INDICATOR_SCALES.get(indicator, _DEFAULT_SCALE)
    return max(-1.5, min(1.5, value / scale))


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

        # Normalise raw economic indicators so they match the training distribution.
        normalised_indicators = {k: _normalise(k, v) for k, v in economic_indicators.items()}
        normalised_news = {k: _normalise(k, v) for k, v in news_signals.items()}

        feature_vector: dict[str, float] = {
            "policy_direction": direction_map[parsed_policy.direction],
            "policy_intensity": intensity_map[parsed_policy.intensity],
            "policy_confidence": parsed_policy.confidence,
            "sector_count": min(1.0, float(len(parsed_policy.sectors)) / 5.0),
            "variable_count": min(1.0, float(len(parsed_policy.variables)) / 5.0),
            "macro_mean": mean(normalised_indicators.values()) if normalised_indicators else 0.0,
        }
        feature_vector.update(normalised_indicators)
        feature_vector.update(normalised_news)
        if overrides:
            feature_vector.update(overrides)
        return feature_vector
