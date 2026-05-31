"""
Lightweight Streamlit chart components.

Plotly, heatmaps, and batch analytics are intentionally excluded. Components
use native Streamlit primitives and simple HTML for fast architecture prep.
"""

from __future__ import annotations

import html
from typing import Iterable, Mapping

import pandas as pd
import streamlit as st


CHART_CSS = """
<style>
.fg-chart-panel {
    padding: 16px;
    border-radius: 8px;
    border: 1px solid rgba(148, 163, 184, 0.20);
    background: rgba(20, 25, 30, 0.92);
}
.fg-chart-title {
    margin-bottom: 12px;
    color: #F8FAFC;
    font-size: 14px;
    font-weight: 850;
}
.fg-risk-meter {
    position: relative;
    height: 16px;
    overflow: hidden;
    border-radius: 999px;
    background: linear-gradient(90deg, #2ECC71 0%, #F39C12 58%, #E74C3C 100%);
    border: 1px solid rgba(255, 255, 255, 0.16);
}
.fg-risk-pin {
    position: absolute;
    top: -4px;
    width: 3px;
    height: 24px;
    background: #FFFFFF;
    box-shadow: 0 0 12px rgba(255, 255, 255, 0.7);
}
.fg-threshold-pin {
    position: absolute;
    top: 0;
    width: 2px;
    height: 16px;
    background: rgba(10, 14, 18, 0.82);
}
.fg-meter-labels {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    margin-top: 8px;
    color: #A8B3BD;
    font-size: 11px;
    font-weight: 700;
}
.fg-factor-row {
    display: grid;
    grid-template-columns: minmax(120px, 0.34fr) 1fr minmax(52px, auto);
    gap: 10px;
    align-items: center;
    margin: 8px 0;
}
.fg-factor-name {
    color: #D8DEE3;
    overflow-wrap: anywhere;
    font-size: 12px;
    font-weight: 750;
}
.fg-factor-track {
    height: 10px;
    overflow: hidden;
    border-radius: 999px;
    background: rgba(148, 163, 184, 0.16);
}
.fg-factor-fill {
    height: 100%;
    border-radius: 999px;
    background: #3498DB;
}
.fg-factor-value {
    color: #A8B3BD;
    font-family: "JetBrains Mono", "IBM Plex Mono", monospace;
    font-size: 11px;
    text-align: right;
}
@media (max-width: 640px) {
    .fg-factor-row { grid-template-columns: 1fr; gap: 5px; }
    .fg-factor-value { text-align: left; }
}
</style>
"""


def _safe_text(value: object) -> str:
    return html.escape("" if value is None else str(value))


def _bounded_float(value: object, default: float = 0.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = default
    return min(max(numeric, 0.0), 1.0)


def render_risk_meter(score: float, threshold: float = 0.50, title: str = "Transaction Risk") -> None:
    """Render a native HTML risk meter for a supplied single score."""
    bounded_score = _bounded_float(score)
    bounded_threshold = _bounded_float(threshold, 0.5)
    score_left = bounded_score * 100
    threshold_left = bounded_threshold * 100

    st.markdown(CHART_CSS, unsafe_allow_html=True)
    st.markdown(
        f"""
        <section class="fg-chart-panel">
            <div class="fg-chart-title">{_safe_text(title)}</div>
            <div class="fg-risk-meter" aria-label="{_safe_text(title)}">
                <div class="fg-threshold-pin" style="left: calc({threshold_left:.2f}% - 1px);"></div>
                <div class="fg-risk-pin" style="left: calc({score_left:.2f}% - 1px);"></div>
            </div>
            <div class="fg-meter-labels">
                <span>Low</span>
                <span>Threshold {threshold_left:.0f}%</span>
                <span>High</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_factor_bars(factors: Iterable[object], title: str = "Risk Factors") -> None:
    """Render lightweight factor bars from supplied explainability labels."""
    factor_list = [str(item).strip() for item in factors if str(item).strip()]
    if not factor_list:
        factor_list = ["No major risk factors detected"]

    st.markdown(CHART_CSS, unsafe_allow_html=True)

    rows = []
    total = len(factor_list)
    for index, factor in enumerate(factor_list, start=1):
        weight = max(24, int(100 - ((index - 1) / max(total, 1)) * 42))
        rows.append(
            f"""
            <div class="fg-factor-row">
                <div class="fg-factor-name">{_safe_text(factor)}</div>
                <div class="fg-factor-track">
                    <div class="fg-factor-fill" style="width: {weight}%;"></div>
                </div>
                <div class="fg-factor-value">{weight}%</div>
            </div>
            """
        )

    st.markdown(
        f"""
        <section class="fg-chart-panel">
            <div class="fg-chart-title">{_safe_text(title)}</div>
            {"".join(rows)}
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_model_score_bars(result: Mapping[str, object], title: str = "Model Scores") -> None:
    """Render individual model scores already returned by ``models.predict``."""
    score_keys = (
        ("xgb_score", "XGBoost Heavy"),
        ("lgbm_score", "LightGBM Heavy"),
        ("xgb_l_score", "XGBoost Light"),
        ("lgbm_l_score", "LightGBM Light"),
    )
    rows = []
    for key, label in score_keys:
        if key not in result:
            continue
        score = _bounded_float(result.get(key))
        rows.append(f"{label}: {score * 100:.1f}%")

    render_factor_bars(rows, title)


def render_table_preview(df: pd.DataFrame | None, max_rows: int = 50) -> None:
    """Render a bounded table preview with stable performance."""
    if df is None or df.empty:
        st.info("No table data is available.")
        return

    bounded_rows = max(1, min(int(max_rows or 50), 500))
    st.dataframe(df.head(bounded_rows), use_container_width=True, hide_index=True)
