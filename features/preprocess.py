# features/preprocess.py

import pandas as pd
import numpy as np
import joblib

from config.paths import (
    ARTIFACTS_DIR,
    PREPROCESS_DIR
)

DROP_COLS = ["TransactionID", "TransactionDT"]

# ================================================================
# Paths
# ================================================================

ENCODERS_PATH = PREPROCESS_DIR / "encoders.pkl"
MEDIANS_PATH  = PREPROCESS_DIR / "medians.pkl"
COLUMNS_PATH  = PREPROCESS_DIR / "feature_columns.pkl"
DROPPED_PATH  = PREPROCESS_DIR / "dropped_cols.pkl"

# ================================================================
# Basic Cleaning
# ================================================================

def drop_useless_cols(df):
    cols = [
        c for c in DROP_COLS
        if c in df.columns
    ]
    df = df.drop(columns=cols)
    print(f"✅ Dropped {len(cols)} useless columns")
    return df


def drop_high_missing(df, threshold=0.90):
    missing_rate = df.isnull().mean()
    high_missing = (
        missing_rate[missing_rate > threshold]
        .index
        .tolist()
    )
    df = df.drop(columns=high_missing)
    print(f"✅ Dropped {len(high_missing)} high-missing columns")
    return df, high_missing

# ================================================================
# Missing Values
# ================================================================

def fill_missing_train(df):
    medians = {}

    # ✅ أسرع بكتير - بنحسب كل الـ medians مرة واحدة
    num_cols = df.select_dtypes(include=np.number).columns
    medians  = df[num_cols].median().to_dict()
    df[num_cols] = df[num_cols].fillna(value=medians)

    # Categorical
    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        df[col] = df[col].fillna("Unknown")

    print("✅ Missing filled (train)")
    return df, medians


def fill_missing_inference(df, medians):
    # 1. تعويض قيم الميديان للأرقام من الـ Artifacts
    for col, med in medians.items():
        if col in df.columns:
            df[col] = df[col].fillna(med)

    # 2. تعويض المفقود للنصوص بـ Unknown
    object_cols = df.select_dtypes(include="object").columns
    for col in object_cols:
        df[col] = df[col].fillna("Unknown")

    print("✅ Missing filled (inference)")
    return df

# ================================================================
# Encoding
# ================================================================

def encode_train(df):
    encoders = {}
    object_cols = df.select_dtypes(include="object").columns

    for col in object_cols:
        # استخراج القيم الفريدة الحقيقية بدون تحويل العمود كاملاً لنصوص مشوهة
        uniques = df[col].dropna().unique().tolist()
        
        # نضمن إن كلمة Unknown متسجلة في الـ Mapping برقم واضح
        if "Unknown" not in uniques:
            uniques.append("Unknown")

        mapping = {val: idx for idx, val in enumerate(uniques)}
        
        # عمل الـ Map والتعويض عن أي Missing بالـ Index بتاع Unknown
        df[col] = df[col].map(mapping).fillna(mapping["Unknown"]).astype(int)
        encoders[col] = mapping

    print(f"✅ Encoded {len(encoders)} columns (train)")
    return df, encoders


def encode_inference(df, encoders):
    for col, mapping in encoders.items():
        if col in df.columns:
            # نجيب الـ Index الافتراضي لـ Unknown، ولو مش موجود نخلي الافتراضي 0 أو -1
            unknown_idx = mapping.get("Unknown", next(iter(mapping.values())))
            
            # عمل المابينج، ولو ظهرت قيمة جديدة أو مفقودة تروح أوتوماتيك للـ Unknown
            df[col] = df[col].map(mapping).fillna(unknown_idx).astype(int)

    print("✅ Encoded (inference)")
    return df

# ================================================================
# Memory Optimization
# ================================================================

def reduce_memory(df):
    before = df.memory_usage().sum() / 1e6

    # ✅ عمود عمود بـ astype (سريع + مش بياكل ميموري زيادة)
    for col in df.select_dtypes(include=["float64"]).columns:
        df[col] = df[col].astype(np.float32)

    for col in df.select_dtypes(include=["int64"]).columns:
        df[col] = df[col].astype(np.int32)

    after = df.memory_usage().sum() / 1e6
    print(f"✅ Memory: {before:.1f} → {after:.1f} MB")
    return df

# ================================================================
# preprocess_train
# ================================================================
def preprocess_train(df):
    print("\n" + "="*60)
    print("TRAIN PREPROCESSING")
    print("="*60)

    PREPROCESS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Drop useless
    df = drop_useless_cols(df)

    # 2. Drop high missing
    df, dropped_cols = drop_high_missing(df)
    
    # 🌟 خطوة أمان 1: قلل الميموري فوراً بعد الحذف لتفريغ الرام
    df = reduce_memory(df)

    # 3. Fill missing
    df, medians = fill_missing_train(df)

    # 4. Encode
    df, encoders = encode_train(df)

    # 5. Reduce memory النهائي
    df = reduce_memory(df)

    # 6. Save artifacts
    joblib.dump(encoders, ENCODERS_PATH)
    joblib.dump(medians, MEDIANS_PATH)
    joblib.dump(df.columns.tolist(), COLUMNS_PATH)
    joblib.dump(dropped_cols, DROPPED_PATH)

    print("\n✅ Artifacts Saved")
    print(f"Final shape: {df.shape}")
    print("="*60)

    return df

# ================================================================
# preprocess_inference
# ================================================================

def preprocess_inference(df):
    print("\n" + "="*60)
    print("INFERENCE PREPROCESSING")
    print("="*60)

    missing = [
        str(path) for path in (ENCODERS_PATH, MEDIANS_PATH, COLUMNS_PATH)
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError(
            "Missing preprocessing artifacts: " + ", ".join(missing)
        )

    # Load artifacts
    encoders = joblib.load(ENCODERS_PATH)
    medians  = joblib.load(MEDIANS_PATH)
    columns  = joblib.load(COLUMNS_PATH)

    # 1. Drop useless cols
    df = drop_useless_cols(df)

    # 2. Fill missing
    df = fill_missing_inference(df, medians)

    # 3. Encode
    df = encode_inference(df, encoders)

    # 4. Align columns with the training schema.
    # Missing numeric training columns should look like training medians, not
    # literal zeroes, otherwise single-row dashboard inference becomes sparse
    # and insensitive to user inputs.
    fill_values = {col: medians.get(col, 0) for col in columns}
    df = df.reindex(columns=columns)
    df = df.fillna(value=fill_values)

    # 5. Reduce memory
    df = reduce_memory(df)

    print(f"Final shape: {df.shape}")
    print("="*60)

    return df

# ================================================================
# Test Run
# ================================================================

if __name__ == "__main__":
    from data.load_data import load_raw_data

    print("\n🚀 TESTING PREPROCESS")

    # Train preprocess اختبار
    df = load_raw_data()
    df = preprocess_train(df)
    print("\n✅ preprocess_train DONE")

    # Inference preprocess اختبار
    df2 = load_raw_data()
    df2 = preprocess_inference(df2)
    print("\n✅ preprocess_inference DONE")
