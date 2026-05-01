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
        impacts: list[DomainImpact] = []
        for domain, model in registry.items():
            predicted, raw_importance = model.predict(feature_vector)
            direction = "neutral"
            if predicted > 0.05:
                direction = "increase"
            elif predicted < -0.05:
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

