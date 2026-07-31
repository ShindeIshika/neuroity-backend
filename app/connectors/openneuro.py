# app/connectors/openneuro.py
from app.connectors.base import BaseConnector
from typing import List, Dict, Any, Optional
import httpx
import asyncio

class OpenNeuroConnector(BaseConnector):
    """OpenNeuro GraphQL connector"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "openneuro"
        self.graphql_url = "https://openneuro.org/graphql"
        self.client = httpx.AsyncClient(timeout=30.0)
        print("✅ OpenNeuro connector ready")
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for datasets on OpenNeuro"""
        try:
            graphql_query = """
            query SearchDatasets($search: String, $limit: Int) {
                datasets(
                    search: $search
                    first: $limit
                ) {
                    edges {
                        node {
                            id
                            datasetId
                            name
                            description
                            authors {
                                name
                            }
                            numberOfSubjects
                            numberOfFiles
                            totalSize
                            createdAt
                            updatedAt
                            license {
                                name
                            }
                        }
                    }
                }
            }
            """
            
            variables = {
                "search": query,
                "limit": limit
            }
            
            response = await self.client.post(
                self.graphql_url,
                json={
                    "query": graphql_query,
                    "variables": variables
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 405:
                # If POST fails, try GET
                import urllib.parse
                params = {
                    "query": graphql_query,
                    "variables": variables
                }
                response = await self.client.get(
                    self.graphql_url,
                    params=params,
                    headers={"Content-Type": "application/json"}
                )
            
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                print(f"OpenNeuro GraphQL errors: {data['errors']}")
                return self._sample_results(query)
            
            edges = data.get('data', {}).get('datasets', {}).get('edges', [])
            
            results = []
            for edge in edges:
                node = edge.get('node', {})
                if not node:
                    continue
                
                description = node.get('description', '')
                if description and len(description) > 500:
                    description = description[:500] + '...'
                
                results.append({
                    "title": node.get('name', 'Unknown Dataset'),
                    "description": description,
                    "source": "openneuro",
                    "license": node.get('license', {}).get('name', 'Unknown') if isinstance(node.get('license'), dict) else 'Unknown',
                    "download_url": f"https://openneuro.org/datasets/{node.get('datasetId', '')}",
                    "source_url": f"https://openneuro.org/datasets/{node.get('datasetId', '')}",
                    "file_type": "BIDS",
                    "tags": ["neuroimaging", "BIDS"],
                    "size": node.get('totalSize', 0),
                    "samples": node.get('numberOfSubjects', 0),
                    "features": node.get('numberOfFiles', 0),
                    "last_updated": node.get('updatedAt', '')
                })
            
            return results
            
        except Exception as e:
            print(f"OpenNeuro search error: {e}")
            return self._sample_results(query)
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed dataset info"""
        try:
            graphql_query = """
            query GetDataset($datasetId: ID!) {
                dataset(id: $datasetId) {
                    id
                    datasetId
                    name
                    description
                    authors {
                        name
                    }
                    numberOfSubjects
                    numberOfFiles
                    totalSize
                    createdAt
                    updatedAt
                    license {
                        name
                        url
                    }
                    modalities
                    tasks
                }
            }
            """
            
            variables = {
                "datasetId": dataset_id
            }
            
            response = await self.client.post(
                self.graphql_url,
                json={
                    "query": graphql_query,
                    "variables": variables
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            node = data.get('data', {}).get('dataset', {})
            
            if not node:
                return None
            
            description = node.get('description', '')
            if description and len(description) > 500:
                description = description[:500] + '...'
            
            tags = []
            modalities = node.get('modalities', [])
            if modalities:
                tags.extend(modalities)
            tasks = node.get('tasks', [])
            if tasks:
                tags.extend(tasks)
            
            return {
                "title": node.get('name', 'Unknown Dataset'),
                "description": description,
                "source": "openneuro",
                "license": node.get('license', {}).get('name', 'Unknown') if isinstance(node.get('license'), dict) else 'Unknown',
                "download_url": f"https://openneuro.org/datasets/{node.get('datasetId', '')}",
                "source_url": f"https://openneuro.org/datasets/{node.get('datasetId', '')}",
                "file_type": "BIDS",
                "tags": tags,
                "size": node.get('totalSize', 0),
                "samples": node.get('numberOfSubjects', 0),
                "features": node.get('numberOfFiles', 0),
                "last_updated": node.get('updatedAt', '')
            }
            
        except Exception as e:
            print(f"OpenNeuro get error: {e}")
            return None
    
    def _sample_results(self, query: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": f"Sample OpenNeuro: {query}",
                "description": "OpenNeuro neuroimaging dataset sample.",
                "source": "openneuro",
                "license": "CC-BY",
                "download_url": "https://openneuro.org/",
                "source_url": "https://openneuro.org/",
                "file_type": "BIDS",
                "tags": ["neuroimaging", "sample"],
                "size": 0,
                "samples": 0,
                "features": 0,
                "last_updated": ""
            }
        ]