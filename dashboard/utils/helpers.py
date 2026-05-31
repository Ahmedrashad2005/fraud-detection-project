# dashboard/utils/helpers.py
"""
Utility helpers for the dashboard.
"""

import pandas as pd
import numpy as np


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


def safe_read_uploaded_file(uploaded_file) -> pd.DataFrame:
    """Safely read an uploaded CSV or Excel file."""
    try:
        name = uploaded_file.name.lower()
        if name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        elif name.endswith((".xlsx", ".xls")):
            return pd.read_excel(uploaded_file)
        else:
            return None
    except Exception:
        return None


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

    # AUC from evaluation report
    auc = 0.897

    return {
        "total":     total,
        "fraud":     fraud_count,
        "rate":      fraud_rate,
        "protected": protected,
        "auc":       auc,
    }
