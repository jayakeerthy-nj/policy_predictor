from datetime import datetime
from uuid import uuid4

from app.connectors.gemini_connector import GeminiConnector
from app.models.schemas import ImpactPredictionResponse, ScenarioPoint, ScenarioResponse


class ScenarioService:
    def __init__(self) -> None:
        self.gemini = GeminiConnector()

    def simulate(
        self,
        prediction: ImpactPredictionResponse,
        shock_factor: float,
        country: str = "India",
    ) -> ScenarioResponse:
        points: list[ScenarioPoint] = []
        for impact in prediction.impacts:
            baseline = impact.impact_percent
            shock = baseline * (1 + shock_factor)
            policy_adjusted = baseline * (1 - (0.5 * shock_factor))
            points.append(
                ScenarioPoint(
                    domain=impact.domain,
                    baseline=round(baseline, 2),
                    shock=round(shock, 2),
                    policy_adjusted=round(policy_adjusted, 2),
                )
            )

        payload = {"prediction_id": prediction.prediction_id, "scenarios": [p.model_dump() for p in points]}
        explanation = self.gemini.generate_scenario_explanation(payload)
        return ScenarioResponse(
            scenario_id=str(uuid4()),
            country=country,
            scenarios=points,
            explanation=explanation,
            generated_at=datetime.utcnow(),
        )

