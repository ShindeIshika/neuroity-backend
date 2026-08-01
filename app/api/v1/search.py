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
    source: Optional[str] = Query(None, description="Search only one provider"),
    filetype: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    """Universal dataset search"""

    connector_map = {
        "kaggle": KaggleConnector,
        "huggingface": HuggingFaceConnector,
        "uci": UCIConnector,
        "openml": OpenMLConnector,
        "zenodo": ZenodoConnector,
        "figshare": FigshareConnector,
        "openneuro": OpenNeuroConnector,
        "physionet": PhysioNetConnector,
        "github": GitHubConnector,
        "google_dataset": GoogleDatasetConnector,
    }

    provider_status = {}

    # Build connector list
    if source:
        source = source.lower()

        if source not in connector_map:
            return {
                "success": False,
                "error": f"Unknown source '{source}'",
                "available_sources": list(connector_map.keys()),
            }

        connectors = [connector_map[source]()]
    else:
        connectors = [cls() for cls in connector_map.values()]

    # Launch searches concurrently
    tasks = [connector.search(q, limit + offset) for connector in connectors]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_results = []

    for connector, result in zip(connectors, results):

        if isinstance(result, Exception):
            print(f"{connector.source_name} failed:")
            print(result)

            provider_status[connector.source_name] = "error"

            continue

        provider_status[connector.source_name] = f"{len(result)} results"

        all_results.extend(result)

    # Remove duplicates
    seen = set()
    unique = []

    for item in all_results:

        key = (
            item.get("title", "").lower(),
            item.get("source", "").lower(),
        )

        if key not in seen:
            seen.add(key)
            unique.append(item)

    all_results = unique

    # File type filter
    if filetype:
        all_results = [
            r
            for r in all_results
            if r.get("file_type", "").lower() == filetype.lower()
        ]

    # Domain filter
    if domain:

        domain = domain.lower()

        filtered = []

        for r in all_results:

            tags = [t.lower() for t in r.get("tags", [])]

            if (
                domain in tags
                or domain in r.get("source", "").lower()
            ):
                filtered.append(r)

        all_results = filtered

    # Relevance scoring
    query = q.lower()

    for r in all_results:

        score = 0

        title = r.get("title", "").lower()

        if query in title:
            score += 10

        if r["source"] == "kaggle":
            score += 2

        elif r["source"] == "huggingface":
            score += 1

        r["_score"] = score

    all_results.sort(
        key=lambda x: x["_score"],
        reverse=True,
    )

    for r in all_results:
        r.pop("_score", None)

    total = len(all_results)

    return {
        "success": True,
        "query": q,
        "total_results": total,
        "offset": offset,
        "limit": limit,
        "providers": provider_status,
        "results": all_results[offset : offset + limit],
    }