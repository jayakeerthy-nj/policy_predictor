from datetime import datetime
from uuid import uuid4

from app.connectors.base import DataConnector
from app.connectors.imf_connector import IMFConnector
from app.connectors.newsapi_connector import NewsAPIConnector
from app.connectors.niti_connector import NITIConnector
from app.connectors.rbi_connector import RBIConnector
from app.connectors.worldbank_connector import WorldBankConnector
from app.models.schemas import IngestionRunRequest, IngestionRunResponse
from app.utils.news_signal_extractor import extract_news_signals
from app.utils.normalization import normalize_indicator_records


class IngestionService:
    def __init__(self) -> None:
        self.connectors: dict[str, DataConnector] = {
            "newsapi": NewsAPIConnector(),
            "worldbank": WorldBankConnector(),
            "imf": IMFConnector(),
            "rbi": RBIConnector(),
            "niti": NITIConnector(),
        }

    def run(self, payload: IngestionRunRequest) -> IngestionRunResponse:
        country = payload.country.strip() or "India"
        selected = payload.sources or list(self.connectors.keys())
        normalized_count = 0
        signal_count = 0
        for source_name in selected:
            connector = self.connectors.get(source_name)
            if connector is None:
                continue
            records = connector.fetch(start_date=payload.start_date, end_date=payload.end_date)
            if source_name == "newsapi":
                signals = extract_news_signals(records)
                signal_count += len(signals)
            else:
                normalized_count += len(normalize_indicator_records(records, source_name))
        return IngestionRunResponse(
            run_id=str(uuid4()),
            country=country,
            ingested_records=normalized_count,
            signals_generated=signal_count,
            sources_used=selected,
            timestamp=datetime.utcnow(),
        )

