# app/connectors/kaggle.py

from app.connectors.base import BaseConnector
from typing import List, Dict, Any, Optional
import asyncio
import os
import json
import tempfile
import traceback
import stat


class KaggleConnector(BaseConnector):
    """Kaggle API connector"""

    def __init__(self):
        super().__init__()
        self.source_name = "kaggle"
        self.api = None
        self.authenticated = False

        print("========== Initializing Kaggle Connector ==========")

        try:
            username = os.getenv("KAGGLE_USERNAME")
            key = os.getenv("KAGGLE_KEY")

            if not username or not key:
                raise RuntimeError(
                    "Missing KAGGLE_USERNAME or KAGGLE_KEY environment variables."
                )

            # Create temporary config directory
            temp_dir = tempfile.mkdtemp()
            os.environ["KAGGLE_CONFIG_DIR"] = temp_dir

            json_path = os.path.join(temp_dir, "kaggle.json")

            with open(json_path, "w") as f:
                json.dump(
                    {
                        "username": username,
                        "key": key,
                    },
                    f,
                )

            # Kaggle expects chmod 600
            os.chmod(json_path, stat.S_IRUSR | stat.S_IWUSR)

            from kaggle.api.kaggle_api_extended import KaggleApi

            self.api = KaggleApi()
            self.api.authenticate()

            self.authenticated = True

            print("✅ Kaggle authenticated successfully!")

        except Exception:
            print("❌ Kaggle authentication failed")
            traceback.print_exc()

            self.authenticated = False
            self.api = None

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search Kaggle datasets"""

        if not self.authenticated or self.api is None:
            print("⚠️ Kaggle unavailable. Returning sample result.")
            return self._sample_results(query)

        try:
            loop = asyncio.get_running_loop()

            datasets = await loop.run_in_executor(
                None,
                lambda: self.api.dataset_list(
                    search=query,
                    page=1,
                ),
            )

            results = []

            for dataset in datasets[:limit]:

                tags = []

                if getattr(dataset, "tags", None):
                    for tag in dataset.tags:
                        if hasattr(tag, "_name"):
                            tags.append(tag._name)
                        elif isinstance(tag, dict):
                            tags.append(tag.get("_name", ""))

                ref = (
                    getattr(dataset, "ref", None)
                    or getattr(dataset, "id", None)
                    or ""
                )

                results.append(
                    {
                        "title": getattr(dataset, "title", "Unknown"),
                        "description": (
                            getattr(dataset, "description", "")[:500]
                            if getattr(dataset, "description", "")
                            else ""
                        ),
                        "source": "kaggle",
                        "license": "Unknown",
                        "download_url": f"https://www.kaggle.com/api/v1/datasets/download/{ref}",
                        "source_url": f"https://www.kaggle.com/datasets/{ref}",
                        "file_type": "csv",
                        "tags": tags,
                        "size": getattr(dataset, "size", 0) or 0,
                        "samples": getattr(dataset, "totalRows", 0) or 0,
                        "features": getattr(dataset, "columnsCount", 0) or 0,
                        "last_updated": str(
                            getattr(dataset, "lastUpdated", "")
                        ),
                    }
                )

            print(f"✅ Kaggle returned {len(results)} datasets")

            return results

        except Exception:
            print("❌ Kaggle search failed")
            traceback.print_exc()
            return self._sample_results(query)

    async def get_dataset(
        self, dataset_id: str
    ) -> Optional[Dict[str, Any]]:

        if not self.authenticated or self.api is None:
            return None

        try:
            loop = asyncio.get_running_loop()

            dataset = await loop.run_in_executor(
                None,
                lambda: self.api.dataset_view(dataset_id),
            )

            tags = []

            if getattr(dataset, "tags", None):
                for tag in dataset.tags:
                    if hasattr(tag, "_name"):
                        tags.append(tag._name)
                    elif isinstance(tag, dict):
                        tags.append(tag.get("_name", ""))

            ref = (
                getattr(dataset, "ref", None)
                or getattr(dataset, "id", None)
                or dataset_id
            )

            return {
                "title": getattr(dataset, "title", "Unknown"),
                "description": getattr(dataset, "description", ""),
                "source": "kaggle",
                "license": "Unknown",
                "download_url": f"https://www.kaggle.com/api/v1/datasets/download/{ref}",
                "source_url": f"https://www.kaggle.com/datasets/{ref}",
                "file_type": "csv",
                "tags": tags,
                "size": getattr(dataset, "size", 0) or 0,
                "samples": getattr(dataset, "totalRows", 0) or 0,
                "features": getattr(dataset, "columnsCount", 0) or 0,
                "last_updated": str(
                    getattr(dataset, "lastUpdated", "")
                ),
            }

        except Exception:
            print("❌ Kaggle dataset lookup failed")
            traceback.print_exc()
            return None

    def _sample_results(self, query: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": f"Sample: {query} dataset",
                "description": "Kaggle connector unavailable.",
                "source": "kaggle",
                "license": "Unknown",
                "download_url": "",
                "source_url": "https://www.kaggle.com/datasets",
                "file_type": "csv",
                "tags": [query],
                "size": 0,
                "samples": 0,
                "features": 0,
                "last_updated": "",
            }
        ]