"""SQLite schema and queries.

Single table `entries`: one row per repository. The owner login lives in
the `profile` column; following status is mirrored across all rows of the
same profile to keep follow state consistent.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    repo         TEXT PRIMARY KEY,
    profile      TEXT NOT NULL,
    clone_url    TEXT NOT NULL,
    html_url     TEXT NOT NULL DEFAULT '',
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL,
    followed     INTEGER NOT NULL DEFAULT 0,
    starred      INTEGER NOT NULL DEFAULT 0,
    idea         REAL,
    skill        REAL,
    description  TEXT,
    security_flag   INTEGER NOT NULL DEFAULT 0,
    security_reason TEXT
);
CREATE INDEX IF NOT EXISTS entries_profile_idx  ON entries(profile);
CREATE INDEX IF NOT EXISTS entries_updated_idx  ON entries(updated_at);
CREATE INDEX IF NOT EXISTS entries_idea_skill_idx ON entries((COALESCE(idea,0) + COALESCE(skill,0)));
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    add_missing_columns(conn)
    conn.commit()
    return conn


def add_missing_columns(conn: sqlite3.Connection) -> None:
    """Idempotently add security columns to a pre-existing entries table
    (CREATE TABLE IF NOT EXISTS does not alter an already-created table)."""
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(entries)")}
    if "security_flag" not in existing:
        conn.execute("ALTER TABLE entries ADD COLUMN security_flag INTEGER NOT NULL DEFAULT 0")
    if "security_reason" not in existing:
        conn.execute("ALTER TABLE entries ADD COLUMN security_reason TEXT")


def known_repos(conn: sqlite3.Connection) -> set[str]:
    return {row["repo"] for row in conn.execute("SELECT repo FROM entries")}


def insert_repo(
    conn: sqlite3.Connection,
    repo: str,
    profile: str,
    clone_url: str,
    html_url: str,
) -> bool:
    """Insert a new repo entry. Returns True if inserted, False if it existed."""
    now = now_iso()
    cur = conn.execute(
        """
        INSERT OR IGNORE INTO entries
            (repo, profile, clone_url, html_url, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (repo, profile, clone_url, html_url, now, now),
    )
    conn.commit()
    return cur.rowcount > 0


def unevaluated(conn: sqlite3.Connection, limit: int | None = None) -> list[sqlite3.Row]:
    sql = "SELECT * FROM entries WHERE idea IS NULL OR skill IS NULL ORDER BY created_at ASC"
    if limit is not None:
        sql += f" LIMIT {int(limit)}"
    return list(conn.execute(sql))


def save_evaluation(
    conn: sqlite3.Connection,
    repo: str,
    idea: float,
    skill: float,
    description: str,
    security_flag: bool = False,
    security_reason: str = "",
) -> None:
    conn.execute(
        """
        UPDATE entries
           SET idea = ?, skill = ?, description = ?,
               security_flag = ?, security_reason = ?, updated_at = ?
         WHERE repo = ?
        """,
        (idea, skill, description, 1 if security_flag else 0,
         security_reason or None, now_iso(), repo),
    )
    conn.commit()


def window_cutoff_iso(hours: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat(timespec="seconds")


def unfollowed_above(
    conn: sqlite3.Connection,
    min_score: float,
    window_hours: int,
) -> list[sqlite3.Row]:
    """Distinct profiles with at least one repo updated in the window where idea+skill > min_score
    and which we have not followed yet. Returns one representative row per profile."""
    cutoff = window_cutoff_iso(window_hours)
    return list(
        conn.execute(
            """
            SELECT * FROM entries
             WHERE followed = 0
               AND updated_at >= ?
               AND idea IS NOT NULL AND skill IS NOT NULL
               AND (idea + skill) > ?
               AND COALESCE(security_flag, 0) = 0
             GROUP BY profile
             ORDER BY (idea + skill) DESC
            """,
            (cutoff, min_score),
        )
    )


def unstarred_above(
    conn: sqlite3.Connection,
    min_score: float,
    window_hours: int,
) -> list[sqlite3.Row]:
    cutoff = window_cutoff_iso(window_hours)
    return list(
        conn.execute(
            """
            SELECT * FROM entries
             WHERE starred = 0
               AND updated_at >= ?
               AND idea IS NOT NULL AND skill IS NOT NULL
               AND (idea + skill) > ?
               AND COALESCE(security_flag, 0) = 0
             ORDER BY (idea + skill) DESC
            """,
            (cutoff, min_score),
        )
    )


def mark_followed(conn: sqlite3.Connection, profile: str) -> None:
    conn.execute("UPDATE entries SET followed = 1 WHERE profile = ?", (profile,))
    conn.commit()


def mark_starred(conn: sqlite3.Connection, repo: str) -> None:
    conn.execute("UPDATE entries SET starred = 1 WHERE repo = ?", (repo,))
    conn.commit()


def stats(conn: sqlite3.Connection) -> dict[str, Any]:
    total = conn.execute("SELECT COUNT(*) AS c FROM entries").fetchone()["c"]
    evaluated = conn.execute(
        "SELECT COUNT(*) AS c FROM entries WHERE idea IS NOT NULL"
    ).fetchone()["c"]
    followed = conn.execute("SELECT COUNT(DISTINCT profile) AS c FROM entries WHERE followed = 1").fetchone()["c"]
    starred = conn.execute("SELECT COUNT(*) AS c FROM entries WHERE starred = 1").fetchone()["c"]
    flagged = conn.execute("SELECT COUNT(*) AS c FROM entries WHERE security_flag = 1").fetchone()["c"]
    return {"total": total, "evaluated": evaluated, "followed": followed,
            "starred": starred, "flagged": flagged}
