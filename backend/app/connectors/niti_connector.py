from datetime import date

from app.connectors.base import DataConnector


class NITIConnector(DataConnector):
    def fetch(self, start_date: date | None, end_date: date | None) -> list[dict]:
        # MVP synthetic proxy metrics until direct NITI integration keys/routes are configured.
        return [
            {"country": "India", "indicator": "health_access_index", "timestamp": "2025-12-31", "value": 0.62},
            {"country": "India", "indicator": "logistics_resilience", "timestamp": "2025-12-31", "value": 0.57},
        ]

