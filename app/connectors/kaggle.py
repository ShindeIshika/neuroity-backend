# app/connectors/kaggle.py
from app.connectors.base import BaseConnector
from typing import List, Dict, Any, Optional
import asyncio
import os
import traceback

class KaggleConnector(BaseConnector):
    """Kaggle API connector using environment variables only"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "kaggle"
        self.api = None
        self.authenticated = False
        
        # Don't authenticate here — do it lazily
        print("✅ Kaggle connector initialized (lazy auth)")
    
    def _authenticate(self):
        """Authenticate using environment variables KAGGLE_USERNAME and KAGGLE_KEY"""
        if self.authenticated and self.api:
            return True
        
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            # Check if environment variables exist
            username = os.environ.get('KAGGLE_USERNAME')
            key = os.environ.get('KAGGLE_KEY')
            
            if not username or not key:
                print("⚠️ KAGGLE_USERNAME or KAGGLE_KEY not set in environment")
                return False
            
            print(f"✅ Using Kaggle credentials from environment (username: {username})")
            
            self.api = KaggleApi()
            self.api.authenticate()
            self.authenticated = True
            print("✅ Kaggle authenticated successfully")
            return True
            
        except Exception as e:
            print(f"⚠️ Kaggle auth failed: {e}")
            traceback.print_exc()
            self.authenticated = False
            self.api = None
            return False
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for datasets on Kaggle"""
        if not self._authenticate():
            return self._sample_results(query)
        
        try:
            loop = asyncio.get_event_loop()
            datasets = await loop.run_in_executor(
                None, 
                lambda: self.api.dataset_list(search=query, page=1)
            )
            
            datasets = datasets[:limit]
            results = []
            for dataset in datasets:
                tags = []
                if hasattr(dataset, 'tags'):
                    if isinstance(dataset.tags, list):
                        for tag in dataset.tags:
                            if hasattr(tag, '_name'):
                                tags.append(tag._name)
                            elif isinstance(tag, dict):
                                tags.append(tag.get('_name', ''))
                
                ref = getattr(dataset, 'ref', None)
                if not ref:
                    ref = getattr(dataset, 'id', None)
                if not ref:
                    ref = 'sample'
                
                results.append({
                    "title": getattr(dataset, 'title', 'Unknown'),
                    "description": getattr(dataset, 'description', '')[:500] if getattr(dataset, 'description', '') else '',
                    "source": "kaggle",
                    "license": "Unknown",
                    "download_url": f"https://www.kaggle.com/api/v1/datasets/download/{ref}",
                    "source_url": f"https://www.kaggle.com/datasets/{ref}",
                    "file_type": "csv",
                    "tags": tags,
                    "size": getattr(dataset, 'size', 0) or 0,
                    "samples": getattr(dataset, 'totalRows', 0) or 0,
                    "features": getattr(dataset, 'columnsCount', 0) or 0,
                    "last_updated": str(getattr(dataset, 'lastUpdated', ''))
                })
            
            return results
            
        except Exception as e:
            print(f"Kaggle search error: {e}")
            traceback.print_exc()
            return self._sample_results(query)
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        if not self._authenticate():
            return None
        
        try:
            loop = asyncio.get_event_loop()
            dataset = await loop.run_in_executor(
                None,
                lambda: self.api.dataset_view(dataset_id)
            )
            
            tags = []
            if hasattr(dataset, 'tags'):
                if isinstance(dataset.tags, list):
                    for tag in dataset.tags:
                        if hasattr(tag, '_name'):
                            tags.append(tag._name)
                        elif isinstance(tag, dict):
                            tags.append(tag.get('_name', ''))
            
            ref = getattr(dataset, 'ref', None)
            if not ref:
                ref = getattr(dataset, 'id', None)
            if not ref:
                ref = dataset_id
            
            return {
                "title": getattr(dataset, 'title', 'Unknown'),
                "description": getattr(dataset, 'description', ''),
                "source": "kaggle",
                "license": "Unknown",
                "download_url": f"https://www.kaggle.com/api/v1/datasets/download/{ref}",
                "source_url": f"https://www.kaggle.com/datasets/{ref}",
                "file_type": "csv",
                "tags": tags,
                "size": getattr(dataset, 'size', 0) or 0,
                "samples": getattr(dataset, 'totalRows', 0) or 0,
                "features": getattr(dataset, 'columnsCount', 0) or 0,
                "last_updated": str(getattr(dataset, 'lastUpdated', ''))
            }
            
        except Exception as e:
            print(f"Kaggle get error: {e}")
            traceback.print_exc()
            return None
    
    def _sample_results(self, query: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": f"Sample: {query} dataset",
                "description": "Kaggle authentication failed. Check logs for details.",
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