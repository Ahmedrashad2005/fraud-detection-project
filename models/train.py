# models/train.py

import pandas as pd
import numpy as np
import joblib

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, f1_score,
    classification_report, confusion_matrix,
    precision_recall_curve
)

from config.paths import (
    HEAVY_DIR, LIGHT_DIR, PREPROCESS_DIR, REFERENCE_STATS,
    LIGHT_THRESHOLD
)
from config.params import (
    XGB_HEAVY_PARAMS, XGB_LIGHT_PARAMS,
    LGBM_HEAVY_PARAMS, LGBM_LIGHT_PARAMS,
    ISO_PARAMS, LIGHT_ENSEMBLE_WEIGHTS, FULL_ENSEMBLE_WEIGHTS
)
from config.settings import TEST_SIZE, RANDOM_STATE
from data.load_data import load_raw_data
from features.preprocess import preprocess_train, preprocess_inference
from features.build_features import build_features
from features.aggregation import fit_aggregation_features, save_aggregation_artifact

TARGET = "isFraud"


# ================================================================
# 1. Split → Train / Val / Test
# ================================================================
def split_data(df):
    print("\n" + "="*50)
    print("SPLIT DATA (70 / 15 / 15)")
    print("="*50)

    X = df.drop(columns=[TARGET])
    y = df[TARGET]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3,
        random_state=RANDOM_STATE, stratify=y
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5,
        random_state=RANDOM_STATE, stratify=y_temp
    )

    print(f"Train : {X_train.shape} | Fraud: {y_train.sum():,}")
    print(f"Val   : {X_val.shape}   | Fraud: {y_val.sum():,}")
    print(f"Test  : {X_test.shape}  | Fraud: {y_test.sum():,}")

    return X_train, X_val, X_test, y_train, y_val, y_test


# ================================================================
# 2. Preprocess + Feature Engineering
# ================================================================
def process_data(X_train, X_val, X_test):

    # ✅ 1. Build features FIRST على raw strings
    X_train = build_features(X_train)
    X_val   = build_features(X_val)
    X_test  = build_features(X_test)

    # ✅ 2. Then preprocess
    X_train = preprocess_train(X_train)
    X_val   = preprocess_inference(X_val)
    X_test  = preprocess_inference(X_test)

    # Align
    X_val  = X_val.reindex(columns=X_train.columns, fill_value=0)
    X_test = X_test.reindex(columns=X_train.columns, fill_value=0)

    return X_train, X_val, X_test

# ================================================================
# 3. Aggregation Features (fit on train only)
# ================================================================
def add_aggregation_features(X_train, X_val, X_test):
    print("\n" + "="*50)
    print("AGGREGATION FEATURES")
    print("="*50)

    X_train, X_val, X_test, artifact = fit_aggregation_features(X_train, X_val, X_test)
    save_aggregation_artifact(artifact)

    print(f"\n✅ Train : {X_train.shape}")
    print(f"✅ Val   : {X_val.shape}")
    print(f"✅ Test  : {X_test.shape}")

    return X_train, X_val, X_test


# ================================================================
# 4. Isolation Forest
# ================================================================
def train_iso(X_train):
    print("\n" + "="*50)
    print("ISOLATION FOREST")
    print("="*50)

    iso = IsolationForest(**ISO_PARAMS)
    iso.fit(X_train)
    print("✅ Isolation Forest trained")
    return iso


# ================================================================
# 5. Find Best Threshold
# ================================================================
def find_best_threshold(y_true, probs, beta=0.5):
    precision, recall, thresholds = precision_recall_curve(
        y_true, probs
    )
    if len(thresholds) == 0:
        return 0.5

    precision = precision[:-1]
    recall = recall[:-1]
    f_beta = ((1 + beta**2) * precision * recall) / \
             (beta**2 * precision + recall + 1e-6)

    best_idx       = np.argmax(f_beta)
    best_threshold = float(thresholds[best_idx])

    print(f"Best Threshold : {best_threshold:.3f}")
    print(f"Precision      : {precision[best_idx]:.3f}")
    print(f"Recall         : {recall[best_idx]:.3f}")
    print(f"F{beta} Score  : {f_beta[best_idx]:.3f}")

    return best_threshold


# ================================================================
# 6. Evaluation
# ================================================================
def evaluate(probs, y, threshold, name="Model"):
    preds = (probs >= threshold).astype(int)

    print(f"\n{'='*50}")
    print(f"📊 {name}")
    print(f"{'='*50}")
    print(f"AUC       : {roc_auc_score(y, probs):.4f}")
    print(f"F1        : {f1_score(y, preds):.4f}")
    print(f"Threshold : {threshold:.3f}")
    print(f"\nConfusion Matrix:")
    print(confusion_matrix(y, preds))
    print(f"\nClassification Report:")
    print(classification_report(y, preds,
                                target_names=['Normal', 'Fraud']))


