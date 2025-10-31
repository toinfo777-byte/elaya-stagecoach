import os
import aiohttp
from typing import Dict, List, Optional

RENDER_API_BASE = "https://api.render.com/v1"

class RenderClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

    async def _get(self, path: str, params: Optional[Dict] = None) -> Dict:
        url = f"{RENDER_API_BASE}{path}"
        async with aiohttp.ClientSession(headers=self.headers) as s:
            async with s.get(url, params=params) as r:
                r.raise_for_status()
                return await r.json()

    async def get_service(self, service_id: str) -> Dict:
        return await self._get(f"/services/{service_id}")

    async def get_last_deploy(self, service_id: str) -> Optional[Dict]:
        data = await self._get(f"/services/{service_id}/deploys", params={"limit": 1})
        if isinstance(data, list) and data:
            return data[0]
        return None

    @staticmethod
    def load_ids_and_labels() -> List[Dict]:
        ids = [x.strip() for x in os.getenv("RENDER_SERVICE_IDS", "").split(",") if x.strip()]
        labels = [x.strip() for x in os.getenv("RENDER_SERVICE_LABELS", "").split(",")] if os.getenv("RENDER_SERVICE_LABELS") else []
        result = []
        for i, sid in enumerate(ids):
            label = labels[i] if i < len(labels) else sid
            result.append({"id": sid, "label": label})
        return result
