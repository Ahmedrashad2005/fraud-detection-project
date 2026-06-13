# dashboard/utils/helpers.py
"""
Utility helpers for the dashboard.
"""

import json
from pathlib import Path

import pandas as pd
import numpy as np

from config.paths import ARTIFACTS_DIR


def format_currency(value: float) -> str:
    """Format a dollar amount with appropriate suffix."""
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        return f"${value / 1_000:.0f}K"
    else:
        return f"${value:,.2f}"


def format_pct(value: float, decimals: int = 1) -> str:
    """Format a fraction as a percentage string."""
    return f"{value * 100:.{decimals}f}%"


def get_threshold_description(threshold: float) -> str:
    """Return a human-readable description for a given threshold value."""
    if threshold >= 0.85:
        return (
            f"Current Threshold: {threshold:.2f} | "
            f"Status: High Precision Mode (Precision: ~90%, Recall: ~40%). "
            f"Minimizes false positives — best for low-volume, high-value transactions."
        )
    elif threshold >= 0.65:
        return (
            f"Current Threshold: {threshold:.2f} | "
            f"Status: Balanced Risk (Precision: ~75%, Recall: ~60%). "
            f"Recommended for maximizing bank asset protection over high false positives."
        )
    elif threshold >= 0.45:
        return (
            f"Current Threshold: {threshold:.2f} | "
            f"Status: Moderate Sensitivity (Precision: ~55%, Recall: ~75%). "
            f"Catches more fraud but increases manual review volume."
        )
    else:
        return (
            f"Current Threshold: {threshold:.2f} | "
            f"Status: High Recall Mode (Precision: ~35%, Recall: ~90%). "
            f"Maximum fraud detection — expect significant false positive overhead."
        )


def _load_ensemble_auc() -> float:
    """Load the ensemble AUC from the evaluation report, with a safe fallback."""
    report_path = ARTIFACTS_DIR / "evaluation_report.json"
    try:
        if report_path.exists():
            with report_path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
            if isinstance(payload, list):
                for entry in payload:
                    if entry.get("model") == "Ensemble":
                        return float(entry.get("auc", 0.0))
    except Exception:
        pass
    return 0.0


def compute_batch_stats(df: pd.DataFrame) -> dict:
    """Compute summary statistics from a processed batch DataFrame."""
    total = len(df)
    fraud_col = None
    if "prediction" in df.columns:
        fraud_col = "prediction"
    elif "isFraud" in df.columns:
        fraud_col = "isFraud"

    if fraud_col:
        fraud_count = int(df[fraud_col].sum())
    else:
        fraud_count = 0

    fraud_rate = (fraud_count / total * 100) if total > 0 else 0

    # Protected amount
    if fraud_col and "TransactionAmt" in df.columns:
        protected = float(df.loc[df[fraud_col] == 1, "TransactionAmt"].sum())
    else:
        protected = 0.0

    # AUC from evaluation report (not hardcoded)
    auc = _load_ensemble_auc()

    return {
        "total":     total,
        "fraud":     fraud_count,
        "rate":      fraud_rate,
        "protected": protected,
        "auc":       auc,
    }
