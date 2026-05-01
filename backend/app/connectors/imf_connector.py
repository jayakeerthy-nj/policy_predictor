from datetime import date

from app.connectors.base import DataConnector


class IMFConnector(DataConnector):
    def fetch(self, start_date: date | None, end_date: date | None) -> list[dict]:
        # MVP fallback placeholder for IMF data source.
        return [
            {
                "country": "India",
                "indicator": "current_account_balance",
                "timestamp": "2025-12-31",
                "value": -1.2,
            }
        ]

