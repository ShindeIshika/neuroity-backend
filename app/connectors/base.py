# app/connectors/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseConnector(ABC):
    """Base class for all dataset platform connectors"""
    
    def __init__(self):
        self.source_name = self.__class__.__name__.replace("Connector", "").lower()
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        pass
    
    def standardize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": raw_data.get("title", "Unknown"),
            "description": raw_data.get("description", ""),
            "source": self.source_name,
            "license": raw_data.get("license", "Unknown"),
            "download_url": raw_data.get("download_url", ""),
            "source_url": raw_data.get("source_url", ""),
            "file_type": raw_data.get("file_type", ""),
            "tags": raw_data.get("tags", []),
            "size": raw_data.get("size", 0),
            "samples": raw_data.get("samples", 0),
            "features": raw_data.get("features", 0),
            "last_updated": raw_data.get("last_updated", "")
        }