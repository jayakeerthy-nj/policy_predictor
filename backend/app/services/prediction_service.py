from datetime import datetime
from uuid import uuid4

from app.ml.registry import build_domain_registry
from app.models.schemas import DomainImpact, ImpactPredictionResponse, PolicyParseResponse
from app.utils.confidence import score_confidence


class PredictionService:
    def predict(
        self,
        parsed_policy: PolicyParseResponse,
        feature_vector: dict[str, float],
        country: str = "India",
    ) -> ImpactPredictionResponse:
        feature_names = sorted(feature_vector.keys())
        registry = build_domain_registry(feature_names=feature_names)

        # Sectors directly mentioned in policy get direction enforced.
        primary_sectors = set(parsed_policy.sectors)
        direction_sign = {
            "increase": 1.0,
            "decrease": -1.0,
            "neutral": 0.0,
        }[parsed_policy.direction]
        intensity_scale = {"low": 0.4, "medium": 0.7, "high": 1.0}[parsed_policy.intensity]

        impacts: list[DomainImpact] = []
        for domain, model in registry.items():
            raw_predicted, raw_importance = model.predict(feature_vector)

            # ── Clamp to realistic bounds ──────────────────────────────────
            # A single policy realistically moves a domain by -15% to +15%.
            MAX_IMPACT = 0.15  # 15%
            clamped = max(-MAX_IMPACT, min(MAX_IMPACT, raw_predicted))

            if domain in primary_sectors and parsed_policy.direction != "neutral":
                # Primary sector: enforce sign from parser, keep model magnitude.
                magnitude = abs(clamped) * intensity_scale
                predicted = direction_sign * max(magnitude, 0.01)
            else:
                # Secondary / ripple sectors: attenuate and keep model sign.
                predicted = clamped * intensity_scale * 0.6

            direction = "neutral"
            if predicted > 0.005:
                direction = "increase"
            elif predicted < -0.005:
                direction = "decrease"

            total = sum(raw_importance.values()) or 1.0
            importance = dict(
                sorted(
                    {k: round(v / total, 4) for k, v in raw_importance.items()}.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )[:5]
            )
            impacts.append(
                DomainImpact(
                    domain=domain,  # type: ignore[arg-type]
                    impact_percent=round(predicted * 100, 2),
                    direction=direction,  # type: ignore[arg-type]
                    confidence=score_confidence(predicted, parsed_policy.confidence),
                    feature_importance=importance,
                )
            )
        return ImpactPredictionResponse(
            prediction_id=str(uuid4()),
            country=country,
            parsed_policy=parsed_policy,
            impacts=impacts,
            generated_at=datetime.utcnow(),
        )
