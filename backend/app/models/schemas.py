from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    postgres: str
    redis: str
    gemini: str


class IngestionRunRequest(BaseModel):
    sources: list[str] = Field(default_factory=list)
    start_date: date | None = None
    end_date: date | None = None
    country: str = "India"


class IngestionRunResponse(BaseModel):
    run_id: str
    country: str
    ingested_records: int
    signals_generated: int
    sources_used: list[str]
    timestamp: datetime


class PolicyParseRequest(BaseModel):
    policy_text: str
    country: str = "India"


class PolicyParseResponse(BaseModel):
    policy_type: str
    sectors: list[str]
    variables: list[str]
    direction: Literal["increase", "decrease", "neutral"]
    intensity: Literal["low", "medium", "high"]
    confidence: float
    method: str


class DomainImpact(BaseModel):
    domain: Literal["markets", "inflation", "healthcare", "trade", "commodities"]
    impact_percent: float
    direction: Literal["increase", "decrease", "neutral"]
    confidence: float
    feature_importance: dict[str, float]


class ImpactPredictionRequest(BaseModel):
    policy_text: str
    context_overrides: dict[str, float] = Field(default_factory=dict)
    country: str = "India"


class ImpactPredictionResponse(BaseModel):
    prediction_id: str
    country: str
    parsed_policy: PolicyParseResponse
    impacts: list[DomainImpact]
    generated_at: datetime


class ScenarioRequest(BaseModel):
    policy_text: str
    shock_factor: float = 0.15
    country: str = "India"


class ScenarioPoint(BaseModel):
    domain: str
    baseline: float
    shock: float
    policy_adjusted: float


class ScenarioResponse(BaseModel):
    scenario_id: str
    country: str
    scenarios: list[ScenarioPoint]
    explanation: str
    generated_at: datetime


class DependencyGraphResponse(BaseModel):
    nodes: list[str]
    edges: list[dict[str, float | str]]
    ripple_effects: dict[str, float]

