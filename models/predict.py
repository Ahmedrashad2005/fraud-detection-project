# models/predict.py
"""
Fraud Detection — Inference Module
===================================
Two inference paths:
  • predict_light()       → manual dashboard (xgb_light + lgbm_light on manual features)
  • predict_batch_heavy() → batch CSV upload  (xgb_heavy + lgbm_heavy + iso_forest)
"""

import pandas as pd
import joblib
import numpy as np
from typing import Optional
from datetime import datetime

from config.paths import HEAVY_DIR, LIGHT_DIR, PREPROCESS_DIR
from features.preprocess import preprocess_inference
from features.build_features import build_features


# ================================================================
# Load Models Once at Startup
# ================================================================
def load_models():
    """Load all models and artifacts. Returns a tuple for backward compat."""
    xgb_heavy  = joblib.load(HEAVY_DIR      / "xgb_heavy.pkl")
    lgbm_heavy = joblib.load(HEAVY_DIR      / "lgbm_heavy.pkl")
    iso        = joblib.load(HEAVY_DIR      / "iso_forest.pkl")
    xgb_light  = joblib.load(LIGHT_DIR      / "xgb_light.pkl")
    lgbm_light = joblib.load(LIGHT_DIR      / "lgbm_light.pkl")
    manual_feats = joblib.load(PREPROCESS_DIR / "manual_features.pkl")
    all_feats  = joblib.load(PREPROCESS_DIR / "all_features.pkl")
    try:
        threshold = float(joblib.load(PREPROCESS_DIR / "threshold.pkl"))
    except Exception:
        threshold = 0.5
    return (xgb_heavy, lgbm_heavy, iso,
            xgb_light, lgbm_light,
            threshold, manual_feats, all_feats)


# Load once at module level
MODELS = load_models()


# ================================================================
# Input Validation
# ================================================================
def validate_input(user_input):
    """Validate and clean user input."""
    errors = []

    amt = user_input.get("TransactionAmt", None)
    if amt is None:
        errors.append("TransactionAmt is required")
    elif amt < 0:
        errors.append("TransactionAmt cannot be negative")
    elif amt > 100000:
        errors.append("TransactionAmt seems too large (>100,000)")

    hour = user_input.get("hour", None)
    if hour is not None:
        if not (0 <= hour <= 23):
            errors.append("hour must be between 0 and 23")

    valid_cards = ["visa", "mastercard", "american express", "discover"]
    card4 = user_input.get("card4", None)
    if card4 and card4.lower() not in valid_cards:
        errors.append(f"card4 must be one of {valid_cards}")

    valid_card6 = ["credit", "debit"]
    card6 = user_input.get("card6", None)
    if card6 and card6.lower() not in valid_card6:
        errors.append(f"card6 must be one of {valid_card6}")

    valid_devices = ["mobile", "desktop"]
    device = user_input.get("DeviceType", None)
    if device and device.lower() not in valid_devices:
        errors.append(f"DeviceType must be one of {valid_devices}")

    if errors:
        raise ValueError(" | ".join(errors))

    return user_input


# ================================================================
# Risk Level
# ================================================================
def get_risk_level(score, threshold):
    """Map a fraud score to a risk category."""
    if score > 0.7:
        return {
            "level":  "HIGH RISK",
            "emoji":  "🚨",
            "action": "Block transaction immediately",
            "color":  "red"
        }
    elif score >= threshold:
        return {
            "level":  "MEDIUM RISK",
            "emoji":  "⚠️",
            "action": "Review required",
            "color":  "orange"
        }
    else:
        return {
            "level":  "LOW RISK",
            "emoji":  "✅",
            "action": "Transaction approved",
            "color":  "green"
        }


