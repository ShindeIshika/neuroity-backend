# app/connectors/physionet.py
from app.connectors.base import BaseConnector
from typing import List, Dict, Any, Optional
import httpx
import asyncio

class PhysioNetConnector(BaseConnector):
    """PhysioNet connector for physiologic signals"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "physionet"
        self.base_url = "https://physionet.org/api/v1"
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        print("✅ PhysioNet connector ready")
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for datasets on PhysioNet"""
        try:
            urls_to_try = [
                f"https://physionet.org/api/v1/projects/search/?q={query}&limit={limit}",
                f"https://physionet.org/api/v1/projects/search?q={query}&limit={limit}",
                f"https://physionet.org/api/v1/datasets?q={query}&limit={limit}"
            ]
            
            data = None
            for url in urls_to_try:
                try:
                    response = await self.client.get(url, follow_redirects=True)
                    if response.status_code == 200:
                        data = response.json()
                        break
                except:
                    continue
            
            if not data:
                print("PhysioNet: No working endpoint found")
                return self._sample_results(query)
            
            results = []
            if isinstance(data, list):
                results = data
            elif isinstance(data, dict):
                results = data.get('results', [])
            
            formatted_results = []
            for item in results:
                if not isinstance(item, dict):
                    continue
                
                description = item.get('description', '')
                if description and len(description) > 500:
                    description = description[:500] + '...'
                
                slug = item.get('slug', '')
                if not slug:
                    slug = item.get('id', '')
                    if not slug:
                        slug = str(item.get('project_id', ''))
                
                formatted_results.append({
                    "title": item.get('title', 'Unknown Dataset'),
                    "description": description,
                    "source": "physionet",
                    "license": item.get('license', 'Unknown'),
                    "download_url": f"https://physionet.org/content/{slug}" if slug else "https://physionet.org/",
                    "source_url": f"https://physionet.org/content/{slug}" if slug else "https://physionet.org/",
                    "file_type": "edf",
                    "tags": item.get('tags', []),
                    "size": item.get('size', 0),
                    "samples": item.get('num_subjects', 0),
                    "features": item.get('num_channels', 0),
                    "last_updated": item.get('updated_at', '')
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"PhysioNet search error: {e}")
            return self._sample_results(query)
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed dataset info"""
        try:
            url = f"{self.base_url}/projects/{dataset_id}"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            description = data.get('description', '')
            if description and len(description) > 500:
                description = description[:500] + '...'
            
            return {
                "title": data.get('title', 'Unknown Dataset'),
                "description": description,
                "source": "physionet",
                "license": data.get('license', 'Unknown'),
                "download_url": f"https://physionet.org/content/{data.get('slug', '')}",
                "source_url": f"https://physionet.org/content/{data.get('slug', '')}",
                "file_type": "edf",
                "tags": data.get('tags', []),
                "size": data.get('size', 0),
                "samples": data.get('num_subjects', 0),
                "features": data.get('num_channels', 0),
                "last_updated": data.get('updated_at', '')
            }
            
        except Exception as e:
            print(f"PhysioNet get error: {e}")
            return None
    
    def _sample_results(self, query: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": f"Sample PhysioNet: {query}",
                "description": "PhysioNet physiologic dataset sample.",
                "source": "physionet",
                "license": "Open Data",
                "download_url": "https://physionet.org/",
                "source_url": "https://physionet.org/",
                "file_type": "edf",
                "tags": ["physiologic", "sample", query],
                "size": 0,
                "samples": 0,
                "features": 0,
                "last_updated": ""
            }
        ]