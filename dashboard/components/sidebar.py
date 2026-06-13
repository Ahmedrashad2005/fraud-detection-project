# dashboard/components/sidebar.py
"""Institutional sidebar navigation."""

import sys
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from dashboard.styles.theme import COLORS
from services.data_loader import get_artifact_status


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("""
        <div class="bk-sidebar-brand">
            <div class="bk-sidebar-logo">FG</div>
            <div>
                <div class="bk-sidebar-title">FraudGuard</div>
                <div class="bk-sidebar-sub">Tier-1 Risk Desk</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="bk-officer-card">
            <div class="bk-officer-avatar">👤</div>
            <div>
                <div class="bk-officer-name">A. Hassan</div>
                <div class="bk-officer-role">Senior Fraud Analyst</div>
                <div class="bk-officer-role">Payment Risk · L2</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="bk-nav-label">Operations</div>', unsafe_allow_html=True)
        page = st.radio(
            label="nav",
            options=[
                "Payment Authorization",
                "Portfolio Surveillance",
            ],
            label_visibility="collapsed",
        )

        st.markdown('<div class="bk-nav-label">Desk Utilities</div>', unsafe_allow_html=True)
        st.caption("Threshold policies sync from model registry.")
        st.markdown('<div class="bk-nav-label">Infrastructure</div>', unsafe_allow_html=True)

        status = get_artifact_status()
        models = [
            ("Authorization (XGB)", "xgb_light"),
            ("Authorization (LGBM)", "lgbm_light"),
            ("Batch Ensemble (XGB)", "xgb_heavy"),
            ("Batch Ensemble (LGBM)", "lgbm_heavy"),
            ("Anomaly Engine (ISO)", "iso_forest"),
        ]
        rows = ""
        for name, key in models:
            ok = status.get(key, False)
            cls = "bk-online" if ok else "bk-offline"
            label = "Online" if ok else "Offline"
            rows += f'<div class="bk-model-row"><span>{name}</span><strong class="{cls}">{label}</strong></div>'

        system_ok = status.get("inference_backend", False)
        st.markdown(f"""
        <div class="bk-status-box">
            <div class="bk-nav-label" style="margin-top:0">Model Registry</div>
            <div style="font-size:12px;font-weight:700;color:{COLORS['gold_light']};margin-bottom:10px;">
                {'● Systems Nominal' if system_ok else '● Degraded Mode'}
            </div>
            {rows}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-top:20px;padding-top:14px;border-top:1px solid {COLORS['border']};">
            <div style="font-size:9px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:{COLORS['text_muted']};">
                Last Registry Sync
            </div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:{COLORS['text_secondary']};margin-top:4px;">
                {datetime.now().strftime('%d %b %Y · %H:%M')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    mapping = {
        "Payment Authorization": "realtime",
        "Portfolio Surveillance": "batch",
    }
    return mapping.get(page, "realtime")
