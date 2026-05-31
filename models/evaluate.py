# models/evaluate.py

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import json

from sklearn.metrics import (
    roc_auc_score, f1_score, precision_score, recall_score,
    classification_report, confusion_matrix,
    roc_curve, precision_recall_curve, average_precision_score
)

from config.paths import (
    HEAVY_DIR, LIGHT_DIR, PREPROCESS_DIR, ARTIFACTS_DIR
)

PLOTS_DIR = ARTIFACTS_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


# ================================================================
# Load Artifacts
# ================================================================
def load_artifacts():
    print("\nLoading artifacts...")

    xgb_heavy      = joblib.load(HEAVY_DIR      / "xgb_heavy.pkl")
    lgbm_heavy     = joblib.load(HEAVY_DIR      / "lgbm_heavy.pkl")
    iso_forest     = joblib.load(HEAVY_DIR      / "iso_forest.pkl")
    xgb_light      = joblib.load(LIGHT_DIR      / "xgb_light.pkl")
    lgbm_light     = joblib.load(LIGHT_DIR      / "lgbm_light.pkl")
    threshold      = joblib.load(PREPROCESS_DIR / "threshold.pkl")
    top35_features = joblib.load(PREPROCESS_DIR / "manual_features.pkl")
    all_features   = joblib.load(PREPROCESS_DIR / "all_features.pkl")

    print("✅ Artifacts Loaded")
    return (xgb_heavy, lgbm_heavy, iso_forest,
            xgb_light, lgbm_light,
            threshold, top35_features, all_features)


# ================================================================
# Ensemble Predict
# ================================================================
def ensemble_predict(xgb, lgbm, xgb_light, lgbm_light,
                     X_heavy, X_light):
    p1 = xgb.predict_proba(X_heavy)[:, 1]
    p2 = lgbm.predict_proba(X_heavy)[:, 1]
    p3 = xgb_light.predict_proba(X_light)[:, 1]
    p4 = lgbm_light.predict_proba(X_light)[:, 1]
    return 0.40*p1 + 0.30*p2 + 0.20*p3 + 0.10*p4


# ================================================================
# Compute Metrics
# ================================================================
def compute_metrics(y_true, probs, threshold, name="Model"):
    preds     = (probs > threshold).astype(int)
    auc       = roc_auc_score(y_true, probs)
    f1        = f1_score(y_true, preds)
    precision = precision_score(y_true, preds)
    recall    = recall_score(y_true, preds)
    cm        = confusion_matrix(y_true, preds)

    print(f"\n{'='*60}")
    print(f"📊 {name}")
    print(f"{'='*60}")
    print(f"AUC       : {auc:.4f}")
    print(f"F1        : {f1:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"Threshold : {threshold:.3f}")
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report:")
    print(classification_report(y_true, preds,
                                target_names=["Normal", "Fraud"]))
    return {
        "model": name, "auc": round(auc, 4),
        "f1": round(f1, 4), "precision": round(precision, 4),
        "recall": round(recall, 4), "threshold": round(threshold, 3)
    }


# ================================================================
# Plot ROC Curves
# ================================================================
def plot_roc_curves(models_probs, y_true):
    plt.figure(figsize=(9, 7))
    colors = ["#E24B4A", "#1D9E75", "#BA7517", "#5B8DB8", "#8E44AD"]

    for i, (name, probs) in enumerate(models_probs.items()):
        fpr, tpr, _ = roc_curve(y_true, probs)
        auc          = roc_auc_score(y_true, probs)
        plt.plot(fpr, tpr, linewidth=2, color=colors[i % len(colors)],
                 label=f"{name} (AUC={auc:.4f})")

    plt.plot([0,1], [0,1], linestyle="--", color="black")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curves")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "roc_curves.png", dpi=150)
    plt.close()
    print("✅ roc_curves.png saved")


# ================================================================
# Plot PR Curves
# ================================================================
def plot_pr_curves(models_probs, y_true):
    plt.figure(figsize=(9, 7))
    colors = ["#E24B4A", "#1D9E75", "#BA7517", "#5B8DB8", "#8E44AD"]

    for i, (name, probs) in enumerate(models_probs.items()):
        precision, recall, _ = precision_recall_curve(y_true, probs)
        ap = average_precision_score(y_true, probs)
        plt.plot(recall, precision, linewidth=2,
                 color=colors[i % len(colors)],
                 label=f"{name} (AP={ap:.4f})")

    baseline = y_true.mean()
    plt.axhline(baseline, linestyle="--", color="black",
                label=f"Baseline={baseline:.4f}")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision Recall Curves")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "pr_curves.png", dpi=150)
    plt.close()
    print("✅ pr_curves.png saved")


# ================================================================
# Plot Confusion Matrix
# ================================================================
def plot_confusion_matrix(y_true, probs, threshold):
    preds   = (probs > threshold).astype(int)
    cm      = confusion_matrix(y_true, preds)
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.heatmap(cm, annot=True, fmt=",", cmap="Reds", ax=axes[0],
                xticklabels=["Normal", "Fraud"],
                yticklabels=["Normal", "Fraud"])
    axes[0].set_title("Confusion Matrix")

    sns.heatmap(cm_norm, annot=True, fmt=".2%", cmap="Reds", ax=axes[1],
                xticklabels=["Normal", "Fraud"],
                yticklabels=["Normal", "Fraud"])
    axes[1].set_title("Normalized Confusion Matrix")

    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "confusion_matrix.png", dpi=150)
    plt.close()
    print("✅ confusion_matrix.png saved")


