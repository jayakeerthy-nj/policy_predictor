from datetime import date, datetime, timedelta

import httpx

from app.connectors.base import DataConnector
from app.core.config import settings


class NewsAPIConnector(DataConnector):
    def fetch(self, start_date: date | None, end_date: date | None) -> list[dict]:
        if not settings.newsapi_key:
            now = datetime.utcnow()
            return [
                {
                    "headline": "Energy prices rise as shipping lanes face delays",
                    "published_at": (now - timedelta(hours=2)).isoformat(),
                    "source": "mock_news",
                },
                {
                    "headline": "Government announces tariff rationalization for key imports",
                    "published_at": (now - timedelta(hours=5)).isoformat(),
                    "source": "mock_news",
                },
            ]
        params = {
            "q": "economy OR inflation OR trade OR commodity",
            "apiKey": settings.newsapi_key,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 50,
        }
        if start_date:
            params["from"] = start_date.isoformat()
        if end_date:
            params["to"] = end_date.isoformat()
        with httpx.Client(timeout=20) as client:
            resp = client.get("https://newsapi.org/v2/everything", params=params)
            resp.raise_for_status()
            payload = resp.json()
        return [
            {
                "headline": article.get("title", ""),
                "published_at": article.get("publishedAt"),
                "source": article.get("source", {}).get("name", "newsapi"),
            }
            for article in payload.get("articles", [])
        ]

