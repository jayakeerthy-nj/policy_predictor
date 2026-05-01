from abc import ABC, abstractmethod
from datetime import date


class DataConnector(ABC):
    @abstractmethod
    def fetch(self, start_date: date | None, end_date: date | None) -> list[dict]:
        raise NotImplementedError

