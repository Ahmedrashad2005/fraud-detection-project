"""
FraudGuard AI — Enterprise Credit Card Fraud Detection Dashboard
================================================================
Cybersecurity Command Center aesthetic.

Run:  streamlit run dashboard/app.py
"""

import sys
from datetime import time as dt_time
from pathlib import Path
import re

# ── Ensure project root is on sys.path ──
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

# ── Dashboard modules ──
from dashboard.styles.theme import inject_theme
from dashboard.components.sidebar import render_sidebar
from dashboard.components.kpi_cards import render_kpi_row
from dashboard.components.charts import (
    render_fraud_by_card_brand,
    render_device_distribution,
    render_temporal_heatmap,
    render_risk_gauge,
    render_model_drift_infrastructure,
)
from dashboard.components.alerts import (
    render_status_banner,
    render_footer,
)
from services.data_loader import (
    get_artifact_status,
    is_realtime_ready,
    load_evaluation_report,
    load_threshold as load_realtime_threshold,
    normalize_batch_input,
    predict_batch_transactions,
    predict_transaction,
    read_uploaded_table,
)
from components.alerts import render_artifact_status as render_realtime_artifact_status
from dashboard.services.mock_data import generate_mock_transactions
from dashboard.utils.helpers import (
    get_threshold_description,
    compute_batch_stats,
)


