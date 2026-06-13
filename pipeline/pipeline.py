"""
End-to-end pipeline: train → evaluate → verify artifacts.
Run: python -m pipeline.pipeline
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_train() -> None:
    from models.train import main
    main()


def run_evaluate() -> None:
    from models.evaluate import main
    main()


def run_smoke_tests() -> bool:
    from models.predict import MODELS, predict_light, predict_batch
    import pandas as pd

    if not MODELS.get("loaded"):
        print(f"❌ Models not loaded: {MODELS.get('error')}")
        return False

    sample = {
        "TransactionAmt": 120.0,
        "card4": "visa",
        "card6": "debit",
        "P_emaildomain": "gmail.com",
        "DeviceType": "desktop",
        "dist1": 12,
        "hour": 14,
        "ProductCD": "W",
    }
    light = predict_light(sample)
    if light.get("error"):
        print(f"❌ predict_light failed: {light['error']}")
        return False

    batch = predict_batch(pd.DataFrame([sample, {**sample, "TransactionAmt": 9000, "hour": 3}]))
    if "risk_score" not in batch.columns:
        print("❌ predict_batch missing risk_score")
        return False

    print("✅ Smoke tests passed")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Fraud detection ML pipeline")
    parser.add_argument(
        "--step",
        choices=["all", "train", "evaluate", "test"],
        default="test",
        help="Pipeline step to run",
    )
    args = parser.parse_args()

    if args.step in ("all", "train"):
        print("\n=== TRAIN ===\n")
        run_train()

    if args.step in ("all", "evaluate"):
        print("\n=== EVALUATE ===\n")
        run_evaluate()

    if args.step in ("all", "test"):
        print("\n=== SMOKE TESTS ===\n")
        ok = run_smoke_tests()
        if not ok:
            sys.exit(1)


if __name__ == "__main__":
    main()
