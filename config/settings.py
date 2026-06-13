# ============================================================
# GENERAL CONFIG
# ============================================================

APP_NAME     = "Fraud Detection System"
VERSION      = "1.1.0"
RANDOM_STATE = 42
TEST_SIZE    = 0.2


# ============================================================
# THRESHOLDS
# ============================================================

# Note: The actual prediction threshold is loaded from
# artifacts/preprocessing/threshold.pkl (calibrated on validation set).
# These are fallback defaults only.
DEFAULT_THRESHOLD = 0.75

# Risk levels (for UI / business logic)
RISK_THRESHOLDS = {
    "high": 0.75,
    "medium": 0.5
}

RISK_LABELS = {
    "high": "HIGH RISK",
    "medium": "MEDIUM RISK",
    "low": "LOW RISK"
}


# ============================================================
# DATABASE
# ============================================================

DB_NAME      = "fraud_detection.db"
DB_PATH      = f"artifacts/{DB_NAME}"

DB_TABLE_TX  = "transactions"
DB_TABLE_LOG = "prediction_logs"


# ============================================================
# DASHBOARD
# ============================================================

REFRESH_RATE     = 30   # seconds
MAX_ROWS_DISPLAY = 100


# ============================================================
# LOGGING
# ============================================================

LOG_LEVEL = "INFO"


# ============================================================
# MLOPS
# ============================================================

DRIFT_THRESHOLD = 0.85
MLFLOW_EXP_NAME = "fraud-detection"