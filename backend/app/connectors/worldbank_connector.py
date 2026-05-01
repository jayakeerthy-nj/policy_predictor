from datetime import date
from pathlib import Path

import pandas as pd

from app.connectors.base import DataConnector


class WorldBankConnector(DataConnector):
    def fetch(self, start_date: date | None, end_date: date | None) -> list[dict]:
        data_root = Path(__file__).resolve().parents[3] / "data" / "samples"
        records: list[dict] = []
        for file_name, indicator in [
            ("WB_gdp.csv", "gdp"),
            ("WB_inflation.csv", "inflation"),
            ("WB_unemployement.csv", "unemployment"),
        ]:
            path = data_root / file_name
            if not path.exists():
                continue
            df = pd.read_csv(path)
            if "Country Name" in df.columns:
                df = df[df["Country Name"].astype(str).str.strip().str.lower() == "india"]
            value_cols = [c for c in df.columns if c.isdigit()]
            if not value_cols:
                continue
            latest_year = value_cols[-1]
            for _, row in df.iterrows():
                value = row.get(latest_year)
                if pd.isna(value):
                    continue
                records.append(
                    {
                        "country": str(row.get("Country Name", "India")),
                        "indicator": indicator,
                        "timestamp": f"{latest_year}-12-31",
                        "value": float(value),
                    }
                )
        return records