# ================================================================
# 7. Train Heavy Models
# ================================================================
def train_heavy(X_train, y_train, X_val, y_val):
    print("\n" + "="*50)
    print("MODEL 1 — HEAVY (All Features)")
    print("="*50)
    print(f"Features: {X_train.shape[1]}")

    xgb = XGBClassifier(**XGB_HEAVY_PARAMS)
    xgb.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=100
    )

    lgbm = LGBMClassifier(**LGBM_HEAVY_PARAMS)
    lgbm.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)]
    )

    print(f"\nXGBoost  VAL AUC: "
          f"{roc_auc_score(y_val, xgb.predict_proba(X_val)[:,1]):.4f}")
    print(f"LightGBM VAL AUC: "
          f"{roc_auc_score(y_val, lgbm.predict_proba(X_val)[:,1]):.4f}")

    return xgb, lgbm


# ================================================================
# 8. Manual Feature Selection
# ================================================================
def get_manual_feature_columns(X_train):



    candidates = [

        # TransactionAmt

        "TransactionAmt",

        "amount_log",

        "amount_sqrt",

        "amount_category",



        # card4

        "card4",

        "is_visa",

        "is_mastercard",

        "is_amex",

        "is_discover",



        # card6

        "card6",

        "is_credit",

        "is_debit",



        # DeviceType

        "DeviceType",

        "is_mobile",



        # dist1

        "dist1",

        "dist1_log",

        "is_far_distance",



        # hour

        "hour",

        "is_morning",

        "is_night",



        # email

        "P_emaildomain",

        "is_free_email",

        "email_missing",

        "is_suspicious_domain",

        "domain_length",



        # ProductCD

        "ProductCD",

        # Risk signals

        "amt_x_distance",

        "geo_amount_risk",

        "night_x_high_amount",

        "amt_hour_risk",

    ]



    return [f for f in candidates if f in X_train.columns]
    


# ================================================================
# 9. Train Light Models (Manual Dashboard Features)
# ================================================================
def train_light(X_train, y_train, X_val, y_val):
    print("\n" + "="*50)
    print("MODEL 2 — LIGHT (Manual Dashboard Features)")
    print("="*50)

    features = get_manual_feature_columns(X_train)
    print(f"Manual Features: {len(features)}")
    print(f"Coverage: 100% dashboard-derived")
    for i, f in enumerate(features, 1):
        print(f"  {i:2d}. {f}")

    X_tr = X_train[features]
    X_va = X_val[features]

    xgb_l = XGBClassifier(**XGB_LIGHT_PARAMS)
    xgb_l.fit(
        X_tr, y_train,
        eval_set=[(X_va, y_val)],
        verbose=100
    )

    lgbm_l = LGBMClassifier(**LGBM_LIGHT_PARAMS)
    lgbm_l.fit(X_tr, y_train)

    print(f"\nXGBoost Manual  VAL AUC: "
          f"{roc_auc_score(y_val, xgb_l.predict_proba(X_va)[:,1]):.4f}")
    print(f"LightGBM Manual VAL AUC: "
          f"{roc_auc_score(y_val, lgbm_l.predict_proba(X_va)[:,1]):.4f}")

    return xgb_l, lgbm_l, features


# ================================================================
# 9. Ensemble Predict
# ================================================================
def ensemble_predict(xgb, lgbm, xgb_l, lgbm_l, X, light_features):
    p1 = xgb.predict_proba(X)[:, 1]
    p2 = lgbm.predict_proba(X)[:, 1]
    p3 = xgb_l.predict_proba(X[light_features])[:, 1]
    p4 = lgbm_l.predict_proba(X[light_features])[:, 1]

    return FULL_ENSEMBLE_WEIGHTS["xgb_h"]*p1 + FULL_ENSEMBLE_WEIGHTS["lgbm_h"]*p2 + FULL_ENSEMBLE_WEIGHTS["xgb_l"]*p3 + FULL_ENSEMBLE_WEIGHTS["lgbm_l"]*p4


