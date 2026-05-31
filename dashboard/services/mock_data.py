# dashboard/services/mock_data.py
"""
Mock Data Generator — Provides realistic simulated data when
artifacts are unavailable or for demo/presentation purposes.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generate_mock_transactions(n_rows=2847, fraud_rate=0.035, seed=42):
    """
    Generate a realistic mock DataFrame for the batch dashboard.

    Args:
        n_rows:     Total number of transactions.
        fraud_rate: Fraction of fraudulent transactions.
        seed:       Random seed for reproducibility.

    Returns:
        pd.DataFrame with realistic transaction data.
    """
    rng = np.random.RandomState(seed)

    n_fraud  = int(n_rows * fraud_rate)
    n_normal = n_rows - n_fraud

    # ── Labels ──
    labels = np.concatenate([np.zeros(n_normal), np.ones(n_fraud)])
    rng.shuffle(labels)

    # ── Transaction Amount ──
    amounts = np.where(
        labels == 1,
        rng.lognormal(mean=5.5, sigma=1.5, size=n_rows),
        rng.lognormal(mean=3.5, sigma=1.0, size=n_rows),
    )
    amounts = np.clip(amounts, 0.5, 50000).round(2)

    # ── Card Brand ──
    card_brands = rng.choice(
        ["visa", "mastercard", "discover", "american express"],
        size=n_rows,
        p=[0.55, 0.25, 0.10, 0.10],
    )

    # ── Card Class ──
    card_classes = rng.choice(
        ["credit", "debit"],
        size=n_rows,
        p=[0.60, 0.40],
    )

    # ── Device Type ──
    device_types = rng.choice(
        ["mobile", "desktop", "tablet"],
        size=n_rows,
        p=[0.50, 0.38, 0.12],
    )

    # ── Email Domain ──
    email_domains = rng.choice(
        ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
         "protonmail.com", "anonymous.com", "icloud.com"],
        size=n_rows,
        p=[0.35, 0.20, 0.15, 0.10, 0.08, 0.02, 0.10],
    )

    # ── Temporal Features ──
    base_date = datetime(2026, 5, 1)
    timestamps = [
        base_date + timedelta(
            days=rng.randint(0, 28),
            hours=rng.randint(0, 23),
            minutes=rng.randint(0, 59),
        )
        for _ in range(n_rows)
    ]
    hours       = np.array([t.hour for t in timestamps])
    days        = np.array([t.weekday() for t in timestamps])

    # ── Risk Score (simulated) ──
    base_risk = np.where(labels == 1, rng.uniform(0.55, 0.98, n_rows),
                         rng.uniform(0.01, 0.40, n_rows))
    risk_scores = np.clip(base_risk, 0, 1).round(4)

    # ── Build DataFrame ──
    df = pd.DataFrame({
        "TransactionAmt": amounts,
        "card4":          card_brands,
        "card6":          card_classes,
        "DeviceType":     device_types,
        "P_emaildomain":  email_domains,
        "hour":           hours,
        "day_of_week":    days,
        "timestamp":      timestamps,
        "risk_score":     risk_scores,
        "isFraud":        labels.astype(int),
    })

    return df


def generate_mock_prediction_result(is_fraud=False):
    """Generate a mock prediction result dict for the light model."""
    rng = np.random.RandomState()
    if is_fraud:
        score = round(rng.uniform(0.65, 0.95), 4)
    else:
        score = round(rng.uniform(0.02, 0.30), 4)

    return {
        "risk_score":  score,
        "risk_level":  "HIGH RISK" if score > 0.5 else "LOW RISK",
        "decision":    "FRAUD" if score > 0.5 else "SAFE",
        "is_fraud":    score > 0.5,
        "xgb_score":   round(score + rng.uniform(-0.05, 0.05), 4),
        "lgbm_score":  round(score + rng.uniform(-0.05, 0.05), 4),
        "xgb_l_score": round(score + rng.uniform(-0.05, 0.05), 4),
        "lgbm_l_score": round(score + rng.uniform(-0.05, 0.05), 4),
        "top_factors": [
            "✅ No major risk factors detected"
        ] if not is_fraud else [
            "💰 High transaction amount",
            "📱 Mobile device (higher risk)",
            "🌙 Unusual time (late night)",
        ],
        "threshold": 0.50,
    }


def generate_temporal_heatmap_data(seed=42):
    """Generate mock heatmap data: days x hours fraud counts."""
    rng = np.random.RandomState(seed)
    days  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = list(range(24))

    # Base pattern: more fraud at night (0-5) and rush hours (8-9, 17-18)
    data = np.zeros((7, 24))
    for d in range(7):
        for h in range(24):
            base = 2
            if h < 6:            # Late night
                base = 12 + rng.randint(0, 8)
            elif h in [8, 9]:    # Morning rush
                base = 8 + rng.randint(0, 5)
            elif h in [17, 18]:  # Evening rush
                base = 9 + rng.randint(0, 6)
            elif h >= 22:        # Late evening
                base = 7 + rng.randint(0, 4)
            else:
                base = 2 + rng.randint(0, 3)
            # Weekend slightly different
            if d >= 5:
                base = int(base * 1.3)
            data[d][h] = base

    return data, days, hours
