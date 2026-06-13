"""Unit tests for inference (requires trained artifacts)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.predict import MODELS, predict, predict_batch, predict_light
from services.batch_io import normalize_batch_input


@pytest.fixture(scope="module")
def require_models():
    if not MODELS.get("loaded"):
        pytest.skip(f"Artifacts not loaded: {MODELS.get('error')}")


SAMPLE = {
    "TransactionAmt": 42.0,
    "ProductCD": "W",
    "card4": "visa",
    "card6": "debit",
    "P_emaildomain": "gmail.com",
    "DeviceType": "desktop",
    "dist1": 5,
    "hour": 14,
}


def test_predict_alias(require_models):
    out = predict(SAMPLE)
    assert "error" not in out
    assert "risk_score" in out
    assert "fraud_probability" in out


def test_predict_light_high_amount(require_models):
    risky = {**SAMPLE, "TransactionAmt": 8000, "hour": 2, "dist1": 900}
    out = predict_light(risky, threshold_override=0.5)
    assert out["risk_score"] >= 0


def test_predict_batch(require_models):
    df = pd.DataFrame([SAMPLE, {**SAMPLE, "TransactionAmt": 1}])
    scored = predict_batch(df)
    assert len(scored) == 2
    assert "risk_score" in scored.columns


def test_normalize_batch_aliases():
    raw = pd.DataFrame({"amount": [10.0, 20.0]})
    result = normalize_batch_input(raw)
    assert result.ok
    assert "TransactionAmt" in result.data.columns
