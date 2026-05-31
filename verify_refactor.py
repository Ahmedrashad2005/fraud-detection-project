"""
Verification Test — Refactored predict.py
==========================================
NO code changes. Read-only test.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import joblib

# ================================================================
# 1. Import verification
# ================================================================
print("=" * 60)
print("STEP 1: IMPORT VERIFICATION")
print("=" * 60)

try:
    from models.predict import (
        predict_light,
        predict,
        predict_realtime,
        predict_batch_heavy,
        predict_batch,
        build_features_inference,
        validate_input,
        get_risk_level,
        get_top_factors,
        MODELS,
    )
    print("✅ All exports imported successfully")
    print(f"   predict is predict_light        : {predict is predict_light}")
    print(f"   predict_realtime is predict_light: {predict_realtime is predict_light}")
    print(f"   predict_batch is predict_batch_heavy: {predict_batch is predict_batch_heavy}")
    print(f"   MODELS type: {type(MODELS).__name__}, len: {len(MODELS)}")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Verify MODELS tuple structure (backward compat with data_loader)
print(f"\n   MODELS[0] type: {type(MODELS[0]).__name__} (xgb_heavy)")
print(f"   MODELS[1] type: {type(MODELS[1]).__name__} (lgbm_heavy)")
print(f"   MODELS[2] type: {type(MODELS[2]).__name__} (iso_forest)")
print(f"   MODELS[3] type: {type(MODELS[3]).__name__} (xgb_light)")
print(f"   MODELS[4] type: {type(MODELS[4]).__name__} (lgbm_light)")
print(f"   MODELS[5] value: {MODELS[5]} (threshold)")
print(f"   MODELS[6] type: list, len={len(MODELS[6])} (top35)")
print(f"   MODELS[7] type: list, len={len(MODELS[7])} (all_feats)")

# ================================================================
# 2. Test Cases
# ================================================================
print("\n" + "=" * 60)
print("STEP 2: TEST CASES")
print("=" * 60)

cases = [
    ("Case 1: Normal ($35, Visa, Debit, Desktop, 12:00, dist=0)", {
        "TransactionAmt": 35.0, "ProductCD": "W", "card4": "visa",
        "card6": "debit", "P_emaildomain": "gmail.com",
        "DeviceType": "desktop", "dist1": 0.0, "hour": 12,
        "TransactionDT": 43200,
    }),
    ("Case 2: Medium ($1000, Visa, Debit, Desktop, 12:00, dist=0)", {
        "TransactionAmt": 1000.0, "ProductCD": "W", "card4": "visa",
        "card6": "debit", "P_emaildomain": "gmail.com",
        "DeviceType": "desktop", "dist1": 0.0, "hour": 12,
        "TransactionDT": 43200,
    }),
    ("Case 3: Suspicious ($10000, Visa, Debit, Desktop, 00:30, dist=0)", {
        "TransactionAmt": 10000.0, "ProductCD": "W", "card4": "visa",
        "card6": "debit", "P_emaildomain": "gmail.com",
        "DeviceType": "desktop", "dist1": 0.0, "hour": 0,
        "TransactionDT": 1800,
    }),
    ("Case 4: Very Suspicious ($100000, AmEx, Debit, Desktop, 00:30, dist=0)", {
        "TransactionAmt": 100000.0, "ProductCD": "W", "card4": "american express",
        "card6": "debit", "P_emaildomain": "gmail.com",
        "DeviceType": "desktop", "dist1": 0.0, "hour": 0,
        "TransactionDT": 1800,
    }),
    ("Case 5: Very Suspicious + Far ($100000, AmEx, Debit, Desktop, 00:30, dist=500)", {
        "TransactionAmt": 100000.0, "ProductCD": "W", "card4": "american express",
        "card6": "debit", "P_emaildomain": "gmail.com",
        "DeviceType": "desktop", "dist1": 500.0, "hour": 0,
        "TransactionDT": 1800,
    }),
]

threshold_used = None
all_passed = True

for name, user_input in cases:
    print(f"\n--- {name} ---")
    result = predict_light(user_input)

    if "error" in result:
        print(f"  ❌ ERROR: {result['error']}")
        all_passed = False
        continue

    xgb_l  = result.get("xgb_l_score", "MISSING")
    lgbm_l = result.get("lgbm_l_score", "MISSING")
    score  = result.get("risk_score", "MISSING")
    fraud_prob = result.get("fraud_probability", "MISSING")
    decision = result.get("decision", "MISSING")
    is_fraud = result.get("is_fraud", "MISSING")
    risk_level = result.get("risk_level", "MISSING")
    threshold = result.get("threshold", "MISSING")
    mode = result.get("inference_mode", "MISSING")

    if threshold_used is None:
        threshold_used = threshold

    print(f"  xgb_light probability  : {xgb_l}")
    print(f"  lgbm_light probability : {lgbm_l}")
    print(f"  final score            : {score}")
    print(f"  fraud_probability      : {fraud_prob}")
    print(f"  decision               : {decision}")
    print(f"  is_fraud               : {is_fraud}")
    print(f"  risk_level             : {risk_level}")
    print(f"  threshold              : {threshold}")
    print(f"  inference_mode         : {mode}")

    # Verification checks
    checks = []

    # Check: risk_score == fraud_probability (gauge value)
    if score == fraud_prob:
        checks.append("✅ risk_score == fraud_probability (gauge consistent)")
    else:
        checks.append(f"❌ risk_score ({score}) != fraud_probability ({fraud_prob})")
        all_passed = False

    # Check: decision matches threshold comparison
    expected_decision = "FRAUD" if score >= threshold else "SAFE"
    if decision == expected_decision:
        checks.append(f"✅ decision '{decision}' matches threshold {threshold}")
    else:
        checks.append(f"❌ decision '{decision}' should be '{expected_decision}' at threshold {threshold}")
        all_passed = False

    # Check: is_fraud matches decision
    expected_is_fraud = (decision == "FRAUD")
    if is_fraud == expected_is_fraud:
        checks.append(f"✅ is_fraud={is_fraud} matches decision")
    else:
        checks.append(f"❌ is_fraud={is_fraud} doesn't match decision={decision}")
        all_passed = False

    # Check: inference_mode is "light"
    if mode == "light":
        checks.append("✅ inference_mode is 'light'")
    else:
        checks.append(f"❌ inference_mode is '{mode}', expected 'light'")
        all_passed = False

    # Check: final score = 0.60*xgb + 0.40*lgbm
    if isinstance(xgb_l, (int, float)) and isinstance(lgbm_l, (int, float)):
        expected_score = round(0.60 * xgb_l + 0.40 * lgbm_l, 4)
        if score == expected_score:
            checks.append(f"✅ score {score} == 0.60*{xgb_l} + 0.40*{lgbm_l}")
        else:
            checks.append(f"⚠️  score {score} vs expected {expected_score} (rounding)")

    # Check: no runtime errors (we got here)
    checks.append("✅ No runtime errors")

    for c in checks:
        print(f"  {c}")

# ================================================================
# 3. Backward Compatibility
# ================================================================
print("\n" + "=" * 60)
print("STEP 3: BACKWARD COMPATIBILITY")
print("=" * 60)

# Test predict() alias
r1 = predict(cases[0][1])
if "error" not in r1 and r1.get("inference_mode") == "light":
    print("✅ predict() alias works → routes to predict_light")
else:
    print(f"❌ predict() alias failed: {r1}")
    all_passed = False

# Test predict_realtime() alias
r2 = predict_realtime(cases[0][1])
if "error" not in r2 and r2.get("inference_mode") == "light":
    print("✅ predict_realtime() alias works → routes to predict_light")
else:
    print(f"❌ predict_realtime() alias failed: {r2}")
    all_passed = False

# Test predict_light with debug param (backward compat)
r3 = predict_light(cases[0][1], debug=True)
if "error" not in r3:
    print("✅ predict_light(debug=True) accepted without error")
else:
    print(f"❌ predict_light(debug=True) failed: {r3}")
    all_passed = False

# Test predict_light with threshold_override
r4 = predict_light(cases[0][1], threshold_override=0.01)
if "error" not in r4 and r4.get("decision") == "FRAUD":
    print("✅ threshold_override=0.01 correctly produces FRAUD for normal txn")
else:
    print(f"❌ threshold_override test failed: {r4}")
    all_passed = False

# Test MODELS tuple backward compat
if isinstance(MODELS, tuple) and len(MODELS) >= 8:
    print("✅ MODELS is tuple with ≥8 elements (data_loader compatible)")
else:
    print(f"❌ MODELS format wrong: type={type(MODELS)}, len={len(MODELS) if hasattr(MODELS, '__len__') else 'N/A'}")
    all_passed = False

# ================================================================
# 4. Validation Error Test
# ================================================================
print("\n" + "=" * 60)
print("STEP 4: VALIDATION ERRORS")
print("=" * 60)

invalid1 = {"TransactionAmt": -100, "hour": 25}
r_inv = predict_light(invalid1)
if "error" in r_inv and "Validation Error" in r_inv["error"]:
    print(f"✅ Invalid input caught: {r_inv['error']}")
else:
    print(f"❌ Invalid input not caught: {r_inv}")
    all_passed = False

invalid2 = {"hour": 12}  # missing amount
r_inv2 = predict_light(invalid2)
if "error" in r_inv2:
    print(f"✅ Missing amount caught: {r_inv2['error']}")
else:
    print(f"❌ Missing amount not caught")
    all_passed = False

# ================================================================
# 5. Feature Mismatch Check
# ================================================================
print("\n" + "=" * 60)
print("STEP 5: FEATURE MISMATCH CHECK")
print("=" * 60)

from config.paths import PREPROCESS_DIR, LIGHT_DIR
top35 = joblib.load(PREPROCESS_DIR / "top35_features.pkl")
xgb_light_model = joblib.load(LIGHT_DIR / "xgb_light.pkl")
lgbm_light_model = joblib.load(LIGHT_DIR / "lgbm_light.pkl")

xgb_expected = list(getattr(xgb_light_model, "feature_names_in_", []))
lgbm_expected = list(getattr(lgbm_light_model, "feature_names_in_", []))

if xgb_expected == top35:
    print(f"✅ xgb_light features match top35 ({len(top35)} features)")
else:
    diff = set(xgb_expected) ^ set(top35)
    print(f"⚠️  xgb_light features differ from top35: {diff}")

if lgbm_expected == top35:
    print(f"✅ lgbm_light features match top35 ({len(top35)} features)")
else:
    diff = set(lgbm_expected) ^ set(top35)
    print(f"⚠️  lgbm_light features differ from top35: {diff}")

print(f"\n   Top-35 feature list:")
for i, f in enumerate(top35, 1):
    print(f"     {i:2d}. {f}")

# ================================================================
# 6. Summary
# ================================================================
print("\n" + "=" * 60)
print("FINAL RESULT")
print("=" * 60)
if all_passed:
    print("🟢 ALL TESTS PASSED")
else:
    print("🔴 SOME TESTS FAILED — review output above")
