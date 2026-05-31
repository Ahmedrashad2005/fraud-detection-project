# dashboard/styles/theme.py

# ================================================================
# Color Palette — Cybersecurity Command Center
# ================================================================

COLORS = {
    "bg_primary":     "#121212",
    "bg_secondary":   "#181818",
    "bg_card":        "#1E1E1E",
    "bg_card_hover":  "#252525",
    "border":         "#343434",
    "border_accent":  "#464646",
    "text_primary":   "#FFFFFF",
    "text_secondary": "#BDC3C7",
    "text_muted":     "#7F8C8D",
    "emerald":        "#2ECC71",
    "emerald_dark":   "#27AE60",
    "emerald_bg":     "rgba(46, 204, 113, 0.08)",
    "crimson":        "#E74C3C",
    "crimson_dark":   "#C0392B",
    "crimson_bg":     "rgba(231, 76, 60, 0.08)",
    "warning":        "#F39C12",
    "warning_bg":     "rgba(243, 156, 18, 0.08)",
    "info":           "#3498DB",
    "info_bg":        "rgba(52, 152, 219, 0.08)",
    "accent_teal":    "#1ABC9C",
}


# ================================================================
# Plotly Dark Template Config
# ================================================================
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#1E1E1E",
    plot_bgcolor="#1E1E1E",
    font=dict(family="Inter, sans-serif", color="#E8E8E8", size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    hoverlabel=dict(
        bgcolor="#2A2A2A",
        bordercolor="#3A3A3A",
        font_size=12,
        font_family="Inter, sans-serif",
    ),
)


