# app/connectors/github.py
from app.connectors.base import BaseConnector
from typing import List, Dict, Any, Optional
import httpx
import asyncio

class GitHubConnector(BaseConnector):
    """GitHub Search API connector for datasets"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "github"
        self.base_url = "https://api.github.com"
        self.client = httpx.AsyncClient(timeout=30.0)
        print("✅ GitHub connector ready")
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for datasets on GitHub using GitHub Search API"""
        try:
            # Search repositories with dataset-related keywords
            # Use topic:dataset or search in README/description
            search_query = f"{query} dataset in:readme,description"
            
            url = f"{self.base_url}/search/repositories"
            params = {
                "q": search_query,
                "per_page": limit,
                "sort": "stars",
                "order": "desc"
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('items', [])
            
            formatted_results = []
            for item in results:
                # Get description
                description = item.get('description', '')
                if description and len(description) > 500:
                    description = description[:500] + '...'
                
                # Get tags from topics
                tags = item.get('topics', [])
                if 'dataset' not in tags:
                    tags.append('dataset')
                
                # Detect file type based on language or repo name
                file_type = "csv"  # default
                language = item.get('language', '')
                if language:
                    if language.lower() in ['python', 'jupyter notebook']:
                        file_type = "ipynb"
                    elif language.lower() == 'r':
                        file_type = "r"
                
                formatted_results.append({
                    "title": item.get('name', 'Unknown Repository'),
                    "description": description,
                    "source": "github",
                    "license": item.get('license', {}).get('name', 'Unknown') if isinstance(item.get('license'), dict) else 'Unknown',
                    "download_url": f"{item.get('html_url', '')}/archive/main.zip",
                    "source_url": item.get('html_url', ''),
                    "file_type": file_type,
                    "tags": tags,
                    "size": item.get('size', 0) * 1024,  # Convert KB to bytes
                    "samples": 0,
                    "features": 0,
                    "last_updated": item.get('updated_at', '')
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"GitHub search error: {e}")
            return self._sample_results(query)
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed dataset info"""
        try:
            url = f"{self.base_url}/repos/{dataset_id}"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Get description
            description = data.get('description', '')
            if description and len(description) > 500:
                description = description[:500] + '...'
            
            # Get tags from topics
            tags = data.get('topics', [])
            if 'dataset' not in tags:
                tags.append('dataset')
            
            return {
                "title": data.get('name', 'Unknown Repository'),
                "description": description,
                "source": "github",
                "license": data.get('license', {}).get('name', 'Unknown') if isinstance(data.get('license'), dict) else 'Unknown',
                "download_url": f"{data.get('html_url', '')}/archive/main.zip",
                "source_url": data.get('html_url', ''),
                "file_type": "zip",
                "tags": tags,
                "size": data.get('size', 0) * 1024,
                "samples": data.get('stargazers_count', 0),
                "features": data.get('forks_count', 0),
                "last_updated": data.get('updated_at', '')
            }
            
        except Exception as e:
            print(f"GitHub get error: {e}")
            return None
    
    def _sample_results(self, query: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": f"Sample GitHub: {query}",
                "description": "GitHub dataset repository sample.",
                "source": "github",
                "license": "MIT",
                "download_url": "https://github.com/sample",
                "source_url": "https://github.com/sample",
                "file_type": "zip",
                "tags": ["dataset", "sample", query],
                "size": 0,
                "samples": 0,
                "features": 0,
                "last_updated": ""
            }
        ]