"""
Data and inference-boundary helpers for the Streamlit fraud UI.
Optimized v2 — Fully aligned with Dictionary-based MODELS state.
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
from services import ServiceResult
from services.audit_log import log_prediction
from services.batch_io import normalize_batch_input as _normalize_batch_df
from services.explain import explain_light_transaction

# Backward-compatible alias
LoadResult = ServiceResult

DEFAULT_THRESHOLD = 0.831
MAX_PREVIEW_ROWS = 5_000
SUPPORTED_UPLOAD_TYPES = (".csv", ".xlsx", ".xls")

# Canonical artifact paths (single source of truth: services/artifacts.py)
# Re-exported here for backward compat with dashboard code.
from services.artifacts import ARTIFACT_PATHS


@dataclass(frozen=True)
class InferenceBackend:
    """Cached handle to models.predict using clean dictionary routing."""
    ok: bool
    predict_light: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    predict_batch_heavy: Callable[..., pd.DataFrame] | None = None
    models: dict[str, Any] | None = None
    message: str = ""


def _coerce_float(value: Any, default: float = DEFAULT_THRESHOLD) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@st.cache_resource(show_spinner=False)
def get_inference_backend() -> InferenceBackend:
    """Import and cache the single source of truth for inference via Dict logic."""
    try:
        module = importlib.import_module("models.predict")
        predict_light_fn = getattr(module, "predict_light", None)
        predict_batch_fn = getattr(module, "predict_batch", None)
        models_dict = getattr(module, "MODELS", None)

        if not callable(predict_light_fn):
            return InferenceBackend(False, message="models.predict.predict_light is not callable.")
        if not callable(predict_batch_fn):
            return InferenceBackend(False, message="models.predict.predict_batch is not callable.")
        if not isinstance(models_dict, dict) or not models_dict.get("loaded", False):
            return InferenceBackend(False, message="models.predict.MODELS dictionary failed to load.")

        return InferenceBackend(
            True,
            predict_light=predict_light_fn,
            predict_batch_heavy=predict_batch_fn,
            models=models_dict,
        )
    except Exception as exc:
        return InferenceBackend(False, message=f"Inference backend unavailable: {exc}")


def predict_transaction(payload: dict[str, Any],
                        threshold: float | None = None,
                        light_only: bool = True,
                        debug: bool = False) -> LoadResult:
    """Run a single prediction through models.predict.predict_light."""
    normalized = normalize_transaction_input(payload)
    if not normalized.ok:
        return normalized

    backend = get_inference_backend()
    if not backend.ok or backend.predict_light is None:
        return LoadResult(False, None, backend.message)

    try:
        if threshold is None:
            result = backend.predict_light(normalized.data)
        else:
            result = backend.predict_light(normalized.data, threshold_override=threshold)
    except Exception as exc:
        return LoadResult(False, None, f"Prediction failed: {exc}")

    if not isinstance(result, dict):
        return LoadResult(False, None, "Prediction returned an unsupported response.")
    if result.get("success") == False or result.get("error"):
        return LoadResult(False, result, str(result.get("error", "Unknown prediction error")))

    log_prediction("dashboard_realtime", normalized.data, result)
    return LoadResult(True, result, "")


def explain_transaction(payload: dict[str, Any], top_n: int = 8) -> LoadResult:
    """SHAP / feature-importance explanation for a single transaction."""
    normalized = normalize_transaction_input(payload)
    if not normalized.ok:
        return normalized

    backend = get_inference_backend()
    if not backend.ok or backend.models is None:
        return LoadResult(False, None, backend.message)

    explanation = explain_light_transaction(normalized.data, backend.models, top_n=top_n)
    if not explanation.get("available"):
        return LoadResult(False, explanation, explanation.get("reason", "Explanation unavailable"))
    return LoadResult(True, explanation, "")


def predict_batch_transactions(df: pd.DataFrame,
                               threshold: float | None = None) -> LoadResult:
    """Run heavy batch inference through models.predict.predict_batch."""
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



@st.cache_data(show_spinner=False)
def load_evaluation_report() -> list[dict[str, Any]]:
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
    backend = get_inference_backend()
    if backend.ok and backend.models:
        value = backend.models.get("threshold", default)
    else:
        value = default
    threshold = _coerce_float(value, default)
    return min(max(threshold, 0.01), 0.99)


def get_artifact_status() -> dict[str, bool]:
    status = {name: path.exists() and path.is_file() for name, path in ARTIFACT_PATHS.items()}
    status["inference_backend"] = get_inference_backend().ok
    return status


def get_artifact_errors() -> list[str]:
    errors = [f"Missing artifact: {name}" for name, available in get_artifact_status().items() if not available]
    backend = get_inference_backend()
    if not backend.ok and backend.message:
        errors.append(backend.message)
    return errors


# ✅ نأمن الـ Realtime بالموديلات الخفيفة فقط كما اقترحت أنت بذكاء لمنع التعطيل!
def is_realtime_ready() -> bool:
    status = get_artifact_status()
    required = ("xgb_light", "lgbm_light", "manual_features")
    return bool(status.get("inference_backend") and all(status.get(name, False) for name in required))


def read_uploaded_table(uploaded_file: Any, max_rows: int = MAX_PREVIEW_ROWS) -> LoadResult:
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


def normalize_batch_input(df: pd.DataFrame) -> ServiceResult:
    return _normalize_batch_df(df)


def normalize_transaction_input(payload: Mapping[str, Any]) -> LoadResult:
    if not isinstance(payload, Mapping):
        return LoadResult(False, None, "Transaction payload must be a mapping.")

    if payload.get("TransactionAmt") in (None, ""):
        return LoadResult(False, None, "Missing required field: TransactionAmt")

    try:
        amount = float(payload["TransactionAmt"])
        dist1  = float(payload.get("dist1", 0) or 0)
        hour   = int(payload.get("hour", 12))
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
        "ProductCD":      str(payload.get("ProductCD", "W") or "W").strip() or "W",
        "card4":          str(payload.get("card4", "visa") or "visa").strip().lower(),
        "card6":          str(payload.get("card6", "debit") or "debit").strip().lower(),
        "P_emaildomain":  str(payload.get("P_emaildomain", "gmail.com") or "gmail.com").strip().lower(),
        "DeviceType":     str(payload.get("DeviceType", "desktop") or "desktop").strip().lower(),
        "dist1":          dist1,
        "hour":           hour,
    }

    transaction_dt = payload.get("TransactionDT")
    if transaction_dt not in (None, ""):
        try:
            normalized["TransactionDT"] = int(transaction_dt)
        except (TypeError, ValueError):
            return LoadResult(False, None, "TransactionDT must be an integer timestamp.")

    return LoadResult(True, normalized, "")
