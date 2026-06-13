"""
Feature drift monitoring against training reference statistics.
"""

from __future__ import annotations

import joblib
import numpy as np
import pandas as pd

from config.paths import PREPROCESS_DIR, REFERENCE_STATS

DRIFT_FEATURES = [
    "TransactionAmt", "amount_log", "dist1", "dist1_log",
    "hour", "is_night", "is_high_amount", "is_mobile",
]


def load_reference_stats() -> dict:
    path = REFERENCE_STATS
    if path.exists():
        stats = joblib.load(path)
        if isinstance(stats, dict):
            return stats

    medians_path = PREPROCESS_DIR / "feature_medians.pkl"
    if medians_path.exists():
        medians = joblib.load(medians_path)
        return {
            col: {"mean": float(medians[col]), "std": 1.0, "p25": 0.0, "p75": 0.0}
            for col in DRIFT_FEATURES
            if col in medians
        }
    return {}


def _feature_health(current: pd.Series, ref: dict) -> float:
    """Return 0–100 health score (100 = no drift)."""
    values = pd.to_numeric(current, errors="coerce").dropna()
    if values.empty:
        return 50.0

    mean = float(values.mean())
    ref_mean = float(ref.get("mean", mean))
    ref_std = float(ref.get("std") or 1e-6)
    z = abs(mean - ref_mean) / max(ref_std, 1e-6)
    return float(np.clip(100 - z * 18, 5, 100))


def compute_drift_report(df: pd.DataFrame) -> dict:
    """
    Compare batch/uploaded data to training reference distributions.
    Returns per-feature health scores and an overall drift index.
    """
    reference = load_reference_stats()
    if not reference or df is None or df.empty:
        return {
            "available": False,
            "overall_health": None,
            "features": [],
            "alert": "Reference statistics not found. Retrain models to enable drift monitoring.",
        }

    rows = []
    for col, ref in reference.items():
        if col not in df.columns:
            continue
        health = _feature_health(df[col], ref)
        rows.append({
            "feature": col,
            "health": round(health, 1),
            "batch_mean": round(float(pd.to_numeric(df[col], errors="coerce").mean()), 4),
            "ref_mean": round(float(ref.get("mean", 0)), 4),
        })

    if not rows:
        return {
            "available": False,
            "overall_health": None,
            "features": [],
            "alert": "No overlapping drift features in the uploaded dataset.",
        }

    overall = float(np.mean([r["health"] for r in rows]))
    alert = None
    if overall < 65:
        alert = "Significant distribution shift detected — consider retraining or threshold review."

    return {
        "available": True,
        "overall_health": round(overall, 1),
        "features": rows,
        "alert": alert,
    }
