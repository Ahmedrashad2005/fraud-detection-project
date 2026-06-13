"""
Institutional layout chrome — headers, trust ribbon, page intros.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
import secrets

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from dashboard.styles.theme import COLORS
from services.data_loader import get_artifact_status, is_realtime_ready


def _session_id() -> str:
    if "bk_session_id" not in st.session_state:
        st.session_state["bk_session_id"] = secrets.token_hex(4).upper()
    return st.session_state["bk_session_id"]


def render_institutional_header() -> None:
    """Top banking console header with compliance strip."""
    status = get_artifact_status()
    online = bool(status.get("inference_backend"))
    realtime = is_realtime_ready()
    now = datetime.now(timezone.utc).strftime("%d %b %Y · %H:%M UTC")
    session = _session_id()

    engine_state = "Risk Engine Active" if online else "Degraded — Artifacts Missing"
    engine_class = "bk-pill-live" if online else "bk-pill-warn"
    rt_class = "bk-pill-live" if realtime else "bk-pill-neutral"

    st.markdown(f"""
    <header class="bk-header">
        <div class="bk-header-top">
            <div class="bk-brand-block">
                <div class="bk-logo-mark">FG</div>
                <div>
                    <div class="bk-institution">FraudGuard</div>
                    <div class="bk-platform">Institutional Fraud &amp; Payment Risk Console</div>
                </div>
            </div>
            <div class="bk-header-meta">
                <div class="bk-meta-item">
                    <span class="bk-meta-label">Session</span>
                    <span class="bk-meta-value">#{session}</span>
                </div>
                <div class="bk-meta-item">
                    <span class="bk-meta-label">Timestamp</span>
                    <span class="bk-meta-value">{now}</span>
                </div>
                <div class="bk-meta-item">
                    <span class="bk-meta-label">Environment</span>
                    <span class="bk-meta-value">Production Sandbox</span>
                </div>
            </div>
        </div>
        <div class="bk-header-bottom">
            <div class="bk-pills">
                <span class="bk-pill {engine_class}">{engine_state}</span>
                <span class="bk-pill {rt_class}">Real-time Scoring {'Online' if realtime else 'Standby'}</span>
                <span class="bk-pill bk-pill-gold">Settlement Desk · Tier-1</span>
            </div>
            <div class="bk-compliance">
                <span class="bk-badge">PCI-DSS Aligned</span>
                <span class="bk-badge">SOC 2 Controls</span>
                <span class="bk-badge">AES-256 Transit</span>
                <span class="bk-badge">Audit Trail Enabled</span>
            </div>
        </div>
    </header>
    """, unsafe_allow_html=True)


def render_trust_ribbon() -> None:
    """Thin operational status ribbon below header."""
    st.markdown(f"""
    <div class="bk-trust-ribbon">
        <div class="bk-trust-item"><span class="bk-dot bk-dot-green"></span>Core Ledger Sync</div>
        <div class="bk-trust-item"><span class="bk-dot bk-dot-green"></span>AML Screening Pipeline</div>
        <div class="bk-trust-item"><span class="bk-dot bk-dot-green"></span>Authorization Gateway</div>
        <div class="bk-trust-item"><span class="bk-dot bk-dot-gold"></span>Model Governance Watch</div>
        <div class="bk-trust-item"><span class="bk-dot bk-dot-green"></span>Median Latency &lt; 50ms</div>
    </div>
    """, unsafe_allow_html=True)


def render_page_intro(title: str, subtitle: str, breadcrumb: str = "Risk Operations") -> None:
    st.markdown(f"""
    <div class="bk-page-intro">
        <div class="bk-breadcrumb">{breadcrumb} / {title}</div>
        <h1 class="bk-page-title">{title}</h1>
        <p class="bk-page-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_explanation_panel(explanation: dict) -> None:
    """Bank-style SHAP factor breakdown."""
    factors = explanation.get("factors") or []
    if not factors:
        return

    rows = ""
    max_impact = max(abs(f.get("impact", 0)) for f in factors) or 1
    for f in factors:
        impact = float(f.get("impact", 0))
        width = min(100, abs(impact) / max_impact * 100)
        bar_class = "bk-bar-risk" if impact > 0 else "bk-bar-safe"
        rows += f"""
        <div class="bk-factor-row">
            <div class="bk-factor-head">
                <span class="bk-factor-name">{f.get('feature', '')}</span>
                <span class="bk-factor-impact">{impact:+.4f}</span>
            </div>
            <div class="bk-factor-bar-track">
                <div class="bk-factor-bar-fill {bar_class}" style="width:{width:.0f}%"></div>
            </div>
            <div class="bk-factor-meta">Value: {f.get('value', '—')} · {f.get('direction', '')}</div>
        </div>
        """

    method = explanation.get("method", "shap").upper()
    st.markdown(f"""
    <div class="bk-panel bk-explain-panel">
        <div class="bk-panel-head">
            <span class="bk-panel-title">Decision Rationale</span>
            <span class="bk-panel-tag">{method} Analysis</span>
        </div>
        {rows}
    </div>
    """, unsafe_allow_html=True)
