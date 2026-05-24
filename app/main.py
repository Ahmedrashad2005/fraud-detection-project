from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from models.predict import predict

app = FastAPI(
    title="Fraud Detection API",
    version="1.0"
)



# ============================================================
# Request Schema
# ============================================================

class TransactionInput(BaseModel):
    TransactionAmt: float

    ProductCD: Optional[str] = "W"

    card4: Optional[str] = "visa"
    card6: Optional[str] = "debit"

    P_emaildomain: Optional[str] = "gmail.com"

    DeviceType: Optional[str] = "desktop"

    dist1: Optional[float] = 0

    hour: Optional[int] = 12


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Fraud Detection API Running",
        "status": "OK"
    }


# ============================================================
# Predict Endpoint
# ============================================================

@app.post("/predict")
def predict_transaction(data: TransactionInput):

    # Convert request to dict
    user_input = data.dict()

    # Run prediction
    result = predict(user_input)

    return result