"""
FraudGuard — Institutional Fraud & Payment Risk Console
Run: streamlit run dashboard/app.py
"""

import sys
from datetime import time as dt_time
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Streamlit puts `dashboard/` on sys.path — drop wrong cached `services` package if any
_wrong = sys.modules.get("services")
if _wrong is not None and not str(getattr(_wrong, "__file__", "") or "").startswith(
    str(PROJECT_ROOT / "services")
):
    del sys.modules["services"]

import pandas as pd
import streamlit as st

from dashboard.styles.theme import inject_theme
from dashboard.components.kpi_cards import render_kpi_row
from dashboard.components.charts import (
    render_fraud_by_card_brand,
    render_device_distribution,
    render_temporal_heatmap,
    render_risk_gauge,
    render_model_drift_infrastructure,
)
from dashboard.components.alerts import render_status_banner, render_footer
from dashboard.components.layout import (
    render_institutional_header,
    render_trust_ribbon,
    render_page_intro,
    render_explanation_panel,
)
from dashboard.components.sidebar import render_sidebar
from mlops.drift_detection import compute_drift_report
from services.audit_log import fetch_recent_predictions
from services.data_loader import (
    explain_transaction,
    get_artifact_status,
    is_realtime_ready,
    load_evaluation_report,
    load_threshold as load_realtime_threshold,
    normalize_batch_input,
    predict_batch_transactions,
    predict_transaction,
    read_uploaded_table,
)
from dashboard.utils.helpers import get_threshold_description, compute_batch_stats


