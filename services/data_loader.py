"""
Data and inference-boundary helpers for the Streamlit fraud UI.

This module owns safe IO, lightweight artifact health checks, and cached access
to the existing inference layer in ``models.predict``. It intentionally does
not load models directly or implement prediction logic.
"""

from __future__ import annotations

import importlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

import pandas as pd
import streamlit as st

from config.paths import ARTIFACTS_DIR, HEAVY_DIR, LIGHT_DIR, PREPROCESS_DIR


DEFAULT_THRESHOLD = 0.50
MAX_PREVIEW_ROWS = 5_000
SUPPORTED_UPLOAD_TYPES = (".csv", ".xlsx", ".xls")


@dataclass(frozen=True)
class LoadResult:
    """Structured, non-throwing result for service operations."""

    ok: bool
    data: Any = None
    message: str = ""


@dataclass(frozen=True)
class InferenceBackend:
    """Cached handle to ``models.predict`` without duplicating model logic."""

    ok: bool
    predict: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    predict_light: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    predict_realtime: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    predict_batch_heavy: Callable[..., pd.DataFrame] | None = None
    models: tuple[Any, ...] | None = None
    message: str = ""


ARTIFACT_PATHS: Mapping[str, Path] = {
    "xgb_heavy": HEAVY_DIR / "xgb_heavy.pkl",
    "lgbm_heavy": HEAVY_DIR / "lgbm_heavy.pkl",
    "iso_forest": HEAVY_DIR / "iso_forest.pkl",
    "xgb_light": LIGHT_DIR / "xgb_light.pkl",
    "lgbm_light": LIGHT_DIR / "lgbm_light.pkl",
    "all_features": PREPROCESS_DIR / "all_features.pkl",
    "top35_features": PREPROCESS_DIR / "manual_features.pkl",
    "encoders": PREPROCESS_DIR / "encoders.pkl",
    "medians": PREPROCESS_DIR / "medians.pkl",
    "feature_columns": PREPROCESS_DIR / "feature_columns.pkl",
    "threshold": PREPROCESS_DIR / "threshold.pkl",
}


def _coerce_float(value: Any, default: float = DEFAULT_THRESHOLD) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@st.cache_resource(show_spinner=False)
def get_inference_backend() -> InferenceBackend:
    """
    Import and cache the single source of truth for inference.

    ``models.predict`` performs model loading at module import. Any import or
    artifact error is captured here so Streamlit callers can render a stable
    error state instead of crashing the app.
    """
    try:
        module = importlib.import_module("models.predict")
        predict_fn = getattr(module, "predict", None)
        predict_light_fn = getattr(module, "predict_light", None)
        predict_realtime_fn = getattr(module, "predict_realtime", None)
        predict_batch_heavy_fn = getattr(module, "predict_batch_heavy", None)
        models = getattr(module, "MODELS", None)

        if not callable(predict_fn):
            return InferenceBackend(False, message="models.predict.predict is not callable.")
        if not callable(predict_light_fn):
            return InferenceBackend(False, message="models.predict.predict_light is not callable.")
        if not callable(predict_realtime_fn):
            return InferenceBackend(False, message="models.predict.predict_realtime is not callable.")
        if not callable(predict_batch_heavy_fn):
            return InferenceBackend(False, message="models.predict.predict_batch_heavy is not callable.")
        if not isinstance(models, tuple) or len(models) < 8:
            return InferenceBackend(False, message="models.predict.MODELS is incomplete.")

        return InferenceBackend(
            True,
            predict=predict_fn,
            predict_light=predict_light_fn,
            predict_realtime=predict_realtime_fn,
            predict_batch_heavy=predict_batch_heavy_fn,
            models=models,
        )
    except Exception as exc:
        return InferenceBackend(False, message=f"Inference backend unavailable: {exc}")


