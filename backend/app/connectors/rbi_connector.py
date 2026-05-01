from datetime import date
from pathlib import Path

import pandas as pd

from app.connectors.base import DataConnector


class RBIConnector(DataConnector):
    def fetch(self, start_date: date | None, end_date: date | None) -> list[dict]:
        data_file = Path(__file__).resolve().parents[3] / "data" / "samples" / "RBI_repo.txt"
        if not data_file.exists():
            return [{"country": "India", "indicator": "repo_rate", "timestamp": "2025-01-01", "value": 6.5}]
        df = pd.read_csv(data_file, sep=None, engine="python")
        date_col = next((c for c in df.columns if "date" in c.lower()), df.columns[0])
        value_col = next((c for c in df.columns if "repo" in c.lower() or "rate" in c.lower()), df.columns[-1])
        return [
            {
                "country": "India",
                "indicator": "repo_rate",
                "timestamp": str(row[date_col]),
                "value": float(row[value_col]),
            }
            for _, row in df.tail(24).iterrows()
            if pd.notna(row[value_col])
        ]

