# models/predict.py
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from typing import Optional

from config.paths import (
    HEAVY_DIR, LIGHT_DIR, PREPROCESS_DIR, MANUAL_FEATURES,
    LIGHT_THRESHOLD, FEATURE_MEDIANS,
)
from config.params import HEAVY_ENSEMBLE_WEIGHTS, LIGHT_ENSEMBLE_WEIGHTS
from features.aggregation import apply_aggregation_features
from features.build_features import build_features
from features.preprocess import preprocess_inference

# ================================================================
# Load Once at Startup
# ================================================================
def _load_models() -> dict:
    try:
        m = {
            "xgb_heavy":       joblib.load(HEAVY_DIR      / "xgb_heavy.pkl"),
            "lgbm_heavy":      joblib.load(HEAVY_DIR      / "lgbm_heavy.pkl"),
            "iso":             joblib.load(HEAVY_DIR      / "iso_forest.pkl"),
            "xgb_light":       joblib.load(LIGHT_DIR      / "xgb_light.pkl"),
            "lgbm_light":      joblib.load(LIGHT_DIR      / "lgbm_light.pkl"),
            "all_feats":       joblib.load(PREPROCESS_DIR / "all_features.pkl"),
            "threshold":       float(joblib.load(PREPROCESS_DIR / "threshold.pkl")),
            "manual_features": joblib.load(MANUAL_FEATURES),
            "feature_medians": joblib.load(FEATURE_MEDIANS) if FEATURE_MEDIANS.exists() else {},
            "loaded":          True,
        }
        # Load calibrated light-only threshold (falls back to ensemble threshold)
        if LIGHT_THRESHOLD.exists():
            m["light_threshold"] = float(joblib.load(LIGHT_THRESHOLD))
        else:
            m["light_threshold"] = m["threshold"]
    except Exception as e:
        m = {"loaded": False, "error": str(e), "threshold": 0.75,
             "light_threshold": 0.75}
    return m

# ✅ Load ONCE
MODELS = _load_models()

# ================================================================
# Helpers
# ================================================================
def _get_threshold(override: Optional[float]) -> float:
    """Get the ensemble threshold (for batch/heavy inference)."""
    t = override if override is not None else MODELS["threshold"]
    return float(min(max(t, 0.01), 0.99))

def _get_light_threshold(override: Optional[float]) -> float:
    """Get the light-model threshold (calibrated for real-time inference)."""
    t = override if override is not None else MODELS["light_threshold"]
    return float(min(max(t, 0.01), 0.99))


def _training_fill_values(columns: list[str]) -> dict:
    medians = MODELS.get("feature_medians", {}) or {}
    return {col: medians.get(col, 0) for col in columns}

def _risk_level(score: float, threshold: float) -> dict:
    # ✅ FIX: منع التناقض بين risk_level و is_fraud
    # HIGH RISK   = فوق الـ threshold
    # MEDIUM RISK = بين 60% و 100% من الـ threshold
    # LOW RISK    = تحت 60% من الـ threshold
    if score >= threshold:
        return {"level": "HIGH RISK",   "emoji": "🚨",
                "action": "Block immediately", "color": "red"}
    elif score >= threshold * 0.6:
        return {"level": "MEDIUM RISK", "emoji": "⚠️",
                "action": "Review required",   "color": "orange"}
    else:
        return {"level": "LOW RISK",    "emoji": "✅",
                "action": "Approved",          "color": "green"}

# ✅ FIX 5: validation أقوى
VALID_CARD4     = {"visa", "mastercard", "american express", "discover"}
VALID_CARD6     = {"debit", "credit", "debit or credit", "charge card"}
VALID_DEVICE    = {"desktop", "mobile"}


def _heuristic_risk(user_input: dict) -> float:
    """Rule-based risk overlay (works without retraining)."""
    score = 0.0
    try:
        amt = float(user_input.get("TransactionAmt", 0) or 0)
        dist = float(user_input.get("dist1", 0) or 0)
        hour = int(user_input.get("hour", 12))
        domain = str(user_input.get("P_emaildomain", "") or "").lower()
    except (TypeError, ValueError):
        return 0.0

    if amt > 1000:
        score += 0.22
    if dist > 500:
        score += 0.18
    if hour < 6:
        score += 0.12
    if domain in {"anonymous.com", "protonmail.com", "mail.ru"}:
        score += 0.20
    if str(user_input.get("DeviceType", "")).lower() == "mobile" and amt > 500:
        score += 0.08
    return float(min(score, 0.85))


def _validate(user_input: dict) -> dict:
    errors = []

    amt = user_input.get("TransactionAmt")
    if amt is None:
        errors.append("TransactionAmt is required")
    else:
        # ✅ FIX: تحقق إن القيمة رقم
        try:
            amt = float(amt)
            if amt < 0:
                errors.append("TransactionAmt cannot be negative")
        except (ValueError, TypeError):
            errors.append("TransactionAmt must be numeric")

    card4 = user_input.get("card4")
    if card4 and str(card4).lower() not in VALID_CARD4:
        errors.append(f"card4 must be one of {VALID_CARD4}")

    card6 = user_input.get("card6")
    if card6 and str(card6).lower() not in VALID_CARD6:
        errors.append(f"card6 must be one of {VALID_CARD6}")

    device = user_input.get("DeviceType")
    if device and str(device).lower() not in VALID_DEVICE:
        errors.append(f"DeviceType must be one of {VALID_DEVICE}")

    if errors:
        raise ValueError(" | ".join(errors))
    return user_input

