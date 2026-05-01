def score_confidence(impact: float, policy_confidence: float) -> float:
    normalized_impact = min(1.0, abs(impact) / 5.0)
    return round(min(0.98, 0.45 + 0.35 * policy_confidence + 0.2 * normalized_impact), 3)

