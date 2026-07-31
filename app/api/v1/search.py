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
from app.connectors.google_dataset import GoogleDatasetConnector  # <-- ADD THIS

router = APIRouter()

@router.get("/search")
async def search_datasets(
    q: str = Query(..., description="Search query"),
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(10, ge=1, le=50, description="Results per page")
):
    """Universal dataset search across all platforms"""
    
    connectors = []
    
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
    
    if not source or source.lower() == "google_dataset":  # <-- ADD THIS
        connectors.append(GoogleDatasetConnector())
    
    if source and not connectors:
        return {
            "success": False,
            "query": q,
            "error": f"Source '{source}' not found",
            "available_sources": ["kaggle", "huggingface", "uci", "openml", "zenodo", "figshare", "openneuro", "physionet", "github", "google_dataset"]
        }
    
    tasks = [c.search(q, limit) for c in connectors]
    results_list = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_results = []
    for result in results_list:
        if isinstance(result, list):
            all_results.extend(result)
    
    return {
        "success": True,
        "query": q,
        "total_results": len(all_results),
        "limit": limit,
        "results": all_results[:limit]
    }