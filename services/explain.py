"""
SHAP-based explanations for light-model (real-time) predictions.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from features.build_features import build_features
from features.preprocess import preprocess_inference


def _prepare_light_matrix(user_input: dict[str, Any], models: dict) -> pd.DataFrame | None:
    if not models.get("loaded"):
        return None

    df = pd.DataFrame([user_input])
    if "hour" in df.columns and pd.notna(df["hour"].iloc[0]):
        h = int(df["hour"].iloc[0])
        df["is_morning"] = int(6 <= h < 12)
        df["is_night"] = int(h < 6)

    df = build_features(df)
    df = preprocess_inference(df)
    manual = models["manual_features"]
    return df.reindex(columns=manual, fill_value=0)


def explain_light_transaction(
    user_input: dict[str, Any],
    models: dict,
    top_n: int = 8,
) -> dict[str, Any]:
    """
    Return top SHAP contributors for the XGBoost light model.
    Falls back to model feature importances if SHAP is unavailable.
    """
    X = _prepare_light_matrix(user_input, models)
    if X is None:
        return {"available": False, "reason": "Models not loaded", "factors": []}

    xgb = models.get("xgb_light")
    if xgb is None:
        return {"available": False, "reason": "Light model missing", "factors": []}

    try:
        import shap

        explainer = shap.TreeExplainer(xgb)
        shap_values = explainer.shap_values(X)
        if isinstance(shap_values, list):
            values = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
        else:
            values = shap_values[0]

        pairs = sorted(
            zip(X.columns, values, X.iloc[0].values),
            key=lambda x: abs(x[1]),
            reverse=True,
        )[:top_n]
        factors = [
            {
                "feature": str(name),
                "impact": round(float(impact), 4),
                "value": round(float(val), 4) if isinstance(val, (int, float, np.floating)) else str(val),
                "direction": "increases risk" if impact > 0 else "decreases risk",
            }
            for name, impact, val in pairs
        ]
        return {"available": True, "method": "shap", "factors": factors}
    except Exception as exc:
        if hasattr(xgb, "feature_importances_"):
            imp = xgb.feature_importances_
            pairs = sorted(zip(X.columns, imp, X.iloc[0].values), key=lambda x: x[1], reverse=True)[:top_n]
            factors = [
                {
                    "feature": str(name),
                    "impact": round(float(score), 4),
                    "value": round(float(val), 4) if isinstance(val, (int, float, np.floating)) else str(val),
                    "direction": "important feature",
                }
                for name, score, val in pairs
            ]
            return {
                "available": True,
                "method": "feature_importance",
                "factors": factors,
                "note": f"SHAP unavailable ({exc}); showing global importances.",
            }
        return {"available": False, "reason": str(exc), "factors": []}
