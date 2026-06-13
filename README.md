# FraudGuard AI — Credit Card Fraud Detection

End-to-end fraud detection on IEEE-CIS-style transaction data: **heavy ensemble** (XGBoost + LightGBM + Isolation Forest) for batch scoring, **light models** for real-time forms, Streamlit dashboard, and FastAPI.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Place Kaggle CSVs under `data/raw/`:

- `train_transaction.csv`, `train_identity.csv`
- `test_transaction.csv`, `test_identity.csv` (optional)

### Train models

```bash
python models/train.py
# or full pipeline:
python -m pipeline.pipeline --step all
```

### Dashboard

```bash
streamlit run dashboard/app.py
```

### API

```bash
uvicorn app.main:app --reload --port 8000
```

- `GET /health` — artifact status  
- `POST /predict` — single transaction  
- `POST /predict/explain` — prediction + SHAP factors  
- `POST /predict/batch` — upload CSV/XLSX  
- `GET /audit/recent` — SQLite prediction log  

### Tests

```bash
pytest tests/ -q
python test_pipeline.py
```

## Architecture

| Mode | Models | Use case |
|------|--------|----------|
| Real-time | `xgb_light` + `lgbm_light` | Manual form, API `/predict` |
| Batch | Heavy ensemble + ISO | CSV upload, `/predict/batch` |

Artifacts live in `artifacts/models/` and `artifacts/preprocessing/`.

## New features (v1.1)

- Risk signal features (`amt_x_distance`, suspicious email domain, …) — **retrain** to include in `manual_features.pkl`
- Heuristic risk overlay on real-time scores (no retrain required)
- SHAP explanations in dashboard + `/predict/explain`
- Data drift monitoring vs `reference_stats.pkl` (saved on train)
- SQLite audit log (`artifacts/fraud_detection.db`)
- Batch CSV export from dashboard

## Retrain after feature changes

```bash
python models/train.py
python -m pipeline.pipeline --step test
```

## Project layout

```
config/          paths, hyperparameters
data/            load_raw_data
features/        build_features, preprocess
models/          train, predict, evaluate
dashboard/       Streamlit UI
app/             FastAPI
services/        data_loader, explain, audit, batch_io
mlops/           drift, optional MLflow
pipeline/        train → evaluate → smoke test
```

## License

Portfolio / educational use.
