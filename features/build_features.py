import pandas as pd
import numpy as np
from datetime import datetime, timedelta

REF_DATE = datetime(2017, 11, 30)


# ================================================================
# Time Features
# ================================================================
def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    if 'TransactionDT' not in df.columns:
        if 'hour' in df.columns:
            hour = pd.to_numeric(df['hour'], errors='coerce').fillna(12).astype(int).clip(0, 23)
            df['hour'] = hour
            df['is_night']     = (hour < 6).astype(int)
            df['is_morning']   = ((hour >= 6)  & (hour < 12)).astype(int)
            df['is_afternoon'] = ((hour >= 12) & (hour < 18)).astype(int)
            df['is_evening']   = (hour >= 18).astype(int)
            df['is_rush_hour'] = (hour.isin([8, 9, 17, 18])).astype(int)
            df['hour_sin']     = np.sin(2 * np.pi * hour / 24)
            df['hour_cos']     = np.cos(2 * np.pi * hour / 24)
            print("✅ Time features built from hour")
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
    
    # ✅ آمن جداً ويمنع الـ NaN للمبالغ الصفريّة
    df['amount_category'] = pd.cut(
        amt,
        bins=[-1, 50, 200, 1000, float('inf')],
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

    free_emails  = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    df['is_free_email']  = df['P_emaildomain'].isin(free_emails).astype(int)
    
    # ✅ الاستخدام الاحترافي لـ .isna() لضمان لقط الـ NaN
    df['email_missing']  = (
        df['P_emaildomain'].isna() | 
        (df['P_emaildomain'] == 'Unknown')
    ).astype(int)

    print("✅ Email features built")
    return df


# ================================================================
# Card Features (on raw strings)
# ================================================================
def add_card_features(df: pd.DataFrame) -> pd.DataFrame:
    if 'card4' in df.columns:
        df['is_discover']     = df['card4'].isin(['discover', 4, 4.0]).astype(int)
        df['is_amex']         = df['card4'].isin(['american express', 3, 3.0]).astype(int)
        df['is_visa']         = df['card4'].isin(['visa', 1, 1.0, 0, 0.0]).astype(int)
        df['is_mastercard']   = df['card4'].isin(['mastercard', 2, 2.0]).astype(int)

        print(f"  card4 sample    : {df['card4'].unique()[:5].tolist()}")
        print(f"  is_discover sum : {df['is_discover'].sum()}")

    if 'card6' in df.columns:
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

    df['is_mobile']         = df['DeviceType'].isin(['mobile', 1, 1.0]).astype(int)
    df['is_desktop']        = df['DeviceType'].isin(['desktop', 2, 2.0]).astype(int)
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
        df['mobile_x_high_amount'] = df['is_mobile'] * df['is_high_amount']

    if 'is_mobile' in df.columns and 'is_night' in df.columns:
        df['mobile_x_night'] = df['is_mobile'] * df['is_night']

    if 'is_discover' in df.columns and 'is_night' in df.columns:
        df['discover_x_night'] = df['is_discover'] * df['is_night']

    if 'is_round_number' in df.columns and 'is_high_amount' in df.columns:
        df['round_x_high'] = df['is_round_number'] * df['is_high_amount']

    print("✅ Cross features built")
    return df


# ================================================================
# Risk Signal Features (velocity / domain / geo)
# ================================================================
SUSPICIOUS_DOMAINS = {
    "anonymous.com", "protonmail.com", "mail.ru", "yandex.ru",
    "guerrillamail.com", "tempmail.com", "10minutemail.com",
}


def add_risk_signal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Heuristic risk signals usable after retrain (manual + heavy feature sets)."""
    if "TransactionAmt" in df.columns and "dist1" in df.columns:
        amt = df["TransactionAmt"].fillna(0)
        dist = df["dist1"].fillna(0)
        df["amt_x_distance"] = amt * np.log1p(dist + 1)
        df["geo_amount_risk"] = (
            (dist > 500).astype(int) * (amt > 500).astype(int)
        )

    if "P_emaildomain" in df.columns:
        domain = df["P_emaildomain"].astype(str).str.lower()
        df["is_suspicious_domain"] = domain.isin(SUSPICIOUS_DOMAINS).astype(int)
        df["domain_length"] = domain.str.len().clip(upper=60)

    if "hour" in df.columns and "is_high_amount" in df.columns and "is_night" in df.columns:
        df["night_x_high_amount"] = df["is_night"] * df["is_high_amount"]

    if "TransactionAmt" in df.columns and "hour" in df.columns:
        df["amt_hour_risk"] = (
            df["TransactionAmt"].fillna(0)
            * df["hour"].isin([0, 1, 2, 3, 4, 5]).astype(int)
        )

    print("✅ Risk signal features built")
    return df


# ================================================================
# Full Pipeline (تم حذف الـ composite_risk)
# ================================================================
def build_features(df: pd.DataFrame) -> pd.DataFrame:
    print("\n" + "="*50)
    print("FEATURE ENGINEERING")
    print("="*50)

    cols_before = df.shape[1]

    df = df.copy()
    df = add_time_features(df)
    df = add_amount_features(df)
    df = add_email_features(df)
    df = add_card_features(df)
    df = add_device_features(df)
    df = add_distance_features(df)
    df = add_cross_features(df)
    df = add_risk_signal_features(df)

    cols_after = df.shape[1]

    print(f"📈 Features added: {cols_after - cols_before}")
    print(f"Total columns: {cols_after}")
    print("="*50)

    return df


if __name__ == "__main__":
    from data.load_data import load_raw_data
    from features.preprocess import preprocess_train

    df = load_raw_data()
    df = build_features(df)

    print("\n--- Debug ---")
    for col in ['is_discover', 'is_mobile', 'is_credit', 'is_night']:
        if col in df.columns:
            print(f"{col}: {df[col].sum():,} positive values")

    df = preprocess_train(df)
    print(f"\nFinal shape: {df.shape}")
