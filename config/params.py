# config/params.py

# scale_pos_weight = neg/pos = 569877/20663 ≈ 27
FRAUD_SCALE_WEIGHT = 25

XGB_HEAVY_PARAMS = {
    "n_estimators":      500,
    "max_depth":         6,
    "learning_rate":     0.05,
    "subsample":         0.8,
    "colsample_bytree":  0.8,
    "eval_metric":       "auc",
    "random_state":      42,
    "n_jobs":            -1,
    "verbosity":         0,
    # ✅ بديل SMOTE في XGBoost
    "scale_pos_weight":  FRAUD_SCALE_WEIGHT,
}

XGB_LIGHT_PARAMS = {
    "n_estimators":      300,
    "max_depth":         5,
    "learning_rate":     0.05,
    "subsample":         0.8,
    "colsample_bytree":  0.8,
    "eval_metric":       "auc",
    "random_state":      42,
    "n_jobs":            -1,
    "verbosity":         0,
    "scale_pos_weight":  FRAUD_SCALE_WEIGHT,
}

LGBM_HEAVY_PARAMS = {
    "n_estimators":  500,
    "max_depth":     6,
    "learning_rate": 0.05,
    "subsample":     0.8,
    "random_state":  42,
    "n_jobs":        -1,
    "verbose":       -1,
    # ✅ بديل SMOTE في LightGBM
    "is_unbalance":  True,
}

LGBM_LIGHT_PARAMS = {
    "n_estimators":  300,
    "max_depth":     5,
    "learning_rate": 0.05,
    "subsample":     0.8,
    "random_state":  42,
    "n_jobs":        -1,
    "verbose":       -1,
    "is_unbalance":  True,
}

ISO_PARAMS = {
    "contamination": 0.035,
    "n_estimators":  200,
    "random_state":  42,
    "n_jobs":        -1,
}

# ================================================================
# Ensemble weights — SINGLE SOURCE OF TRUTH
# ================================================================

# Full ensemble (training evaluation: all 4 models together)
FULL_ENSEMBLE_WEIGHTS = {
    "xgb_h":  0.40,
    "lgbm_h": 0.30,
    "xgb_l":  0.20,
    "lgbm_l": 0.10,
}

# Heavy ensemble (batch/production: xgb_heavy + lgbm_heavy + iso_forest)
HEAVY_ENSEMBLE_WEIGHTS = {"xgb": 0.45, "lgbm": 0.35, "iso": 0.20}

# Light ensemble (real-time: xgb_light + lgbm_light only)
LIGHT_ENSEMBLE_WEIGHTS = {"xgb": 0.60, "lgbm": 0.40}
