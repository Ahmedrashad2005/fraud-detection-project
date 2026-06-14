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
    """Operational status is now integrated into the page hero."""
    return None


def render_page_intro(title: str, subtitle: str, breadcrumb: str = "Risk Operations") -> None:
    status = get_artifact_status()
    engine_ok = bool(status.get("inference_backend"))
    realtime_ok = is_realtime_ready()
    engine_label = "Live" if engine_ok else "Degraded"
    scoring_label = "Ready" if realtime_ok else "Standby"
    engine_class = "hero-chip-ok" if engine_ok else "hero-chip-warn"
    scoring_class = "hero-chip-ok" if realtime_ok else "hero-chip-warn"

    st.markdown(f"""
    <div class="bk-page-hero">
        <div class="bk-hero-copy">
            <div class="bk-breadcrumb">{breadcrumb}</div>
            <h1 class="bk-page-title">{title}</h1>
            <p class="bk-page-subtitle">{subtitle}</p>
        </div>
        <div class="bk-hero-status">
            <span class="hero-chip {engine_class}"><i></i>Risk Engine {engine_label}</span>
            <span class="hero-chip {scoring_class}"><i></i>Scoring {scoring_label}</span>
            <span class="hero-chip hero-chip-soft"><i></i>Latency &lt; 50ms</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_empty_state(title: str, body: str, details: list[str] | None = None) -> None:
    detail_html = ""
    if details:
        detail_html = '<div class="bk-empty-chips">' + "".join(
            f"<span>{item}</span>" for item in details
        ) + "</div>"

    st.markdown(f"""
    <div class="bk-empty-state">
        <div class="bk-empty-icon">FG</div>
        <div>
            <div class="bk-empty-title">{title}</div>
            <div class="bk-empty-body">{body}</div>
            {detail_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_explanation_panel(explanation: dict) -> None:
    """Bank-style SHAP factor breakdown rendered via st.components.v1.html."""
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
    c = COLORS
    # Calculate height based on number of factors (each row ~70px + header ~60px + padding)
    panel_height = len(factors) * 70 + 80

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'DM Sans', 'Inter', sans-serif;
            background: transparent;
            color: {c['text_primary']};
        }}
        .bk-panel {{
            background: linear-gradient(165deg, rgba(15, 40, 71, 0.92), rgba(11, 31, 58, 0.95));
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 22px 24px;
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        }}
        .bk-panel-head {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid {c['border']};
        }}
        .bk-panel-title {{
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {c['gold_light']};
        }}
        .bk-panel-tag {{
            font-size: 10px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 4px;
            color: {c['text_muted']};
            border: 1px solid {c['border']};
            background: rgba(0,0,0,0.2);
        }}
        .bk-factor-row {{ margin-bottom: 14px; }}
        .bk-factor-head {{
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            margin-bottom: 4px;
        }}
        .bk-factor-name {{ color: {c['text_secondary']}; font-weight: 600; }}
        .bk-factor-impact {{
            font-family: 'IBM Plex Mono', monospace;
            color: {c['gold_light']};
        }}
        .bk-factor-bar-track {{
            height: 4px;
            background: rgba(0,0,0,0.25);
            border-radius: 2px;
            overflow: hidden;
        }}
        .bk-factor-bar-fill {{ height: 100%; border-radius: 2px; }}
        .bk-bar-risk {{ background: linear-gradient(90deg, {c['crimson']}, #E8A0A0); }}
        .bk-bar-safe {{ background: linear-gradient(90deg, {c['emerald']}, #7FD4A8); }}
        .bk-factor-meta {{
            margin-top: 4px;
            font-size: 10px;
            color: {c['text_muted']};
        }}
    </style>
    </head>
    <body>
        <div class="bk-panel bk-explain-panel">
            <div class="bk-panel-head">
                <span class="bk-panel-title">Decision Rationale</span>
                <span class="bk-panel-tag">{method} Analysis</span>
            </div>
            {rows}
        </div>
    </body>
    </html>
    """
    import streamlit.components.v1 as components
    components.html(html_content, height=panel_height, scrolling=False)
