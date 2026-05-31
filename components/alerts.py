"""
Reusable alert and status components for Streamlit.
"""

from __future__ import annotations

import html
from typing import Iterable, Mapping

import streamlit as st


ALERT_CSS = """
<style>
.fg-alert {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    padding: 13px 15px;
    margin: 8px 0 14px;
    border-radius: 8px;
    border: 1px solid rgba(148, 163, 184, 0.22);
    background: rgba(20, 25, 30, 0.94);
    color: #D8DEE3;
    font-size: 13px;
    font-weight: 650;
    line-height: 1.45;
}
.fg-alert strong { color: #F8FAFC; }
.fg-alert-dot {
    width: 9px;
    height: 9px;
    flex: 0 0 auto;
    margin-top: 5px;
    border-radius: 999px;
}
.fg-alert-success { border-color: rgba(46, 204, 113, 0.34); background: rgba(46, 204, 113, 0.08); }
.fg-alert-success .fg-alert-dot { background: #2ECC71; box-shadow: 0 0 14px rgba(46, 204, 113, 0.7); }
.fg-alert-warning { border-color: rgba(243, 156, 18, 0.34); background: rgba(243, 156, 18, 0.08); }
.fg-alert-warning .fg-alert-dot { background: #F39C12; box-shadow: 0 0 14px rgba(243, 156, 18, 0.7); }
.fg-alert-danger { border-color: rgba(231, 76, 60, 0.34); background: rgba(231, 76, 60, 0.08); }
.fg-alert-danger .fg-alert-dot { background: #E74C3C; box-shadow: 0 0 14px rgba(231, 76, 60, 0.7); }
.fg-alert-info { border-color: rgba(52, 152, 219, 0.34); background: rgba(52, 152, 219, 0.08); }
.fg-alert-info .fg-alert-dot { background: #3498DB; box-shadow: 0 0 14px rgba(52, 152, 219, 0.7); }
.fg-status-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
    margin: 8px 0 16px;
}
.fg-status-pill {
    min-height: 44px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    border: 1px solid rgba(148, 163, 184, 0.18);
    background: rgba(20, 25, 30, 0.92);
}
.fg-status-name {
    color: #D8DEE3;
    overflow-wrap: anywhere;
    font-size: 12px;
    font-weight: 750;
}
.fg-status-state {
    flex: 0 0 auto;
    font-size: 11px;
    font-weight: 850;
    text-transform: uppercase;
}
.fg-online { color: #2ECC71; }
.fg-offline { color: #F39C12; }
@media (max-width: 760px) {
    .fg-status-grid { grid-template-columns: 1fr; }
}
</style>
"""


def _safe_text(value: object) -> str:
    return html.escape("" if value is None else str(value))


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def render_alert(message: str, title: str = "Notice", tone: str = "info") -> None:
    """Render a compact status alert."""
    active_tone = tone if tone in {"success", "warning", "danger", "info"} else "info"
    st.markdown(ALERT_CSS, unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="fg-alert fg-alert-{active_tone}" role="status">
            <span class="fg-alert-dot"></span>
            <div><strong>{_safe_text(title)}</strong><br>{_safe_text(message)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_error_list(errors: Iterable[str], title: str = "System Check") -> None:
    """Render bounded backend or artifact errors."""
    messages = [str(error) for error in errors if str(error).strip()]
    if not messages:
        render_alert("All required artifacts are available.", title, "success")
        return

    render_alert(" | ".join(messages[:4]), title, "warning")


def render_prediction_alert(result: Mapping[str, object]) -> None:
    """Render the main verdict alert from ``models.predict.predict`` output."""
    if result.get("error"):
        render_alert(str(result["error"]), "Prediction Unavailable", "danger")
        return

    decision = str(result.get("decision", "UNKNOWN"))
    score = _safe_float(result.get("risk_score"))
    threshold = _safe_float(result.get("threshold"), 0.5)
    action = str(result.get("risk_action", "Review result"))

    if decision == "FRAUD":
        render_alert(
            f"Risk score {score * 100:.1f}% exceeds the active threshold of {threshold * 100:.0f}%. {action}.",
            "Transaction Blocked",
            "danger",
        )
    elif score >= threshold * 0.70:
        render_alert(
            f"Risk score {score * 100:.1f}% is elevated but below the active threshold of {threshold * 100:.0f}%.",
            "Manual Review Recommended",
            "warning",
        )
    else:
        render_alert(
            f"Risk score {score * 100:.1f}% is below the active threshold of {threshold * 100:.0f}%.",
            "Transaction Approved",
            "success",
        )


def render_artifact_status(status: Mapping[str, bool]) -> None:
    """Render artifact availability without throwing when keys are missing."""
    st.markdown(ALERT_CSS, unsafe_allow_html=True)

    ordered_names = (
        "inference_backend",
        "xgb_heavy",
        "lgbm_heavy",
        "iso_forest",
        "xgb_light",
        "lgbm_light",
        "top35_features",
        "all_features",
        "encoders",
        "medians",
        "feature_columns",
    )
    rows = []
    for name in ordered_names:
        online = bool(status.get(name, False))
        rows.append(
            f"""
            <div class="fg-status-pill">
                <span class="fg-status-name">{_safe_text(name.replace("_", " ").title())}</span>
                <span class="fg-status-state {'fg-online' if online else 'fg-offline'}">
                    {'Online' if online else 'Missing'}
                </span>
            </div>
            """
        )

    st.markdown(f'<section class="fg-status-grid">{"".join(rows)}</section>', unsafe_allow_html=True)
