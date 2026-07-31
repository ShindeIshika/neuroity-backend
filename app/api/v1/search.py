# app/api/v1/search.py
from fastapi import APIRouter, Query
from typing import Optional
import asyncio
from app.connectors.kaggle import KaggleConnector
from app.connectors.huggingface import HuggingFaceConnector
from app.connectors.uci import UCIConnector
from app.connectors.openml import OpenMLConnector
from app.connectors.zenodo import ZenodoConnector
from app.connectors.figshare import FigshareConnector
from app.connectors.openneuro import OpenNeuroConnector
from app.connectors.physionet import PhysioNetConnector
from app.connectors.github import GitHubConnector
from app.connectors.google_dataset import GoogleDatasetConnector

router = APIRouter()

@router.get("/search")
async def search_datasets(
    q: str = Query(..., description="Search query"),
    source: Optional[str] = Query(None, description="Filter by source"),
    filetype: Optional[str] = Query(None, description="Filter by file type"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    limit: int = Query(10, ge=1, le=50, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """Universal dataset search across all 10 platforms"""
    
    connectors = []
    available_sources = ["kaggle", "huggingface", "uci", "openml", "zenodo", 
                        "figshare", "openneuro", "physionet", "github", "google_dataset"]
    provider_status = {}
    
    if not source or source.lower() == "kaggle":
        connectors.append(KaggleConnector())
    if not source or source.lower() == "huggingface":
        connectors.append(HuggingFaceConnector())
    if not source or source.lower() == "uci":
        connectors.append(UCIConnector())
    if not source or source.lower() == "openml":
        connectors.append(OpenMLConnector())
    if not source or source.lower() == "zenodo":
        connectors.append(ZenodoConnector())
    if not source or source.lower() == "figshare":
        connectors.append(FigshareConnector())
    if not source or source.lower() == "openneuro":
        connectors.append(OpenNeuroConnector())
    if not source or source.lower() == "physionet":
        connectors.append(PhysioNetConnector())
    if not source or source.lower() == "github":
        connectors.append(GitHubConnector())
    if not source or source.lower() == "google_dataset":
        connectors.append(GoogleDatasetConnector())
    
    if source and not connectors:
        return {
            "success": False,
            "query": q,
            "error": f"Source '{source}' not found",
            "available_sources": available_sources
        }
    
    # Run all searches concurrently
    tasks = []
    connector_names = []
    for c in connectors:
        tasks.append(c.search(q, limit + offset))
        connector_names.append(c.source_name)
    
    results_list = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Track provider status
    all_results = []
    for i, result in enumerate(results_list):
        source_name = connector_names[i] if i < len(connector_names) else "unknown"
        if isinstance(result, Exception):
            provider_status[source_name] = f"error: {str(result)[:50]}"
        elif isinstance(result, list):
            provider_status[source_name] = f"ok ({len(result)} results)"
            all_results.extend(result)
        else:
            provider_status[source_name] = "unknown response"
    
    # Deduplicate based on title + source
    seen = set()
    unique_results = []
    for r in all_results:
        key = f"{r.get('title', '').lower()}_{r.get('source', '')}"
        if key not in seen:
            seen.add(key)
            unique_results.append(r)
    all_results = unique_results
    
    # Apply filters
    if filetype:
        all_results = [r for r in all_results if r.get("file_type", "").lower() == filetype.lower()]
    
    if domain:
        domain_lower = domain.lower()
        filtered_by_domain = []
        for r in all_results:
            tags = [t.lower() for t in r.get("tags", [])]
            if domain_lower in tags or domain_lower in r.get("source", "").lower():
                filtered_by_domain.append(r)
        all_results = filtered_by_domain
    
    # Sort by relevance (title match + source priority)
    for r in all_results:
        score = 0
        title_lower = r.get('title', '').lower()
        if q.lower() in title_lower:
            score += 10
        if r.get('source') == 'kaggle':
            score += 2
        elif r.get('source') == 'huggingface':
            score += 1
        r['_score'] = score
    
    all_results.sort(key=lambda x: x.get('_score', 0), reverse=True)
    
    # Remove internal score field
    for r in all_results:
        if '_score' in r:
            del r['_score']
    
    # Pagination
    total_results = len(all_results)
    paginated_results = all_results[offset:offset + limit]
    
    return {
        "success": True,
        "query": q,
        "total_results": total_results,
        "offset": offset,
        "limit": limit,
        "providers": provider_status,
        "results": paginated_results
    }