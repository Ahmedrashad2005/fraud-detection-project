from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

# Data
DATA_DIR       = BASE_DIR / "data"
RAW_DIR        = DATA_DIR / "raw"
PROCESSED_DIR  = DATA_DIR / "processed"

# Raw Files
TRAIN_TX = RAW_DIR / "train_transaction.csv"
TRAIN_ID = RAW_DIR / "train_identity.csv"
TEST_TX  = RAW_DIR / "test_transaction.csv"
TEST_ID  = RAW_DIR / "test_identity.csv"

# Artifacts
ARTIFACTS_DIR  = BASE_DIR / "artifacts"
MODELS_DIR     = ARTIFACTS_DIR / "models"
HEAVY_DIR      = MODELS_DIR / "heavy"
LIGHT_DIR      = MODELS_DIR / "light"
PREPROCESS_DIR = ARTIFACTS_DIR / "preprocessing"

# Heavy Models
XGB_HEAVY  = HEAVY_DIR / "xgb_heavy.pkl"
LGBM_HEAVY = HEAVY_DIR / "lgbm_heavy.pkl"
ISO_FOREST = HEAVY_DIR / "iso_forest.pkl"

# Light Models
XGB_LIGHT  = LIGHT_DIR / "xgb_light.pkl"
LGBM_LIGHT = LIGHT_DIR / "lgbm_light.pkl"

# Preprocessing
ALL_FEATURES    = PREPROCESS_DIR / "all_features.pkl"
DROPPED_COLS    = PREPROCESS_DIR / "dropped_cols.pkl"
FEATURE_COLUMNS = PREPROCESS_DIR / "feature_columns.pkl"
FEATURE_MEDIANS = PREPROCESS_DIR / "feature_medians.pkl"
MEDIANS         = PREPROCESS_DIR / "medians.pkl"
THRESHOLD       = PREPROCESS_DIR / "threshold.pkl"
LIGHT_THRESHOLD = PREPROCESS_DIR / "light_threshold.pkl"
MANUAL_FEATURES = PREPROCESS_DIR / "manual_features.pkl"
REFERENCE_STATS = PREPROCESS_DIR / "reference_stats.pkl"
AGGREGATION_MAPS = PREPROCESS_DIR / "aggregation_maps.pkl"

# Auto-create dirs
for path in [RAW_DIR, PROCESSED_DIR,
             HEAVY_DIR, LIGHT_DIR, PREPROCESS_DIR]:
    path.mkdir(parents=True, exist_ok=True)
