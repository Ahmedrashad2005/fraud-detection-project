"""
Optional MLflow experiment tracking.
Enable with: MLFLOW_TRACKING=1 python models/train.py
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator

from config.settings import MLFLOW_EXP_NAME


@contextmanager
def mlflow_run(run_name: str = "train") -> Iterator[Any]:
    if os.getenv("MLFLOW_TRACKING", "").lower() not in {"1", "true", "yes"}:
        yield None
        return

    try:
        import mlflow

        mlflow.set_experiment(MLFLOW_EXP_NAME)
        with mlflow.start_run(run_name=run_name) as run:
            yield run
    except Exception:
        yield None


def log_metrics(metrics: dict[str, float]) -> None:
    if os.getenv("MLFLOW_TRACKING", "").lower() not in {"1", "true", "yes"}:
        return
    try:
        import mlflow

        for key, value in metrics.items():
            mlflow.log_metric(key, float(value))
    except Exception:
        pass