# ================================================================
# 10. Save Artifacts
# ================================================================
def save_all(models, all_features, light_features,
             X_train, threshold, light_threshold):
    print("\n" + "="*50)
    print("SAVING ARTIFACTS")
    print("="*50)

    HEAVY_DIR.mkdir(parents=True, exist_ok=True)
    LIGHT_DIR.mkdir(parents=True, exist_ok=True)
    PREPROCESS_DIR.mkdir(parents=True, exist_ok=True)

    # Heavy Models
    joblib.dump(models["xgb_heavy"],  HEAVY_DIR / "xgb_heavy.pkl")
    joblib.dump(models["lgbm_heavy"], HEAVY_DIR / "lgbm_heavy.pkl")
    joblib.dump(models["iso_forest"], HEAVY_DIR / "iso_forest.pkl")
    print("✅ xgb_heavy.pkl  → heavy/")
    print("✅ lgbm_heavy.pkl → heavy/")
    print("✅ iso_forest.pkl → heavy/")

    # Light Models
    joblib.dump(models["xgb_light"],  LIGHT_DIR / "xgb_light.pkl")
    joblib.dump(models["lgbm_light"], LIGHT_DIR / "lgbm_light.pkl")
    print("✅ xgb_light.pkl  → light/")
    print("✅ lgbm_light.pkl → light/")

    # Preprocessing Artifacts
    joblib.dump(all_features,   PREPROCESS_DIR / "all_features.pkl")
    joblib.dump(light_features, PREPROCESS_DIR / "manual_features.pkl")
    joblib.dump(threshold,      PREPROCESS_DIR / "threshold.pkl")
    joblib.dump(light_threshold, LIGHT_THRESHOLD)
    print(f"✅ threshold.pkl       (ensemble): {threshold:.3f}")
    print(f"✅ light_threshold.pkl (light):    {light_threshold:.3f}")

    medians = X_train.median().to_dict()
    joblib.dump(medians, PREPROCESS_DIR / "feature_medians.pkl")

    drift_cols = [
        c for c in [
            "TransactionAmt", "amount_log", "dist1", "dist1_log",
            "hour", "is_night", "is_high_amount", "is_mobile",
        ]
        if c in X_train.columns
    ]
    reference_stats = {}
    for col in drift_cols:
        series = X_train[col].dropna()
        reference_stats[col] = {
            "mean": float(series.mean()),
            "std": float(series.std() or 1e-6),
            "p25": float(series.quantile(0.25)),
            "p75": float(series.quantile(0.75)),
        }
    joblib.dump(reference_stats, REFERENCE_STATS)
    print("✅ reference_stats → preprocessing/")
    print("✅ artifacts      → preprocessing/")


# ================================================================
# MAIN
# ================================================================
def main():
    print("\n" + "="*50)
    print("TRAINING PIPELINE")
    print("="*50)

    # 1. Load
    df = load_raw_data()

    # 2. Split
    X_train, X_val, X_test, \
    y_train, y_val, y_test = split_data(df)

    # 🌟 فرّغ الرام من الـ df الأصلي (~2GB)
    del df
    import gc; gc.collect()

    # 3. Preprocess + Features
    X_train, X_val, X_test = process_data(X_train, X_val, X_test)

    # 4. Aggregation
    X_train, X_val, X_test = add_aggregation_features(
        X_train, X_val, X_test
    )

    # 5. ISO + iso_score feature
    iso = train_iso(X_train)
    X_train['iso_score'] = iso.decision_function(X_train)
    X_val['iso_score']   = iso.decision_function(X_val)
    X_test['iso_score']  = iso.decision_function(X_test)
    print("✅ iso_score added as feature")

    # 6. Heavy Models
    xgb, lgbm = train_heavy(X_train, y_train, X_val, y_val)

    # 7. Light Models (Manual Dashboard Features)
    xgb_l, lgbm_l, light_features = train_light(
        X_train, y_train, X_val, y_val
    )

    # 8. Threshold on Val — Full Ensemble
    print("\n" + "="*50)
    print("THRESHOLD TUNING ON VAL SET (FULL ENSEMBLE)")
    print("="*50)
    val_probs = ensemble_predict(
        xgb, lgbm, xgb_l, lgbm_l, X_val, light_features
    )
    threshold = find_best_threshold(y_val, val_probs, beta=0.5)

    # 8b. Threshold on Val — Light-Only (calibrated for real-time)
    w = LIGHT_ENSEMBLE_WEIGHTS
    light_val_probs = (
        w["xgb"] * xgb_l.predict_proba(X_val[light_features])[:, 1] +
        w["lgbm"] * lgbm_l.predict_proba(X_val[light_features])[:, 1]
    )
    print("\n" + "="*50)
    print("THRESHOLD TUNING ON VAL SET (LIGHT ONLY)")
    print("="*50)
    light_threshold = find_best_threshold(y_val, light_val_probs, beta=0.5)

    # 9. Final Evaluation on Test
    print("\n" + "="*50)
    print("FINAL EVALUATION ON TEST SET")
    print("="*50)
    test_probs = ensemble_predict(
        xgb, lgbm, xgb_l, lgbm_l, X_test, light_features
    )
    evaluate(test_probs, y_test, threshold, "FINAL ENSEMBLE")

    # 9b. Light-Only Evaluation on Test
    print("\n" + "="*50)
    print("LIGHT-ONLY EVALUATION (Manual Features)")
    print("="*50)
    light_test_probs = (
        w["xgb"] * xgb_l.predict_proba(X_test[light_features])[:, 1] +
        w["lgbm"] * lgbm_l.predict_proba(X_test[light_features])[:, 1]
    )
    evaluate(light_test_probs, y_test, light_threshold, "LIGHT MANUAL")

    # 10. Save
    save_all(
        {"xgb_heavy":  xgb,
         "lgbm_heavy": lgbm,
         "iso_forest": iso,
         "xgb_light":  xgb_l,
         "lgbm_light": lgbm_l},
        X_train.columns.tolist(),
        light_features,
        X_train,
        threshold,
        light_threshold,
    )

    print("\n🎉 TRAINING COMPLETE!")


if __name__ == "__main__":
    main()
