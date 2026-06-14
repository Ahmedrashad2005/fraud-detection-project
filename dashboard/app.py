"""
FraudGuard — Institutional Fraud & Payment Risk Console
Run: streamlit run dashboard/app.py
"""

import sys
from datetime import datetime, timezone, time as dt_time
from html import escape
from pathlib import Path
import re
from urllib.parse import quote

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

from config.paths import ARTIFACTS_DIR
from dashboard.styles.theme import inject_theme
from dashboard.components.kpi_cards import render_kpi_row
from dashboard.components.charts import (
    render_fraud_by_card_brand,
    render_device_distribution,
    render_temporal_heatmap,
    render_risk_gauge,
    render_model_drift_infrastructure,
)
from dashboard.components.alerts import render_footer
from dashboard.components.layout import (
    render_institutional_header,
    render_trust_ribbon,
    render_page_intro,
    render_explanation_panel,
    render_empty_state,
)
from dashboard.components.sidebar import render_sidebar
from mlops.drift_detection import compute_drift_report
from services.audit_log import (
    fetch_latest_review_statuses,
    fetch_recent_predictions,
    fetch_review_actions,
    log_review_action,
)
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
from features.build_features import REF_DATE

LATEST_BATCH_PATH = ARTIFACTS_DIR / "latest_batch_predictions.csv"


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
        "review_statuses": None,
        "selected_queue_id": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
    if st.session_state["review_statuses"] is None:
        st.session_state["review_statuses"] = fetch_latest_review_statuses()


init_session_state()
render_institutional_header()
render_trust_ribbon()

page = render_sidebar()


def _store_latest_batch(df: pd.DataFrame) -> None:
    try:
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(LATEST_BATCH_PATH, index=False)
    except Exception as exc:
        st.warning(f"Could not save latest portfolio cache: {exc}")


def _load_latest_batch() -> pd.DataFrame | None:
    cached = st.session_state.get("batch_predictions")
    if isinstance(cached, pd.DataFrame) and not cached.empty:
        return cached
    if not LATEST_BATCH_PATH.exists():
        return None
    try:
        df = pd.read_csv(LATEST_BATCH_PATH, low_memory=False)
    except Exception:
        return None
    if df.empty:
        return None
    st.session_state["batch_predictions"] = df
    return df


def _evaluation_lookup() -> dict:
    return {
        str(item.get("model")): item
        for item in load_evaluation_report()
        if isinstance(item, dict)
    }


def _recent_fraud_count(logs: list[dict]) -> int:
    total = 0
    now = datetime.now(timezone.utc)
    for row in logs:
        try:
            created = datetime.fromisoformat(str(row.get("created_at", "")).replace("Z", "+00:00"))
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if (now - created).total_seconds() <= 24 * 3600 and int(row.get("is_fraud", 0) or 0):
            total += 1
    return total


def _bar_row(label: str, value: float, tone: str = "ok") -> str:
    pct = max(0, min(float(value), 1.0)) * 100
    color = "#2D8A62" if tone == "ok" else "#C9A04A" if tone == "warn" else "#C45C5C"
    pill_cls = "ov-pill-ok" if tone == "ok" else "ov-pill-warn"
    pill = "Stable" if tone == "ok" else "Review"
    return (
        f'<div class="ov-bar-row">'
        f'<span>{label}</span>'
        f'<div class="ov-bar-track"><div class="ov-bar-fill" '
        f'style="width:{pct:.1f}%;background:{color};"></div></div>'
        f'<span class="ov-pill {pill_cls}">{pct:.0f}%</span>'
        f'</div>'
    )


def _format_money(value: float) -> str:
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def _risk_bucket_rows(df: pd.DataFrame) -> str:
    if "risk_score" not in df.columns or df.empty:
        return ""

    scores = pd.to_numeric(df["risk_score"], errors="coerce").fillna(0).clip(0, 1)
    buckets = [
        ("Low", int((scores < 0.25).sum()), "#2D8A62"),
        ("Watch", int(((scores >= 0.25) & (scores < 0.50)).sum()), "#C9A04A"),
        ("High", int(((scores >= 0.50) & (scores < 0.75)).sum()), "#C45C5C"),
        ("Critical", int((scores >= 0.75).sum()), "#D96B6B"),
    ]
    total = max(len(scores), 1)
    rows = []
    for label, count, color in buckets:
        pct = count / total * 100
        rows.append(
            '<div class="insight-bucket-row">'
            f'<span>{label}</span>'
            '<div class="insight-bucket-track">'
            f'<div style="width:{pct:.1f}%;background:{color};"></div>'
            '</div>'
            f'<strong>{count:,}</strong>'
            '</div>'
        )
    return "".join(rows)


