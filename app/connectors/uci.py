# app/connectors/uci.py
from app.connectors.base import BaseConnector
from typing import List, Dict, Any, Optional
import asyncio
import sys

class UCIConnector(BaseConnector):
    """UCI Machine Learning Repository connector"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "uci"
        
        try:
            from ucimlrepo import fetch_ucirepo
            # Note: We'll use the search functionality differently
            self.fetch_ucirepo = fetch_ucirepo
            self.authenticated = True
            print("✅ UCI connector ready")
        except Exception as e:
            print(f"⚠️ UCI import failed: {e}")
            self.authenticated = False
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for datasets on UCI using predefined dataset list"""
        if not self.authenticated:
            return self._sample_results(query)
        
        try:
            # Use known dataset IDs for common searches
            # This is a curated list of popular UCI datasets
            dataset_map = {
                "iris": 53,
                "wine": 109,
                "breast cancer": 17,
                "diabetes": 46,
                "heart": 45,
                "boston": 165,
                "housing": 165,
                "sonar": 151,
                "mushroom": 73,
                "abalone": 1,
                "adult": 2,
                "credit": 27,
                "bank": 222,
                "parkinsons": 174,
                "vehicle": 149,
                "wine quality": 186
            }
            
            results = []
            matched_ids = []
            
            # Check if query matches any known dataset
            query_lower = query.lower()
            for name, ds_id in dataset_map.items():
                if query_lower in name or name in query_lower:
                    matched_ids.append(ds_id)
            
            if not matched_ids:
                # If no match, use Iris as default
                matched_ids = [53]
            
            # Limit results
            matched_ids = matched_ids[:limit]
            
            # Fetch each dataset
            loop = asyncio.get_event_loop()
            for ds_id in matched_ids:
                try:
                    dataset = await loop.run_in_executor(
                        None,
                        lambda: self.fetch_ucirepo(id=ds_id)
                    )
                    
                    # Get metadata
                    if hasattr(dataset, 'metadata'):
                        meta = dataset.metadata
                        name = meta.name if hasattr(meta, 'name') else "Unknown"
                        desc = meta.summary[:500] if hasattr(meta, 'summary') and meta.summary else ""
                        
                        results.append({
                        "title": name,
                        "description": desc,
                        "source": "uci",
                        "license": "CC BY 4.0",  # UCI datasets are CC BY 4.0
                        "download_url": f"https://archive.ics.uci.edu/dataset/{ds_id}",
                        "source_url": f"https://archive.ics.uci.edu/dataset/{ds_id}",
                        "file_type": "csv",
                        "tags": [],
                        "size": 0,
                        "samples": meta.num_instances if hasattr(meta, 'num_instances') else 0,
                        "features": meta.num_features if hasattr(meta, 'num_features') else 0,
                        "last_updated": ""
                    })
                except Exception as e:
                    print(f"Error fetching UCI dataset {ds_id}: {e}")
            
            return results
            
        except Exception as e:
            print(f"UCI search error: {e}")
            return self._sample_results(query)
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed dataset info"""
        if not self.authenticated:
            return None
        
        try:
            loop = asyncio.get_event_loop()
            dataset = await loop.run_in_executor(
                None,
                lambda: self.fetch_ucirepo(id=int(dataset_id))
            )
            
            return {
                "title": dataset.metadata.name if hasattr(dataset, 'metadata') and hasattr(dataset.metadata, 'name') else "Unknown",
                "description": dataset.metadata.summary[:500] if hasattr(dataset, 'metadata') and hasattr(dataset.metadata, 'summary') else "",
                "source": "uci",
                "license": "Unknown",
                "download_url": f"https://archive.ics.uci.edu/dataset/{dataset_id}",
                "source_url": f"https://archive.ics.uci.edu/dataset/{dataset_id}",
                "file_type": "csv",
                "tags": [],
                "size": 0,
                "samples": 0,
                "features": 0,
                "last_updated": ""
            }
            
        except Exception as e:
            print(f"UCI get error: {e}")
            return None
    
    def _sample_results(self, query: str) -> List[Dict[str, Any]]:
        """Return sample data when API is not available"""
        return [
            {
                "title": f"Sample UCI: {query}",
                "description": "UCI dataset sample. Install ucimlrepo for real data.",
                "source": "uci",
                "license": "Unknown",
                "download_url": "https://archive.ics.uci.edu/",
                "source_url": "https://archive.ics.uci.edu/",
                "file_type": "csv",
                "tags": [],
                "size": 0,
                "samples": 0,
                "features": 0,
                "last_updated": ""
            }
        ]