# ================================================================
# predict_light — Manual Form → Light Models Only
# ================================================================
def predict_light(user_input: dict,
                  threshold_override: Optional[float] = None) -> dict:
    """
    Real-time: Manual form → xgb_light + lgbm_light ONLY
    """
    try:
        if not MODELS.get("loaded"):
            return {"error": f"Models not loaded: {MODELS.get('error')}"}

        _validate(user_input)
        threshold = _get_light_threshold(threshold_override)

        df = pd.DataFrame([user_input])

        # اشتق is_morning و is_night من hour مباشرة
        # عشان build_features بيحتاج TransactionDT لاشتقاقهم
        # ولو مش موجود هيديهم 0، فبنحسبهم هنا صح
        if "hour" in df.columns and pd.notna(df["hour"].iloc[0]):
            h = int(df["hour"].iloc[0])
            df["is_morning"] = int(6 <= h < 12)
            df["is_night"]   = int(h < 6)

        # build_features بدون TransactionDT — هيشتغل على الـ features الموجودة
        df = build_features(df)
        df = preprocess_inference(df)
        df = apply_aggregation_features(df)

        # ✅ FIX 6: reindex بـ manual_features كاملة بالترتيب الصح
        manual_features = MODELS["manual_features"]
        X_light = df.reindex(columns=manual_features)
        X_light = X_light.fillna(value=_training_fill_values(manual_features))

        w = LIGHT_ENSEMBLE_WEIGHTS
        p1 = float(MODELS["xgb_light"].predict_proba(X_light)[0, 1])
        p2 = float(MODELS["lgbm_light"].predict_proba(X_light)[0, 1])
        ml_score = w["xgb"] * p1 + w["lgbm"] * p2
        heuristic = _heuristic_risk(user_input)
        score = float(min(0.99, 0.92 * ml_score + 0.08 * heuristic))
        risk     = _risk_level(score, threshold)
        is_fraud = score >= threshold

        return {
            "timestamp":      datetime.now().isoformat(),
            "risk_score":     round(score, 4),
            "fraud_probability": round(score, 4),
            "ml_score":       round(ml_score, 4),
            "heuristic_risk": round(heuristic, 4),
            "is_fraud":       bool(is_fraud),
            "decision":       "FRAUD" if is_fraud else "SAFE",
            "risk_level":     risk["level"],
            "risk_emoji":     risk["emoji"],
            "risk_action":    risk["action"],
            "risk_color":     risk["color"],
            "xgb_l_score":    round(p1, 4),
            "lgbm_l_score":   round(p2, 4),
            "threshold":      round(threshold, 3),
            "inference_mode": "light",
        }
    except ValueError as e:
        return {"error": f"Validation: {e}"}
    except Exception as e:
        return {"error": f"Prediction: {e}"}

# ================================================================
# predict_batch — CSV Upload → Heavy Models Only
# ================================================================
def predict_batch(df: pd.DataFrame,
                  threshold_override: Optional[float] = None) -> pd.DataFrame:
    """
    Batch: CSV upload → xgb_heavy + lgbm_heavy + iso_forest ONLY
    """
    if not MODELS.get("loaded"):
        raise RuntimeError(f"Models not loaded: {MODELS.get('error')}")
    if df is None or df.empty:
        raise ValueError("Empty DataFrame")
    if "TransactionAmt" not in df.columns:
        raise ValueError("Missing TransactionAmt column")

    threshold = _get_threshold(threshold_override)
    original  = df.copy()

    # Pipeline
    X = build_features(df.copy())
    X = preprocess_inference(X)
    X = apply_aggregation_features(X)

    # ISO score — compute BEFORE reindexing to prevent stale zeros
    iso      = MODELS["iso"]
    iso_cols = [
        c for c in getattr(iso, "feature_names_in_", [])
        if c != "iso_score"
    ]
    if iso_cols:
        X_iso = X.reindex(columns=iso_cols)
        X_iso = X_iso.fillna(value=_training_fill_values(iso_cols))
        iso_score = iso.decision_function(X_iso)
    else:
        iso_score = np.zeros(len(X))

    # Reindex to training schema and inject fresh iso_score
    X = X.reindex(columns=MODELS["all_feats"])
    X = X.fillna(value=_training_fill_values(MODELS["all_feats"]))
    if "iso_score" in X.columns:
        X["iso_score"] = iso_score
    else:
        X.insert(len(X.columns), "iso_score", iso_score)

    # Heavy predictions — X is now in the exact training column order
    p1 = MODELS["xgb_heavy"].predict_proba(X)[:, 1]
    p2 = MODELS["lgbm_heavy"].predict_proba(X)[:, 1]

    # Normalize iso_score to [0, 1]
    iso_min, iso_max = iso_score.min(), iso_score.max()
    if len(iso_score) < 2 or abs(float(iso_max - iso_min)) < 1e-8:
        iso_norm = np.full(len(iso_score), 0.5)
    else:
        iso_norm = (iso_score - iso_min) / (iso_max - iso_min)
    iso_fraud = 1.0 - iso_norm  # lower iso score = more anomalous

    w = HEAVY_ENSEMBLE_WEIGHTS
    final = w["xgb"] * p1 + w["lgbm"] * p2 + w["iso"] * iso_fraud

    original["risk_score"]     = np.round(final, 4)
    original["fraud_probability"] = np.round(final, 4)
    original["prediction"]     = (final >= threshold).astype(int)
    original["is_fraud"]       = original["prediction"]
    original["xgb_score"]      = np.round(p1, 4)
    original["lgbm_score"]     = np.round(p2, 4)
    original["iso_score"]      = np.round(iso_score, 4)
    original["threshold"]      = round(threshold, 3)
    original["inference_mode"] = "heavy_ensemble"

    return original


def predict(user_input: dict,
            threshold_override: Optional[float] = None) -> dict:
    """API-compatible alias for real-time light inference."""
    return predict_light(user_input, threshold_override=threshold_override)

