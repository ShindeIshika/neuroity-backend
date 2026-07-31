# app/connectors/zenodo.py
from app.connectors.base import BaseConnector
from typing import List, Dict, Any, Optional
import httpx
import asyncio

class ZenodoConnector(BaseConnector):
    """Zenodo REST API connector"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "zenodo"
        self.base_url = "https://zenodo.org/api"
        self.client = httpx.AsyncClient(timeout=30.0)
        print("✅ Zenodo connector ready")
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for datasets on Zenodo"""
        try:
            url = f"{self.base_url}/records"
            params = {
                "q": query,
                "size": limit,
                "sort": "mostviewed"
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('hits', {}).get('hits', [])
            
            formatted_results = []
            for item in results:
                metadata = item.get('metadata', {})
                
                # Get creators
                creators = metadata.get('creators', [])
                creator_names = [c.get('name', '') for c in creators[:2]]
                authors = ', '.join(creator_names) if creator_names else "Unknown"
                
                # Get description
                description = metadata.get('description', '')
                if description:
                    # Remove HTML tags
                    import re
                    description = re.sub(r'<[^>]+>', '', description)
                    description = description[:500] + '...' if len(description) > 500 else description
                
                # Check if files exist
                has_files = bool(item.get('files', []))
                
                formatted_results.append({
                    "title": metadata.get('title', 'Unknown Title'),
                    "description": description,
                    "source": "zenodo",
                    "license": metadata.get('license', {}).get('id', 'Unknown') if isinstance(metadata.get('license'), dict) else metadata.get('license', 'Unknown'),
                    "download_url": f"https://zenodo.org/record/{item.get('id')}" if has_files else "",
                    "source_url": f"https://zenodo.org/record/{item.get('id')}",
                    "file_type": "dataset",
                    "tags": metadata.get('keywords', []),
                    "size": 0,
                    "samples": 0,
                    "features": 0,
                    "last_updated": item.get('updated', '')
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Zenodo search error: {e}")
            return self._sample_results(query)
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed dataset info"""
        try:
            url = f"{self.base_url}/records/{dataset_id}"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            metadata = data.get('metadata', {})
            
            # Get creators
            creators = metadata.get('creators', [])
            creator_names = [c.get('name', '') for c in creators[:3]]
            authors = ', '.join(creator_names) if creator_names else "Unknown"
            
            # Get description
            description = metadata.get('description', '')
            if description:
                import re
                description = re.sub(r'<[^>]+>', '', description)
            
            return {
                "title": metadata.get('title', 'Unknown Title'),
                "description": description,
                "source": "zenodo",
                "license": metadata.get('license', {}).get('id', 'Unknown') if isinstance(metadata.get('license'), dict) else metadata.get('license', 'Unknown'),
                "download_url": f"https://zenodo.org/record/{data.get('id')}",
                "source_url": f"https://zenodo.org/record/{data.get('id')}",
                "file_type": "dataset",
                "tags": metadata.get('keywords', []),
                "size": 0,
                "samples": 0,
                "features": 0,
                "last_updated": data.get('updated', '')
            }
            
        except Exception as e:
            print(f"Zenodo get error: {e}")
            return None
    
    def _sample_results(self, query: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": f"Sample Zenodo: {query}",
                "description": "Zenodo dataset sample.",
                "source": "zenodo",
                "license": "CC-BY",
                "download_url": "https://zenodo.org/",
                "source_url": "https://zenodo.org/",
                "file_type": "dataset",
                "tags": ["sample", query],
                "size": 0,
                "samples": 0,
                "features": 0,
                "last_updated": ""
            }
        ]