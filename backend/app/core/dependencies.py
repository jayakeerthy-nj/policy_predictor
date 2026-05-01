from app.services.dependency_graph_service import DependencyGraphService
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.ingestion_service import IngestionService
from app.services.policy_parser_service import PolicyParserService
from app.services.prediction_service import PredictionService
from app.services.scenario_service import ScenarioService


def get_ingestion_service() -> IngestionService:
    return IngestionService()


def get_policy_parser_service() -> PolicyParserService:
    return PolicyParserService()


def get_feature_engineering_service() -> FeatureEngineeringService:
    return FeatureEngineeringService()


def get_prediction_service() -> PredictionService:
    return PredictionService()


def get_dependency_graph_service() -> DependencyGraphService:
    return DependencyGraphService()


def get_scenario_service() -> ScenarioService:
    return ScenarioService()