# ================================================================
# Inject Full CSS Theme
# ================================================================
def inject_theme():
    """Return the full CSS string for the Streamlit dashboard."""
    return f"""
    <style>
        /* ========== Google Font ========== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

        /* ========== Global Reset ========== */
        html, body, [data-testid="stAppViewContainer"] {{
            background:
                linear-gradient(rgba(255, 255, 255, 0.025) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.025) 1px, transparent 1px),
                radial-gradient(circle at 78% 18%, rgba(46, 204, 113, 0.08), transparent 28%),
                radial-gradient(circle at 90% 76%, rgba(231, 76, 60, 0.08), transparent 24%),
                {COLORS['bg_primary']} !important;
            background-size: 40px 40px, 40px 40px, auto, auto, auto !important;
            color: {COLORS['text_primary']} !important;
            font-family: 'Inter', sans-serif !important;
        }}

        .main .block-container {{
            max-width: 1500px;
            padding-top: 28px;
            padding-bottom: 28px;
        }}

        [data-testid="stHeader"] {{
            background-color: transparent !important;
        }}

        /* ========== Sidebar ========== */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(30, 30, 30, 0.98), rgba(18, 18, 18, 0.98)) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        }}
        [data-testid="stSidebar"] * {{
            color: {COLORS['text_primary']} !important;
        }}
        [data-testid="stSidebar"] .stRadio label {{
            display: flex;
            align-items: center;
            padding: 11px 12px;
            border-radius: 8px;
            transition: background 0.2s ease;
        }}
        [data-testid="stSidebar"] .stRadio [role="radiogroup"] {{
            gap: 8px;
        }}
        [data-testid="stSidebar"] .stRadio label > div:first-child {{
            display: none !important;
        }}
        [data-testid="stSidebar"] .stRadio label p {{
            font-size: 13px !important;
            font-weight: 700 !important;
            line-height: 1.25 !important;
            text-transform: none !important;
            letter-spacing: 0 !important;
        }}
        [data-testid="stSidebar"] .stRadio label:hover {{
            background: {COLORS['bg_card']} !important;
        }}
        [data-testid="stSidebar"] .stRadio [aria-checked="true"] {{
            background: rgba(46, 204, 113, 0.08) !important;
            border: 1px solid rgba(46, 204, 113, 0.35) !important;
            box-shadow: inset 4px 0 0 {COLORS['emerald']}, 0 0 20px rgba(46, 204, 113, 0.08);
        }}

        .fg-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 0 18px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 18px;
        }}
        .fg-shield {{
            width: 42px;
            height: 42px;
            display: grid;
            place-items: center;
            border-radius: 8px;
            background: rgba(46, 204, 113, 0.12);
            border: 1px solid rgba(46, 204, 113, 0.58);
            color: {COLORS['emerald']};
            box-shadow: 0 0 28px rgba(46, 204, 113, 0.25);
            font-size: 22px;
        }}
        .fg-brand-title {{
            font-size: 19px;
            font-weight: 800;
            color: #FFFFFF;
        }}
        .fg-brand-subtitle {{
            margin-top: 3px;
            color: {COLORS['text_secondary']};
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.6px;
            text-transform: uppercase;
        }}
        .fg-profile {{
            display: grid;
            grid-template-columns: 48px 1fr;
            gap: 12px;
            align-items: center;
            padding: 13px;
            margin-bottom: 24px;
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
        }}
        .fg-avatar {{
            width: 48px;
            height: 48px;
            border-radius: 8px;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, rgba(46, 204, 113, 0.9), rgba(46, 204, 113, 0.2));
            border: 1px solid rgba(46, 204, 113, 0.42);
            font-size: 23px;
        }}
        .fg-profile-name {{
            color: #FFFFFF;
            font-size: 12px;
            font-weight: 800;
            line-height: 1.35;
        }}
        .fg-profile-meta {{
            margin-top: 5px;
            color: {COLORS['text_secondary']};
            font-size: 10px;
        }}
        .fg-sidebar-label {{
            color: {COLORS['text_muted']};
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.8px;
            text-transform: uppercase;
            margin: 4px 0 10px;
        }}
        .fg-status-box {{
            margin-top: 28px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.026);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
        }}
        .fg-status-title {{
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 800;
            margin-bottom: 12px;
        }}
        .fg-status-title span {{
            color: {COLORS['emerald']};
            text-shadow: 0 0 12px rgba(46, 204, 113, 0.65);
        }}
        .fg-model-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 4px 0;
            color: {COLORS['text_secondary']};
            font-size: 11px;
        }}
        .fg-model-row strong {{
            color: {COLORS['emerald']};
            font-size: 10px;
        }}
        .fg-model-row strong * {{
            color: {COLORS['emerald']} !important;
        }}

        /* ========== Metric Cards ========== */
        .metric-card {{
            background: {COLORS['bg_card']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 18px 20px;
            transition: border-color 0.25s ease, box-shadow 0.25s ease;
        }}
        .metric-card:hover {{
            border-color: {COLORS['border_accent']};
            box-shadow: 0 2px 12px rgba(0,0,0,0.3);
        }}
        .metric-card .metric-label {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: {COLORS['text_secondary']};
            margin-bottom: 6px;
        }}
        .metric-card .metric-value {{
            font-size: 26px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            line-height: 1.2;
        }}
        .metric-card .metric-sub {{
            font-size: 11px;
            color: {COLORS['text_muted']};
            margin-top: 4px;
        }}

        /* ========== Executive Bank Batch View ========== */
        .bank-page-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 20px;
            padding: 22px 24px;
            margin-bottom: 18px;
            background: linear-gradient(135deg, rgba(23, 26, 29, 0.96), rgba(18, 22, 25, 0.96));
            border: 1px solid rgba(214, 169, 74, 0.18);
            border-radius: 8px;
            box-shadow: 0 18px 48px rgba(0, 0, 0, 0.26), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        }}
        .bank-title {{
            margin: 0;
            color: #FFFFFF;
            font-size: 24px;
            font-weight: 850;
            letter-spacing: 0;
        }}
        .bank-subtitle {{
            margin-top: 6px;
            color: #9EAAB1;
            font-size: 12px;
            font-weight: 600;
        }}
        .bank-state {{
            display: flex;
            align-items: center;
            gap: 9px;
            padding: 9px 12px;
            border-radius: 8px;
            background: rgba(33, 184, 166, 0.08);
            border: 1px solid rgba(33, 184, 166, 0.22);
            color: #D8DEE3;
            font-size: 12px;
            font-weight: 800;
            white-space: nowrap;
        }}
        .bank-state-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #21B8A6;
            box-shadow: 0 0 14px rgba(33, 184, 166, 0.58);
        }}
        .bank-metric-card {{
            position: relative;
            min-height: 124px;
            background:
                linear-gradient(180deg, rgba(27, 32, 36, 0.98), rgba(20, 24, 27, 0.98));
            border: 1px solid rgba(189, 195, 199, 0.13);
            box-shadow: 0 14px 38px rgba(0, 0, 0, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.035);
            overflow: hidden;
        }}
        .bank-metric-card::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: #2E3A40;
        }}
        .bank-tone-ledger::before {{ background: #5B8DEF; }}
        .bank-tone-risk::before {{ background: #D94B4B; }}
        .bank-tone-review::before {{ background: #D6A94A; }}
        .bank-tone-safe::before {{ background: #38B46B; }}
        .bank-metric-card:hover {{
            border-color: rgba(214, 169, 74, 0.26);
            box-shadow: 0 18px 46px rgba(0, 0, 0, 0.3);
        }}
        .bank-metric-card .metric-label {{
            color: #9EAAB1;
            font-size: 10px;
            font-weight: 850;
            letter-spacing: 1.1px;
        }}
        .bank-metric-card .metric-value {{
            font-size: 28px;
            font-weight: 800;
        }}
        .bank-metric-card .metric-sub {{
            color: #7F8C8D;
            font-size: 11px;
            font-weight: 600;
        }}
        .bank-alert {{
            margin-top: 8px;
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 11px;
            font-weight: 700;
            line-height: 1.45;
        }}
        .bank-alert-risk {{
            color: #F1B3AD;
            background: rgba(217, 75, 75, 0.08);
            border: 1px solid rgba(217, 75, 75, 0.26);
        }}
        .bank-alert-review {{
            color: #E8CB84;
            background: rgba(214, 169, 74, 0.08);
            border: 1px solid rgba(214, 169, 74, 0.24);
        }}
        .bank-section-divider {{
            height: 1px;
            margin: 18px 0;
            background: linear-gradient(90deg, transparent, rgba(214, 169, 74, 0.26), transparent);
        }}
        [data-testid="stFileUploader"] {{
            background: rgba(27, 32, 36, 0.8);
            border: 1px solid rgba(189, 195, 199, 0.13);
            border-radius: 8px;
            padding: 10px;
        }}
        [data-testid="stFileUploader"] button {{
            background: rgba(214, 169, 74, 0.1) !important;
            color: #E8CB84 !important;
            border: 1px solid rgba(214, 169, 74, 0.28) !important;
            border-radius: 8px !important;
            min-height: 38px !important;
            box-shadow: none !important;
        }}
        [data-testid="stFileUploader"] small,
        [data-testid="stFileUploader"] span {{
            color: #9EAAB1 !important;
        }}

        /* ========== Section Headers ========== */
        .section-header {{
            font-size: 15px;
            font-weight: 800;
            color: {COLORS['text_primary']};
            border-bottom: 1px solid rgba(189, 195, 199, 0.12);
            padding-bottom: 8px;
            margin-bottom: 16px;
            letter-spacing: 0.2px;
        }}

        /* ========== Status Banner ========== */
        .status-banner {{
            background: {COLORS['bg_card']};
            border: 1px solid {COLORS['border']};
            border-left: 3px solid {COLORS['emerald']};
            border-radius: 6px;
            padding: 10px 16px;
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }}
        .status-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            color: {COLORS['text_secondary']};
        }}
        .status-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            display: inline-block;
            animation: pulse-dot 2s ease-in-out infinite;
        }}
        .status-dot.green {{ background: {COLORS['emerald']}; }}
        .status-dot.orange {{ background: {COLORS['warning']}; }}

        @keyframes pulse-dot {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.4; }}
        }}

        /* ========== Alert Boxes ========== */
        .alert-box {{
            border-radius: 6px;
            padding: 12px 16px;
            font-size: 13px;
            line-height: 1.5;
            border: 1px solid;
        }}
        .alert-success {{
            background: {COLORS['emerald_bg']};
            border-color: {COLORS['emerald_dark']};
            color: {COLORS['emerald']};
        }}
        .alert-danger {{
            background: {COLORS['crimson_bg']};
            border-color: {COLORS['crimson_dark']};
            color: {COLORS['crimson']};
        }}
        .alert-warning {{
            background: {COLORS['warning_bg']};
            border-color: {COLORS['warning']};
            color: {COLORS['warning']};
        }}
        .alert-info {{
            background: {COLORS['info_bg']};
            border-color: {COLORS['info']};
            color: {COLORS['info']};
        }}

        /* ========== Verdict Boxes ========== */
        .verdict-approved {{
            background: linear-gradient(135deg, rgba(46,204,113,0.12) 0%, rgba(46,204,113,0.04) 100%);
            border: 1px solid {COLORS['emerald']};
            border-radius: 8px;
            padding: 16px 20px;
            text-align: center;
        }}
        .verdict-blocked {{
            background: linear-gradient(135deg, rgba(231,76,60,0.12) 0%, rgba(231,76,60,0.04) 100%);
            border: 1px solid {COLORS['crimson']};
            border-radius: 8px;
            padding: 16px 20px;
            text-align: center;
        }}
        .verdict-review {{
            background: linear-gradient(135deg, rgba(243,156,18,0.12) 0%, rgba(243,156,18,0.04) 100%);
            border: 1px solid {COLORS['warning']};
            border-radius: 8px;
            padding: 16px 20px;
            text-align: center;
        }}

        /* ========== Chart Containers ========== */
        .chart-container {{
            background: {COLORS['bg_card']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 16px;
        }}

        /* ========== Progress Bar (Health) ========== */
        .health-bar-container {{
            margin-bottom: 14px;
        }}
        .health-bar-label {{
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: {COLORS['text_secondary']};
            margin-bottom: 4px;
        }}
        .health-bar-track {{
            background: {COLORS['bg_primary']};
            border-radius: 4px;
            height: 8px;
            overflow: hidden;
        }}
        .health-bar-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.6s ease;
        }}

        /* ========== Footer ========== */
        .footer {{
            text-align: center;
            padding: 20px 0 10px;
            border-top: 1px solid {COLORS['border']};
            margin-top: 40px;
        }}
        .footer-text {{
            font-size: 11px;
            color: {COLORS['text_muted']};
            letter-spacing: 0.5px;
        }}
        .footer-engine {{
            font-size: 10px;
            color: {COLORS['text_muted']};
            font-family: 'JetBrains Mono', monospace;
            margin-top: 4px;
            opacity: 0.7;
        }}

        /* ========== Streamlit Overrides ========== */
        .stButton > button {{
            background: linear-gradient(180deg, #35d97d, {COLORS['emerald']}) !important;
            color: #07140d !important;
            border: 1px solid rgba(46, 204, 113, 0.8) !important;
            border-radius: 8px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 800 !important;
            min-height: 48px;
            box-shadow: 0 0 24px rgba(46, 204, 113, 0.22) !important;
            transition: all 0.2s ease !important;
        }}
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 0 34px rgba(46, 204, 113, 0.34) !important;
            border-color: {COLORS['emerald']} !important;
        }}
        .stDownloadButton > button {{
            background: {COLORS['bg_card']} !important;
            color: {COLORS['text_primary']} !important;
            border: 1px solid {COLORS['border']} !important;
            border-radius: 6px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            padding: 8px 24px !important;
            transition: all 0.2s ease !important;
        }}
        .stSelectbox, .stTextInput, .stNumberInput {{
            font-family: 'Inter', sans-serif !important;
        }}
        .stTextInput input,
        .stNumberInput input,
        div[data-baseweb="select"] > div {{
            min-height: 52px !important;
            background: #151515 !important;
            border-color: rgba(255, 255, 255, 0.14) !important;
            border-radius: 8px !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }}
        .stTextInput label,
        .stNumberInput label,
        .stSelectbox label,
        .stSlider label {{
            color: {COLORS['text_secondary']} !important;
            font-size: 11px !important;
            font-weight: 800 !important;
            letter-spacing: 0.4px !important;
            text-transform: uppercase !important;
        }}
        div[data-baseweb="select"] {{
            background: {COLORS['bg_card']} !important;
        }}
        .stSlider [data-baseweb="slider"] {{
            margin-top: 0 !important;
        }}

        /* ========== Tabs ========== */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background: {COLORS['bg_card']} !important;
            border-radius: 6px 6px 0 0 !important;
            border: 1px solid {COLORS['border']} !important;
            border-bottom: none !important;
            color: {COLORS['text_secondary']} !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 13px !important;
        }}
        .stTabs [aria-selected="true"] {{
            border-bottom: 2px solid {COLORS['emerald']} !important;
            color: {COLORS['text_primary']} !important;
        }}

        /* Hide default decorations */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header {{ visibility: hidden; }}

        /* ========== Premium Realtime Page ========== */
        .fg-page-title {{
            margin: 0 0 22px;
            color: #FFFFFF;
            font-size: 26px;
            font-weight: 850;
        }}
        .fg-premium-panel {{
            background: linear-gradient(180deg, rgba(30, 30, 30, 0.96), rgba(24, 24, 24, 0.96));
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 24px 70px rgba(0, 0, 0, 0.32), inset 0 1px 0 rgba(255, 255, 255, 0.045);
            position: relative;
            overflow: hidden;
            margin-bottom: 24px;
        }}
        .fg-premium-panel::before {{
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(120deg, rgba(46, 204, 113, 0.05), transparent 35%, rgba(231, 76, 60, 0.035));
        }}
        .fg-premium-panel > * {{
            position: relative;
            z-index: 1;
        }}
        .fg-subpanel {{
            background: rgba(18, 18, 18, 0.45);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 20px;
            min-height: 520px;
        }}
        .fg-approved {{
            min-height: 68px;
            display: grid;
            place-items: center;
            border-radius: 8px;
            border: 1px solid rgba(46, 204, 113, 0.72);
            background: linear-gradient(135deg, rgba(46, 204, 113, 0.18), rgba(46, 204, 113, 0.055));
            color: {COLORS['emerald']};
            font-size: 20px;
            font-weight: 900;
            box-shadow: 0 0 32px rgba(46, 204, 113, 0.16);
            margin-top: 16px;
        }}
        .fg-gauge-card {{
            background: rgba(18, 18, 18, 0.45);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 28px 22px;
            min-height: 520px;
        }}
        .fg-gauge-title {{
            margin: 0 0 34px;
            color: #FFFFFF;
            font-size: 20px;
            font-weight: 850;
        }}
        .fg-gauge-wrap {{
            width: min(360px, 100%);
            aspect-ratio: 1;
            margin: 0 auto;
            position: relative;
            display: grid;
            place-items: center;
            filter: drop-shadow(0 0 32px rgba(231, 76, 60, 0.26));
        }}
        .fg-gauge {{
            position: absolute;
            inset: 0;
            border-radius: 50%;
            background:
                radial-gradient(circle, #191919 0 54%, transparent 55%),
                conic-gradient({COLORS['crimson']} 0deg 262.08deg, rgba(255, 255, 255, 0.085) 262.08deg 360deg);
            border: 1px solid rgba(231, 76, 60, 0.45);
            box-shadow: inset 0 0 42px rgba(231, 76, 60, 0.16), 0 0 58px rgba(231, 76, 60, 0.18);
        }}
        .fg-gauge-value {{
            position: relative;
            text-align: center;
        }}
        .fg-gauge-value strong {{
            color: {COLORS['crimson']};
            font-size: 70px;
            line-height: 1;
            font-weight: 900;
            text-shadow: 0 0 28px rgba(231, 76, 60, 0.54);
        }}
        .fg-gauge-value span {{
            display: block;
            margin-top: 12px;
            color: {COLORS['text_secondary']};
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        .fg-admin-head {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            margin-bottom: 18px;
        }}
        .fg-admin-title {{
            margin: 0;
            color: #FFFFFF;
            font-size: 24px;
            font-weight: 850;
        }}
        .fg-tools {{
            display: flex;
            gap: 10px;
        }}
        .fg-tool-button {{
            width: 46px;
            height: 42px;
            display: grid;
            place-items: center;
            border-radius: 8px;
            color: {COLORS['text_secondary']};
            background: rgba(255, 255, 255, 0.035);
            border: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 18px;
        }}
        .fg-threshold-copy {{
            margin: 14px 0 18px;
            color: {COLORS['text_secondary']};
            font-size: 14px;
            line-height: 1.55;
            font-weight: 650;
        }}
        .fg-threshold-copy strong {{
            color: #FFFFFF;
        }}
        .fg-sensitivity {{
            height: 42px;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            overflow: hidden;
            background: #151515;
        }}
        .fg-sensitivity div {{
            display: grid;
            place-items: center;
            color: #FFFFFF;
            font-size: 11px;
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }}
        .fg-sensitivity .low {{
            background: linear-gradient(90deg, rgba(46, 204, 113, 0.86), rgba(46, 204, 113, 0.5));
        }}
        .fg-sensitivity .mid {{
            background: linear-gradient(90deg, rgba(243, 156, 18, 0.5), rgba(243, 156, 18, 0.88));
        }}
        .fg-sensitivity .high {{
            background: linear-gradient(90deg, rgba(231, 76, 60, 0.62), rgba(231, 76, 60, 0.94));
        }}
        .fg-premium-panel .stSlider [data-baseweb="slider"] > div {{
            background: linear-gradient(90deg, {COLORS['emerald']}, {COLORS['warning']} 62%, {COLORS['crimson']}) !important;
        }}
        .fg-premium-panel .stSlider [role="slider"] {{
            border-color: {COLORS['warning']} !important;
            box-shadow: 0 0 22px rgba(243, 156, 18, 0.4) !important;
        }}
    </style>
    """
