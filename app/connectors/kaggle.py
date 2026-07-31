# app/connectors/kaggle.py
from app.connectors.base import BaseConnector
from typing import List, Dict, Any, Optional
import asyncio

class KaggleConnector(BaseConnector):
    """Kaggle API connector"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "kaggle"
        
        # Try to import and authenticate kaggle
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            self.api = KaggleApi()
            self.api.authenticate()
            self.authenticated = True
            print("✅ Kaggle authenticated successfully")
        except Exception as e:
            print(f"⚠️ Kaggle auth failed: {e}")
            print("   Make sure kaggle.json is in ~/.kaggle/")
            self.authenticated = False
            self.api = None
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for datasets on Kaggle"""
        if not self.authenticated or not self.api:
            return self._sample_results(query)
        
        try:
            # Run in thread pool because kaggle API is synchronous
            loop = asyncio.get_event_loop()
            datasets = await loop.run_in_executor(
                None, 
                lambda: self.api.dataset_list(search=query, page=1)
            )
            
            # Limit results
            datasets = datasets[:limit]
            
            results = []
            for dataset in datasets:
                results.append({
                    "title": dataset.title if hasattr(dataset, 'title') else "Unknown",
                    "description": dataset.description[:500] if hasattr(dataset, 'description') and dataset.description else "",
                    "source": "kaggle",
                    "license": "Unknown",
                    "download_url": f"https://www.kaggle.com/api/v1/datasets/download/{dataset.ref}",
                    "source_url": f"https://www.kaggle.com/datasets/{dataset.ref}",
                    "file_type": "csv",
                    "tags": dataset.tags if hasattr(dataset, 'tags') else [],
                    "size": dataset.size if hasattr(dataset, 'size') else 0,
                    "samples": dataset.totalRows if hasattr(dataset, 'totalRows') else 0,
                    "features": dataset.columnsCount if hasattr(dataset, 'columnsCount') else 0,
                    "last_updated": str(dataset.lastUpdated) if hasattr(dataset, 'lastUpdated') else ""
                })
            
            return results
            
        except Exception as e:
            print(f"Kaggle search error: {e}")
            return self._sample_results(query)
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed dataset info"""
        if not self.authenticated or not self.api:
            return None
        
        try:
            loop = asyncio.get_event_loop()
            dataset = await loop.run_in_executor(
                None,
                lambda: self.api.dataset_view(dataset_id)
            )
            
            return {
                "title": dataset.title,
                "description": dataset.description,
                "source": "kaggle",
                "license": "Unknown",
                "download_url": f"https://www.kaggle.com/api/v1/datasets/download/{dataset_id}",
                "source_url": f"https://www.kaggle.com/datasets/{dataset_id}",
                "file_type": "csv",
                "tags": dataset.tags if hasattr(dataset, 'tags') else [],
                "size": dataset.size if hasattr(dataset, 'size') else 0,
                "samples": dataset.totalRows if hasattr(dataset, 'totalRows') else 0,
                "features": dataset.columnsCount if hasattr(dataset, 'columnsCount') else 0,
                "last_updated": str(dataset.lastUpdated) if hasattr(dataset, 'lastUpdated') else ""
            }
            
        except Exception as e:
            print(f"Kaggle get error: {e}")
            return None
    
    def _sample_results(self, query: str) -> List[Dict[str, Any]]:
        """Return sample data when API is not available"""
        return [
            {
                "title": f"Sample: {query} dataset",
                "description": "This is a sample Kaggle dataset. Install kaggle package and set up credentials for real data.",
                "source": "kaggle",
                "license": "MIT",
                "download_url": "https://www.kaggle.com/datasets/sample",
                "source_url": "https://www.kaggle.com/datasets/sample",
                "file_type": "csv",
                "tags": ["sample", query],
                "size": 1024000,
                "samples": 1000,
                "features": 10,
                "last_updated": "2026-01-01"
            }
        ]