def predict_transaction(payload: dict[str, Any],
                        threshold: float | None = None,
                        light_only: bool = True,
                        debug: bool = False) -> LoadResult:
    """Run a single prediction through ``models.predict`` only."""
    normalized = normalize_transaction_input(payload)
    if not normalized.ok:
        return normalized

    backend = get_inference_backend()
    predict_fn = backend.predict_light if light_only else backend.predict_realtime
    if not backend.ok or predict_fn is None:
        return LoadResult(False, None, backend.message)

    try:
        if threshold is None:
            result = predict_fn(normalized.data, debug=debug)
        else:
            result = predict_fn(normalized.data, threshold_override=threshold, debug=debug)
    except Exception as exc:
        return LoadResult(False, None, f"Prediction failed: {exc}")

    if not isinstance(result, dict):
        return LoadResult(False, None, "Prediction returned an unsupported response.")
    if result.get("error"):
        return LoadResult(False, result, str(result["error"]))

    return LoadResult(True, result, "")


def predict_batch_transactions(df: pd.DataFrame,
                               threshold: float | None = None) -> LoadResult:
    """Run heavy batch inference through ``models.predict.predict_batch_heavy``."""
    if df is None or df.empty:
        return LoadResult(False, None, "No rows are available for inference.")

    backend = get_inference_backend()
    if not backend.ok or backend.predict_batch_heavy is None:
        return LoadResult(False, None, backend.message)

    try:
        if threshold is None:
            result = backend.predict_batch_heavy(df)
        else:
            result = backend.predict_batch_heavy(df, threshold_override=threshold)
    except Exception as exc:
        return LoadResult(False, None, f"Batch inference failed: {exc}")

    return LoadResult(True, result, f"Scored {len(result):,} transactions.")


def _models_tuple() -> tuple[Any, ...] | None:
    backend = get_inference_backend()
    return backend.models if backend.ok else None


def load_model_artifacts() -> dict[str, Any]:
    """
    Compatibility wrapper exposing models already loaded by ``models.predict``.

    This function does not perform artifact loading itself.
    """
    models = _models_tuple()
    if models is None:
        return {}

    names = ("xgb_heavy", "lgbm_heavy", "iso_forest", "xgb_light", "lgbm_light")
    return {name: models[index] for index, name in enumerate(names)}


def load_preprocessing_artifacts() -> dict[str, Any]:
    """
    Compatibility wrapper for preprocessing assets exposed by ``models.predict``.

    Only assets already loaded by the inference layer are returned.
    """
    models = _models_tuple()
    if models is None:
        return {}

    _, _, _, _, _, threshold, top35, all_features = models[:8]
    return {
        "threshold": threshold,
        "top35_features": top35,
        "all_features": all_features,
    }


@st.cache_data(show_spinner=False)
def load_evaluation_report() -> list[dict[str, Any]]:
    """Load the optional evaluation report produced by offline training."""
    report_path = ARTIFACTS_DIR / "evaluation_report.json"
    try:
        if not report_path.exists():
            return []
        with report_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return payload if isinstance(payload, list) else []
    except Exception:
        return []


def load_threshold(default: float = DEFAULT_THRESHOLD) -> float:
    """Return the active threshold from the inference layer or a safe default."""
    value = load_preprocessing_artifacts().get("threshold", default)
    threshold = _coerce_float(value, default)
    return min(max(threshold, 0.01), 0.99)


def get_artifact_status() -> dict[str, bool]:
    """Return file and backend availability without loading artifacts here."""
    status = {name: path.exists() and path.is_file() for name, path in ARTIFACT_PATHS.items()}
    status["inference_backend"] = get_inference_backend().ok
    return status


def get_artifact_errors() -> list[str]:
    """Return user-safe artifact/backend diagnostics for alert components."""
    errors = [f"Missing artifact: {name}" for name, available in get_artifact_status().items() if not available]
    backend = get_inference_backend()
    if not backend.ok and backend.message:
        errors.append(backend.message)
    return errors


def is_realtime_ready() -> bool:
    """Check whether the single-transaction inference backend is ready."""
    status = get_artifact_status()
    required = ("xgb_heavy", "lgbm_heavy", "iso_forest", "xgb_light", "lgbm_light", "top35_features", "all_features")
    return bool(status.get("inference_backend") and all(status.get(name, False) for name in required))


