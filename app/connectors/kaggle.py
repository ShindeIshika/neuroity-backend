# app/connectors/kaggle.py
from app.connectors.base import BaseConnector
from typing import List, Dict, Any, Optional
import asyncio
import os
import json
import tempfile

class KaggleConnector(BaseConnector):
    """Kaggle API connector"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "kaggle"
        
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            # Use temp directory for credentials
            temp_dir = tempfile.mkdtemp()
            os.environ['KAGGLE_CONFIG_DIR'] = temp_dir
            
            json_path = os.path.join(temp_dir, 'kaggle.json')
            with open(json_path, 'w') as f:
                json.dump({
                    "username": "KGAT",
                    "key": "32d9e621f06055558c70e4201f2c3fcc"
                }, f)
            
            self.api = KaggleApi()
            self.api.authenticate()
            self.authenticated = True
            print("✅ Kaggle authenticated successfully (temp dir)")
        except Exception as e:
            print(f"⚠️ Kaggle auth failed: {e}")
            self.authenticated = False
            self.api = None
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for datasets on Kaggle"""
        if not self.authenticated or not self.api:
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
                # Handle tags safely
                tags = []
                if hasattr(dataset, 'tags'):
                    if isinstance(dataset.tags, list):
                        for tag in dataset.tags:
                            if hasattr(tag, '_name'):
                                tags.append(tag._name)
                            elif isinstance(tag, dict):
                                tags.append(tag.get('_name', ''))
                
                # Get ref/id safely
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
            return self._sample_results(query)
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        if not self.authenticated or not self.api:
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
            
            # Get ref/id safely
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
            return None
    
    def _sample_results(self, query: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": f"Sample: {query} dataset",
                "description": "Kaggle credentials not configured.",
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