from datetime import datetime


def _score(headline: str, keywords: list[str]) -> float:
    text = headline.lower()
    hits = sum(1 for k in keywords if k in text)
    return min(1.0, hits / max(1, len(keywords) // 2))


def extract_news_signals(news_records: list[dict]) -> list[dict]:
    signals: list[dict] = []
    for record in news_records:
        headline = record.get("headline", "")
        signals.append(
            {
                "headline": headline,
                "published_at": record.get("published_at", datetime.utcnow().isoformat()),
                "inflation_pressure": _score(headline, ["inflation", "price", "cost", "fuel"]),
                "supply_shock": _score(headline, ["supply", "shortage", "shipping", "disruption"]),
                "trade_disruption": _score(headline, ["tariff", "import", "export", "sanction"]),
                "source": record.get("source", "news"),
            }
        )
    return signals


def aggregate_news_signals(signals: list[dict]) -> dict[str, float]:
    if not signals:
        return {"inflation_pressure": 0.0, "supply_shock": 0.0, "trade_disruption": 0.0}
    keys = ["inflation_pressure", "supply_shock", "trade_disruption"]
    return {k: round(sum(float(s[k]) for s in signals) / len(signals), 4) for k in keys}