def _dashboard_brief(df: pd.DataFrame, threshold: float) -> None:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return

    fraud_col = "prediction" if "prediction" in df.columns else "isFraud" if "isFraud" in df.columns else None
    risk = pd.to_numeric(df.get("risk_score", pd.Series([0] * len(df))), errors="coerce").fillna(0).clip(0, 1)
    amount = pd.to_numeric(df.get("TransactionAmt", pd.Series([0] * len(df))), errors="coerce").fillna(0)

    top_network = "Unavailable"
    top_network_sub = "card4 not present"
    if fraud_col and "card4" in df.columns:
        brand_frame = df[["card4", fraud_col]].copy()
        brand_frame["card4"] = brand_frame["card4"].fillna("Unknown").astype(str)
        brand_frame[fraud_col] = pd.to_numeric(brand_frame[fraud_col], errors="coerce").fillna(0)
        brand_stats = brand_frame.groupby("card4")[fraud_col].agg(["mean", "count"]).reset_index()
        if not brand_stats.empty:
            brand_stats = brand_stats.sort_values(["mean", "count"], ascending=[False, False])
            top = brand_stats.iloc[0]
            top_network = escape(str(top["card4"]).title())
            top_network_sub = f'{float(top["mean"]) * 100:.1f}% decline rate · {int(top["count"]):,} txns'

    peak_window = "Unavailable"
    peak_window_sub = "time field not present"
    if "hour" in df.columns:
        hours = pd.to_numeric(df["hour"], errors="coerce")
    elif "TransactionDT" in df.columns:
        tx_seconds = pd.to_numeric(df["TransactionDT"], errors="coerce")
        dt = pd.to_datetime(REF_DATE) + pd.to_timedelta(tx_seconds, unit="s")
        hours = dt.dt.hour
    else:
        hours = pd.Series(dtype=float)
    if len(hours) == len(df) and hours.notna().any():
        hour_frame = pd.DataFrame({"hour": hours, "risk_score": risk})
        hour_stats = hour_frame.dropna().groupby("hour")["risk_score"].mean().sort_values(ascending=False)
        if not hour_stats.empty:
            hour = int(hour_stats.index[0])
            peak_window = f"{hour:02d}:00"
            peak_window_sub = f"{float(hour_stats.iloc[0]) * 100:.1f}% avg risk"

    review_count = int((risk >= threshold).sum())
    review_exposure = float(amount[risk >= threshold].sum()) if len(amount) == len(risk) else 0.0

    agreement = "Unavailable"
    agreement_sub = "model score columns not present"
    if {"xgb_score", "lgbm_score"}.issubset(df.columns):
        xgb_score = pd.to_numeric(df["xgb_score"], errors="coerce")
        lgbm_score = pd.to_numeric(df["lgbm_score"], errors="coerce")
        valid = xgb_score.notna() & lgbm_score.notna()
        if valid.any():
            agreement_rate = ((xgb_score[valid] - lgbm_score[valid]).abs() <= 0.10).mean()
            agreement = f"{agreement_rate * 100:.1f}%"
            agreement_sub = "XGB/LGBM agreement within 10 pts"

    bucket_rows = _risk_bucket_rows(df)
    st.markdown(f"""
    <section class="insight-brief">
        <div class="insight-head">
            <div>
                <div class="insight-kicker">Executive Risk Brief</div>
                <h3>What changed in the latest portfolio</h3>
            </div>
            <span>{len(df):,} real transactions analysed</span>
        </div>
        <div class="insight-grid">
            <div class="insight-tile">
                <label>Highest Network Risk</label>
                <strong>{top_network}</strong>
                <span>{top_network_sub}</span>
            </div>
            <div class="insight-tile">
                <label>Peak Risk Window</label>
                <strong>{peak_window}</strong>
                <span>{peak_window_sub}</span>
            </div>
            <div class="insight-tile">
                <label>Review Queue</label>
                <strong>{review_count:,}</strong>
                <span>{_format_money(review_exposure)} exposure above policy</span>
            </div>
            <div class="insight-tile">
                <label>Model Agreement</label>
                <strong>{agreement}</strong>
                <span>{agreement_sub}</span>
            </div>
        </div>
        <div class="insight-buckets">
            <div class="insight-bucket-title">Risk Segmentation</div>
            {bucket_rows}
        </div>
    </section>
    """, unsafe_allow_html=True)


