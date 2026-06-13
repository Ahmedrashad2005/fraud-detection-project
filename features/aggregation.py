"""Train-time aggregation features and inference-time replay."""

from __future__ import annotations

from typing import Any

import joblib
import pandas as pd

from config.paths import AGGREGATION_MAPS

AGG_CONFIGS = [
    ("card1", "TransactionAmt", ["mean", "std", "count"]),
    ("card2", "TransactionAmt", ["mean", "count"]),
    ("P_emaildomain", "TransactionAmt", ["mean", "count"]),
    ("DeviceType", "TransactionAmt", ["mean", "count"]),
]


def fit_aggregation_features(
    X_train: pd.DataFrame,
    X_val: pd.DataFrame,
    X_test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """
    Fit aggregation mappings on train only, apply them to all splits, and
    return serializable maps for inference replay.
    """
    artifact: dict[str, Any] = {"features": [], "derived": []}

    for group_col, value_col, aggs in AGG_CONFIGS:
        if group_col not in X_train.columns or value_col not in X_train.columns:
            continue

        for agg in aggs:
            col_name = f"{group_col}_{value_col}_{agg}"
            agg_map = X_train.groupby(group_col)[value_col].agg(agg).fillna(0)
            default = float(X_train[value_col].agg(agg)) if agg != "count" else 0.0
            if pd.isna(default):
                default = 0.0

            for frame in (X_train, X_val, X_test):
                frame[col_name] = frame[group_col].map(agg_map).fillna(default)

            artifact["features"].append({
                "group_col": group_col,
                "value_col": value_col,
                "agg": agg,
                "col_name": col_name,
                "mapping": agg_map.to_dict(),
                "default": default,
            })
            print(f"  OK {col_name}")

    if "card1_TransactionAmt_mean" in X_train.columns:
        for frame in (X_train, X_val, X_test):
            frame["amt_vs_card1_mean"] = (
                frame["TransactionAmt"] / (frame["card1_TransactionAmt_mean"] + 1)
            )
        artifact["derived"].append("amt_vs_card1_mean")
        print("  OK amt_vs_card1_mean")

    return X_train, X_val, X_test, artifact


def save_aggregation_artifact(artifact: dict[str, Any]) -> None:
    AGGREGATION_MAPS.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, AGGREGATION_MAPS)


def apply_aggregation_features(df: pd.DataFrame) -> pd.DataFrame:
    """Replay train-fitted aggregation features during inference."""
    if not AGGREGATION_MAPS.exists():
        return df

    artifact = joblib.load(AGGREGATION_MAPS)
    if not isinstance(artifact, dict):
        return df

    df = df.copy()
    for spec in artifact.get("features", []):
        group_col = spec.get("group_col")
        col_name = spec.get("col_name")
        mapping = spec.get("mapping", {})
        default = spec.get("default", 0.0)
        if not group_col or not col_name or group_col not in df.columns:
            continue
        df[col_name] = df[group_col].map(mapping).fillna(default)

    if (
        "amt_vs_card1_mean" in artifact.get("derived", [])
        and "TransactionAmt" in df.columns
        and "card1_TransactionAmt_mean" in df.columns
    ):
        df["amt_vs_card1_mean"] = (
            df["TransactionAmt"] / (df["card1_TransactionAmt_mean"] + 1)
        )

    return df
