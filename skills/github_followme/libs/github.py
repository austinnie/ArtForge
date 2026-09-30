"""Minimal GitHub REST helpers (stdlib only)."""

from __future__ import annotations

import base64
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


GITHUB_API = "https://api.github.com"

logger = logging.getLogger(__name__)


def auth_headers(token: str) -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "followme",
    }


def git_basic_auth_header(token: str) -> str:
    if not token:
        return ""
    raw = base64.b64encode(f"x-access-token:{token}".encode("utf-8")).decode("ascii")
    return f"Authorization: Basic {raw}"


def request(
    method: str,
    path: str,
    settings: dict[str, Any],
    params: dict[str, Any] | None = None,
) -> tuple[int, Any]:
    url = f"{GITHUB_API}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url=url, method=method, headers=auth_headers(settings["github_token"]))
    try:
        with urllib.request.urlopen(req, timeout=settings["request_timeout_seconds"]) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.getcode(), (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            body = {"raw": raw}
        return exc.code, body


def search_recent_repositories(settings: dict[str, Any], wanted: int, skip: set[str]) -> list[dict[str, Any]]:
    """Search GitHub for recent repos; return up to `wanted` items whose full_name is not in `skip`."""
    out: list[dict[str, Any]] = []
    seen: set[str] = set(skip)
    query = f"language:{settings['language']} stars:<{settings['max_stars']}"
    page = 1
    while len(out) < wanted and page <= 10:
        code, body = request(
            "GET", "/search/repositories", settings,
            params={"q": query, "sort": "updated", "order": "desc", "per_page": 100, "page": page},
        )
        if code != 200 or not isinstance(body, dict):
            logger.error(f"Search failed (code={code}): {body}")
            break
        items = body.get("items") or []
        if not items:
            break
        for item in items:
            if not isinstance(item, dict):
                continue
            full_name = str(item.get("full_name", "")).strip()
            owner = item.get("owner") or {}
            login = str(owner.get("login", "")).strip() if isinstance(owner, dict) else ""
            clone_url = str(item.get("clone_url", "")).strip()
            if not full_name or not login or not clone_url or full_name in seen:
                continue
            seen.add(full_name)
            out.append({
                "full_name": full_name,
                "owner_login": login,
                "clone_url": clone_url,
                "html_url": str(item.get("html_url", "")),
            })
            if len(out) >= wanted:
                break
        page += 1
    return out


def is_starred(settings: dict[str, Any], repo: str) -> bool:
    code, body = request("GET", f"/user/starred/{repo}", settings)
    return code == 204


def star(settings: dict[str, Any], repo: str) -> bool:
    if is_starred(settings, repo):
        return False
    code, body = request("PUT", f"/user/starred/{repo}", settings)
    if code == 204:
        return True
    logger.warning(f"Star failed for {repo}: {code} {body}")
    return False


def is_following(settings: dict[str, Any], login: str) -> bool:
    code, body = request("GET", f"/user/following/{login}", settings)
    return code == 204


def follow(settings: dict[str, Any], login: str) -> bool:
    if is_following(settings, login):
        return False
    code, body = request("PUT", f"/user/following/{login}", settings)
    if code == 204:
        return True
    logger.warning(f"Follow failed for {login}: {code} {body}")
    return False
