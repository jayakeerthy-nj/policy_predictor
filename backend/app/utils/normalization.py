from datetime import datetime


def normalize_indicator_records(records: list[dict], source: str) -> list[dict]:
    normalized = []
    for row in records:
        normalized.append(
            {
                "country": row.get("country", "India"),
                "indicator": row.get("indicator", "unknown"),
                "timestamp": row.get("timestamp", datetime.utcnow().isoformat()),
                "value": float(row.get("value", 0.0)),
                "source": source,
            }
        )
    return normalized


def summarize_latest_indicators(records: list[dict]) -> dict[str, float]:
    latest: dict[str, float] = {}
    for row in records:
        latest[row["indicator"]] = float(row["value"])
    return latest

