from app.ml.registry import build_domain_registry


def train_models(sample_feature_names: list[str]) -> dict[str, str]:
    registry = build_domain_registry(sample_feature_names)
    return {name: f"{model.name}_linear_seeded" for name, model in registry.items()}

