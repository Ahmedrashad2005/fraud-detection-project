# dashboard/components/alerts.py
"""
Alerts — Status banners, model health indicators, and warning boxes.
"""

import streamlit as st
from dashboard.styles.theme import COLORS


# ================================================================
# Live Operational Status Banner
# ================================================================
def render_status_banner():
    """Render institutional operations status ribbon."""
    st.markdown("""
    <div class="status-banner">
        <div class="status-item">
            <span class="status-dot green"></span>
            <span>Real-Time Authorization Engine</span>
        </div>
        <div class="status-item">
            <span class="status-dot green"></span>
            <span>SWIFT / Card Network Gateway</span>
        </div>
        <div class="status-item">
            <span class="status-dot green"></span>
            <span>End-to-End Encryption Active</span>
        </div>
        <div class="status-item">
            <span class="status-dot orange"></span>
            <span>Regulatory Reporting Queue · Normal</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ================================================================
# Model Health Indicators
# ================================================================
def render_model_health():
    """Render model drift and health monitoring bars."""
    st.markdown(
        '<div class="section-header">Model Drift & Health Monitoring</div>',
        unsafe_allow_html=True,
    )

    health_data = [
        ("XGBoost Heavy",   94, COLORS['emerald']),
        ("LightGBM Heavy",  91, COLORS['emerald']),
        ("Isolation Forest", 67, COLORS['warning']),
    ]

    for name, pct, color in health_data:
        status_text = "Healthy" if pct >= 85 else "Anomaly Shift Detected"
        text_color = COLORS['emerald'] if pct >= 85 else COLORS['warning']

        st.markdown(f"""
        <div class="health-bar-container">
            <div class="health-bar-label">
                <span>{name}</span>
                <span style="color: {text_color}; font-family: 'JetBrains Mono', monospace;">
                    {pct}% — {status_text}</span>
            </div>
            <div class="health-bar-track">
                <div class="health-bar-fill" style="width: {pct}%; background: {color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Warning alert
    st.markdown(f"""
    <div class="alert-box alert-warning" style="margin-top: 12px;">
        ⚠️ <strong>Warning:</strong> Isolation Forest flags an increase in unclassified anomalies.
        Retraining recommended.
    </div>
    """, unsafe_allow_html=True)


# ================================================================
# Verdict Display — Transaction Result
# ================================================================
def render_verdict(result: dict, threshold: float):
    """Render the transaction verdict box (approved/blocked/review)."""
    score = result.get("risk_score", 0)
    decision = result.get("decision", "SAFE")
    latency  = result.get("latency_ms", 0)
    mode     = result.get("mode", "live")

    pct_str = f"{score * 100:.1f}%"

    if decision == "FRAUD":
        st.markdown(f"""
        <div class="verdict-blocked">
            <div style="font-size: 22px; font-weight: 700; color: {COLORS['crimson']};
                        margin-bottom: 4px;">
                🚫 BLOCKED — High Fraud Risk</div>
            <div style="font-size: 13px; color: {COLORS['text_secondary']};">
                Risk Score: {pct_str} | Latency: {latency:.0f}ms | Mode: {mode}</div>
        </div>
        """, unsafe_allow_html=True)
    elif score >= threshold * 0.7:
        st.markdown(f"""
        <div class="verdict-review">
            <div style="font-size: 22px; font-weight: 700; color: {COLORS['warning']};
                        margin-bottom: 4px;">
                ⚠️ REVIEW — Elevated Risk Detected</div>
            <div style="font-size: 13px; color: {COLORS['text_secondary']};">
                Risk Score: {pct_str} | Latency: {latency:.0f}ms | Mode: {mode}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="verdict-approved">
            <div style="font-size: 22px; font-weight: 700; color: {COLORS['emerald']};
                        margin-bottom: 4px;">
                ✅ APPROVED — Safe Transaction</div>
            <div style="font-size: 13px; color: {COLORS['text_secondary']};">
                Risk Score: {pct_str} | Latency: {latency:.0f}ms | Mode: {mode}</div>
        </div>
        """, unsafe_allow_html=True)


# ================================================================
# Risk Factors Display
# ================================================================
def render_risk_factors(factors: list):
    """Render risk factor list."""
    if not factors:
        return

    st.markdown(
        '<div class="section-header" style="margin-top: 16px;">Risk Factors</div>',
        unsafe_allow_html=True,
    )

    factors_html = ""
    for f in factors:
        factors_html += f"""
        <div style="padding: 6px 10px; font-size: 12px;
                    color: {COLORS['text_secondary']};
                    border-left: 2px solid {COLORS['border']};
                    margin-bottom: 4px;">{f}</div>
        """

    st.markdown(factors_html, unsafe_allow_html=True)


# ================================================================
# Footer
# ================================================================
def render_footer():
    """Render institutional footer."""
    st.markdown(f"""
    <div class="footer">
        <div class="footer-text">FraudGuard Institutional Risk Platform</div>
        <div class="footer-engine">
            Confidential · Internal Use Only · © 2026 FraudGuard Banking Systems
        </div>
    </div>
    """, unsafe_allow_html=True)
