"""
SQLite audit log for predictions (dashboard / API).
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config.settings import DB_PATH

_DB_READY = False
logger = logging.getLogger(__name__)


def _db_path() -> Path:
    path = Path(DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _ensure_schema() -> None:
    global _DB_READY
    if _DB_READY:
        return
    with sqlite3.connect(_db_path()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS prediction_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                mode TEXT NOT NULL,
                payload_json TEXT,
                risk_score REAL,
                is_fraud INTEGER,
                decision TEXT
            )
            """
        )
        conn.commit()
    _DB_READY = True


def log_prediction(
    mode: str,
    payload: dict[str, Any],
    result: dict[str, Any],
) -> None:
    """Persist a single prediction for audit / analytics."""
    try:
        _ensure_schema()
        with sqlite3.connect(_db_path()) as conn:
            conn.execute(
                """
                INSERT INTO prediction_logs
                (created_at, mode, payload_json, risk_score, is_fraud, decision)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    mode,
                    json.dumps(payload, default=str),
                    float(result.get("risk_score", 0) or 0),
                    int(bool(result.get("is_fraud", False))),
                    str(result.get("decision", "")),
                ),
            )
            conn.commit()
    except Exception as exc:
        logger.warning("Prediction audit log write failed: %s", exc)


def fetch_recent_predictions(limit: int = 50) -> list[dict[str, Any]]:
    _ensure_schema()
    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT created_at, mode, risk_score, is_fraud, decision
            FROM prediction_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (max(1, int(limit)),),
        ).fetchall()
    return [dict(r) for r in rows]
