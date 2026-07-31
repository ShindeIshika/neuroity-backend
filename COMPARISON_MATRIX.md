# Dataset Platforms Comparison Matrix

## Overview
Comparison of 10 dataset platforms integrated into the Neuroity backend API.

---

## Quick Comparison Table

| Platform | Type | Access Method | Auth Required | Python Library | Async Support | Data Quality |
|----------|------|---------------|---------------|----------------|---------------|--------------|
| **Kaggle** | Repository | Official API | ✅ Yes | `kaggle` | ✅ | High |
| **Hugging Face** | Repository | Hub API | ❌ No | `datasets` | ✅ | High |
| **UCI** | Repository | Python Library | ❌ No | `ucimlrepo` | ✅ | High |
| **OpenML** | Repository | REST API | ❌ No | `openml` | ✅ | High |
| **Zenodo** | Repository | REST API | ❌ No | `requests` | ✅ | High |
| **Figshare** | Repository | REST API | ❌ No | `requests` | ✅ | High |
| **OpenNeuro** | Repository | GraphQL | ❌ No | `httpx` | ✅ | High |
| **PhysioNet** | Repository | REST API | ❌ No | `httpx` | ✅ | High |
| **GitHub** | Repository | Search API | ❌ No | `httpx` | ✅ | Medium |
| **Google Dataset** | Search Engine | Scraping | ❌ No | `httpx` + `bs4` | ✅ | N/A |

---

## Detailed Feature Comparison

| Platform | Primary Domain | Dataset Count | File Formats | License Info |
|----------|---------------|---------------|--------------|--------------|
| **Kaggle** | All domains | 500,000+ | CSV, JSON, ZIP | Various |
| **Hugging Face** | NLP, CV, Audio | 10,000+ | Dataset format | Various |
| **UCI** | Tabular, ML | 600+ | CSV | Open |
| **OpenML** | Tabular, Benchmarks | 5,000+ | ARFF, CSV | Open |
| **Zenodo** | Research, Scientific | 1,000,000+ | All formats | Various |
| **Figshare** | Academic, Research | 100,000+ | All formats | Various |
| **OpenNeuro** | Neuroimaging | 1,000+ | BIDS | Open |
| **PhysioNet** | Physiologic Signals | 100+ | EDF, CSV | Open |
| **GitHub** | All domains | Unlimited | All formats | Various |
| **Google Dataset** | All domains | 45,000,000+ | All formats | Various |

---

## API Integration Status

| Platform | Search | Get Dataset | Filters | Caching |
|----------|--------|-------------|---------|---------|
| Kaggle | ✅ | ✅ | ✅ | ⏳ |
| Hugging Face | ✅ | ✅ | ✅ | ⏳ |
| UCI | ✅ | ✅ | ✅ | ⏳ |
| OpenML | ✅ | ✅ | ✅ | ⏳ |
| Zenodo | ✅ | ✅ | ✅ | ⏳ |
| Figshare | ✅ | ✅ | ✅ | ⏳ |
| OpenNeuro | ⚠️ | ✅ | ✅ | ⏳ |
| PhysioNet | ⚠️ | ✅ | ✅ | ⏳ |
| GitHub | ✅ | ✅ | ✅ | ⏳ |
| Google Dataset | ⚠️ | ❌ | ❌ | ⏳ |

---

## Authentication & Rate Limits

| Platform | API Key | Rate Limit | Cost |
|----------|---------|------------|------|
| Kaggle | ✅ | Yes | Free |
| Hugging Face | ❌ | Yes | Free |
| UCI | ❌ | No | Free |
| OpenML | ❌ | Yes | Free |
| Zenodo | ❌ | Yes | Free |
| Figshare | ❌ | Yes | Free |
| OpenNeuro | ❌ | Yes | Free |
| PhysioNet | ❌ | Yes | Free |
| GitHub | ❌ | Yes | Free |
| Google Dataset | ❌ | No | Free |

---

## Recommendations Summary

| Domain | Primary | Secondary |
|--------|---------|-----------|
| **Computer Vision** | Kaggle, Hugging Face | GitHub |
| **NLP / LLMs** | Hugging Face | Kaggle |
| **Medical** | Zenodo, PhysioNet | Kaggle |
| **Tabular Data** | UCI, OpenML | Kaggle |
| **Research** | Zenodo, Figshare | OpenNeuro |
| **Open Data** | Data.gov (future) | GitHub |

---

*Generated: July 31, 2026*