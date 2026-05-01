import re

from transformers import pipeline

from app.core.config import settings
from app.models.schemas import PolicyParseResponse


class PolicyParserService:
    def __init__(self) -> None:
        self._classifier = None

    def _get_classifier(self):
        if self._classifier is None:
            try:
                self._classifier = pipeline(
                    "text-classification",
                    model=settings.hf_model_name,
                )
            except Exception:
                self._classifier = None
        return self._classifier

    def parse(self, policy_text: str) -> PolicyParseResponse:
        classifier = self._get_classifier()
        model_conf = 0.0
        if classifier is not None:
            try:
                result = classifier(policy_text[:512])[0]
                model_conf = float(result.get("score", 0.0))
            except Exception:
                model_conf = 0.0

        rule_resp = self._rule_parse(policy_text)
        if model_conf < settings.policy_confidence_threshold:
            rule_resp.method = "rule_fallback"
            rule_resp.confidence = max(rule_resp.confidence, 0.55)
            return rule_resp

        rule_resp.method = "hybrid_hf_rule"
        rule_resp.confidence = min(0.95, 0.65 + (model_conf / 3))
        return rule_resp

    def _rule_parse(self, policy_text: str) -> PolicyParseResponse:
        text = policy_text.lower()
        sectors = []
        for keyword, sector in [
            ("health", "healthcare"),
            ("hospital", "healthcare"),
            ("import", "trade"),
            ("export", "trade"),
            ("fuel", "commodities"),
            ("agri", "commodities"),
            ("stock", "markets"),
            ("bank", "markets"),
        ]:
            if keyword in text and sector not in sectors:
                sectors.append(sector)

        variables = []
        for var in ["inflation", "gdp", "repo rate", "interest rate", "unemployment"]:
            if var in text:
                variables.append(var)

        direction = "increase"
        if re.search(r"\b(reduce|cut|decrease|lower)\b", text):
            direction = "decrease"
        elif re.search(r"\b(maintain|stable|unchanged)\b", text):
            direction = "neutral"

        intensity = "medium"
        if re.search(r"\b(slight|minor|small)\b", text):
            intensity = "low"
        elif re.search(r"\b(major|aggressive|significant|strong)\b", text):
            intensity = "high"

        policy_type = "fiscal"
        if any(k in text for k in ["repo", "interest rate", "liquidity"]):
            policy_type = "monetary"
        elif "tariff" in text:
            policy_type = "trade"

        return PolicyParseResponse(
            policy_type=policy_type,
            sectors=sectors or ["markets", "inflation"],
            variables=variables or ["inflation", "gdp"],
            direction=direction,  # type: ignore[arg-type]
            intensity=intensity,  # type: ignore[arg-type]
            confidence=0.6,
            method="rule_engine",
        )

