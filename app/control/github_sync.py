# app/control/github_sync.py
import os
import aiohttp

GH_OWNER = os.getenv("GH_OWNER")
GH_REPO = os.getenv("GH_REPO")
GH_PAT = os.getenv("GH_PAT")

API_URL = f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/dispatches"

class GithubSyncError(Exception):
    pass

async def send_status_sync(block: str, content: str) -> None:
    if not (GH_OWNER and GH_REPO and GH_PAT):
        raise GithubSyncError("GH_OWNER/GH_REPO/GH_PAT not set")

    payload = {
        "event_type": "status_sync",
        "client_payload": { "block": block, "content": content }
    }
    headers = {
        "Authorization": f"Bearer {GH_PAT}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "elaya-stagecoach-bot"
    }

    async with aiohttp.ClientSession(headers=headers) as s:
        async with s.post(API_URL, json=payload, timeout=20) as r:
            if r.status not in (200, 201, 202, 204):
                txt = await r.text()
                raise GithubSyncError(f"GitHub dispatch failed: {r.status} {txt}")