def _risk_level(score: float) -> str:
    if score >= 0.75:
        return "High"
    if score >= 0.35:
        return "Medium"
    return "Low"


def _risk_class(level: str) -> str:
    return {
        "High": "risk-high",
        "Medium": "risk-medium",
        "Low": "risk-low",
    }.get(level, "risk-low")


def _row_value(row: pd.Series, names: list[str], default: str = "Unavailable") -> str:
    for name in names:
        if name in row.index:
            value = row.get(name)
            if pd.notna(value) and str(value).strip() != "":
                return str(value)
    return default


def _transaction_id(row: pd.Series, index: int) -> str:
    value = _row_value(row, ["TransactionID", "transaction_id", "TransactionId", "id"], "")
    if value:
        try:
            if float(value).is_integer():
                return str(int(float(value)))
        except (TypeError, ValueError):
            pass
        return value
    return f"TX{index + 1:06d}"


def _queue_frame(df: pd.DataFrame) -> pd.DataFrame:
    queue = df.copy().reset_index(drop=True)
    queue["_queue_id"] = [_transaction_id(row, idx) for idx, row in queue.iterrows()]
    queue["_risk_score"] = pd.to_numeric(
        queue.get("risk_score", pd.Series([0] * len(queue))), errors="coerce"
    ).fillna(0).clip(0, 1)
    queue["_risk_level"] = queue["_risk_score"].apply(_risk_level)
    statuses = st.session_state.get("review_statuses") or {}
    queue["_review_status"] = queue["_queue_id"].map(statuses).fillna("Pending")
    return queue


def _transaction_hour(row: pd.Series) -> str:
    if "hour" in row.index and pd.notna(row.get("hour")):
        try:
            return f"{int(float(row.get('hour'))) % 24:02d}:00"
        except (TypeError, ValueError):
            pass
    if "TransactionDT" in row.index and pd.notna(row.get("TransactionDT")):
        try:
            dt = pd.to_datetime(REF_DATE) + pd.to_timedelta(float(row.get("TransactionDT")), unit="s")
            return dt.strftime("%a %H:%M")
        except (TypeError, ValueError):
            pass
    return "Unavailable"


def _policy_signals(row: pd.Series) -> list[tuple[str, float]]:
    signals: list[tuple[str, float]] = []
    amount = float(pd.to_numeric(pd.Series([row.get("TransactionAmt", 0)]), errors="coerce").fillna(0).iloc[0])
    distance = float(pd.to_numeric(pd.Series([row.get("dist1", 0)]), errors="coerce").fillna(0).iloc[0])
    hour_text = _transaction_hour(row)
    hour = None
    if ":" in hour_text:
        try:
            hour = int(hour_text.split(":", 1)[0].split()[-1])
        except ValueError:
            hour = None
    domain = _row_value(row, ["P_emaildomain", "email_domain"], "").lower()
    device = _row_value(row, ["DeviceType"], "").lower()
    card = _row_value(row, ["card4"], "").lower()

    if distance > 1000:
        signals.append(("High geo deviation", 0.08))
    elif distance > 250:
        signals.append(("Elevated geo deviation", 0.04))
    if amount > 5000:
        signals.append(("Large transaction amount", 0.08))
    elif amount > 1000:
        signals.append(("Above-normal amount", 0.04))
    if hour is not None and (hour < 6 or hour >= 23):
        signals.append(("Night transaction", 0.05))
    if any(token in domain for token in ["anonymous", "proton", "mailinator", "tempmail"]):
        signals.append(("High-risk email domain", 0.05))
    if device == "mobile":
        signals.append(("Mobile channel", 0.02))
    if card == "discover":
        signals.append(("Elevated network risk", 0.03))
    if not signals:
        signals.append(("No major policy adjustment detected", 0.0))
    return signals