# ================================================================
# Plot Feature Importance
# ================================================================
def plot_feature_importance(model, feature_names, top_n=20):
    importance = pd.Series(
        model.feature_importances_, index=feature_names
    ).sort_values().tail(top_n)

    plt.figure(figsize=(10, 8))
    importance.plot(kind="barh", color="#E24B4A")
    plt.title("Top Feature Importance")
    plt.xlabel("Importance Score")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "feature_importance.png", dpi=150)
    plt.close()
    print("✅ feature_importance.png saved")


# ================================================================
# Plot Score Distribution
# ================================================================
def plot_score_distribution(y_true, probs, threshold):
    plt.figure(figsize=(10, 6))
    plt.hist(probs[y_true == 0], bins=50, alpha=0.6,
             density=True, label="Normal", color="#1D9E75")
    plt.hist(probs[y_true == 1], bins=50, alpha=0.6,
             density=True, label="Fraud",  color="#E24B4A")
    plt.axvline(threshold, linestyle="--", linewidth=2,
                color="black", label=f"Threshold={threshold:.3f}")
    plt.xlabel("Fraud Probability")
    plt.ylabel("Density")
    plt.title("Fraud Score Distribution")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "score_distribution.png", dpi=150)
    plt.close()
    print("✅ score_distribution.png saved")


# ================================================================
# Save Metrics Report
# ================================================================
def save_metrics_report(metrics):
    report_path = ARTIFACTS_DIR / "evaluation_report.json"
    with open(report_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print("✅ evaluation_report.json saved")


# ================================================================
# Main Evaluation
# ================================================================
def run_evaluation(X_test, y_test):
    print("\n" + "="*60)
    print("EVALUATION PIPELINE")
    print("="*60)

    (xgb, lgbm, iso, xgb_light, lgbm_light,
     threshold, top35, all_features) = load_artifacts()

    # Align features
    X_test = X_test.reindex(columns=all_features, fill_value=0)

    # ISO score
    X_test        = X_test.copy()
    iso_features  = [c for c in iso.feature_names_in_
                     if c in X_test.columns]
    X_test["iso_score"] = iso.decision_function(
        X_test[iso_features]
    )

    # Light features
    valid_top35 = [c for c in top35 if c in X_test.columns]
    X_light     = X_test[valid_top35].copy()

    # Individual probs
    models_probs = {
        "XGBoost Heavy":  xgb.predict_proba(X_test)[:, 1],
        "LightGBM Heavy": lgbm.predict_proba(X_test)[:, 1],
        "XGBoost Light":  xgb_light.predict_proba(X_light)[:, 1],
        "LightGBM Light": lgbm_light.predict_proba(X_light)[:, 1],
    }

    # Ensemble
    ensemble_probs = ensemble_predict(
        xgb, lgbm, xgb_light, lgbm_light, X_test, X_light
    )
    models_probs["Ensemble"] = ensemble_probs

    # Metrics
    all_metrics = []
    for name, probs in models_probs.items():
        m = compute_metrics(y_test, probs, threshold, name)
        all_metrics.append(m)

    # Plots
    plot_roc_curves(models_probs, y_test)
    plot_pr_curves(models_probs, y_test)
    plot_confusion_matrix(y_test, ensemble_probs, threshold)
    plot_score_distribution(y_test, ensemble_probs, threshold)
    plot_feature_importance(xgb, X_test.columns.tolist(), top_n=20)

    # Save
    save_metrics_report(all_metrics)

    print("\n🎉 EVALUATION COMPLETE")
    print(f"📁 Plots → {PLOTS_DIR}")

    return all_metrics


# ================================================================
# Run
# ================================================================
if __name__ == "__main__":
    from data.load_data import load_raw_data
    from models.train import split_data
    from features.preprocess import preprocess_inference
    from features.build_features import build_features

    df = load_raw_data()
    _, _, test_df, _, _, y_test = split_data(df)

    # ✅ Build features FIRST
    X_test = build_features(test_df)

    # ✅ Then preprocess
    X_test = preprocess_inference(X_test)

    run_evaluation(X_test, y_test)