import sys
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from models.predict import MODELS, build_features, preprocess_inference

cases = {
    "Case 1": {
        "TransactionAmt": 35.0, "ProductCD": "W", "card4": "visa",
        "card6": "debit", "P_emaildomain": "gmail.com",
        "DeviceType": "desktop", "dist1": 0.0, "hour": 12,
        "TransactionDT": 43200,
    },
    "Case 2": {
        "TransactionAmt": 1000.0, "ProductCD": "W", "card4": "visa",
        "card6": "debit", "P_emaildomain": "gmail.com",
        "DeviceType": "desktop", "dist1": 0.0, "hour": 12,
        "TransactionDT": 43200,
    },
    "Case 3": {
        "TransactionAmt": 10000.0, "ProductCD": "W", "card4": "visa",
        "card6": "debit", "P_emaildomain": "gmail.com",
        "DeviceType": "desktop", "dist1": 0.0, "hour": 0,
        "TransactionDT": 1800,
    },
    "Case 4": {
        "TransactionAmt": 100000.0, "ProductCD": "W", "card4": "american express",
        "card6": "debit", "P_emaildomain": "gmail.com",
        "DeviceType": "desktop", "dist1": 0.0, "hour": 0,
        "TransactionDT": 1800,
    },
    "Case 5": {
        "TransactionAmt": 100000.0, "ProductCD": "W", "card4": "american express",
        "card6": "debit", "P_emaildomain": "gmail.com",
        "DeviceType": "desktop", "dist1": 500.0, "hour": 0,
        "TransactionDT": 1800,
    },
}

# Load Models
(_, _, _, _, _, _, top35, _) = MODELS

print("TOP35 FEATURES:", top35)
print("\n" + "="*80)
print("1. EXACT 35-FEATURE VECTORS")
print("="*80)

vectors = {}
for name, user_input in cases.items():
    df = pd.DataFrame([user_input])
    df = build_features(df)
    df = preprocess_inference(df)
    df = df.reindex(columns=top35, fill_value=0)
    vectors[name] = df.iloc[0].to_dict()
    
    print(f"\n{name} Feature Vector:")
    non_zero_count = 0
    for f in top35:
        val = vectors[name][f]
        print(f"  {f:25}: {val}")
        if val != 0:
            non_zero_count += 1
    print(f"Total non-zero features: {non_zero_count} / 35")

print("\n" + "="*80)
print("2. FEATURES THAT DIFFER BETWEEN CASES")
print("="*80)
features_diff = []
for f in top35:
    vals = [vectors[case][f] for case in cases]
    if len(set(vals)) > 1:
        features_diff.append(f)
        print(f"  {f:25}: { {case: vectors[case][f] for case in cases} }")

print("\n" + "="*80)
print("3. SPECIFIC VALUE CHECK")
print("="*80)
target_features = [
    "amount_sqrt", "amount_category", "card6", "is_credit", 
    "is_debit", "is_morning", "iso_score", "device_risk_score"
]

for name, user_input in cases.items():
    print(f"\n{name}:")
    df = pd.DataFrame([user_input])
    df = build_features(df)
    df = preprocess_inference(df)
    for tf in target_features:
        val = df.iloc[0].get(tf, "NOT IN DF")
        print(f"  {tf:25}: {val}")

print("\n" + "="*80)
print("4. QUESTIONS ANALYSIS")
print("="*80)

# Check card4 (american express)
print("\nVerifying if 'american express' changes any top35 feature:")
df_c3 = pd.DataFrame([cases["Case 3"]])
df_c3 = build_features(df_c3)
df_c3 = preprocess_inference(df_c3).reindex(columns=top35, fill_value=0).iloc[0]

df_c4 = pd.DataFrame([cases["Case 4"]])
df_c4 = build_features(df_c4)
df_c4 = preprocess_inference(df_c4).reindex(columns=top35, fill_value=0).iloc[0]

c3_c4_diff = []
for f in top35:
    if df_c3[f] != df_c4[f]:
        c3_c4_diff.append((f, df_c3[f], df_c4[f]))
if c3_c4_diff:
    for f, v3, v4 in c3_c4_diff:
        print(f"  Feature '{f}' changed from {v3} (Visa) to {v4} (Amex)")
else:
    print("  NO top35 features changed between Case 3 and Case 4 due to card4/Amex!")

# Check distance=500
print("\nVerifying if distance=500 changes any top35 feature:")
df_c5 = pd.DataFrame([cases["Case 5"]])
df_c5 = build_features(df_c5)
df_c5 = preprocess_inference(df_c5).reindex(columns=top35, fill_value=0).iloc[0]

c4_c5_diff = []
for f in top35:
    if df_c4[f] != df_c5[f]:
        c4_c5_diff.append((f, df_c4[f], df_c5[f]))
if c4_c5_diff:
    for f, v4, v5 in c4_c5_diff:
        print(f"  Feature '{f}' changed from {v4} (dist=0) to {v5} (dist=500)")
else:
    print("  NO top35 features changed between Case 4 and Case 5 due to distance=500!")

# Check hour=00:30
print("\nVerifying if hour=00:30 (compared to hour=12) changes any top35 feature:")
df_c2 = pd.DataFrame([cases["Case 2"]])
df_c2 = build_features(df_c2)
df_c2 = preprocess_inference(df_c2).reindex(columns=top35, fill_value=0).iloc[0]

c2_c3_diff = []
for f in top35:
    # Note: Case 2 and 3 differ by hour (12 to 00:30) and amount (1,000 to 10,000). Let's construct a case with same amt but different hour
    pass

user_input_12 = cases["Case 3"].copy()
user_input_12["hour"] = 12
user_input_12["TransactionDT"] = 43200
df_12 = pd.DataFrame([user_input_12])
df_12 = build_features(df_12)
df_12 = preprocess_inference(df_12).reindex(columns=top35, fill_value=0).iloc[0]

df_00 = pd.DataFrame([cases["Case 3"]])
df_00 = build_features(df_00)
df_00 = preprocess_inference(df_00).reindex(columns=top35, fill_value=0).iloc[0]

h_diff = []
for f in top35:
    if df_12[f] != df_00[f]:
        h_diff.append((f, df_12[f], df_00[f]))
if h_diff:
    for f, v12, v00 in h_diff:
        print(f"  Feature '{f}' changed from {v12} (hour=12) to {v00} (hour=00:30)")
else:
    print("  NO top35 features changed due to hour=00:30!")
