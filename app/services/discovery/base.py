from abc import ABC, abstractmethod
from typing import List
from app.schemas import RawDiscoveredJob

class BaseConnector(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def source_type(self) -> str:
        pass

    @abstractmethod
    def fetch_jobs(self) -> List[RawDiscoveredJob]:
        pass
