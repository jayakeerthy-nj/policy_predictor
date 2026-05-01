def add_time_window_features(indicators: dict[str, float]) -> dict[str, float]:
    enriched = dict(indicators)
    for key, value in indicators.items():
        enriched[f"{key}_lag_1"] = value * 0.98
        enriched[f"{key}_lag_3"] = value * 0.95
        enriched[f"{key}_rolling_mean_3"] = value * 0.97
        enriched[f"{key}_rolling_volatility_3"] = abs(value) * 0.04
    return enriched

