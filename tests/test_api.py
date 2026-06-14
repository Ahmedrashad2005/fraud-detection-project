"""API smoke tests (requires trained artifacts)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import TransactionInput, home, predict_transaction
from models.predict import MODELS


def test_home():
    body = home()
    assert "FraudGuard" in body["message"]
    assert "models_loaded" in body


@pytest.mark.skipif(not MODELS.get("loaded"), reason="models not loaded")
def test_predict_endpoint():
    payload = TransactionInput(**{
        "TransactionAmt": 50,
        "card4": "visa",
        "card6": "debit",
        "P_emaildomain": "gmail.com",
        "DeviceType": "desktop",
        "dist1": 0,
        "hour": 12,
    })
    body = predict_transaction(payload)
    assert "risk_score" in body
