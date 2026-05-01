import networkx as nx

from app.models.schemas import DependencyGraphResponse, DomainImpact


class DependencyGraphService:
    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self.graph.add_weighted_edges_from(
            [
                ("commodities", "inflation", 0.7),
                ("inflation", "markets", 0.6),
                ("markets", "healthcare", 0.25),
                ("trade", "commodities", 0.55),
                ("trade", "markets", 0.45),
            ]
        )

    def build_response(self, impacts: list[DomainImpact]) -> DependencyGraphResponse:
        seeds = {impact.domain: impact.impact_percent / 100.0 for impact in impacts}
        ripple = {node: 0.0 for node in self.graph.nodes}
        for node, value in seeds.items():
            if node in ripple:
                ripple[node] += value
                for _, neighbor, data in self.graph.out_edges(node, data=True):
                    ripple[neighbor] += value * float(data["weight"])

        edges = [
            {"source": u, "target": v, "weight": float(data["weight"])}
            for u, v, data in self.graph.edges(data=True)
        ]
        return DependencyGraphResponse(
            nodes=list(self.graph.nodes),
            edges=edges,
            ripple_effects={k: round(v, 4) for k, v in ripple.items()},
        )

