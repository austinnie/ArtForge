"""Environment loading and default settings."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, sep, value = line.partition("=")
        if not sep:
            continue
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def env_str(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def load_settings(project_root: Path) -> dict[str, Any]:
    """Merge .env into os.environ (without overriding), then build settings dict."""
    for key, value in parse_env_file(project_root / ".env").items():
        os.environ.setdefault(key, value)

    token = env_str("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set (.env or environment)")

    ollama_url = env_str("OLLAMA_URL", "http://localhost:11434").rstrip("/")
    if "://" not in ollama_url:
        ollama_url = f"http://{ollama_url}"

    return {
        "project_root": str(project_root),
        "github_token": token,
        "ollama_url": ollama_url,
        "ollama_model": env_str("OLLAMA_MODEL", "qwen2.5-coder:7b"),
        "language": env_str("LANGUAGE", "Python"),
        "max_stars": int(env_str("MAX_STARS", "100")),
        "db_path": str(project_root / env_str("DB_PATH", "data/followme.sqlite")),
        "repo_dir": str(project_root / env_str("REPO_DIR", "data/repo")),
        "clone_depth": int(env_str("CLONE_DEPTH", "1")),
        "request_timeout_seconds": int(env_str("HTTP_TIMEOUT", "30")),
        "max_files": int(env_str("MAX_FILES", "20")),
        "max_lines_per_file": int(env_str("MAX_LINES_PER_FILE", "80")),
        "max_chars_per_file": int(env_str("MAX_CHARS_PER_FILE", "4000")),
        "max_total_chars": int(env_str("MAX_TOTAL_CHARS", "40000")),
        "max_file_bytes": int(env_str("MAX_FILE_BYTES", "262144")),
        "extensions": [
            ext.strip()
            for ext in env_str(
                "EXTENSIONS",
                ".py,.pyi,.js,.ts,.tsx,.jsx,.go,.rs,.java,.kt,.c,.h,.cpp,.hpp,"
                ".cs,.php,.rb,.swift,.scala,.lua,.sh,.sql,.yaml,.yml,.toml,.md",
            ).split(",")
            if ext.strip()
        ],
        "fetch_count": int(env_str("FETCH_COUNT", "5")),
        "subscribe_threshold": float(env_str("SUBSCRIBE_THRESHOLD", "14.0")),
        "star_threshold": float(env_str("STAR_THRESHOLD", "16.0")),
        "window_hours": int(env_str("WINDOW_HOURS", "24")),
        "dry_run": env_str("DRY_RUN", "false").lower() in ("1", "true", "yes"),
    }
