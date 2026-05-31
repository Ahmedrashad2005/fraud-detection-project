# inspect_features.py

import pandas as pd
from features.build_features import build_features

sample = pd.DataFrame([
    {
        "TransactionAmt": 1000,
        "card4": "visa",
        "card6": "debit",
        "DeviceType": "desktop",
        "P_emaildomain": "gmail.com",
        "dist1": 50,
        "ProductCD": "W",
        "hour": 14,
    }
])

print("=" * 60)
print("RAW COLUMNS")
print("=" * 60)
print(sample.columns.tolist())

df = build_features(sample)

print("\n" + "=" * 60)
print("FEATURE COLUMNS")
print("=" * 60)

for i, col in enumerate(sorted(df.columns), 1):
    print(f"{i:3d}. {col}")

print("\nTotal Features:", len(df.columns))