# dashboard/components/charts.py
"""
Charts — All Plotly chart rendering functions.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.styles.theme import COLORS, PLOTLY_LAYOUT
from features.build_features import REF_DATE

BANK = {
    "panel": "#0F2847",
    "plot": "#0A1E36",
    "grid": "rgba(197, 165, 114, 0.08)",
    "teal": "#3D8B8B",
    "gold": "#C5A572",
    "green": "#2D8A62",
    "red": "#C45C5C",
    "blue": "#5B8DEF",
    "muted": "#6B7F94",
}


def _render_chart_empty(title: str, body: str) -> None:
    st.markdown(f"""
    <div class="bk-chart-empty">
        <div>
            <strong>{title}</strong>
            <span>{body}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _bank_layout(height: int):
    """Shared executive banking chart layout."""
    layout = {
        **PLOTLY_LAYOUT,
        "height": height,
        "paper_bgcolor": BANK["panel"],
        "plot_bgcolor": BANK["plot"],
        "font": dict(family="Inter, sans-serif", color="#D8DEE3", size=12),
        "margin": dict(l=44, r=24, t=28, b=40),
        "xaxis": dict(
            gridcolor=BANK["grid"],
            zerolinecolor=BANK["grid"],
            tickfont=dict(color="#AAB4BA", size=10),
            title=dict(font=dict(color="#BDC3C7", size=11)),
        ),
        "yaxis": dict(
            gridcolor="rgba(189, 195, 199, 0.04)",
            zerolinecolor=BANK["grid"],
            tickfont=dict(color="#D8DEE3", size=11),
            title=dict(font=dict(color="#BDC3C7", size=11)),
        ),
        "hoverlabel": dict(
            bgcolor="#20262B",
            bordercolor="#3B474F",
            font_size=12,
            font_family="Inter, sans-serif",
        ),
    }
    return layout


def _fraud_column(df: pd.DataFrame) -> str | None:
    if df is None:
        return None
    if "prediction" in df.columns:
        return "prediction"
    if "isFraud" in df.columns:
        return "isFraud"
    return None


# ================================================================
# Fraud by Card Brand — Horizontal Bar
# ================================================================
def render_fraud_by_card_brand(df: pd.DataFrame):
    """Render horizontal bar chart of fraud rate by card brand."""
    st.markdown(
        '<div class="section-header">Fraud Rate by Card Brand</div>',
        unsafe_allow_html=True,
    )

    fraud_col = _fraud_column(df)
    if df is None or "card4" not in df.columns or not fraud_col:
        _render_chart_empty(
            "Card brand analysis unavailable",
            "Upload data with card4 and prediction columns to populate this view.",
        )
        return

    brand_stats = (
        df.groupby("card4")[fraud_col]
        .mean()
        .sort_values(ascending=True)
        .reset_index()
    )
    brand_stats.columns = ["Card Brand", "Fraud Rate"]
    brand_stats["Fraud Rate %"] = (brand_stats["Fraud Rate"] * 100).round(2)

    # Color mapping
    colors = []
    max_rate = brand_stats["Fraud Rate %"].max()
    for rate in brand_stats["Fraud Rate %"]:
        if rate == max_rate:
            colors.append(BANK["red"])
        elif rate > 4.0:
            colors.append(BANK["gold"])
        else:
            colors.append(BANK["green"])

    fig = go.Figure(go.Bar(
        x=brand_stats["Fraud Rate %"],
        y=brand_stats["Card Brand"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1f}%" for v in brand_stats["Fraud Rate %"]],
        textposition="auto",
        textfont=dict(size=12, family="JetBrains Mono", color="#FFFFFF"),
        marker_line=dict(width=0),
    ))

    fig.update_layout(**_bank_layout(300), xaxis_title="Fraud Rate (%)",
                      yaxis_title="Card Brand", showlegend=False)

    st.plotly_chart(fig, use_container_width=True, key="fraud_by_brand")

    # Highlight max risk brand
    max_brand = brand_stats.loc[brand_stats["Fraud Rate %"].idxmax(), "Card Brand"]
    if brand_stats["Fraud Rate %"].max() >= 5:
        st.markdown(f"""
        <div class="bank-alert bank-alert-risk">
            <strong>{max_brand}</strong> is the highest-risk card network in this batch.
        </div>
        """, unsafe_allow_html=True)


