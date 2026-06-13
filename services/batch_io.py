"""Batch file helpers without Streamlit dependency."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import io

import pandas as pd

from services import ServiceResult

MAX_PREVIEW_ROWS = 5_000
SUPPORTED_UPLOAD_TYPES = (".csv", ".xlsx", ".xls")

# Backward-compatible alias
BatchResult = ServiceResult


def normalize_batch_input(df: pd.DataFrame) -> BatchResult:
    if df is None or df.empty:
        return BatchResult(False, None, "Uploaded file contains no rows.")

    normalized = df.copy()

    # ✅ Aliases for TransactionAmt — case-insensitive, covers many naming conventions
    aliases = {
        # TransactionAmt variants
        "transactionamt":        "TransactionAmt",
        "transaction amount":    "TransactionAmt",
        "transaction_amount":    "TransactionAmt",
        "transaction_amt":       "TransactionAmt",
        "transactionamount":     "TransactionAmt",
        "amount":                "TransactionAmt",
        "amt":                   "TransactionAmt",
        "price":                 "TransactionAmt",
        "value":                 "TransactionAmt",
        "tx_amount":             "TransactionAmt",
        "txn_amount":            "TransactionAmt",
        "txamt":                 "TransactionAmt",
        # Optional column aliases
        "card_type":             "card4",
        "card_network":          "card4",
        "card_brand":            "card4",
        "product_cd":            "ProductCD",
        "product":               "ProductCD",
        "device":                "DeviceType",
        "device_type":           "DeviceType",
        "email":                 "P_emaildomain",
        "email_domain":          "P_emaildomain",
        "p_email":               "P_emaildomain",
        "distance":              "dist1",
        "dist":                  "dist1",
        "transaction_dt":        "TransactionDT",
        "transaction_time":      "TransactionDT",
        "timestamp":             "TransactionDT",
    }

    rename_map = {}
    current_cols = set(normalized.columns)
    for column in normalized.columns:
        canonical = aliases.get(str(column).strip().lower())
        if canonical and canonical not in current_cols:
            rename_map[column] = canonical

    if rename_map:
        normalized = normalized.rename(columns=rename_map)

    missing = sorted({"TransactionAmt"} - set(normalized.columns))
    if missing:
        found_cols = ", ".join(sorted(df.columns.tolist())[:10])
        return BatchResult(
            False, None,
            f"Uploaded file is missing required columns: {', '.join(missing)}. "
            f"Found columns: [{found_cols}]. "
            f"Rename your amount column to 'TransactionAmt' (or use: amount, amt, value, price, tx_amount).",
        )
    return BatchResult(True, normalized, "")


def read_table_bytes(content: bytes, filename: str, max_rows: int = MAX_PREVIEW_ROWS) -> BatchResult:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_UPLOAD_TYPES:
        return BatchResult(False, None, "Unsupported file type. Upload CSV, XLSX, or XLS.")

    bounded = max(1, min(int(max_rows), MAX_PREVIEW_ROWS))
    try:
        buf = io.BytesIO(content)
        if suffix == ".csv":
            df = pd.read_csv(buf, low_memory=False, nrows=bounded)
        else:
            df = pd.read_excel(buf, nrows=bounded)
    except Exception as exc:
        return BatchResult(False, None, f"Unable to read file: {exc}")

    if df.empty:
        return BatchResult(False, None, "File contains no rows.")
    return BatchResult(True, df, f"Loaded {len(df):,} rows.")