def _model_score(row: pd.Series) -> float:
    scores = []
    for col in ["xgb_score", "lgbm_score"]:
        if col in row.index and pd.notna(row.get(col)):
            scores.append(float(row.get(col)))
    if scores:
        return sum(scores) / len(scores)
    return float(row.get("_risk_score", row.get("risk_score", 0)) or 0)


def _render_queue_item(row: pd.Series, selected_id: str | None) -> str:
    tx_id = str(row["_queue_id"])
    score = float(row["_risk_score"])
    level = str(row["_risk_level"])
    status = str(row["_review_status"])
    active = "is-selected" if tx_id == selected_id else ""
    cls = _risk_class(level)
    href = f"?view=queue&tx={quote(tx_id)}"
    return (
        f'<a class="queue-item {active}" href="{href}" target="_self">'
        f'<span class="queue-risk-dot {cls}"></span>'
        f'<span class="queue-item-main"><strong>{escape(tx_id)}</strong>'
        f'<em>{escape(status)}</em></span>'
        f'<span class="queue-score"><b>{score * 100:.0f}%</b><small>fraud</small></span>'
        f'<span class="queue-level {cls}">{level}</span>'
        f'</a>'
    )


def _queue_filter_chips(kind: str, current: str, values: list[str]) -> str:
    chips = []
    for value in values:
        active = "is-active" if current == value else ""
        params = {"view": "queue"}
        if kind == "risk" and value != "All":
            params["risk"] = value
        if kind == "status" and value != "All":
            params["status"] = value
        if kind == "risk":
            try:
                status = st.query_params.get("status", "All")
            except Exception:
                status = "All"
            if status != "All":
                params["status"] = status
        if kind == "status":
            try:
                risk = st.query_params.get("risk", "All")
            except Exception:
                risk = "All"
            if risk != "All":
                params["risk"] = risk
        href = "?" + "&".join(f"{key}={quote(str(val))}" for key, val in params.items())
        chips.append(f'<a class="queue-filter-chip {active}" href="{href}" target="_self">{escape(value)}</a>')
    return "".join(chips)


def _queue_inbox_tabs(current: str) -> str:
    tabs = [
        ("All", "All"),
        ("High Risk", "High"),
        ("Pending", "Pending"),
        ("Blocked", "Blocked"),
        ("Approved", "Approved"),
    ]
    links = []
    for label, value in tabs:
        active = "is-active" if current == value else ""
        href = "?view=queue" if value == "All" else f"?view=queue&tab={quote(value)}"
        links.append(f'<a class="queue-inbox-tab {active}" href="{href}" target="_self">{escape(label)}</a>')
    return "".join(links)


def _render_timeline(tx_id: str) -> None:
    actions = list(reversed(fetch_review_actions(tx_id, limit=50)))
    rows = [
        '<div class="timeline-row"><i></i><div><strong>Created</strong><span>Loaded from latest portfolio batch</span></div></div>',
        '<div class="timeline-row"><i></i><div><strong>Scored</strong><span>Model and policy scores generated</span></div></div>',
    ]
    for action in actions:
        created = str(action.get("created_at", ""))
        label = escape(str(action.get("new_status", "Reviewed")))
        reason = escape(str(action.get("reason", "") or "No reason supplied"))
        analyst = escape(str(action.get("analyst", "A. Hassan")))
        rows.append(
            '<div class="timeline-row"><i></i><div>'
            f'<strong>{label}</strong><span>{created[:19]} · {analyst} · {reason}</span>'
            '</div></div>'
        )
    st.markdown(
        '<div class="queue-timeline"><div class="queue-section-title">Transaction Timeline</div>'
        + "".join(rows)
        + "</div>",
        unsafe_allow_html=True,
    )