def read_uploaded_table(uploaded_file: Any, max_rows: int = MAX_PREVIEW_ROWS) -> LoadResult:
    """Read a Streamlit uploaded CSV or Excel file safely."""
    if uploaded_file is None:
        return LoadResult(False, None, "No file was uploaded.")

    filename = str(getattr(uploaded_file, "name", "") or "")
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_UPLOAD_TYPES:
        return LoadResult(False, None, "Unsupported file type. Upload a CSV, XLSX, or XLS file.")

    bounded_rows = max(1, min(int(max_rows or MAX_PREVIEW_ROWS), MAX_PREVIEW_ROWS))
    try:
        if suffix == ".csv":
            df = pd.read_csv(uploaded_file, low_memory=False, nrows=bounded_rows)
        else:
            df = pd.read_excel(uploaded_file, nrows=bounded_rows)
    except Exception as exc:
        return LoadResult(False, None, f"Unable to read uploaded file: {exc}")

    if df.empty:
        return LoadResult(False, None, "Uploaded file contains no rows.")

    return LoadResult(True, df, f"Loaded {len(df):,} rows.")


def normalize_batch_input(df: pd.DataFrame) -> LoadResult:
    """Validate uploaded batch data and apply supported column aliases."""
    if df is None or df.empty:
        return LoadResult(False, None, "Uploaded file contains no rows.")

    normalized = df.copy()
    aliases = {
        "transactionamt": "TransactionAmt",
        "transaction amount": "TransactionAmt",
        "transaction_amt": "TransactionAmt",
        "amount": "TransactionAmt",
        "amt": "TransactionAmt",
    }
    existing_columns = set(normalized.columns)
    rename_map = {}

    for column in normalized.columns:
        canonical = aliases.get(str(column).strip().lower())
        if canonical and canonical not in existing_columns:
            rename_map[column] = canonical

    if rename_map:
        normalized = normalized.rename(columns=rename_map)

    required_columns = {"TransactionAmt"}
    missing_columns = sorted(required_columns - set(normalized.columns))
    if missing_columns:
        missing = ", ".join(missing_columns)
        return LoadResult(
            False,
            None,
            f"Uploaded file is missing required columns: {missing}.",
        )

    return LoadResult(True, normalized, "")


def normalize_transaction_input(payload: Mapping[str, Any]) -> LoadResult:
    """Validate and normalize one transaction payload before inference."""
    if not isinstance(payload, Mapping):
        return LoadResult(False, None, "Transaction payload must be a mapping.")

    if payload.get("TransactionAmt") in (None, ""):
        return LoadResult(False, None, "Missing required field: TransactionAmt")

    try:
        amount = float(payload["TransactionAmt"])
        dist1 = float(payload.get("dist1", 0) or 0)
        hour = int(payload.get("hour", 12))
    except (TypeError, ValueError):
        return LoadResult(False, None, "Transaction amount, distance, and hour must be numeric.")

    if amount < 0:
        return LoadResult(False, None, "Transaction amount cannot be negative.")
    if amount > 100_000:
        return LoadResult(False, None, "Transaction amount exceeds the supported limit.")
    if dist1 < 0:
        return LoadResult(False, None, "Distance cannot be negative.")
    if not 0 <= hour <= 23:
        return LoadResult(False, None, "Hour must be an integer from 0 to 23.")

    normalized: dict[str, Any] = {
        "TransactionAmt": amount,
        "ProductCD": str(payload.get("ProductCD", "W") or "W").strip() or "W",
        "card4": str(payload.get("card4", "visa") or "visa").strip().lower(),
        "card6": str(payload.get("card6", "debit") or "debit").strip().lower(),
        "P_emaildomain": str(payload.get("P_emaildomain", "gmail.com") or "gmail.com").strip().lower(),
        "DeviceType": str(payload.get("DeviceType", "desktop") or "desktop").strip().lower(),
        "dist1": dist1,
        "hour": hour,
    }

    transaction_dt = payload.get("TransactionDT")
    if transaction_dt not in (None, ""):
        try:
            normalized["TransactionDT"] = int(transaction_dt)
        except (TypeError, ValueError):
            return LoadResult(False, None, "TransactionDT must be an integer timestamp.")

    return LoadResult(True, normalized, "")


def build_demo_transaction() -> dict[str, Any]:
    """Return a deterministic transaction useful for empty UI states."""
    return {
        "TransactionAmt": 35.00,
        "ProductCD": "W",
        "card4": "visa",
        "card6": "debit",
        "P_emaildomain": "gmail.com",
        "DeviceType": "desktop",
        "dist1": 0,
        "hour": 12,
    }
