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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS review_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                transaction_id TEXT NOT NULL,
                previous_status TEXT NOT NULL,
                new_status TEXT NOT NULL,
                reason TEXT,
                analyst TEXT NOT NULL,
                risk_score REAL
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


def log_review_action(
    transaction_id: str,
    previous_status: str,
    new_status: str,
    reason: str = "",
    analyst: str = "A. Hassan",
    risk_score: float | None = None,
) -> None:
    """Persist a human review decision for operational traceability."""
    try:
        _ensure_schema()
        with sqlite3.connect(_db_path()) as conn:
            conn.execute(
                """
                INSERT INTO review_actions
                (created_at, transaction_id, previous_status, new_status, reason, analyst, risk_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    str(transaction_id),
                    str(previous_status),
                    str(new_status),
                    str(reason or ""),
                    str(analyst or "A. Hassan"),
                    None if risk_score is None else float(risk_score),
                ),
            )
            conn.commit()
    except Exception as exc:
        logger.warning("Review audit log write failed: %s", exc)


def fetch_review_actions(transaction_id: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
    """Fetch analyst review actions, newest first."""
    _ensure_schema()
    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        if transaction_id:
            rows = conn.execute(
                """
                SELECT created_at, transaction_id, previous_status, new_status, reason, analyst, risk_score
                FROM review_actions
                WHERE transaction_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (str(transaction_id), max(1, int(limit))),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT created_at, transaction_id, previous_status, new_status, reason, analyst, risk_score
                FROM review_actions
                ORDER BY id DESC
                LIMIT ?
                """,
                (max(1, int(limit)),),
            ).fetchall()
    return [dict(r) for r in rows]


def fetch_latest_review_statuses(limit: int = 5000) -> dict[str, str]:
    """Return the latest human review status per transaction."""
    actions = fetch_review_actions(limit=limit)
    statuses: dict[str, str] = {}
    for action in actions:
        transaction_id = str(action.get("transaction_id", ""))
        if transaction_id and transaction_id not in statuses:
            statuses[transaction_id] = str(action.get("new_status", "Pending"))
    return statuses