st.set_page_config(
    page_title="FraudGuard | Institutional Risk Console",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(inject_theme(), unsafe_allow_html=True)


def init_session_state():
    initial_threshold = min(max(float(load_realtime_threshold() or 0.75), 0.05), 0.95)
    defaults = {
        "threshold": initial_threshold,
        "batch_threshold": initial_threshold,
        "uploaded_file_data": None,
        "batch_predictions": None,
        "last_prediction": None,
        "last_explanation": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()
render_institutional_header()
render_trust_ribbon()

page = render_sidebar()


def page_realtime():
    render_page_intro(
        title="Payment Authorization",
        subtitle=(
            "Single-transaction authorization desk for card-not-present payments. "
            "Scores are produced by the light authorization ensemble with policy-driven thresholds."
        ),
        breadcrumb="Card Payments",
    )

    left_col, right_col = st.columns([1.25, 1], gap="large")
    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    with left_col:
        st.markdown('<div class="bk-panel">', unsafe_allow_html=True)
        st.markdown('<div class="bk-card-title">Authorization Request</div>', unsafe_allow_html=True)

        amount = st.number_input(
            "Transaction Amount (USD)",
            min_value=0.0,
            max_value=100000.0,
            value=35.00,
            format="%.2f",
        )
        email = st.text_input("Cardholder Email", value="customer@gmail.com")

        f1, f2 = st.columns(2)
        with f1:
            card_brand = st.selectbox(
                "Card Network",
                ["visa", "mastercard", "american express", "discover"],
            )
            device_type = st.selectbox("Channel", ["desktop", "mobile"])
        with f2:
            card_type = st.selectbox("Product Type", ["debit", "credit"])
            transaction_time = st.time_input("Authorization Time (UTC)", value=dt_time(12, 0))

        distance = st.number_input(
            "Geo Deviation (km from profile)",
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
            st.error("Amount must be non-negative.")
        if not email_valid:
            st.error("Enter a valid cardholder email.")
        if not is_realtime_ready():
            st.warning("Authorization models offline — deploy artifacts to `artifacts/`.")

        if st.button(
            "Submit Authorization Decision",
            type="primary",
            use_container_width=True,
            disabled=analyze_disabled,
        ):
            domain = email.strip().split("@", 1)[1].lower()
            h = transaction_time.hour
            user_input = {
                "TransactionAmt": float(amount),
                "ProductCD": "W",
                "card4": card_brand,
                "card6": card_type,
                "P_emaildomain": domain,
                "DeviceType": device_type,
                "dist1": float(distance),
                "TransactionDT": h * 3600 + transaction_time.minute * 60,
                "hour": h,
            }
            with st.spinner("Screening against authorization policy..."):
                prediction = predict_transaction(
                    user_input,
                    threshold=float(st.session_state["threshold"]),
                    light_only=True,
                )
            st.session_state["last_prediction"] = (
                prediction.data if prediction.ok else {"error": prediction.message}
            )
            if prediction.ok:
                expl = explain_transaction(user_input, top_n=8)
                st.session_state["last_explanation"] = expl.data if expl.ok else None

        result = st.session_state.get("last_prediction")
        if isinstance(result, dict) and result.get("error"):
            st.error(result["error"])
        elif isinstance(result, dict):
            fraud_p = float(result.get("fraud_probability", result.get("risk_score", 0)) or 0)
            risk = float(result.get("risk_score", fraud_p) or 0)
            is_fraud = bool(result.get("is_fraud", result.get("decision") == "FRAUD"))
            css = "rt-blocked" if is_fraud else "rt-approved"
            title = "DECLINED — High Risk" if is_fraud else "APPROVED — Within Policy"
            sub = "Refer to fraud investigations" if is_fraud else "Proceed to settlement"

            st.markdown(f"""
            <div class="rt-decision {css}">
                <strong>{title}</strong>
                <span>{sub}</span>
            </div>
            <div class="rt-score-grid">
                <div class="rt-score">
                    <label>Fraud Probability</label>
                    <strong>{fraud_p * 100:.1f}%</strong>
                </div>
                <div class="rt-score">
                    <label>Composite Risk Score</label>
                    <strong>{risk * 100:.1f}%</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

            expl = st.session_state.get("last_explanation")
            if expl:
                render_explanation_panel(expl)
        else:
            st.info("Complete the authorization request form and submit for a decision.")

        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="bk-panel">', unsafe_allow_html=True)
        st.markdown('<div class="bk-card-title">Policy Controls</div>', unsafe_allow_html=True)

        threshold = st.slider(
            "Authorization Threshold",
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
        gauge = 0.0
        if isinstance(result, dict) and not result.get("error"):
            gauge = float(result.get("risk_score", 0) or 0)
        render_risk_gauge(gauge, threshold)

        status = get_artifact_status()
        st.markdown(f"""
        <div class="bk-panel" style="margin-top:16px;padding:16px;">
            <div class="bk-card-title">Registry Status</div>
            <div class="bk-model-row"><span>Inference Core</span>
                <strong class="{'bk-online' if status.get('inference_backend') else 'bk-offline'}">
                {'Online' if status.get('inference_backend') else 'Offline'}</strong></div>
            <div class="bk-model-row"><span>Authorization Models</span>
                <strong class="{'bk-online' if status.get('xgb_light') and status.get('lgbm_light') else 'bk-offline'}">
                {'Ready' if status.get('xgb_light') else 'Missing'}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def page_batch():
    render_page_intro(
        title="Portfolio Surveillance",
        subtitle=(
            "Executive batch screening for settlement risk, merchant portfolios, and end-of-day "
            "fraud exposure. Heavy ensemble with anomaly detection."
        ),
        breadcrumb="Risk Operations",
    )

    hdr1, hdr2, hdr3 = st.columns([2.2, 1, 1])
    with hdr1:
        st.markdown("""
        <div class="bank-page-header">
            <div>
                <h2 class="bank-title">Batch Screening Console</h2>
                <div class="bank-subtitle">Upload merchant or cardholder transaction files for overnight risk review</div>
            </div>
            <div class="bank-state"><span class="bank-state-dot"></span>EOD Surveillance Active</div>
        </div>
        """, unsafe_allow_html=True)
    with hdr2:
        st.slider(
            "Portfolio Threshold",
            min_value=0.05,
            max_value=0.95,
            step=0.01,
            key="batch_threshold",
        )
    with hdr3:
        uploaded_file = st.file_uploader(
            "Transaction file (CSV / XLSX)",
            type=["csv", "xlsx", "xls"],
            key="batch_upload",
        )

    render_status_banner()

    df = None
    inference_note = ""

    if uploaded_file is not None:
        load_result = read_uploaded_table(uploaded_file, max_rows=5000)
        if not load_result.ok:
            st.error(load_result.message)
        else:
            normalized = normalize_batch_input(load_result.data)
            if not normalized.ok:
                st.error(normalized.message)
            else:
                batch_thr = float(st.session_state.get("batch_threshold", st.session_state["threshold"]))
                with st.spinner("Running portfolio-wide ensemble screening..."):
                    inference_result = predict_batch_transactions(normalized.data, threshold=batch_thr)
                if inference_result.ok:
                    df = inference_result.data
                    st.session_state["batch_predictions"] = df
                    inference_note = (
                        f"{inference_result.message} · Policy threshold {batch_thr:.2f}"
                    )
                else:
                    st.error(inference_result.message)

    if df is None:
        st.info("Upload a CSV or Excel transaction file to run portfolio screening.")
        with st.expander("Required file format"):
            st.markdown(
                "The file must include `TransactionAmt`. Optional useful columns include "
                "`TransactionID`, `card4`, `card6`, `DeviceType`, `P_emaildomain`, "
                "`dist1`, and `TransactionDT`."
            )
        return

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

    c1, c2 = st.columns(2, gap="medium")
    drift_report = compute_drift_report(df)
    with c1:
        render_model_drift_infrastructure(get_artifact_status(), drift_report)
        if drift_report and drift_report.get("alert"):
            st.warning(drift_report["alert"])
    with c2:
        render_fraud_by_card_brand(df)

    st.markdown('<div class="bank-section-divider"></div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        render_temporal_heatmap(df)
    with c4:
        render_device_distribution(df)

    st.markdown('<div class="bank-section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Priority Review Queue</div>', unsafe_allow_html=True)

    if "risk_score" in df.columns:
        display_cols = [
            c for c in [
                "TransactionID", "TransactionAmt", "card4", "card6",
                "DeviceType", "P_emaildomain", "risk_score", "prediction", "iso_score",
            ]
            if c in df.columns
        ]
        top_risk = df.sort_values("risk_score", ascending=False).head(25)
        st.dataframe(top_risk[display_cols], use_container_width=True, hide_index=True)

        if st.session_state.get("batch_predictions") is not None:
            st.download_button(
                "Export screened portfolio (CSV)",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="fraud_screened_portfolio.csv",
                mime="text/csv",
                use_container_width=True,
            )
    else:
        st.warning("Risk scores unavailable for the current dataset.")

    with st.expander("Audit trail — last authorizations"):
        logs = fetch_recent_predictions(25)
        if logs:
            st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
        else:
            st.caption("No entries yet. Authorization and batch runs are logged automatically.")


if page == "realtime":
    page_realtime()
else:
    page_batch()

render_footer()
