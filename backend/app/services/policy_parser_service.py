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

        # ── External shock detection ──────────────────────────────────────────
        # Phrases like "X puts/imposes tariffs/sanctions ON India/Indian ..."
        # represent an external negative shock: bad for India regardless of verb.
        _external_negative = bool(re.search(
            r"(us|usa|china|europe|eu|uk|foreign|external|global)\b.{0,60}"
            r"\b(tariff|sanction|ban|restrict|levy|duty|impose|block).{0,40}"
            r"\b(india|indian|on india)",
            text,
        ) or re.search(
            r"\b(tariff|sanction|ban|restrict|levy|duty|impose|block).{0,40}"
            r"\b(india|indian).{0,40}\b(export|import|goods|product|service)",
            text,
        ))

        sectors = []
        for keyword, sector in [
            # Healthcare
            ("health", "healthcare"),
            ("hospital", "healthcare"),
            ("medical", "healthcare"),
            ("pharma", "healthcare"),
            ("drug", "healthcare"),
            ("vaccine", "healthcare"),
            # Trade
            ("import", "trade"),
            ("export", "trade"),
            ("tariff", "trade"),
            ("trade", "trade"),
            ("customs", "trade"),
            ("duty", "trade"),
            # Commodities
            ("fuel", "commodities"),
            ("agri", "commodities"),
            ("oil", "commodities"),
            ("gas", "commodities"),
            ("commodity", "commodities"),
            ("food", "commodities"),
            ("wheat", "commodities"),
            ("fertilizer", "commodities"),
            ("energy", "commodities"),
            ("power", "commodities"),
            # Markets / Finance
            ("stock", "markets"),
            ("bank", "markets"),
            ("finance", "markets"),
            ("capital", "markets"),
            ("market", "markets"),
            ("equity", "markets"),
            ("investment", "markets"),
            ("tax", "markets"),
            ("revenue", "markets"),
            # Inflation-linked
            ("inflation", "inflation"),
            ("price", "inflation"),
            ("repo", "inflation"),
            ("interest rate", "inflation"),
            ("monetary", "inflation"),
            ("liquidity", "inflation"),
            # Sector-specific spending (map to markets as fiscal impact)
            ("defence", "markets"),
            ("defense", "markets"),
            ("military", "markets"),
            ("education", "markets"),
            ("school", "markets"),
            ("university", "markets"),
            ("infrastructure", "markets"),
            ("road", "markets"),
            ("rail", "markets"),
            ("transport", "markets"),
            ("digital", "markets"),
            ("technology", "markets"),
            ("software", "markets"),
            ("it sector", "markets"),
            (" it ", "markets"),
            ("pension", "markets"),
            ("welfare", "healthcare"),
            ("subsidy", "commodities"),
            ("allocation", "markets"),
            ("budget", "markets"),
            ("spending", "markets"),
        ]:
            if keyword in text and sector not in sectors:
                sectors.append(sector)

        variables = []
        for var in ["inflation", "gdp", "repo rate", "interest rate", "unemployment",
                    "fiscal deficit", "current account", "exchange rate"]:
            if var in text:
                variables.append(var)

        # ── Direction detection ───────────────────────────────────────────────
        # External shocks (foreign tariffs/sanctions imposed ON India) are always
        # negative for the Indian economy, regardless of the verb used.
        if _external_negative:
            direction = "decrease"
        elif re.search(r"\b(reduce|cut|cuts|decrease|decreased|lower|lowered|decline|slash|curtail|withdraw|restrict|ban|sanction|impose|levy)\b", text):
            direction = "decrease"
        elif re.search(r"\b(maintain|stable|unchanged|steady|no change|hold)\b", text):
            direction = "neutral"
        elif re.search(r"\b(increase|increased|raise|raised|boost|boosted|hike|expand|allocat|invest)\b", text):
            direction = "increase"
        else:
            direction = "increase"  # default optimistic

        # ── Intensity — percentage magnitude cues ─────────────────────────────
        intensity = "medium"
        pct_match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
        if pct_match:
            pct = float(pct_match.group(1))
            if pct <= 2:
                intensity = "low"
            elif pct >= 15:
                intensity = "high"
            else:
                intensity = "medium"
        elif re.search(r"\b(slight|minor|small|marginal)\b", text):
            intensity = "low"
        elif re.search(r"\b(major|aggressive|significant|strong|large|substantial|massive|sweeping|radical)\b", text):
            intensity = "high"

        policy_type = "fiscal"
        if any(k in text for k in ["repo", "interest rate", "liquidity", "monetary"]):
            policy_type = "monetary"
        elif any(k in text for k in ["tariff", "trade", "import", "export", "customs"]):
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