# ================================================================
# Page Config
# ================================================================
st.set_page_config(
    page_title="FraudGuard AI — Enterprise Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject theme CSS ──
st.markdown(inject_theme(), unsafe_allow_html=True)


# ================================================================
# Session State Initialization
# ================================================================
def init_session_state():
    """Initialize all session state variables."""
    initial_threshold = min(max(float(load_realtime_threshold() or 0.75), 0.05), 0.95)
    defaults = {
        "threshold":          initial_threshold,
        "uploaded_file_data": None,
        "batch_predictions":  None,
        "last_prediction":    None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()


# ================================================================
# Sidebar Navigation
# ================================================================
page = render_sidebar()


# ================================================================
# PAGE 1: Real-time Verification & Control
# ================================================================
def page_realtime():
    """Render Page 1: real-time transaction verification."""
    st.markdown("""
    <style>
        .rt-title { margin: 0 0 6px; color: #FFFFFF; font-size: 30px; font-weight: 850; letter-spacing: 0; }
        .rt-subtitle { margin: 0 0 22px; color: #BDC3C7; font-size: 13px; font-weight: 650; }
        .rt-card { min-height: 642px; padding: 22px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1); background: rgba(18, 18, 18, 0.48); }
        .rt-card-title { margin-bottom: 16px; color: #FFFFFF; font-size: 18px; font-weight: 850; }
        .rt-decision { min-height: 108px; display: grid; align-content: center; gap: 5px; padding: 18px; margin-top: 16px; border-radius: 8px; text-align: center; }
        .rt-decision strong { display: block; font-size: 24px; font-weight: 900; letter-spacing: 0; }
        .rt-decision span { color: #F8FAFC; font-size: 13px; font-weight: 800; }
        .rt-approved { border: 1px solid rgba(46, 204, 113, 0.72); background: linear-gradient(135deg, rgba(46, 204, 113, 0.18), rgba(46, 204, 113, 0.055)); color: #2ECC71; box-shadow: 0 0 32px rgba(46, 204, 113, 0.16); }
        .rt-blocked { border: 1px solid rgba(231, 76, 60, 0.72); background: linear-gradient(135deg, rgba(231, 76, 60, 0.18), rgba(231, 76, 60, 0.055)); color: #E74C3C; box-shadow: 0 0 32px rgba(231, 76, 60, 0.16); }
        .rt-score-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 14px; }
        .rt-score { min-height: 88px; padding: 14px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1); background: rgba(255, 255, 255, 0.035); }
        .rt-score label { display: block; color: #A8B3BD; font-size: 11px; font-weight: 800; text-transform: uppercase; }
        .rt-score strong { display: block; margin-top: 8px; color: #FFFFFF; font-family: "JetBrains Mono", monospace; font-size: 25px; line-height: 1.1; }
        .rt-status-card { padding: 16px; margin-top: 16px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1); background: rgba(255, 255, 255, 0.035); }
        .rt-status-line { display: flex; justify-content: space-between; gap: 12px; color: #D8DEE3; font-size: 12px; font-weight: 750; }
        .rt-status-line strong { color: #2ECC71; font-size: 11px; text-transform: uppercase; }
        .rt-status-line .offline { color: #F39C12; }
        @media (max-width: 760px) { .rt-score-grid { grid-template-columns: 1fr; } .rt-card { min-height: auto; } }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="fg-premium-panel">', unsafe_allow_html=True)
    st.markdown('<h1 class="rt-title">Real-time Verification</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="rt-subtitle">Manual transaction screening with ensemble inference and live risk controls.</p>',
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1.28, 1], gap="large")
    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    with left_col:
        st.markdown('<section class="rt-card">', unsafe_allow_html=True)
        st.markdown('<div class="rt-card-title">Transaction Verification Card</div>', unsafe_allow_html=True)

        amount = st.number_input(
            "Transaction Amount ($)",
            min_value=0.0,
            max_value=100000.0,
            value=35.00,
            step=None,
            format="%.2f",
        )
        email = st.text_input("Customer Email", value="customer@gmail.com")

        f1, f2 = st.columns(2)
        with f1:
            card_brand = st.selectbox(
                "Card Brand",
                ["visa", "mastercard", "american express", "discover"],
                index=0,
            )
            device_type = st.selectbox("Device Type", ["desktop", "mobile"], index=0)
        with f2:
            card_type = st.selectbox("Card Type", ["debit", "credit"], index=0)
            transaction_time = st.time_input("Transaction Time", value=dt_time(12, 0))

        distance = st.number_input(
            "Distance From Usual Location",
            min_value=0.0,
            max_value=10000.0,
            value=0.0,
            step=10.0,
            format="%.1f",
        )


        amount_valid = float(amount) >= 0
        email_valid = re.match(email_pattern, email.strip()) is not None
        analyze_disabled = not amount_valid or not email_valid or not is_realtime_ready()

        if not amount_valid:
            st.error("Amount must be greater than or equal to 0.")
        if not email_valid:
            st.error("Enter a valid email address.")
        if not is_realtime_ready():
            st.warning("Real-time inference is unavailable until required artifacts are online.")

        analyze_clicked = st.button(
            "Analyze Transaction",
            type="primary",
            use_container_width=True,
            disabled=analyze_disabled,
        )

        if analyze_clicked:
            domain = email.strip().split("@", 1)[1].lower()
            # Convert selected time to TransactionDT (seconds since midnight)
            selected_hour = transaction_time.hour
            selected_minute = transaction_time.minute
            transaction_dt_seconds = selected_hour * 3600 + selected_minute * 60
            user_input = {
                "TransactionAmt": float(amount),
                "ProductCD": "W",
                "card4": card_brand,
                "card6": card_type,
                "P_emaildomain": domain,
                "DeviceType": device_type,
                "dist1": float(distance),
                "TransactionDT": transaction_dt_seconds,
                "hour": selected_hour,
            }
            with st.spinner("Analyzing transaction..."):
                prediction = predict_transaction(
                    user_input,
                    threshold=float(st.session_state["threshold"]),
                    light_only=True,
                )
            st.session_state["last_prediction"] = prediction.data if prediction.ok else {"error": prediction.message}

        result = st.session_state.get("last_prediction")
        if isinstance(result, dict) and result.get("error"):
            st.error(result["error"])
        elif isinstance(result, dict):
            fraud_probability = float(result.get("fraud_probability", result.get("risk_score", 0.0)) or 0.0)
            risk_score = float(result.get("risk_score", fraud_probability) or 0.0)
            is_fraud = bool(result.get("is_fraud", result.get("decision") == "FRAUD"))
            state_class = "rt-blocked" if is_fraud else "rt-approved"
            state_title = "🔴 BLOCKED" if is_fraud else "🟢 APPROVED"
            state_subtitle = "High Fraud Risk" if is_fraud else "Safe Transaction"

            st.markdown(f"""
            <div class="rt-decision {state_class}">
                <strong>{state_title}</strong>
                <span>{state_subtitle}</span>
            </div>
            <div class="rt-score-grid">
                <div class="rt-score">
                    <label>Fraud Probability</label>
                    <strong>{fraud_probability * 100:.1f}%</strong>
                </div>
                <div class="rt-score">
                    <label>Risk Score</label>
                    <strong>{risk_score * 100:.1f}%</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.info("Enter transaction details and run analysis to display the decision.")

        st.markdown('</section>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<section class="rt-card">', unsafe_allow_html=True)
        st.markdown('<div class="rt-card-title">Risk Controls</div>', unsafe_allow_html=True)
        
        threshold = st.slider(
            "Classification Threshold",
            min_value=0.05,
            max_value=0.95,
            step=0.01,
            key="threshold",
        )
        st.markdown(
            f'<p class="fg-threshold-copy">{get_threshold_description(threshold)}</p>',
            unsafe_allow_html=True,
        )

        result = st.session_state.get("last_prediction")
        gauge_score = 0.0
        if isinstance(result, dict) and not result.get("error"):
            gauge_score = float(result.get("risk_score", 0.0) or 0.0)
        render_risk_gauge(gauge_score, threshold)

        status = get_artifact_status()
        backend_online = bool(status.get("inference_backend"))
        heavy_online = bool(status.get("xgb_heavy") and status.get("lgbm_heavy") and status.get("iso_forest"))
        light_online = bool(status.get("xgb_light") and status.get("lgbm_light") and status.get("top35_features"))
        st.markdown(f"""
        <div class="rt-status-card">
            <div class="rt-card-title">Model Status</div>
            <div class="rt-status-line">
                <span>Inference Backend</span>
                <strong class="{'' if backend_online else 'offline'}">{'Online' if backend_online else 'Offline'}</strong>
            </div>
            <div class="rt-status-line">
                <span>Heavy Ensemble</span>
                <strong class="{'' if heavy_online else 'offline'}">{'Ready' if heavy_online else 'Missing'}</strong>
            </div>
            <div class="rt-status-line">
                <span>Light Models</span>
                <strong class="{'' if light_online else 'offline'}">{'Ready' if light_online else 'Missing'}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        render_realtime_artifact_status(status)
        st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ================================================================
# PAGE 2: Executive Batch Dashboard
# ================================================================
def page_batch():
    """Render the executive batch processing and analytics page."""

    st.markdown("""
    <style>
        .batch-demo { margin: 12px 0 18px; padding: 13px 15px; border-radius: 8px; border: 1px solid rgba(243, 156, 18, 0.32); background: rgba(243, 156, 18, 0.08); color: #F8FAFC; font-size: 13px; font-weight: 700; }
        .batch-demo span { color: #F39C12; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

    hdr1, hdr2, hdr3 = st.columns([2.4, 1, 1])
    with hdr1:
        st.markdown("""
        <div class="bank-page-header">
            <div>
                <h2 class="bank-title">Executive Batch Dashboard</h2>
                <div class="bank-subtitle">
                    Bank-grade portfolio surveillance, transaction screening, and risk operations console
                </div>
            </div>
            <div class="bank-state">
                <span class="bank-state-dot"></span>
                Settlement Risk Monitor
            </div>
        </div>
        """, unsafe_allow_html=True)
    with hdr2:
        batch_threshold = st.slider(
            "Batch Threshold",
            min_value=0.05,
            max_value=0.95,
            step=0.01,
            key="threshold",
        )
    with hdr3:
        uploaded_file = st.file_uploader(
            "Load CSV or XLSX",
            type=["csv", "xlsx", "xls"],
            key="batch_upload",
        )

    render_status_banner()
    st.markdown('<div class="bank-section-divider"></div>', unsafe_allow_html=True)

    df = None
    inference_note = ""
    demo_mode = False

    if uploaded_file is not None:
        load_result = read_uploaded_table(uploaded_file, max_rows=5000)
        if not load_result.ok:
            st.error(load_result.message)
        else:
            normalized_upload = normalize_batch_input(load_result.data)
            if not normalized_upload.ok:
                st.error(normalized_upload.message)
            else:
                raw_df = normalized_upload.data
                with st.spinner("Running heavy ensemble and Isolation Forest inference..."):
                    inference_result = predict_batch_transactions(
                        raw_df,
                        threshold=float(st.session_state["threshold"]),
                    )
                if inference_result.ok:
                    df = inference_result.data
                    st.session_state["batch_predictions"] = df
                    st.session_state["uploaded_file_data"] = raw_df.copy()
                    inference_note = (
                        f"{inference_result.message} Heavy ensemble and Isolation Forest scoring completed. "
                        f"Threshold: {st.session_state['threshold']:.2f}."
                    )
                else:
                    st.error(inference_result.message)

    if df is None:
        demo_mode = True
        df = generate_mock_transactions(n_rows=3000, fraud_rate=0.041, seed=42)
        df.insert(0, "TransactionID", range(10_000_001, 10_000_001 + len(df)))

    if demo_mode:
        st.markdown("""
        <div class="batch-demo">
            <span>Demo mode:</span> No batch file is loaded. Displaying a realistic simulated
            portfolio of 3,000 transactions with a 4.1% fraud rate.
        </div>
        """, unsafe_allow_html=True)

    stats = compute_batch_stats(df)

    if inference_note:
        st.success(inference_note)

    report = load_evaluation_report()
    if report:
        for entry in report:
            if entry.get("model") == "Ensemble":
                stats["auc"] = entry.get("auc", stats["auc"])
                break

    render_kpi_row(
        total_transactions=stats["total"],
        fraud_count=stats["fraud"],
        fraud_rate=stats["rate"],
        protected_amount=stats["protected"],
        auc_score=stats["auc"],
    )

    st.markdown('<div class="bank-section-divider"></div>', unsafe_allow_html=True)

    r2c1, r2c2 = st.columns(2, gap="medium")
    with r2c1:
        render_model_drift_infrastructure(get_artifact_status())
    with r2c2:
        render_fraud_by_card_brand(df)

    st.markdown('<div class="bank-section-divider"></div>', unsafe_allow_html=True)

    r3c1, r3c2 = st.columns(2, gap="medium")
    with r3c1:
        render_temporal_heatmap(df)
    with r3c2:
        render_device_distribution(df)

    st.markdown('<div class="bank-section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Top Risk Transactions</div>',
                unsafe_allow_html=True)
    if "risk_score" in df.columns:
        display_cols = [
            col for col in [
                "TransactionID", "TransactionAmt", "card4", "card6",
                "DeviceType", "P_emaildomain", "risk_score",
                "prediction", "iso_score"
            ]
            if col in df.columns
        ]
        top_risk = df.sort_values("risk_score", ascending=False).head(25)
        st.dataframe(top_risk[display_cols], use_container_width=True,
                     hide_index=True)
    else:
        st.warning("No risk_score column is available for the current dataset.")


# ================================================================
# Router
# ================================================================
if page == "Executive Batch Dashboard":
    page_batch()
else:
    page_realtime()

# ── Footer ──
render_footer()
