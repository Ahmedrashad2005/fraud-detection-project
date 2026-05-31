"""
Reusable premium KPI cards for Streamlit.

These components render supplied values only. They do not compute business
analytics and do not own prediction logic.
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from typing import Iterable, Mapping

import streamlit as st


CARD_CSS = """
<style>
.fg-card-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin: 8px 0 18px;
}
.fg-kpi-card {
    min-height: 116px;
    padding: 16px 18px;
    border-radius: 8px;
    border: 1px solid rgba(148, 163, 184, 0.22);
    background: linear-gradient(180deg, rgba(24, 30, 36, 0.98), rgba(16, 20, 24, 0.98));
    box-shadow: 0 16px 38px rgba(0, 0, 0, 0.24), inset 0 1px 0 rgba(255, 255, 255, 0.04);
}
.fg-kpi-label {
    color: #A8B3BD;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0;
    text-transform: uppercase;
}
.fg-kpi-value {
    margin-top: 8px;
    color: #F8FAFC;
    overflow-wrap: anywhere;
    font-family: "JetBrains Mono", "IBM Plex Mono", monospace;
    font-size: 26px;
    font-weight: 800;
    line-height: 1.15;
}
.fg-kpi-caption {
    margin-top: 8px;
    color: #7F8A94;
    font-size: 12px;
    font-weight: 600;
    line-height: 1.4;
}
.fg-kpi-accent-safe { border-top: 3px solid #2ECC71; }
.fg-kpi-accent-risk { border-top: 3px solid #E74C3C; }
.fg-kpi-accent-review { border-top: 3px solid #F39C12; }
.fg-kpi-accent-info { border-top: 3px solid #3498DB; }
.fg-kpi-accent-muted { border-top: 3px solid #7F8A94; }
@media (max-width: 1000px) {
    .fg-card-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
    .fg-card-grid { grid-template-columns: 1fr; }
}
</style>
"""


@dataclass(frozen=True)
class KpiCard:
    label: str
    value: object
    caption: object = ""
    accent: str = "info"


def _safe_text(value: object) -> str:
    return html.escape("" if value is None else str(value))


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _accent(value: str) -> str:
    return value if value in {"safe", "risk", "review", "info", "muted"} else "info"


def render_kpi_cards(cards: Iterable[KpiCard]) -> None:
    """Render a responsive grid of KPI cards."""
    card_items = list(cards)
    if not card_items:
        return

    st.markdown(CARD_CSS, unsafe_allow_html=True)
    card_html = []
    for card in card_items:
        card_html.append(
            f"""
            <article class="fg-kpi-card fg-kpi-accent-{_accent(card.accent)}">
                <div class="fg-kpi-label">{_safe_text(card.label)}</div>
                <div class="fg-kpi-value">{_safe_text(card.value)}</div>
                <div class="fg-kpi-caption">{_safe_text(card.caption)}</div>
            </article>
            """
        )

    st.markdown(f'<section class="fg-card-grid">{"".join(card_html)}</section>', unsafe_allow_html=True)


def render_prediction_kpis(result: Mapping[str, object]) -> None:
    """Render operational cards from the ``models.predict.predict`` response."""
    if result.get("error"):
        render_kpi_cards(
            (
                KpiCard("Prediction", "Unavailable", "Inference returned an error", "risk"),
                KpiCard("Risk Score", "N/A", "No score produced", "muted"),
                KpiCard("Decision", "ERROR", "No verdict available", "risk"),
                KpiCard("Threshold", "N/A", "No active threshold", "muted"),
            )
        )
        return

    score = _safe_float(result.get("risk_score"))
    threshold = _safe_float(result.get("threshold"), 0.5)
    decision = str(result.get("decision", "UNKNOWN"))
    risk_level = str(result.get("risk_level", "UNKNOWN"))
    decision_accent = "risk" if decision == "FRAUD" else "safe"

    render_kpi_cards(
        (
            KpiCard("Risk Score", f"{score * 100:.1f}%", risk_level, decision_accent),
            KpiCard("Decision", decision, "Current threshold verdict", decision_accent),
            KpiCard("Threshold", f"{threshold * 100:.0f}%", "Active model threshold", "info"),
            KpiCard("Action", result.get("risk_action", "Review result"), "Recommended control", decision_accent),
        )
    )
