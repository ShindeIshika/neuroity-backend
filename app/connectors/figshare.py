# app/connectors/figshare.py
from app.connectors.base import BaseConnector
from typing import List, Dict, Any, Optional
import httpx
import asyncio

class FigshareConnector(BaseConnector):
    """Figshare API v2 connector"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "figshare"
        self.base_url = "https://api.figshare.com/v2"
        self.client = httpx.AsyncClient(timeout=30.0)
        print("✅ Figshare connector ready")
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for datasets on Figshare"""
        try:
            url = f"{self.base_url}/articles/search"
            
            payload = {
                "search_for": query,
                "limit": limit,
                "offset": 0,
                "order": "published_date",
                "order_direction": "desc"
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if isinstance(data, list):
                results = data
            elif isinstance(data, dict):
                results = data.get('results', [])
            
            formatted_results = []
            for item in results:
                if not isinstance(item, dict):
                    continue
                
                title = item.get('title', 'Unknown Title')
                description = item.get('description', '')
                if description and len(description) > 500:
                    description = description[:500] + '...'
                
                authors = item.get('authors', [])
                author_names = [a.get('full_name', '') for a in authors[:2] if isinstance(a, dict)]
                
                files = item.get('files', [])
                file_types = []
                for f in files[:3]:
                    if isinstance(f, dict):
                        ext = f.get('name', '').split('.')[-1] if f.get('name') else ''
                        if ext:
                            file_types.append(ext)
                file_type = ','.join(file_types) if file_types else "dataset"
                
                download_url = ""
                if files and isinstance(files[0], dict):
                    download_url = files[0].get('download_url', '')
                
                tags = item.get('tags', [])
                if isinstance(tags, str):
                    tags = [tags]
                elif not isinstance(tags, list):
                    tags = []
                
                formatted_results.append({
                    "title": title,
                    "description": description,
                    "source": "figshare",
                    "license": item.get('license', {}).get('value', 'Unknown') if isinstance(item.get('license'), dict) else item.get('license', 'Unknown'),
                    "download_url": download_url,
                    "source_url": item.get('url', ''),
                    "file_type": file_type,
                    "tags": tags,
                    "size": item.get('size', 0),
                    "samples": 0,
                    "features": 0,
                    "last_updated": item.get('published_date', '')
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Figshare search error: {e}")
            return self._sample_results(query)
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed dataset info"""
        try:
            url = f"{self.base_url}/articles/{dataset_id}"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            description = data.get('description', '')
            if description and len(description) > 500:
                description = description[:500] + '...'
            
            files = data.get('files', [])
            file_types = []
            for f in files:
                ext = f.get('name', '').split('.')[-1] if f.get('name') else ''
                if ext:
                    file_types.append(ext)
            file_type = ','.join(file_types[:3]) if file_types else "dataset"
            
            download_url = ""
            if files:
                download_url = files[0].get('download_url', '')
            
            return {
                "title": data.get('title', 'Unknown Title'),
                "description": description,
                "source": "figshare",
                "license": data.get('license', {}).get('value', 'Unknown') if isinstance(data.get('license'), dict) else 'Unknown',
                "download_url": download_url,
                "source_url": data.get('url', ''),
                "file_type": file_type,
                "tags": data.get('tags', []),
                "size": data.get('size', 0),
                "samples": 0,
                "features": 0,
                "last_updated": data.get('published_date', '')
            }
            
        except Exception as e:
            print(f"Figshare get error: {e}")
            return None
    
    def _sample_results(self, query: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": f"Sample Figshare: {query}",
                "description": "Figshare dataset sample.",
                "source": "figshare",
                "license": "CC-BY",
                "download_url": "",
                "source_url": "https://figshare.com/",
                "file_type": "dataset",
                "tags": ["sample", query],
                "size": 0,
                "samples": 0,
                "features": 0,
                "last_updated": ""
            }
        ]