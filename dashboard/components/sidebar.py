# dashboard/components/sidebar.py
"""Institutional sidebar navigation."""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

def render_sidebar() -> str:
    try:
        current = st.query_params.get("view", "dashboard")
    except Exception:
        current = "dashboard"
    if current == "overview":
        current = "dashboard"
    if current not in {"dashboard", "realtime", "batch", "queue"}:
        current = "dashboard"

    with st.sidebar:
        dashboard_cls = "is-active" if current == "dashboard" else ""
        realtime_cls = "is-active" if current == "realtime" else ""
        batch_cls = "is-active" if current == "batch" else ""
        queue_cls = "is-active" if current == "queue" else ""
        st.markdown(f"""
        <nav class="fg-side-nav" aria-label="Primary navigation">
            <a class="fg-side-button {dashboard_cls}" href="?view=dashboard" target="_self">
                <span class="fg-side-kicker">01</span>
                <span>Dashboard</span>
            </a>
            <a class="fg-side-button {realtime_cls}" href="?view=realtime" target="_self">
                <span class="fg-side-kicker">02</span>
                <span>Authorization</span>
            </a>
            <a class="fg-side-button {batch_cls}" href="?view=batch" target="_self">
                <span class="fg-side-kicker">03</span>
                <span>Executive Batch</span>
            </a>
            <div class="fg-side-divider"></div>
            <a class="fg-side-button {queue_cls}" href="?view=queue" target="_self">
                <span class="fg-side-kicker">04</span>
                <span>Review Queue</span>
            </a>
        </nav>
        """, unsafe_allow_html=True)

    return current
