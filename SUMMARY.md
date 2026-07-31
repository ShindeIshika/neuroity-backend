# Neuroity Backend - Data Sources Summary

**Project:** Neuroity AI Backend  
**Date:** July 31, 2026  
**Total Platforms:** 10

---

## Summary Table

| # | Platform | Access Method | Python Library | Auth | Status |
|---|----------|---------------|----------------|------|--------|
| 1 | **Kaggle** | Official API | `kaggle` | ✅ Yes | ✅ Working |
| 2 | **Hugging Face** | Hub API | `datasets` / `httpx` | ❌ No | ✅ Working |
| 3 | **UCI** | Python Library | `ucimlrepo` | ❌ No | ✅ Working |
| 4 | **OpenML** | REST API | `openml` | ❌ No | ✅ Working |
| 5 | **Zenodo** | REST API | `httpx` | ❌ No | ✅ Working |
| 6 | **Figshare** | REST API | `httpx` | ❌ No | ✅ Working |
| 7 | **OpenNeuro** | GraphQL | `httpx` | ❌ No | ⚠️ Fallback |
| 8 | **PhysioNet** | REST API | `httpx` | ❌ No | ⚠️ Fallback |
| 9 | **GitHub** | Search API | `httpx` | ❌ No | ✅ Working |
| 10 | **Google Dataset** | Scraping | `httpx` + `bs4` | ❌ No | ⚠️ Limited |

---

## Access Method Details

### Official APIs (Working)
- **Kaggle:** Uses `kaggle` Python package with API key authentication
- **Hugging Face:** Uses `httpx` to query Hugging Face Hub API
- **UCI:** Uses `ucimlrepo` Python library
- **OpenML:** Uses `openml` Python library
- **Zenodo:** REST API via `httpx`
- **Figshare:** REST API v2 via `httpx`
- **GitHub:** GitHub Search API via `httpx`

### Fallback/Scraping
- **OpenNeuro:** GraphQL endpoint (fallback when API fails)
- **PhysioNet:** Multiple endpoint attempts with fallback
- **Google Dataset:** Web scraping with BeautifulSoup (no official API)

---

## Authentication Status

| Status | Platforms |
|--------|-----------|
| **Required** | Kaggle |
| **Not Required** | Hugging Face, UCI, OpenML, Zenodo, Figshare, OpenNeuro, PhysioNet, GitHub, Google Dataset |

---

## API Response Format

All responses follow this unified format:

```json
{
  "success": true,
  "query": "iris",
  "total_results": 54,
  "limit": 10,
  "results": [
    {
      "title": "Dataset Name",
      "description": "Dataset description",
      "source": "platform_name",
      "license": "License type",
      "download_url": "https://...",
      "source_url": "https://...",
      "file_type": "csv",
      "tags": ["tag1", "tag2"],
      "size": 0,
      "samples": 150,
      "features": 4,
      "last_updated": "2024-01-01"
    }
  ]
}