# ================================================================
# Device Type Distribution — Pie/Donut
# ================================================================
def render_device_distribution(df: pd.DataFrame):
    """Render fraud channel distribution by device type as a donut chart."""
    st.markdown(
        '<div class="section-header">Fraud Channels by Device Type</div>',
        unsafe_allow_html=True,
    )

    fraud_col = _fraud_column(df)
    if df is None or "DeviceType" not in df.columns or not fraud_col:
        _render_chart_empty(
            "Channel distribution unavailable",
            "Upload data with DeviceType and prediction columns to populate this view.",
        )
        return

    fraud_df = df[df[fraud_col] == 1]
    device_counts = fraud_df["DeviceType"].value_counts().reset_index()
    device_counts.columns = ["Device", "Count"]
    if device_counts.empty:
        _render_chart_empty(
            "No declined transactions in this batch",
            "Channel distribution appears after at least one transaction is flagged.",
        )
        return

    color_map = {
        "mobile":  BANK["red"],
        "desktop": BANK["teal"],
        "tablet":  BANK["gold"],
        "Mobile":  BANK["red"],
        "Desktop": BANK["teal"],
        "Tablet":  BANK["gold"],
    }
    device_colors = [
        color_map.get(d, COLORS['text_muted'])
        for d in device_counts["Device"]
    ]

    fig = go.Figure(go.Pie(
        labels=device_counts["Device"],
        values=device_counts["Count"],
        hole=0.5,
        marker=dict(colors=device_colors,
                    line=dict(color=BANK["panel"], width=3)),
        textinfo="label+percent",
        textfont=dict(size=11, family="Inter", color="#FFFFFF"),
        hoverinfo="label+value+percent",
    ))

    fig.update_layout(
        **_bank_layout(300),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="right",
            x=1.15,
            font=dict(size=11, color="#BDC3C7"),
        ),
    )

    st.plotly_chart(fig, use_container_width=True, key="device_dist")

    mobile_count = int(device_counts.loc[
        device_counts["Device"].astype(str).str.lower() == "mobile", "Count"
    ].sum())
    total_count = int(device_counts["Count"].sum())
    if total_count and mobile_count / total_count >= 0.6:
        st.markdown("""
        <div class="bank-alert bank-alert-review">
            Mobile channel concentration is elevated in the declined queue.
        </div>
        """, unsafe_allow_html=True)


# ================================================================
# Temporal Fraud Heatmap
# ================================================================
def render_temporal_heatmap(df: pd.DataFrame = None):
    """Render temporal fraud heatmap: days of week × hours of day."""
    st.markdown(
        '<div class="section-header">Temporal Fraud Heatmap</div>',
        unsafe_allow_html=True,
    )

    days_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    fraud_col = _fraud_column(df)
    if df is not None and fraud_col and (
        ("hour" not in df.columns or "day_of_week" not in df.columns)
        and "TransactionDT" in df.columns
    ):
        df = df.copy()
        tx_seconds = pd.to_numeric(df["TransactionDT"], errors="coerce")
        dt = pd.to_datetime(REF_DATE) + pd.to_timedelta(tx_seconds, unit="s")
        df["hour"] = dt.dt.hour
        df["day_of_week"] = dt.dt.dayofweek

    if not (df is not None and "hour" in df.columns and "day_of_week" in df.columns and fraud_col):
        _render_chart_empty(
            "Temporal heatmap unavailable",
            "Upload data with TransactionDT or hour and day_of_week fields to populate this view.",
        )
        return

    fraud_df = df[df[fraud_col] == 1]
    if fraud_df.empty and "risk_score" in df.columns:
        pivot = (
            df.groupby(["day_of_week", "hour"])["risk_score"]
            .mean()
            .mul(100)
            .round(1)
            .unstack(fill_value=0)
        )
        colorbar_title = "Avg Risk"
        hover_text = "Day: %{y}<br>Hour: %{x}:00<br>Avg Risk: %{z:.1f}%<extra></extra>"
    else:
        pivot = fraud_df.groupby(["day_of_week", "hour"]).size().unstack(fill_value=0)
        colorbar_title = "Count"
        hover_text = "Day: %{y}<br>Hour: %{x}:00<br>Fraud Count: %{z}<extra></extra>"

    # Ensure all hours and days
    pivot = pivot.reindex(index=range(7), columns=range(24), fill_value=0)
    z_data = pivot.values

    fig = go.Figure(go.Heatmap(
        z=z_data,
        x=list(range(24)),
        y=days_labels,
        colorscale=[
            [0.0,  BANK["plot"]],
            [0.35, "#25453D"],
            [0.68, BANK["gold"]],
            [1.0,  BANK["red"]],
        ],
        hovertemplate=hover_text,
        colorbar=dict(
            title=dict(text=colorbar_title, font=dict(size=10)),
            tickfont=dict(size=9),
            len=0.8,
        ),
    ))

    fig.update_layout(**_bank_layout(320), xaxis_title="Hour of Day",
                      yaxis_title="")
    fig.update_xaxes(dtick=2, tickfont=dict(size=10, color="#AAB4BA"))
    fig.update_yaxes(tickfont=dict(size=10, color="#D8DEE3"))

    st.plotly_chart(fig, use_container_width=True, key="temporal_heatmap")