# ================================================================
# Explainability
# ================================================================
def get_top_factors(user_input, score):
    """Generate human-readable risk factors from visible inputs."""
    factors = []

    if user_input.get("TransactionAmt", 0) > 1000:
        factors.append("💰 High transaction amount")

    hour = user_input.get("hour", 12)
    if isinstance(hour, (int, float)) and hour < 6:
        factors.append("🌙 Unusual time (late night)")

    if user_input.get("DeviceType", "") == "mobile":
        factors.append("📱 Mobile device (higher risk)")

    if user_input.get("card4", "") == "discover":
        factors.append("💳 Discover card (highest fraud rate)")

    if user_input.get("P_emaildomain", "") in [
        "anonymous.com", "guerrillamail.com"
    ]:
        factors.append("📧 Suspicious email domain")

    if user_input.get("dist1", 0) > 500:
        factors.append("📍 Large distance from usual location")

    if score > 0.7:
        factors.append("🤖 All models flagged as suspicious")

    if not factors:
        factors.append("✅ No major risk factors detected")

    return factors


# ================================================================
# Internal Helpers
# ================================================================
def _active_threshold(default_threshold, threshold_override=None):
    """Resolve the active threshold, clamped to [0.01, 0.99]."""
    if threshold_override is None:
        threshold = default_threshold
    else:
        threshold = threshold_override
    try:
        threshold = float(threshold)
    except (TypeError, ValueError):
        threshold = default_threshold
    return min(max(float(threshold), 0.01), 0.99)


def _finalize_prediction(user_input, score, threshold, model_scores):
    """Build the standard prediction response dict."""
    risk     = get_risk_level(score, threshold)
    is_fraud = score >= threshold
    factors  = get_top_factors(user_input, score)

    return {
        "timestamp":        datetime.now().isoformat(),
        "risk_score":       round(float(score), 4),
        "fraud_probability": round(float(score), 4),
        "risk_level":       risk["level"],
        "risk_emoji":       risk["emoji"],
        "risk_action":      risk["action"],
        "risk_color":       risk["color"],
        "decision":         "FRAUD" if is_fraud else "SAFE",
        "is_fraud":         bool(is_fraud),
        **model_scores,
        "top_factors":      factors,
        "threshold":        round(float(threshold), 3),
    }


# ================================================================
# Light Prediction — Manual Dashboard
# ================================================================
def predict_light(user_input,
                  threshold_override=None,
                  debug=False):
    """
    Real-time prediction for manual dashboard transactions.

    Uses xgb_light (60%) + lgbm_light (40%) on manual dashboard features.
    Isolation Forest is NOT used here (trained on all_features,
    not manual features).
    """
    try:
        user_input = validate_input(user_input)

        (_, _, _, xgb_l, lgbm_l,
         stored_threshold, manual_feats, _) = MODELS
        threshold = _active_threshold(stored_threshold, threshold_override)

        # Pipeline: raw → features → preprocess → align to manual features
        df = pd.DataFrame([user_input])
        df = build_features(df)
        df = preprocess_inference(df)
        df = df.reindex(columns=manual_feats, fill_value=0)

        # Score from light models only
        p1 = xgb_l.predict_proba(df)[:, 1][0]
        p2 = lgbm_l.predict_proba(df)[:, 1][0]
        score = 0.60 * p1 + 0.40 * p2

        return _finalize_prediction(
            user_input, score, threshold,
            {
                "xgb_l_score":    round(float(p1), 4),
                "lgbm_l_score":   round(float(p2), 4),
                "inference_mode": "light",
            },
        )

    except ValueError as e:
        return {"error": f"Validation Error: {str(e)}"}
    except Exception as e:
        return {"error": f"Prediction Error: {str(e)}"}


# ================================================================
# Backward-Compatible Aliases
# ================================================================
predict          = predict_light
predict_realtime = predict_light


