"""
diagnostic.py — run this to check why batch results are all 0
Usage: python diagnostic.py
"""
import sys
sys.path.insert(0, '.')

import numpy as np
import pandas as pd
import joblib

from config.paths import HEAVY_DIR, LIGHT_DIR, PREPROCESS_DIR, MANUAL_FEATURES
from features.build_features import build_features
from features.preprocess import preprocess_inference

SEP = "=" * 60


def load_all():
    print(SEP)
    print("1. LOADING ARTIFACTS")
    print(SEP)
    m = {}
    try:
        m["xgb_heavy"]  = joblib.load(HEAVY_DIR      / "xgb_heavy.pkl")
        m["lgbm_heavy"] = joblib.load(HEAVY_DIR      / "lgbm_heavy.pkl")
        m["xgb_light"]  = joblib.load(LIGHT_DIR      / "xgb_light.pkl")
        m["lgbm_light"] = joblib.load(LIGHT_DIR      / "lgbm_light.pkl")
        m["iso"]        = joblib.load(HEAVY_DIR      / "iso_forest.pkl")
        m["threshold"]  = float(joblib.load(PREPROCESS_DIR / "threshold.pkl"))
        m["manual_feats"] = joblib.load(MANUAL_FEATURES)
        m["all_feats"]    = joblib.load(PREPROCESS_DIR / "all_features.pkl")
        print(f"  ✅ All models loaded")
        print(f"  Threshold         : {m['threshold']:.4f}")
        print(f"  manual_features   : {len(m['manual_feats'])} features")
        print(f"  all_features      : {len(m['all_feats'])} features")
        print(f"  Manual feats list : {m['manual_feats']}")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        sys.exit(1)
    return m


def test_single(m):
    print("\n" + SEP)
    print("2. SINGLE ROW TESTS")
    print(SEP)

    cases = {
        "🚨 SUSPICIOUS (fraud-like)": {
            "TransactionAmt": 5000.0, "card4": "discover", "card6": "credit",
            "P_emaildomain": "anonymous.com", "DeviceType": "mobile",
            "dist1": 800.0, "TransactionDT": 10800, "hour": 3,
        },
        "✅ NORMAL (safe-like)": {
            "TransactionAmt": 35.0, "card4": "visa", "card6": "debit",
            "P_emaildomain": "gmail.com", "DeviceType": "desktop",
            "dist1": 5.0, "TransactionDT": 50400, "hour": 14,
        },
    }

    threshold = m["threshold"]

    for label, row in cases.items():
        print(f"\n  {label}")
        df = pd.DataFrame([row])
        X = build_features(df.copy())
        X = preprocess_inference(X)
        X_light = X.reindex(columns=m["manual_feats"], fill_value=0)
        X_heavy = X.reindex(columns=m["all_feats"],    fill_value=0)

        # Check NaN
        nan_l = X_light.isnull().sum().sum()
        nan_h = X_heavy.isnull().sum().sum()
        print(f"    NaN in light features : {nan_l}")
        print(f"    NaN in heavy features : {nan_h}")

        p_xgb_l  = float(m["xgb_light"].predict_proba(X_light)[0, 1])
        p_lgbm_l = float(m["lgbm_light"].predict_proba(X_light)[0, 1])
        p_xgb_h  = float(m["xgb_heavy"].predict_proba(X_heavy)[0, 1])
        p_lgbm_h = float(m["lgbm_heavy"].predict_proba(X_heavy)[0, 1])

        light_score = 0.6 * p_xgb_l  + 0.4 * p_lgbm_l
        heavy_score = 0.5 * p_xgb_h  + 0.5 * p_lgbm_h

        print(f"    XGB  Light  : {p_xgb_l:.4f}")
        print(f"    LGBM Light  : {p_lgbm_l:.4f}")
        print(f"    Light Score : {light_score:.4f}  → {'🚨 FRAUD' if light_score >= threshold else '✅ SAFE'}")
        print(f"    XGB  Heavy  : {p_xgb_h:.4f}")
        print(f"    LGBM Heavy  : {p_lgbm_h:.4f}")
        print(f"    Heavy Score : {heavy_score:.4f}  → {'🚨 FRAUD' if heavy_score >= threshold else '✅ SAFE'}")
        print(f"    (Threshold  = {threshold:.4f})")


