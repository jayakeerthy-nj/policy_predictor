def linear_baseline_score(feature_vector: dict[str, float]) -> float:
    # Lightweight deterministic baseline for sanity checks.
    weighted = (
        0.2 * feature_vector.get("policy_direction", 0.0)
        + 0.3 * feature_vector.get("policy_intensity", 0.0)
        + 0.2 * feature_vector.get("inflation_pressure", 0.0)
        + 0.15 * feature_vector.get("supply_shock", 0.0)
        + 0.15 * feature_vector.get("trade_disruption", 0.0)
    )
    return round(weighted, 4)

