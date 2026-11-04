"""Private, independent SQLite report history for WifCam Helper.

This is NOT YadroKreator's factory.sqlite3 and never stores raw microphone or
video recordings. The legacy last-report.json stays untouched until a new
report has been committed to history.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import sqlite3
from uuid import uuid4


@contextmanager
def _connect(state: Path):
    state.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(state, 0o700)
    db_path = state / "history.sqlite3"
    if db_path.is_symlink():
        raise ValueError("Symlinked Helper history database refused")
    fd = os.open(db_path, os.O_RDWR | os.O_CREAT, 0o600)
    os.close(fd)
    os.chmod(db_path, 0o600)
    # The parent directory is 0700. Do not mutate process-global umask
    # in ThreadingHTTPServer while concurrent diagnostics are running.
    con = sqlite3.connect(db_path, timeout=10)
    try:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA busy_timeout=10000")
        con.execute(
            "CREATE TABLE IF NOT EXISTS reports ("
            "id TEXT PRIMARY KEY, created_utc TEXT NOT NULL, "
            "test_name TEXT NOT NULL, payload TEXT NOT NULL)"
        )
        # Idempotently import the old last report without deleting it.
        legacy = state / "last-report.json"
        if legacy.is_file() and not legacy.is_symlink():
            try:
                doc = json.loads(legacy.read_text(encoding="utf-8"))
                if (isinstance(doc, dict)
                    and doc.get("schema") == "peginelab.wifcam-helper.report.v1"
                    and isinstance(doc.get("result"), dict)):
                    con.execute(
                        "INSERT OR IGNORE INTO reports VALUES (?,?,?,?)",
                        ("legacy-last-report", str(doc.get("created_utc", "")),
                         str(doc["result"].get("test", "legacy")),
                         json.dumps(doc, ensure_ascii=False)),
                    )
            except (json.JSONDecodeError, UnicodeError):
                # Keep malformed original intact for manual inspection.
                pass
        con.commit()
        yield con
        con.commit()
    finally:
        con.close()


def append(state: Path, doc: dict) -> None:
    with _connect(state) as con:
        con.execute(
            "INSERT INTO reports (id, created_utc, test_name, payload) VALUES (?,?,?,?)",
            (uuid4().hex, doc["created_utc"],
             str(doc["result"].get("test", "other")),
             json.dumps(doc, ensure_ascii=False)),
        )


def recent(state: Path, limit: int = 20) -> list[dict]:
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ValueError("History limit must be 1..100")
    with _connect(state) as con:
        return [
            json.loads(row[0])
            for row in con.execute(
                "SELECT payload FROM reports ORDER BY rowid DESC LIMIT ?", (limit,)
            )
        ]


def summary(state: Path) -> dict:
    with _connect(state) as con:
        count = con.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
        last = con.execute(
            "SELECT created_utc, test_name FROM reports ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
    return {"total": count, "last_utc": last[0] if last else None,
            "last_test": last[1] if last else None,
            "path": str(state / "history.sqlite3")}
