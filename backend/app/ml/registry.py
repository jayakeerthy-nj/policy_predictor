import numpy as np
from sklearn.linear_model import LinearRegression

from app.ml.domain_models import DomainModel


def _seed_model(domain: str, feature_names: list[str]) -> DomainModel:
    rng = np.random.default_rng(abs(hash(domain)) % 2**31)
    x = rng.normal(0, 1, size=(256, len(feature_names)))
    weights = rng.normal(0, 0.2, size=len(feature_names))
    y = x @ weights + rng.normal(0, 0.1, size=256)
    model = LinearRegression()
    model.fit(x, y)
    return DomainModel(name=domain, regressor=model, feature_names=feature_names)


def build_domain_registry(feature_names: list[str]) -> dict[str, DomainModel]:
    domains = ["markets", "inflation", "healthcare", "trade", "commodities"]
    return {domain: _seed_model(domain, feature_names) for domain in domains}

