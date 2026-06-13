"""Artifact health checks without Streamlit."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Mapping

from config.paths import AGGREGATION_MAPS, HEAVY_DIR, LIGHT_DIR, PREPROCESS_DIR

ARTIFACT_PATHS: Mapping[str, Path] = {
    "xgb_heavy": HEAVY_DIR / "xgb_heavy.pkl",
    "lgbm_heavy": HEAVY_DIR / "lgbm_heavy.pkl",
    "iso_forest": HEAVY_DIR / "iso_forest.pkl",
    "xgb_light": LIGHT_DIR / "xgb_light.pkl",
    "lgbm_light": LIGHT_DIR / "lgbm_light.pkl",
    "all_features": PREPROCESS_DIR / "all_features.pkl",
    "manual_features": PREPROCESS_DIR / "manual_features.pkl",
    "threshold": PREPROCESS_DIR / "threshold.pkl",
    "light_threshold": PREPROCESS_DIR / "light_threshold.pkl",
    "feature_medians": PREPROCESS_DIR / "feature_medians.pkl",
    "aggregation_maps": AGGREGATION_MAPS,
}


def get_artifact_status() -> dict[str, bool]:
    status = {
        name: path.exists() and path.is_file()
        for name, path in ARTIFACT_PATHS.items()
    }
    try:
        module = importlib.import_module("models.predict")
        status["inference_backend"] = bool(
            getattr(module, "MODELS", {}).get("loaded", False)
        )
    except Exception:
        status["inference_backend"] = False
    return status
