# features/build_features.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

REF_DATE = datetime(2017, 11, 30)


# ================================================================
# Time Features
# ================================================================
def add_time_features(df: pd.DataFrame) -> pd.DataFrame:

    if 'TransactionDT' not in df.columns:
        return df

    dt = df['TransactionDT'].apply(
        lambda x: REF_DATE + timedelta(seconds=x)
    )

    df['hour']         = dt.dt.hour
    df['day_of_week']  = dt.dt.dayofweek
    df['day_of_month'] = dt.dt.day
    df['week']         = dt.dt.isocalendar().week.astype(int)
    df['is_night']     = (df['hour'] < 6).astype(int)
    df['is_morning']   = ((df['hour'] >= 6)  & (df['hour'] < 12)).astype(int)
    df['is_afternoon'] = ((df['hour'] >= 12) & (df['hour'] < 18)).astype(int)
    df['is_evening']   = (df['hour'] >= 18).astype(int)
    df['is_weekend']   = (df['day_of_week'] >= 5).astype(int)
    df['is_rush_hour'] = (df['hour'].isin([8, 9, 17, 18])).astype(int)
    df['hour_sin']     = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos']     = np.cos(2 * np.pi * df['hour'] / 24)
    df['dow_sin']      = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['dow_cos']      = np.cos(2 * np.pi * df['day_of_week'] / 7)

    print("✅ Time features built")
    return df


# ================================================================
# Amount Features
# ================================================================
def add_amount_features(df: pd.DataFrame) -> pd.DataFrame:

    if 'TransactionAmt' not in df.columns:
        return df

    amt = df['TransactionAmt']

    df['amount_log']      = np.log1p(amt)
    df['amount_sqrt']     = np.sqrt(amt)
    df['is_high_amount']  = (amt > 1000).astype(int)
    df['is_low_amount']   = (amt < 10).astype(int)
    df['is_round_number'] = (amt % 100 == 0).astype(int)
    df['amount_cents']    = amt % 1
    df['has_no_cents']    = (df['amount_cents'] == 0).astype(int)
    df['amount_category'] = pd.cut(
        amt,
        bins=[0, 50, 200, 1000, float('inf')],
        labels=[0, 1, 2, 3]
    ).astype(float)

    print("✅ Amount features built")
    return df


# ================================================================
# Email Features (on raw strings)
# ================================================================
def add_email_features(df: pd.DataFrame) -> pd.DataFrame:

    if 'P_emaildomain' not in df.columns:
        return df

    free_emails  = ['gmail.com', 'yahoo.com',
                    'hotmail.com', 'outlook.com']
    risky_emails = ['anonymous.com', 'guerrillamail.com',
                    'temp-mail.org']

    df['is_free_email']  = df['P_emaildomain']\
                            .isin(free_emails).astype(int)
    df['is_risky_email'] = df['P_emaildomain']\
                            .isin(risky_emails).astype(int)

    # ✅ بعد preprocess بتبقى Unknown مش NaN
    df['email_missing']  = df['P_emaildomain']\
                            .isin(['Unknown', None, np.nan])\
                            .astype(int)

    print("✅ Email features built")
    return df


# ================================================================
# Card Features (on raw strings)
# ================================================================
def add_card_features(df: pd.DataFrame) -> pd.DataFrame:
    # خريطة تدعم الأسماء والنصوص وكذلك الأرقام المقابلة ليها لو معمل لها Encoding
    card_risk_map = {
        'visa': 0.018, 1: 0.018, 0: 0.018, # أضفنا الأرقام المقابلة المتوقعة
        'mastercard': 0.031, 2: 0.031,
        'american express': 0.052, 3: 0.052,
        'discover': 0.078, 4: 0.078,
    }

    if 'card4' in df.columns:
        df['card_risk_score'] = df['card4'].map(card_risk_map).fillna(0.04)
        # التشيك يقبل النص أو الرقم المقابل ليه في عينة الداتا
        df['is_discover']     = df['card4'].isin(['discover', 4, 4.0]).astype(int)
        df['is_amex']         = df['card4'].isin(['american express', 3, 3.0]).astype(int)
        df['is_visa']         = df['card4'].isin(['visa', 1, 1.0, 0, 0.0]).astype(int)
        df['is_mastercard']   = df['card4'].isin(['mastercard', 2, 2.0]).astype(int)

        print(f"  card4 sample    : {df['card4'].unique()[:5].tolist()}")
        print(f"  is_discover sum : {df['is_discover'].sum()}")

    if 'card6' in df.columns:
        # دعم النصوص والأرقام الظاهرة في الـ sample
        df['is_credit'] = df['card6'].isin(['credit', 1, 1.0]).astype(int)
        df['is_debit']  = df['card6'].isin(['debit', 2, 2.0]).astype(int)

        print(f"  card6 sample    : {df['card6'].unique()[:5].tolist()}")
        print(f"  is_credit sum   : {df['is_credit'].sum()}")

    print("✅ Card features built")
    return df


