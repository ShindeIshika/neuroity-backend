# app/connectors/huggingface.py
from app.connectors.base import BaseConnector
from typing import List, Dict, Any, Optional
import asyncio
import httpx

class HuggingFaceConnector(BaseConnector):
    """Hugging Face Hub API connector"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "huggingface"
        self.base_url = "https://huggingface.co/api"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for datasets on Hugging Face"""
        try:
            url = f"{self.base_url}/datasets"
            params = {
                "search": query,
                "limit": limit
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data[:limit]:
                results.append({
                    "title": item.get("id", "Unknown"),
                    "description": item.get("description", "")[:500],
                    "source": "huggingface",
                    "license": item.get("license", "Unknown"),
                    "download_url": f"https://huggingface.co/datasets/{item.get('id')}",
                    "source_url": f"https://huggingface.co/datasets/{item.get('id')}",
                    "file_type": "dataset",
                    "tags": item.get("tags", []),
                    "size": 0,
                    "samples": 0,
                    "features": 0,
                    "last_updated": item.get("lastModified", "")
                })
            
            return results
            
        except Exception as e:
            print(f"HuggingFace search error: {e}")
            return self._sample_results(query)
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed dataset info"""
        try:
            url = f"{self.base_url}/datasets/{dataset_id}"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            return {
                "title": data.get("id", "Unknown"),
                "description": data.get("description", "")[:500],
                "source": "huggingface",
                "license": data.get("license", "Unknown"),
                "download_url": f"https://huggingface.co/datasets/{data.get('id')}",
                "source_url": f"https://huggingface.co/datasets/{data.get('id')}",
                "file_type": "dataset",
                "tags": data.get("tags", []),
                "size": data.get("size", 0),
                "samples": data.get("samples", 0),
                "features": 0,
                "last_updated": data.get("lastModified", "")
            }
            
        except Exception as e:
            print(f"HuggingFace get error: {e}")
            return None
    
    def _sample_results(self, query: str) -> List[Dict[str, Any]]:
        """Return sample data when API is not available"""
        return [
            {
                "title": f"Sample HF: {query}",
                "description": "Hugging Face dataset sample",
                "source": "huggingface",
                "license": "MIT",
                "download_url": "https://huggingface.co/datasets/sample",
                "source_url": "https://huggingface.co/datasets/sample",
                "file_type": "dataset",
                "tags": ["sample", query],
                "size": 0,
                "samples": 0,
                "features": 0,
                "last_updated": "2026-01-01"
            }
        ]