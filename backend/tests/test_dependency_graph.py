from app.models.schemas import DomainImpact
from app.services.dependency_graph_service import DependencyGraphService


def test_graph_ripple_has_inflation_node():
    impacts = [
        DomainImpact(
            domain="commodities",
            impact_percent=2.0,
            direction="increase",
            confidence=0.7,
            feature_importance={"fuel": 0.6},
        )
    ]
    response = DependencyGraphService().build_response(impacts)
    assert "inflation" in response.ripple_effects

