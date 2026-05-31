# dashboard/components/sidebar.py
"""
Sidebar — Navigation and system info panel.
"""

import streamlit as st
from datetime import datetime
from dashboard.styles.theme import COLORS
from services.data_loader import get_artifact_status

def render_sidebar():
    """Render the sidebar navigation and return the selected page."""
    with st.sidebar:
        # ── Brand Header ──
        st.markdown(f"""
        <div class="fg-brand">
            <div class="fg-shield">🛡️</div>
            <div>
                <div class="fg-brand-title">FraudGuard AI</div>
                <div class="fg-brand-subtitle">Enterprise Detection</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="fg-profile">
            <div class="fg-avatar">👤</div>
            <div>
                <div class="fg-profile-name">
                </div>
                <div class="fg-profile-meta"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Navigation ──
        st.markdown('<div class="fg-sidebar-label">Navigation</div>',
                    unsafe_allow_html=True)

        page = st.radio(
            label="nav",
            options=[
                "Real-time Verification",
                "Executive Batch Dashboard",
            ],
            label_visibility="collapsed",
        )

        # ── System Status ──
        status = get_artifact_status()
        model_items = [
            ("XGB Heavy", "xgb_heavy"),
            ("LGBM Heavy", "lgbm_heavy"),
            ("Iso Forest", "iso_forest"),
            ("XGB Light", "xgb_light"),
            ("LGBM Light", "lgbm_light"),
        ]
        model_rows = "".join(
            (
                f'<div class="fg-model-row"><span>{name}</span>'
                f'<strong>● {"Online" if status.get(key, False) else "Missing"}</strong></div>'
            )
            for name, key in model_items
        )
        system_online = bool(status.get("inference_backend"))
        st.markdown(f"""
        <div class="fg-status-box">
            <div class="fg-sidebar-label">System Status</div>
            <div class="fg-status-title">
                System Status: <span>{'🟢 Optimal Performance' if system_online else '🟠 Degraded Mode'}</span>
            </div>
            {model_rows}
        </div>
        """, unsafe_allow_html=True)

        # ── Timestamp ──
        st.markdown(f"""
        <div style="margin-top: 18px; padding-top: 12px;
                    border-top: 1px solid {COLORS['border']};">
            <div style="font-size: 10px; color: {COLORS['text_muted']};">
                Last Update: {datetime.now().strftime('%d %b %Y, %H:%M')}</div>
        </div>
        """, unsafe_allow_html=True)

    return page
