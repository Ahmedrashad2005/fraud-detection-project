"""API smoke tests (requires trained artifacts)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app
from models.predict import MODELS

client = TestClient(app)


def test_home():
    r = client.get("/")
    assert r.status_code == 200
    assert "FraudGuard" in r.json()["message"]


@pytest.mark.skipif(not MODELS.get("loaded"), reason="models not loaded")
def test_predict_endpoint():
    payload = {
        "TransactionAmt": 50,
        "card4": "visa",
        "card6": "debit",
        "P_emaildomain": "gmail.com",
        "DeviceType": "desktop",
        "dist1": 0,
        "hour": 12,
    }
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "risk_score" in body
