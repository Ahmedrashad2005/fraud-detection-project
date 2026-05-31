"""
Pre-Training Verification: Manual Feature List
===============================================
Prints the exact feature list that train_light() will use.
Does NOT load data or train models.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# ================================================================
# 1. Print the implementation
# ================================================================
print("=" * 60)
print("IMPLEMENTATION: get_manual_feature_columns()")
print("=" * 60)

import inspect
from models.train import get_manual_feature_columns
print(inspect.getsource(get_manual_feature_columns))

# ================================================================
# 2. Simulate with a sample row to see which features exist
# ================================================================
print("=" * 60)
print("SIMULATING FEATURE GENERATION")
print("=" * 60)

import pandas as pd
from features.build_features import build_features
from features.preprocess import preprocess_inference

sample = pd.DataFrame([{
    "TransactionAmt": 1000.0,
    "ProductCD": "W",
    "card4": "visa",
    "card6": "debit",
    "P_emaildomain": "gmail.com",
    "DeviceType": "desktop",
    "dist1": 50.0,
    "hour": 14,
    "TransactionDT": 50400,
}])

df = build_features(sample)
df = preprocess_inference(df)

# Now call get_manual_feature_columns with this processed dataframe
manual_features = get_manual_feature_columns(df)

# ================================================================
# 3. Results
# ================================================================
print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)

print(f"\nlen(manual_features) = {len(manual_features)}")
print(f"\nsorted(manual_features):")
for i, f in enumerate(sorted(manual_features), 1):
    print(f"  {i:2d}. {f}")

# ================================================================
# 4. Dashboard field mapping
# ================================================================
print("\n" + "=" * 60)
print("DASHBOARD FIELD → FEATURE MAPPING")
print("=" * 60)

field_map = {
    "TransactionAmt": ["TransactionAmt", "amount_log", "amount_sqrt", "amount_category"],
    "card4":          ["card4", "is_visa", "is_mastercard", "is_amex", "is_discover", "card_risk_score"],
    "card6":          ["card6", "is_credit", "is_debit"],
    "DeviceType":     ["DeviceType", "is_mobile", "device_risk_score"],
    "dist1":          ["dist1", "dist1_log", "is_far_distance"],
    "hour":           ["hour", "is_morning", "is_night"],
    "P_emaildomain":  ["P_emaildomain", "is_free_email", "is_risky_email", "email_missing"],
    "ProductCD":      ["ProductCD"],
}

for field, features in field_map.items():
    present = [f for f in features if f in manual_features]
    missing = [f for f in features if f not in manual_features]
    print(f"\n  {field}:")
    for f in present:
        print(f"    ✅ {f}")
    for f in missing:
        print(f"    ❌ {f} (NOT in X_train)")

# ================================================================
# 5. Verify NO IEEE-CIS columns leaked in
# ================================================================
print("\n" + "=" * 60)
print("IEEE-CIS LEAK CHECK")
print("=" * 60)

leaks = []
for f in manual_features:
    if f.startswith("V") and f[1:].isdigit():
        leaks.append(f)
    elif f.startswith("C") and f[1:].isdigit():
        leaks.append(f)
    elif f.startswith("D") and f[1:].isdigit():
        leaks.append(f)
    elif f.startswith("id_"):
        leaks.append(f)
    elif f in ["card1", "card2", "card3", "card5", "addr1", "addr2"]:
        leaks.append(f)
    elif f == "iso_score":
        leaks.append(f)

if leaks:
    print(f"  🔴 LEAKED IEEE-CIS columns found: {leaks}")
else:
    print("  🟢 CLEAN — No IEEE-CIS median-filled columns in manual_features")

# ================================================================
# 6. Coverage vs all_features
# ================================================================
print("\n" + "=" * 60)
print("COVERAGE")
print("=" * 60)

import joblib
from config.paths import PREPROCESS_DIR

all_features = joblib.load(PREPROCESS_DIR / "all_features.pkl")
print(f"  manual_features count : {len(manual_features)}")
print(f"  all_features count    : {len(all_features)}")
print(f"  percentage            : {len(manual_features)/len(all_features)*100:.1f}%")

print("\n" + "=" * 60)
print("DONE — Ready to train")
print("=" * 60)