# ================================================================
# Batch Prediction — Heavy Ensemble
# ================================================================
def predict_batch_heavy(df, threshold_override=None):
    """
    Batch inference on uploaded CSV data.

    Uses xgb_heavy (45%) + lgbm_heavy (35%) + iso_forest normalized (20%).
    iso_score is also injected as a feature since heavy models were
    trained with it.
    """
    if df is None or df.empty:
        raise ValueError("No transaction rows are available for batch inference")
    if "TransactionAmt" not in df.columns:
        raise ValueError("Uploaded data must include TransactionAmt")

    (xgb, lgbm, iso, _, _,
     stored_threshold, _, all_feats) = MODELS
    threshold = _active_threshold(stored_threshold, threshold_override)

    original_df = df.copy()

    # Pipeline: raw → features → preprocess → align to all_features
    X = build_features(df.copy())
    X = preprocess_inference(X)
    X = X.reindex(columns=all_feats, fill_value=0)

    # Isolation Forest anomaly score
    iso_features = [c for c in getattr(iso, "feature_names_in_", [])
                    if c in X.columns]
    if iso_features:
        iso_raw = iso.decision_function(X[iso_features])
    else:
        iso_raw = np.zeros(len(X))

    # Heavy models expect iso_score as a feature
    X["iso_score"] = iso_raw

    # Model predictions
    p1 = xgb.predict_proba(X)[:, 1]
    p2 = lgbm.predict_proba(X)[:, 1]

    # Normalize iso: more negative = more anomalous → higher fraud prob
    iso_norm = 1.0 / (1.0 + np.exp(iso_raw))

    # Ensemble
    score = 0.45 * p1 + 0.35 * p2 + 0.20 * iso_norm

    # Enrich original DataFrame
    original_df["risk_score"]       = np.round(score.astype(float), 4)
    original_df["fraud_probability"] = original_df["risk_score"]
    original_df["prediction"]       = (score >= threshold).astype(int)
    original_df["is_fraud"]         = original_df["prediction"]
    original_df["xgb_score"]        = np.round(p1.astype(float), 4)
    original_df["lgbm_score"]       = np.round(p2.astype(float), 4)
    original_df["iso_score"]        = np.round(iso_raw.astype(float), 6)
    original_df["threshold"]        = round(float(threshold), 3)
    original_df["inference_mode"]   = "heavy_ensemble"

    if "isFraud" not in original_df.columns:
        original_df["isFraud"] = original_df["prediction"]

    if "hour" not in original_df.columns and "TransactionDT" in original_df.columns:
        original_df["hour"] = (
            (original_df["TransactionDT"].fillna(0).astype(int) // 3600) % 24
        ).astype(int)
    if "day_of_week" not in original_df.columns and "TransactionDT" in original_df.columns:
        original_df["day_of_week"] = (
            (original_df["TransactionDT"].fillna(0).astype(int) // 86400) % 7
        ).astype(int)

    return original_df


# Alias
predict_batch = predict_batch_heavy


# ================================================================
# Feature Preparation Helper (used by test_pipeline.py)
# ================================================================
def build_features_inference(df, all_features=None):
    """Build and align inference features for external callers."""
    df = df.copy()
    df = build_features(df)
    df = preprocess_inference(df)
    if all_features is not None:
        df = df.reindex(columns=all_features, fill_value=0)
    return df


# ================================================================
# Run
# ================================================================
if __name__ == "__main__":

    # Test 1 - Suspicious
    suspicious = {
        "TransactionAmt": 5000,
        "ProductCD":      "W",
        "card4":          "discover",
        "card6":          "credit",
        "P_emaildomain":  "anonymous.com",
        "DeviceType":     "mobile",
        "dist1":          800,
        "hour":           3,
    }

    # Test 2 - Normal
    normal = {
        "TransactionAmt": 50,
        "ProductCD":      "W",
        "card4":          "visa",
        "card6":          "debit",
        "P_emaildomain":  "gmail.com",
        "DeviceType":     "desktop",
        "dist1":          10,
        "hour":           14,
    }

    # Test 3 - Invalid input
    invalid = {
        "TransactionAmt": -100,
        "hour":           25,
    }

    print("\n" + "="*50)
    print("TEST 1 — Suspicious Transaction")
    print("="*50)
    result1 = predict_light(suspicious)
    for k, v in result1.items():
        print(f"  {k:20}: {v}")

    print("\n" + "="*50)
    print("TEST 2 — Normal Transaction")
    print("="*50)
    result2 = predict_light(normal)
    for k, v in result2.items():
        print(f"  {k:20}: {v}")

    print("\n" + "="*50)
    print("TEST 3 — Invalid Input")
    print("="*50)
    result3 = predict_light(invalid)
    print(f"  {result3}")