# ================================================================
# Model Drift & Infrastructure Health
# ================================================================
def render_model_drift_infrastructure(status: dict = None, drift_report: dict | None = None):
    """Render infrastructure health and optional data-drift scores."""
    st.markdown(
        '<div class="section-header">Model Drift & Infrastructure Health</div>',
        unsafe_allow_html=True,
    )

    status = status or {}
    drift_report = drift_report or {}
    drift_health = drift_report.get("overall_health")

    labels = ["XGB Heavy", "LGBM Heavy", "Isolation Forest", "Feature Pipeline", "Artifact Store"]
    values = [
        96 if status.get("xgb_heavy", True) else 28,
        94 if status.get("lgbm_heavy", True) else 28,
        82 if status.get("iso_forest", True) else 25,
        91 if status.get("all_features", True) and status.get("manual_features", True) else 35,
        95 if status.get("inference_backend", True) else 30,
    ]

    if drift_health is not None:
        labels.append("Data Drift Index")
        values.append(float(drift_health))
    colors = [BANK["green"] if value >= 85 else BANK["gold"] if value >= 65 else BANK["red"] for value in values]

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{value}%" for value in values],
        textposition="auto",
        textfont=dict(size=12, family="JetBrains Mono", color="#FFFFFF"),
        hovertemplate="%{y}<br>Health: %{x}%<extra></extra>",
    ))

    fig.update_layout(
        **_bank_layout(320),
        xaxis_title="Health Score",
        yaxis_title="",
        showlegend=False,
    )
    fig.update_xaxes(range=[0, 100], ticksuffix="%")

    st.plotly_chart(fig, use_container_width=True, key="model_drift_infra")


# ================================================================
# Fraud Risk Gauge — Single Transaction
# ================================================================
def render_risk_gauge(score: float, threshold: float = 0.50):
    """Render a premium Plotly gauge meter for fraud risk score."""

    if score >= threshold:
        bar_color = COLORS['crimson']
    elif score >= threshold * 0.7:
        bar_color = COLORS['warning']
    else:
        bar_color = COLORS['emerald']

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score * 100,
        number=dict(
            suffix="%",
            font=dict(size=36, family="JetBrains Mono", color=bar_color),
        ),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1,
                      tickcolor=COLORS['text_muted'],
                      tickfont=dict(size=9)),
            bar=dict(color=bar_color, thickness=0.3),
            bgcolor=COLORS['bg_primary'],
            borderwidth=1,
            bordercolor=COLORS['border'],
            steps=[
                dict(range=[0, threshold * 70], color=COLORS['emerald_bg']),
                dict(range=[threshold * 70, threshold * 100],
                     color=COLORS['warning_bg']),
                dict(range=[threshold * 100, 100],
                     color=COLORS['crimson_bg']),
            ],
            threshold=dict(
                line=dict(color=COLORS['text_primary'], width=2),
                thickness=0.8,
                value=threshold * 100,
            ),
        ),
        title=dict(
            text="Fraud Risk Score",
            font=dict(size=13, color=COLORS['text_secondary']),
        ),
    ))

    gauge_layout = {**PLOTLY_LAYOUT, "margin": dict(l=30, r=30, t=60, b=20)}
    fig.update_layout(
        **gauge_layout,
        height=260,
    )

    st.plotly_chart(fig, use_container_width=True, key="risk_gauge")


# ================================================================
# SHAP Feature Impact Bars
# ================================================================
def render_shap_bars(shap_values, feature_names, top_n=10):
    """Render SHAP feature impact horizontal bar chart."""
    st.markdown(
        '<div class="section-header">🔬 SHAP Feature Impact Analysis</div>',
        unsafe_allow_html=True,
    )

    if shap_values is None or feature_names is None:
        st.markdown(f"""
        <div class="alert-box alert-info">
            ℹ️ SHAP explainability artifacts are not available.
            Run the pipeline with SHAP enabled to generate feature impact analysis.
        </div>
        """, unsafe_allow_html=True)
        return

    # Sort by absolute impact
    impact = pd.DataFrame({
        "Feature": feature_names,
        "SHAP Value": shap_values,
    })
    impact["Abs"] = impact["SHAP Value"].abs()
    impact = impact.nlargest(top_n, "Abs").sort_values("SHAP Value")

    colors = [
        COLORS['crimson'] if v > 0 else COLORS['emerald']
        for v in impact["SHAP Value"]
    ]

    fig = go.Figure(go.Bar(
        x=impact["SHAP Value"],
        y=impact["Feature"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:+.3f}" for v in impact["SHAP Value"]],
        textposition="outside",
        textfont=dict(size=10, family="JetBrains Mono"),
    ))

    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=max(250, top_n * 30),
        xaxis_title="SHAP Value (→ Fraud | ← Safe)",
        yaxis_title="",
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True, key="shap_bars")

    # Legend
    st.markdown(f"""
    <div style="display: flex; gap: 16px; font-size: 10px;
                color: {COLORS['text_muted']}; margin-top: -8px;">
        <span>🔴 Positive = pushes toward fraud</span>
        <span>🟢 Negative = pushes toward safety</span>
    </div>
    """, unsafe_allow_html=True)