# ================================================================
# Device Features (on raw strings)
# ================================================================
def add_device_features(df: pd.DataFrame) -> pd.DataFrame:
    if 'DeviceType' not in df.columns:
        return df

    device_risk = {
        'mobile':  0.062, 1: 0.062,
        'desktop': 0.031, 2: 0.031,
    }

    df['is_mobile']         = df['DeviceType'].isin(['mobile', 1, 1.0]).astype(int)
    df['is_desktop']        = df['DeviceType'].isin(['desktop', 2, 2.0]).astype(int)
    df['device_risk_score'] = df['DeviceType'].map(device_risk).fillna(0.04)
    df['device_missing']    = df['DeviceType'].isin(['Unknown', None, np.nan, 0, 0.0]).astype(int)

    print(f"  DeviceType sample : {df['DeviceType'].unique()[:5].tolist()}")
    print(f"  is_mobile sum     : {df['is_mobile'].sum()}")

    print("✅ Device features built")
    return df


# ================================================================
# Distance Features
# ================================================================
def add_distance_features(df: pd.DataFrame) -> pd.DataFrame:

    if 'dist1' not in df.columns:
        return df

    df['dist1_log']       = np.log1p(df['dist1'].fillna(0))
    df['dist1_missing']   = df['dist1'].isnull().astype(int)
    df['is_far_distance'] = (df['dist1'] > 500).astype(int)

    print("✅ Distance features built")
    return df


# ================================================================
# Cross Features
# ================================================================
def add_cross_features(df: pd.DataFrame) -> pd.DataFrame:

    if 'is_mobile' in df.columns and 'is_high_amount' in df.columns:
        df['mobile_x_high_amount'] = (
            df['is_mobile'] * df['is_high_amount']
        )

    if 'is_mobile' in df.columns and 'is_night' in df.columns:
        df['mobile_x_night'] = (
            df['is_mobile'] * df['is_night']
        )

    if 'is_discover' in df.columns and 'is_night' in df.columns:
        df['discover_x_night'] = (
            df['is_discover'] * df['is_night']
        )

    if 'is_round_number' in df.columns and 'is_high_amount' in df.columns:
        df['round_x_high'] = (
            df['is_round_number'] * df['is_high_amount']
        )

    if 'is_risky_email' in df.columns and 'is_high_amount' in df.columns:
        df['risky_email_x_amount'] = (
            df['is_risky_email'] * df['is_high_amount']
        )

    print("✅ Cross features built")
    return df


# ================================================================
# Composite Risk Score
# ================================================================
def add_composite_risk(df: pd.DataFrame) -> pd.DataFrame:

    df['composite_risk'] = (
        df.get('device_risk_score', pd.Series(0, index=df.index)) * 0.25 +
        df.get('card_risk_score',   pd.Series(0, index=df.index)) * 0.25 +
        df.get('is_night',          pd.Series(0, index=df.index)) * 0.20 +
        df.get('is_high_amount',    pd.Series(0, index=df.index)) * 0.15 +
        df.get('is_risky_email',    pd.Series(0, index=df.index)) * 0.10 +
        df.get('is_far_distance',   pd.Series(0, index=df.index)) * 0.05
    )

    print("✅ Composite risk built")
    return df


# ================================================================
# Full Pipeline
# ================================================================
def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full feature engineering pipeline.
    Must run BEFORE preprocessing (on raw string values).
    """
    print("\n" + "="*50)
    print("FEATURE ENGINEERING")
    print("="*50)

    cols_before = df.shape[1]

    # ✅ الترتيب مهم جداً
    df = df.copy()
    df = add_time_features(df)
    df = add_amount_features(df)
    df = add_email_features(df)    # ← على raw strings
    df = add_card_features(df)     # ← على raw strings
    df = add_device_features(df)   # ← على raw strings
    df = add_distance_features(df)
    df = add_cross_features(df)
    df = add_composite_risk(df)

    cols_after = df.shape[1]

    print(f"📈 Features added: {cols_after - cols_before}")
    print(f"Total columns: {cols_after}")
    print("="*50)

    return df


# ================================================================
# Run
# ================================================================
if __name__ == "__main__":
    from data.load_data import load_raw_data
    from features.preprocess import preprocess_train

    df = load_raw_data()

    # ✅ Features first
    df = build_features(df)

    # Debug
    print("\n--- Debug ---")
    for col in ['is_discover', 'is_mobile', 'is_credit',
                'is_risky_email', 'is_night']:
        if col in df.columns:
            print(f"{col}: {df[col].sum():,} positive values")

    # ✅ Then preprocess
    df = preprocess_train(df)
    print(f"\nFinal shape: {df.shape}")