import numpy as np
from sklearn.linear_model import LinearRegression

from app.ml.domain_models import DomainModel

# Domain-specific feature weights that reflect real-world relationships.
# Each domain responds differently to policy direction, intensity, and
# economic indicators. These are calibrated heuristics — positive weight
# means the feature pushes the domain impact up, negative means down.
_DOMAIN_WEIGHTS: dict[str, dict[str, float]] = {
    "markets": {
        "policy_direction": 0.45,
        "policy_intensity": 0.30,
        "policy_confidence": 0.10,
        "sector_count": 0.05,
        "variable_count": 0.03,
        "macro_mean": 0.07,
        "gdp": 0.12,
        "inflation": -0.18,
        "unemployment": -0.10,
        "inflation_pressure": -0.22,
        "supply_shock": -0.15,
        "trade_disruption": -0.08,
        "repo_rate": -0.14,
    },
    "inflation": {
        "policy_direction": -0.35,
        "policy_intensity": 0.25,
        "policy_confidence": 0.05,
        "sector_count": 0.02,
        "variable_count": 0.02,
        "macro_mean": 0.06,
        "gdp": -0.08,
        "inflation": 0.30,
        "unemployment": 0.05,
        "inflation_pressure": 0.40,
        "supply_shock": 0.28,
        "trade_disruption": 0.20,
        "repo_rate": -0.25,
    },
    "healthcare": {
        "policy_direction": 0.30,
        "policy_intensity": 0.35,
        "policy_confidence": 0.08,
        "sector_count": 0.05,
        "variable_count": 0.03,
        "macro_mean": 0.05,
        "gdp": 0.10,
        "inflation": -0.12,
        "unemployment": -0.08,
        "inflation_pressure": -0.10,
        "supply_shock": -0.05,
        "trade_disruption": -0.04,
        "repo_rate": -0.06,
    },
    "trade": {
        "policy_direction": 0.38,
        "policy_intensity": 0.28,
        "policy_confidence": 0.07,
        "sector_count": 0.04,
        "variable_count": 0.04,
        "macro_mean": 0.05,
        "gdp": 0.15,
        "inflation": -0.10,
        "unemployment": -0.07,
        "inflation_pressure": -0.12,
        "supply_shock": -0.20,
        "trade_disruption": -0.35,
        "repo_rate": -0.08,
    },
    "commodities": {
        "policy_direction": 0.28,
        "policy_intensity": 0.22,
        "policy_confidence": 0.06,
        "sector_count": 0.04,
        "variable_count": 0.03,
        "macro_mean": 0.06,
        "gdp": 0.08,
        "inflation": 0.22,
        "unemployment": -0.05,
        "inflation_pressure": 0.30,
        "supply_shock": 0.35,
        "trade_disruption": 0.18,
        "repo_rate": -0.10,
    },
}


def _build_domain_model(domain: str, feature_names: list[str]) -> DomainModel:
    """Build a LinearRegression model whose coefficients reflect domain-specific
    economic relationships rather than random noise.

    We synthesize training data by:
    1. Drawing 512 random feature samples.
    2. Computing targets using domain-specific weights (with small Gaussian noise
       to allow the regression to generalise slightly).
    This ensures the model's predictions vary meaningfully with the input features.
    """
    domain_w = _DOMAIN_WEIGHTS.get(domain, {})
    weight_vector = np.array([domain_w.get(name, 0.01) for name in feature_names])

    rng = np.random.default_rng(abs(hash(domain)) % 2**31)
    # Draw samples from a realistic distribution of normalised features.
    x = rng.normal(0, 1, size=(512, len(feature_names)))
    # Ground-truth targets = domain weights · features + small noise.
    y = x @ weight_vector + rng.normal(0, 0.05, size=512)

    model = LinearRegression()
    model.fit(x, y)
    return DomainModel(name=domain, regressor=model, feature_names=feature_names)


def build_domain_registry(feature_names: list[str]) -> dict[str, DomainModel]:
    domains = ["markets", "inflation", "healthcare", "trade", "commodities"]
    return {domain: _build_domain_model(domain, feature_names) for domain in domains}

