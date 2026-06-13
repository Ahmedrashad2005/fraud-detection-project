# dashboard/components/kpi_cards.py
"""
KPI Metric Cards — Premium metric card rendering.
"""

import streamlit as st
from dashboard.styles.theme import COLORS


def render_metric_card(label: str, value: str, sub: str = "",
                       color: str = None, icon: str = "", tone: str = "neutral"):
    """Render a single premium metric card."""
    val_color = color or COLORS['text_primary']
    icon_html = f'<span style="font-size: 14px; margin-right: 4px;">{icon}</span>' if icon else ''

    return f"""
    <div class="metric-card bank-metric-card bank-tone-{tone}">
        <div class="metric-label">{icon_html}{label}</div>
        <div class="metric-value" style="color: {val_color};">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>
    """


def render_kpi_row(total_transactions: int, fraud_count: int,
                   fraud_rate: float, protected_amount: float,
                   auc_score: float = 0.942):
    """Render the executive batch KPI row."""

    col1, col2, col3, col4 = st.columns(4, gap="small")

    with col1:
        st.markdown(render_metric_card(
            label="Model Discrimination (AUC)",
            value=f"{auc_score * 100:.1f}%",
            sub="Held-out test ensemble",
            color="#E8EDF2",
            icon="◈",
            tone="ledger",
        ), unsafe_allow_html=True)

    with col2:
        rate_color = COLORS['crimson'] if fraud_rate > 5 else COLORS['gold']
        st.markdown(render_metric_card(
            label="Decline Rate",
            value=f"{fraud_rate:.2f}%",
            sub=f"{fraud_count:,} transactions declined",
            color=rate_color,
            icon="⚑",
            tone="risk",
        ), unsafe_allow_html=True)

    with col3:
        st.markdown(render_metric_card(
            label="Portfolio Volume",
            value=f"{total_transactions:,}",
            sub="Transactions in screening batch",
            color="#C5A572",
            icon="▤",
            tone="review",
        ), unsafe_allow_html=True)

    with col4:
        if protected_amount >= 1_000_000:
            amt_str = f"${protected_amount / 1_000_000:.1f}M"
        elif protected_amount >= 1_000:
            amt_str = f"${protected_amount / 1_000:.0f}K"
        else:
            amt_str = f"${protected_amount:,.0f}"

        st.markdown(render_metric_card(
            label="Exposure Mitigated",
            value=amt_str,
            sub="Declined fraudulent volume",
            color="#2D8A62",
            icon="◆",
            tone="safe",
        ), unsafe_allow_html=True)
