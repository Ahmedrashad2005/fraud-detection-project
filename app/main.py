"""
Fraud Detection REST API.
Run: uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from models.predict import MODELS, predict, predict_batch, predict_light
from services.audit_log import fetch_recent_predictions, log_prediction
from services.artifacts import get_artifact_status
from services.batch_io import normalize_batch_input
from services.explain import explain_light_transaction

app = FastAPI(
    title="FraudGuard AI API",
    version="1.1.0",
    description="Real-time and batch credit-card fraud scoring",
)


class TransactionInput(BaseModel):
    TransactionAmt: float = Field(..., ge=0)
    ProductCD: Optional[str] = "W"
    card4: Optional[str] = "visa"
    card6: Optional[str] = "debit"
    P_emaildomain: Optional[str] = "gmail.com"
    DeviceType: Optional[str] = "desktop"
    dist1: Optional[float] = Field(0, ge=0)
    hour: Optional[int] = Field(12, ge=0, le=23)
    threshold: Optional[float] = Field(None, ge=0.01, le=0.99)


@app.get("/")
def home() -> dict[str, Any]:
    return {
        "message": "FraudGuard AI API",
        "status": "OK" if MODELS.get("loaded") else "degraded",
        "models_loaded": bool(MODELS.get("loaded")),
    }


@app.get("/health")
def health() -> dict[str, Any]:
    status = get_artifact_status()
    return {
        "status": "healthy" if status.get("inference_backend") else "unhealthy",
        "artifacts": status,
        "default_threshold": MODELS.get("threshold"),
    }


@app.post("/predict")
def predict_transaction(data: TransactionInput) -> dict[str, Any]:
    if not MODELS.get("loaded"):
        raise HTTPException(503, detail=f"Models not loaded: {MODELS.get('error')}")

    payload = data.model_dump(exclude={"threshold"})
    threshold = data.threshold
    result = predict(payload, threshold_override=threshold)

    if result.get("error"):
        raise HTTPException(400, detail=result["error"])

    log_prediction("api_realtime", payload, result)
    return result


@app.post("/predict/explain")
def predict_with_explanation(data: TransactionInput) -> dict[str, Any]:
    if not MODELS.get("loaded"):
        raise HTTPException(503, detail=f"Models not loaded: {MODELS.get('error')}")

    payload = data.model_dump(exclude={"threshold"})
    result = predict_light(payload, threshold_override=data.threshold)
    if result.get("error"):
        raise HTTPException(400, detail=result["error"])

    explanation = explain_light_transaction(payload, MODELS)
    log_prediction("api_explain", payload, result)
    return {"prediction": result, "explanation": explanation}


@app.post("/predict/batch")
async def predict_batch_upload(
    file: UploadFile = File(...),
    threshold: Optional[float] = Query(None, ge=0.01, le=0.99),
) -> dict[str, Any]:
    if not MODELS.get("loaded"):
        raise HTTPException(503, detail=f"Models not loaded: {MODELS.get('error')}")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".csv", ".xlsx", ".xls"}:
        raise HTTPException(400, detail="Upload CSV or Excel (.xlsx/.xls)")

    raw = await file.read()
    try:
        if suffix == ".csv":
            df = pd.read_csv(io.BytesIO(raw), nrows=5000)
        else:
            df = pd.read_excel(io.BytesIO(raw), nrows=5000)
    except Exception as exc:
        raise HTTPException(400, detail=f"Could not parse file: {exc}") from exc

    norm = normalize_batch_input(df)
    if not norm.ok:
        raise HTTPException(400, detail=norm.message)

    try:
        scored = predict_batch(norm.data, threshold_override=threshold)
    except Exception as exc:
        raise HTTPException(500, detail=str(exc)) from exc

    preview = scored.head(100).to_dict(orient="records")
    fraud_count = int(scored.get("prediction", scored.get("is_fraud", pd.Series([0]))).sum())
    effective_threshold = (
        float(scored["threshold"].iloc[0])
        if "threshold" in scored.columns and len(scored)
        else float(MODELS.get("threshold", 0.75))
    )
    return {
        "rows_scored": len(scored),
        "fraud_flagged": fraud_count,
        "threshold": effective_threshold,
        "preview": preview,
    }


@app.get("/audit/recent")
def audit_recent(limit: int = 25) -> dict[str, Any]:
    return {"predictions": fetch_recent_predictions(limit=min(limit, 200))}
