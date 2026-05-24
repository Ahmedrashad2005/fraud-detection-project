# models/predict.py

import pandas as pd
import joblib
from datetime import datetime

from config.paths import (
    HEAVY_DIR, LIGHT_DIR, PREPROCESS_DIR
)
from features.preprocess import preprocess_inference
from features.build_features import build_features


# ================================================================
# Load Models Once at Startup
# ================================================================
def load_models():
    xgb_heavy  = joblib.load(HEAVY_DIR      / "xgb_heavy.pkl")
    lgbm_heavy = joblib.load(HEAVY_DIR      / "lgbm_heavy.pkl")
    iso        = joblib.load(HEAVY_DIR      / "iso_forest.pkl")
    xgb_light  = joblib.load(LIGHT_DIR      / "xgb_light.pkl")
    lgbm_light = joblib.load(LIGHT_DIR      / "lgbm_light.pkl")
    top35      = joblib.load(PREPROCESS_DIR / "top35_features.pkl")
    all_feats  = joblib.load(PREPROCESS_DIR / "all_features.pkl")
    threshold = 0.5
    return (xgb_heavy, lgbm_heavy, iso,
            xgb_light, lgbm_light,
            threshold, top35, all_feats)


# ✅ Load once at module level
MODELS = load_models()


# ================================================================
# Input Validation
# ================================================================
def validate_input(user_input: dict) -> dict:
    """Validate and clean user input."""
    errors = []

    # TransactionAmt
    amt = user_input.get("TransactionAmt", None)
    if amt is None:
        errors.append("TransactionAmt is required")
    elif amt < 0:
        errors.append("TransactionAmt cannot be negative")
    elif amt > 100000:
        errors.append("TransactionAmt seems too large (>100,000)")

    # hour
    hour = user_input.get("hour", None)
    if hour is not None:
        if not (0 <= hour <= 23):
            errors.append("hour must be between 0 and 23")

    # card4
    valid_cards = ["visa", "mastercard",
                   "american express", "discover"]
    card4 = user_input.get("card4", None)
    if card4 and card4.lower() not in valid_cards:
        errors.append(f"card4 must be one of {valid_cards}")

    # card6
    valid_card6 = ["credit", "debit"]
    card6 = user_input.get("card6", None)
    if card6 and card6.lower() not in valid_card6:
        errors.append(f"card6 must be one of {valid_card6}")

    # DeviceType
    valid_devices = ["mobile", "desktop"]
    device = user_input.get("DeviceType", None)
    if device and device.lower() not in valid_devices:
        errors.append(f"DeviceType must be one of {valid_devices}")

    if errors:
        raise ValueError(" | ".join(errors))

    return user_input


# ================================================================
# Prepare Input
# ================================================================
def prepare_input(user_input: dict,
                  all_features: list) -> pd.DataFrame:
    df = pd.DataFrame([user_input])
    df = preprocess_inference(df)
    df = build_features(df)
    df = df.reindex(columns=all_features, fill_value=0)
    return df


# ================================================================
# Risk Level
# ================================================================
def get_risk_level(score: float, threshold: float) -> dict:
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
def get_top_factors(user_input: dict, score: float) -> list:
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
# Main Predict
# ================================================================
def predict(user_input: dict) -> dict:
    """
    Main prediction function.

    Args:
        user_input: dict with transaction features
        Keys: TransactionAmt, ProductCD, card4, card6,
              P_emaildomain, DeviceType, dist1, hour

    Returns:
        dict with risk score, level, decision, factors
    """
    try:
        # Validate
        user_input = validate_input(user_input)

        # Unpack models (loaded once at startup)
        (xgb, lgbm, iso, xgb_l, lgbm_l,
         threshold, top35, all_feats) = MODELS

        # Prepare input
        X = prepare_input(user_input, all_feats)

        # ISO score
        X          = X.copy()
        iso_feats  = [c for c in iso.feature_names_in_
                      if c in X.columns]
        X["iso_score"] = iso.decision_function(X[iso_feats])

        # Individual probabilities
        p1 = xgb.predict_proba(X)[:, 1][0]
        p2 = lgbm.predict_proba(X)[:, 1][0]

        valid_top35 = [c for c in top35 if c in X.columns]
        X_light     = X[valid_top35]

        p3 = xgb_l.predict_proba(X_light)[:, 1][0]
        p4 = lgbm_l.predict_proba(X_light)[:, 1][0]

        # Ensemble score
        final_score = 0.40*p1 + 0.30*p2 + 0.20*p3 + 0.10*p4

        # Risk level
        risk     = get_risk_level(final_score, threshold)
        is_fraud = final_score >= threshold
        factors  = get_top_factors(user_input, final_score)

        return {
            "timestamp":    datetime.now().isoformat(),
            "risk_score":   round(float(final_score), 4),
            "risk_level":   risk["level"],
            "risk_emoji":   risk["emoji"],
            "risk_action":  risk["action"],
            "risk_color":   risk["color"],
            "decision":     "FRAUD" if is_fraud else "SAFE",
            "is_fraud":     bool(is_fraud),
            "xgb_score":    round(float(p1), 4),
            "lgbm_score":   round(float(p2), 4),
            "xgb_l_score":  round(float(p3), 4),
            "lgbm_l_score": round(float(p4), 4),
            "top_factors":  factors,
            "threshold":    round(float(threshold), 3),
        }

    except ValueError as e:
        return {"error": f"Validation Error: {str(e)}"}

    except Exception as e:
        return {"error": f"Prediction Error: {str(e)}"}


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
    result1 = predict(suspicious)
    for k, v in result1.items():
        print(f"  {k:15}: {v}")

    print("\n" + "="*50)
    print("TEST 2 — Normal Transaction")
    print("="*50)
    result2 = predict(normal)
    for k, v in result2.items():
        print(f"  {k:15}: {v}")

    print("\n" + "="*50)
    print("TEST 3 — Invalid Input")
    print("="*50)
    result3 = predict(invalid)
    print(f"  {result3}")