def page_dashboard():
    render_page_intro(
        title="Dashboard",
        subtitle=(
            "Live risk snapshot from model reports, audit logs, and the latest screened portfolio."
        ),
        breadcrumb="Executive Monitoring",
    )

    evals = _evaluation_lookup()
    ensemble = evals.get("Ensemble", {})
    xgb = evals.get("XGBoost Heavy", {})
    lgbm = evals.get("LightGBM Heavy", {})
    iso_health = 0.82
    auc = float(ensemble.get("auc", 0) or 0)
    recall = float(ensemble.get("recall", 0) or 0)

    batch_df = _load_latest_batch()
    logs = fetch_recent_predictions(200)
    recent_fraud = _recent_fraud_count(logs)

    if isinstance(batch_df, pd.DataFrame) and not batch_df.empty:
        stats = compute_batch_stats(batch_df)
        total = stats["total"]
        fraud = stats["fraud"]
        fraud_rate = stats["rate"]
        protected = stats["protected"]
        protected_copy = (
            f"${protected / 1_000_000:.1f}M" if protected >= 1_000_000
            else f"${protected / 1_000:.0f}K" if protected >= 1_000
            else f"${protected:,.0f}"
        )
        source_note = f"{total:,} screened transactions"
    else:
        fraud = 0
        fraud_rate = 0.0
        protected_copy = "No batch"
        source_note = "Upload a portfolio batch to populate operational exposure"

    st.markdown(f"""
    <div class="ov-grid">
        <div class="ov-card">
            <div class="ov-label">Exposure Mitigated</div>
            <div class="ov-value">{protected_copy}</div>
            <div class="ov-sub">{source_note}</div>
        </div>
        <div class="ov-card">
            <div class="ov-label">Declined Transactions</div>
            <div class="ov-value">{fraud:,}</div>
            <div class="ov-sub">Latest screened portfolio</div>
        </div>
        <div class="ov-card">
            <div class="ov-label">Decline Rate</div>
            <div class="ov-value">{fraud_rate:.1f}%</div>
            <div class="ov-sub">Portfolio policy result</div>
        </div>
        <div class="ov-card">
            <div class="ov-label">Model Discrimination</div>
            <div class="ov-value">{auc * 100:.1f}%</div>
            <div class="ov-sub">Ensemble AUC · Recall {recall * 100:.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if isinstance(batch_df, pd.DataFrame) and not batch_df.empty:
        _dashboard_brief(batch_df, float(st.session_state.get("batch_threshold", 0.75)))

    if not isinstance(batch_df, pd.DataFrame) or batch_df.empty:
        render_empty_state(
            "Operational charts need a real portfolio batch",
            "Open Portfolio, upload a CSV or Excel file, and this dashboard will update from those predictions.",
            ["Real portfolio data only", "Uses latest portfolio cache", f"{recent_fraud} fraud audit entries in last 24h"],
        )

    left, right = st.columns([1.25, 0.95], gap="medium")
    with left:
        model_rows = (
            _bar_row("XGBoost", float(xgb.get("auc", 0) or 0), "ok") +
            _bar_row("LightGBM", float(lgbm.get("auc", 0) or 0), "ok") +
            _bar_row("Isolation Forest", iso_health, "warn")
        )
        st.markdown(
            '<div class="ov-panel">'
            '<div class="ov-panel-title">Model Drift & Registry Health</div>'
            f'{model_rows}'
            '<div class="ov-note">Isolation Forest should be reviewed when uploaded '
            'portfolio drift drops below policy tolerance.</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with right:
        if isinstance(batch_df, pd.DataFrame) and not batch_df.empty:
            render_fraud_by_card_brand(batch_df)
        else:
            st.markdown("""
            <div class="ov-panel">
                <div class="ov-panel-title">Fraud by Card Network</div>
                <div class="bk-chart-empty"><div><strong>No portfolio loaded</strong><span>Upload a real batch to show network risk.</span></div></div>
            </div>
            """, unsafe_allow_html=True)

    lower_left, lower_right = st.columns([1.25, 0.95], gap="medium")
    with lower_left:
        if isinstance(batch_df, pd.DataFrame) and not batch_df.empty:
            render_temporal_heatmap(batch_df)
        else:
            st.markdown("""
            <div class="ov-panel">
                <div class="ov-panel-title">Fraud Heatmap</div>
                <div class="bk-chart-empty"><div><strong>No temporal batch data</strong><span>Upload data with TransactionDT or time fields.</span></div></div>
            </div>
            """, unsafe_allow_html=True)
    with lower_right:
        if isinstance(batch_df, pd.DataFrame) and not batch_df.empty:
            render_device_distribution(batch_df)
        else:
            st.markdown("""
            <div class="ov-panel">
                <div class="ov-panel-title">Fraud by Device</div>
                <div class="bk-chart-empty"><div><strong>No device distribution yet</strong><span>Upload a real batch with DeviceType.</span></div></div>
            </div>
            """, unsafe_allow_html=True)


def page_realtime():
    render_page_intro(
        title="Payment Authorization",
        subtitle=(
            "Single-transaction screening with policy thresholds and explainable risk signals."
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
            action = result.get("risk_action", "Review required" if is_fraud else "Approved")
            mode = str(result.get("inference_mode", "light")).replace("_", " ").title()
            threshold_value = float(result.get("threshold", st.session_state["threshold"]) or 0)

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
            <div class="rt-action-grid">
                <div class="rt-action-item">
                    <label>Recommended Action</label>
                    <strong>{action}</strong>
                </div>
                <div class="rt-action-item">
                    <label>Policy Threshold</label>
                    <strong>{threshold_value * 100:.1f}%</strong>
                </div>
                <div class="rt-action-item">
                    <label>Scoring Mode</label>
                    <strong>{mode}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

            expl = st.session_state.get("last_explanation")
            if expl:
                render_explanation_panel(expl)
        else:
            st.markdown("""
            <div class="rt-waiting">
                <div>
                    <strong>Authorization decision pending</strong>
                    <span>Complete the request fields and submit the transaction for screening.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

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
            "Batch screening for settlement risk, merchant portfolios, and exposure review."
        ),
        breadcrumb="Risk Operations",
    )

    st.markdown("""
    <div class="batch-control-panel">
        <div>
            <div class="batch-control-title">Screen a Portfolio Batch</div>
            <div class="batch-control-copy">
                Upload real transaction data, tune the policy threshold, and run the heavy ensemble.
                Results update the Dashboard automatically.
            </div>
            <div class="batch-control-meta">
                <span>CSV / XLSX</span>
                <span>Max file 1GB</span>
                <span>Scores first 5,000 rows</span>
                <span>Requires TransactionAmt</span>
            </div>
        </div>
        <div></div>
    </div>
    """, unsafe_allow_html=True)

    ctrl1, ctrl2 = st.columns([1.25, 1], gap="large")
    with ctrl1:
        uploaded_file = st.file_uploader(
            "Transaction file",
            type=["csv", "xlsx", "xls"],
            key="batch_upload",
        )
    with ctrl2:
        st.slider(
            "Portfolio Threshold",
            min_value=0.05,
            max_value=0.95,
            step=0.01,
            key="batch_threshold",
        )
        st.markdown(
            f'<p class="fg-threshold-copy">{get_threshold_description(float(st.session_state["batch_threshold"]))}</p>',
            unsafe_allow_html=True,
        )

    df = None
    inference_note = ""

    if uploaded_file is not None:
        load_result = read_uploaded_table(uploaded_file, max_rows=5000)
        if not load_result.ok:
            st.error(load_result.message)
        else:
            st.caption(f"Loaded preview: {len(load_result.data):,} rows from `{uploaded_file.name}`")
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
                    _store_latest_batch(df)
                    inference_note = (
                        f"{inference_result.message} · Policy threshold {batch_thr:.2f}"
                    )
                else:
                    st.error(inference_result.message)

    if df is None:
        render_empty_state(
            "Portfolio screening ready",
            "Upload a CSV or Excel transaction file to score the batch with the heavy ensemble.",
            [
                "TransactionAmt",
                "card4",
                "card6",
                "DeviceType",
                "P_emaildomain",
                "dist1",
                "TransactionDT",
            ],
        )
        return

    stats = compute_batch_stats(df)
    if inference_note:
        st.markdown(f"""
        <div class="batch-result-strip">
            <div class="batch-result-item">
                <label>Inference Status</label>
                <strong>Scored</strong>
            </div>
            <div class="batch-result-item">
                <label>Rows Processed</label>
                <strong>{len(df):,}</strong>
            </div>
            <div class="batch-result-item">
                <label>Policy Threshold</label>
                <strong>{float(st.session_state.get("batch_threshold", st.session_state["threshold"])):.2f}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

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


def page_queue():
    render_page_intro(
        title="Review Queue",
        subtitle="Operational workstation for analyst decisions, policy review, and audit traceability.",
        breadcrumb="Fraud Operations",
    )

    batch_df = _load_latest_batch()
    if not isinstance(batch_df, pd.DataFrame) or batch_df.empty:
        render_empty_state(
            "No portfolio loaded for review",
            "Run Executive Batch once. The Review Queue will automatically load the latest scored transactions.",
            ["No duplicate upload required", "Reads latest portfolio cache", "Human decisions are audited"],
        )
        st.markdown(
            '<a class="queue-upload-link" href="?view=batch" target="_self">Open Executive Batch</a>',
            unsafe_allow_html=True,
        )
        return

    queue = _queue_frame(batch_df)
    queue = queue.sort_values("_risk_score", ascending=False).reset_index(drop=True)

    try:
        tx_param = st.query_params.get("tx", "")
        active_tab = st.query_params.get("tab", "All")
    except Exception:
        tx_param = ""
        active_tab = "All"

    if active_tab not in {"All", "High", "Pending", "Blocked", "Approved"}:
        active_tab = "All"

    st.markdown(f'<div class="queue-inbox-tabs">{_queue_inbox_tabs(active_tab)}</div>', unsafe_allow_html=True)
    search = st.text_input("Search Transaction ID", value="", key="queue_search")

    filtered = queue.copy()
    if active_tab == "High":
        filtered = filtered[filtered["_risk_level"] == "High"]
    elif active_tab in {"Pending", "Blocked", "Approved"}:
        filtered = filtered[filtered["_review_status"] == active_tab]
    if search.strip():
        needle = search.strip().lower()
        filtered = filtered[filtered["_queue_id"].astype(str).str.lower().str.contains(needle, regex=False)]

    if filtered.empty:
        selected = None
        selected_id = None
    else:
        candidate_ids = set(filtered["_queue_id"].astype(str))
        selected_id = str(tx_param) if tx_param and str(tx_param) in candidate_ids else str(filtered.iloc[0]["_queue_id"])
        st.session_state["selected_queue_id"] = selected_id
        selected = filtered[filtered["_queue_id"].astype(str) == selected_id].iloc[0]

    pending_count = int((queue["_review_status"] == "Pending").sum())
    high_count = int((queue["_risk_level"] == "High").sum())
    items_html = (
        "".join(_render_queue_item(row, selected_id) for _, row in filtered.iterrows())
        if not filtered.empty
        else '<div class="queue-empty-mini">No transactions match the current filters.</div>'
    )

    left, right = st.columns([0.92, 1.38], gap="large")

    with left:
        st.markdown(
            '<section class="queue-panel queue-list-panel">'
            '<div class="queue-section-title">All Transactions</div>'
            '<div class="queue-summary-strip">'
            f'<div><label>Showing</label><strong>{len(filtered):,}</strong></div>'
            f'<div><label>Pending</label><strong>{pending_count:,}</strong></div>'
            f'<div><label>High Risk</label><strong>{high_count:,}</strong></div>'
            '</div>'
            f'<div class="queue-items">{items_html}</div>'
            '</section>',
            unsafe_allow_html=True,
        )

    with right:
        if selected is None:
            st.markdown(
                '<section class="queue-panel queue-detail-panel">'
                '<div class="queue-empty-detail">Select a transaction to review details.</div>'
                '</section>',
                unsafe_allow_html=True,
            )
            return

        tx_id = str(selected["_queue_id"])
        risk_score = float(selected["_risk_score"])
        risk_level = str(selected["_risk_level"])
        status = str(selected["_review_status"])
        threshold = float(selected.get("threshold", st.session_state.get("batch_threshold", 0.75)) or 0.75)
        amount = float(pd.to_numeric(pd.Series([selected.get("TransactionAmt", 0)]), errors="coerce").fillna(0).iloc[0])
        distance = float(pd.to_numeric(pd.Series([selected.get("dist1", 0)]), errors="coerce").fillna(0).iloc[0])
        card = escape(_row_value(selected, ["card4"], "Unavailable"))
        product = escape(_row_value(selected, ["card6"], "Unavailable"))
        domain = escape(_row_value(selected, ["P_emaildomain"], "Unavailable"))
        device = escape(_row_value(selected, ["DeviceType"], "Unavailable"))
        tx_time = escape(_transaction_hour(selected))
        model_score = _model_score(selected)
        policy_signals = _policy_signals(selected)
        policy_delta = min(sum(delta for _, delta in policy_signals), 0.25)
        policy_score = min(model_score + policy_delta, 1.0)
        decision = (
            "BLOCK" if status == "Blocked"
            else "APPROVE" if status == "Approved"
            else "REVIEW" if status == "Under Review"
            else "BLOCK" if risk_score >= threshold
            else "MANUAL REVIEW" if risk_score >= 0.35
            else "APPROVE"
        )
        risk_cls = _risk_class(risk_level)
        signal_rows = "".join(
            f'<li><span>{escape(label)}</span><strong>+{delta * 100:.0f} pts</strong></li>'
            for label, delta in policy_signals
        )

        st.markdown(
            f'<section class="queue-panel queue-detail-panel">'
            f'<div class="queue-detail-head"><div><div class="queue-eyebrow">Selected Transaction</div>'
            f'<h2>{escape(tx_id)}</h2></div><span class="queue-status-pill">{escape(status)}</span></div>'
            f'<div class="queue-score-hero"><div><label>Fraud Score</label>'
            f'<strong>{risk_score * 100:.1f}%</strong></div><span class="queue-level {risk_cls}">{risk_level}</span></div>'
            f'<div class="queue-info-grid">'
            f'<div><label>Amount</label><strong>{_format_money(amount)}</strong></div>'
            f'<div><label>Geo Deviation</label><strong>{distance:,.0f} km</strong></div>'
            f'<div><label>Card Network</label><strong>{card}</strong></div>'
            f'<div><label>Product Type</label><strong>{product}</strong></div>'
            f'<div><label>Email Domain</label><strong>{domain}</strong></div>'
            f'<div><label>Device Type</label><strong>{device}</strong></div>'
            f'<div><label>Transaction Time</label><strong>{tx_time}</strong></div>'
            f'<div><label>Threshold</label><strong>{threshold * 100:.0f}%</strong></div>'
            f'</div>'
            f'<div class="queue-model-policy"><div class="queue-section-title">Model vs Policy</div>'
            f'<div class="policy-row"><span>Model Score</span><strong>{model_score * 100:.1f}%</strong></div>'
            f'<div class="policy-row"><span>Policy Score</span><strong>{policy_score * 100:.1f}%</strong></div>'
            f'<div class="policy-row policy-final"><span>Final Decision</span><strong>{decision}</strong></div></div>'
            f'</section>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="queue-section-title">Decision Center</div>', unsafe_allow_html=True)
        reason = "Analyst decision from Review Queue"
        analyst = "A. Hassan"
        a1, a2, a3 = st.columns(3)

        def apply_decision(new_status: str) -> None:
            previous = str((st.session_state.get("review_statuses") or {}).get(tx_id, "Pending"))
            st.session_state["review_statuses"][tx_id] = new_status
            log_review_action(
                transaction_id=tx_id,
                previous_status=previous,
                new_status=new_status,
                reason=reason,
                analyst=analyst,
                risk_score=risk_score,
            )
            st.toast(f"{tx_id} marked {new_status}")
            st.rerun()

        with a1:
            if st.button("APPROVE", use_container_width=True, key=f"approve_{tx_id}"):
                apply_decision("Approved")
        with a2:
            if st.button("BLOCK", use_container_width=True, key=f"block_{tx_id}"):
                apply_decision("Blocked")
        with a3:
            if st.button("MANUAL REVIEW", use_container_width=True, key=f"review_{tx_id}"):
                apply_decision("Under Review")

        with st.expander("History"):
            _render_timeline(tx_id)


if page == "dashboard":
    page_dashboard()
elif page == "realtime":
    page_realtime()
elif page == "batch":
    page_batch()
elif page == "queue":
    page_queue()
else:
    page_dashboard()

render_footer()