def test_batch(m):
    print("\n" + SEP)
    print("3. BATCH TEST (5 fraud-like + 5 normal)")
    print(SEP)

    rows = []
    for i in range(5):
        rows.append({
            "TransactionAmt": 5000 + i * 200,
            "card4": "discover", "card6": "credit",
            "P_emaildomain": "anonymous.com", "DeviceType": "mobile",
            "dist1": 900 + i * 10, "TransactionDT": 7200, "hour": 2,
        })
    for i in range(5):
        rows.append({
            "TransactionAmt": 30 + i * 5,
            "card4": "visa", "card6": "debit",
            "P_emaildomain": "gmail.com", "DeviceType": "desktop",
            "dist1": 3 + i, "TransactionDT": 50000, "hour": 13,
        })

    batch = pd.DataFrame(rows)
    X = build_features(batch.copy())
    X = preprocess_inference(X)
    X_h = X.reindex(columns=m["all_feats"], fill_value=0)

    p1 = m["xgb_heavy"].predict_proba(X_h)[:, 1]
    p2 = m["lgbm_heavy"].predict_proba(X_h)[:, 1]

    # ISO
    iso = m["iso"]
    iso_cols = [c for c in getattr(iso, "feature_names_in_", []) if c in X_h.columns]
    iso_score = iso.decision_function(X_h[iso_cols]) if iso_cols else np.zeros(len(X_h))
    iso_norm  = (iso_score - iso_score.min()) / (iso_score.max() - iso_score.min() + 1e-8)
    iso_fraud = 1.0 - iso_norm

    threshold = m["threshold"]
    scores = 0.45 * p1 + 0.35 * p2 + 0.20 * iso_fraud
    preds  = (scores >= threshold).astype(int)

    print(f"\n  Score range  : {scores.min():.4f} → {scores.max():.4f}")
    print(f"  Threshold    : {threshold:.4f}")
    print(f"  Fraud flagged: {preds.sum()} / {len(preds)}")
    print(f"\n  {'Row':<5} {'Expected':<12} {'Score':<8} {'Pred'}")
    for i, (s, p) in enumerate(zip(scores, preds)):
        expected = "FRAUD" if i < 5 else "SAFE"
        pred_label = "🚨 FRAUD" if p else "✅ SAFE"
        match = "✅" if (expected == "FRAUD") == bool(p) else "❌"
        print(f"  {i+1:<5} {expected:<12} {s:.4f}   {pred_label}  {match}")

    # Show distribution
    print(f"\n  p1 (XGB)   range: {p1.min():.4f} → {p1.max():.4f}  mean={p1.mean():.4f}")
    print(f"  p2 (LGBM)  range: {p2.min():.4f} → {p2.max():.4f}  mean={p2.mean():.4f}")
    print(f"  iso_fraud  range: {iso_fraud.min():.4f} → {iso_fraud.max():.4f}  mean={iso_fraud.mean():.4f}")


def check_calibration(m):
    print("\n" + SEP)
    print("4. THRESHOLD CALIBRATION CHECK")
    print(SEP)
    threshold = m["threshold"]
    print(f"  Saved threshold : {threshold:.4f}")
    if threshold > 0.80:
        print("  ⚠️  VERY HIGH threshold — almost nothing will be flagged!")
        print("      Consider retraining or manually lowering to 0.5–0.65")
    elif threshold < 0.20:
        print("  ⚠️  VERY LOW threshold — almost everything will be flagged!")
    else:
        print("  ✅ Threshold looks reasonable")


if __name__ == "__main__":
    m = load_all()
    check_calibration(m)
    test_single(m)
    test_batch(m)
    print("\n" + SEP)
    print("DIAGNOSTIC COMPLETE")
    print(SEP)
