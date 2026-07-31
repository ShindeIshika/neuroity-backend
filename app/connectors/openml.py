# app/connectors/openml.py
from app.connectors.base import BaseConnector
from typing import List, Dict, Any, Optional
import asyncio

class OpenMLConnector(BaseConnector):
    """OpenML REST API connector"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "openml"
        
        try:
            import openml
            self.openml = openml
            self.authenticated = True
            print("✅ OpenML connector ready")
        except Exception as e:
            print(f"⚠️ OpenML import failed: {e}")
            self.authenticated = False
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for datasets on OpenML"""
        if not self.authenticated:
            return self._sample_results(query)
        
        try:
            loop = asyncio.get_event_loop()
            
            datasets = await loop.run_in_executor(
                None,
                lambda: self.openml.datasets.list_datasets(
                    output_format='dataframe',
                    size=limit,
                    status='active'
                )
            )
            
            results = []
            if datasets is not None and not datasets.empty:
                for idx, (did, row) in enumerate(datasets.iterrows()):
                    if idx >= limit:
                        break
                    
                    name = row.get('name', 'Unknown')
                    if query.lower() not in name.lower():
                        continue
                    
                    description = row.get('description', '')
                    if description and len(description) > 500:
                        description = description[:500] + '...'
                    
                    results.append({
                        "title": name,
                        "description": description,
                        "source": "openml",
                        "license": "Unknown",
                        "download_url": f"https://www.openml.org/d/{did}",
                        "source_url": f"https://www.openml.org/d/{did}",
                        "file_type": "csv",
                        "tags": [],
                        "size": row.get('NumberOfInstances', 0) * row.get('NumberOfFeatures', 0),
                        "samples": row.get('NumberOfInstances', 0),
                        "features": row.get('NumberOfFeatures', 0),
                        "last_updated": ""
                    })
            
            return results
            
        except Exception as e:
            print(f"OpenML search error: {e}")
            return self._sample_results(query)
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed dataset info"""
        if not self.authenticated:
            return None
        
        try:
            loop = asyncio.get_event_loop()
            dataset = await loop.run_in_executor(
                None,
                lambda: self.openml.datasets.get_dataset(int(dataset_id))
            )
            
            return {
                "title": dataset.name,
                "description": dataset.description[:500] if dataset.description else "",
                "source": "openml",
                "license": "Unknown",
                "download_url": f"https://www.openml.org/d/{dataset_id}",
                "source_url": f"https://www.openml.org/d/{dataset_id}",
                "file_type": "csv",
                "tags": [],
                "size": 0,
                "samples": dataset.instances if hasattr(dataset, 'instances') else 0,
                "features": dataset.features if hasattr(dataset, 'features') else 0,
                "last_updated": ""
            }
            
        except Exception as e:
            print(f"OpenML get error: {e}")
            return None
    
    def _sample_results(self, query: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": f"Sample OpenML: {query}",
                "description": "OpenML dataset sample.",
                "source": "openml",
                "license": "Unknown",
                "download_url": "https://www.openml.org/",
                "source_url": "https://www.openml.org/",
                "file_type": "csv",
                "tags": [],
                "size": 0,
                "samples": 0,
                "features": 0,
                "last_updated": ""
            }
        ]