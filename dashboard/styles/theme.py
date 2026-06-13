# dashboard/styles/theme.py
"""Institutional banking design system for FraudGuard."""

# ================================================================
# Color Palette — Private Banking / Tier-1 Risk Console
# ================================================================

COLORS = {
    "bg_primary":     "#071525",
    "bg_secondary":   "#0B1F3A",
    "bg_card":        "#0F2847",
    "bg_card_hover":  "#14325A",
    "border":         "rgba(197, 165, 114, 0.18)",
    "border_accent":  "rgba(197, 165, 114, 0.38)",
    "text_primary":   "#F4F7FA",
    "text_secondary": "#A8B8C8",
    "text_muted":     "#6B7F94",
    "gold":           "#C5A572",
    "gold_light":     "#E8D5B5",
    "gold_bg":        "rgba(197, 165, 114, 0.10)",
    "navy":           "#0B1F3A",
    "navy_light":     "#1A3A5C",
    "emerald":        "#2D8A62",
    "emerald_dark":   "#1D6F4A",
    "emerald_bg":     "rgba(45, 138, 98, 0.12)",
    "crimson":        "#C45C5C",
    "crimson_dark":   "#9E3D3D",
    "crimson_bg":     "rgba(196, 92, 92, 0.12)",
    "warning":        "#C9A04A",
    "warning_bg":     "rgba(201, 160, 74, 0.12)",
    "info":           "#4A7EB8",
    "info_bg":        "rgba(74, 126, 184, 0.12)",
    "accent_teal":    "#3D8B8B",
}

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#0F2847",
    plot_bgcolor="#0A1E36",
    font=dict(family="DM Sans, Inter, sans-serif", color="#E8EDF2", size=12),
    margin=dict(l=44, r=24, t=40, b=40),
    hoverlabel=dict(
        bgcolor="#14325A",
        bordercolor="rgba(197, 165, 114, 0.35)",
        font_size=12,
        font_family="DM Sans, Inter, sans-serif",
    ),
)


def inject_theme() -> str:
    """Return full CSS for institutional banking UI."""
    c = COLORS
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

        html, body, [data-testid="stAppViewContainer"] {{
            background:
                radial-gradient(ellipse 80% 50% at 100% -10%, rgba(197, 165, 114, 0.07), transparent 50%),
                radial-gradient(ellipse 60% 40% at 0% 100%, rgba(45, 138, 98, 0.04), transparent 45%),
                linear-gradient(180deg, #071525 0%, #0B1F3A 40%, #071525 100%) !important;
            color: {c['text_primary']} !important;
            font-family: 'DM Sans', 'Inter', sans-serif !important;
        }}

        .main .block-container {{
            max-width: 1480px;
            padding-top: 0.5rem;
            padding-bottom: 2rem;
        }}

        [data-testid="stHeader"] {{ background: transparent !important; }}
        #MainMenu, footer, header {{ visibility: hidden; }}

        /* ========== Sidebar ========== */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0A1A30 0%, #061220 100%) !important;
            border-right: 1px solid {c['border']} !important;
            box-shadow: 8px 0 32px rgba(0, 0, 0, 0.35);
        }}
        [data-testid="stSidebar"] > div {{
            padding-top: 1.25rem;
        }}
        [data-testid="stSidebar"] * {{
            color: {c['text_primary']} !important;
        }}
        [data-testid="stSidebar"] .stRadio label {{
            padding: 12px 14px;
            border-radius: 6px;
            border: 1px solid transparent;
            margin-bottom: 4px;
            transition: all 0.2s ease;
        }}
        [data-testid="stSidebar"] .stRadio label > div:first-child {{ display: none !important; }}
        [data-testid="stSidebar"] .stRadio label p {{
            font-size: 12px !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em !important;
        }}
        [data-testid="stSidebar"] .stRadio label:hover {{
            background: rgba(197, 165, 114, 0.06) !important;
            border-color: {c['border']} !important;
        }}
        [data-testid="stSidebar"] .stRadio [aria-checked="true"] {{
            background: linear-gradient(90deg, rgba(197, 165, 114, 0.14), transparent) !important;
            border: 1px solid {c['border_accent']} !important;
            box-shadow: inset 3px 0 0 {c['gold']};
        }}

        /* ========== Institutional Header ========== */
        .bk-header {{
            margin: 0 -1rem 1rem;
            padding: 0;
            border-bottom: 1px solid {c['border']};
            background: linear-gradient(180deg, rgba(15, 40, 71, 0.95), rgba(11, 31, 58, 0.88));
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
        }}
        .bk-header-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 24px;
            padding: 18px 24px 14px;
            flex-wrap: wrap;
        }}
        .bk-brand-block {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .bk-logo-mark {{
            width: 52px;
            height: 52px;
            display: grid;
            place-items: center;
            font-family: 'Cormorant Garamond', serif;
            font-size: 22px;
            font-weight: 700;
            color: {c['gold_light']};
            background: linear-gradient(145deg, rgba(197, 165, 114, 0.22), rgba(197, 165, 114, 0.05));
            border: 1px solid {c['border_accent']};
            border-radius: 8px;
            letter-spacing: 0.05em;
        }}
        .bk-institution {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 28px;
            font-weight: 700;
            color: {c['text_primary']};
            letter-spacing: 0.02em;
            line-height: 1.1;
        }}
        .bk-platform {{
            margin-top: 4px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: {c['gold']};
        }}
        .bk-header-meta {{
            display: flex;
            gap: 28px;
            flex-wrap: wrap;
        }}
        .bk-meta-item {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .bk-meta-label {{
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: {c['text_muted']};
        }}
        .bk-meta-value {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 12px;
            color: {c['text_secondary']};
        }}
        .bk-header-bottom {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            padding: 10px 24px 14px;
            border-top: 1px solid rgba(255, 255, 255, 0.04);
            flex-wrap: wrap;
        }}
        .bk-pills {{ display: flex; gap: 8px; flex-wrap: wrap; }}
        .bk-pill {{
            padding: 5px 12px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            border: 1px solid transparent;
        }}
        .bk-pill-live {{
            color: #A8E0C8;
            background: {c['emerald_bg']};
            border-color: rgba(45, 138, 98, 0.35);
        }}
        .bk-pill-warn {{
            color: #F0D9A8;
            background: {c['warning_bg']};
            border-color: rgba(201, 160, 74, 0.35);
        }}
        .bk-pill-neutral {{
            color: {c['text_secondary']};
            background: rgba(255,255,255,0.04);
            border-color: {c['border']};
        }}
        .bk-pill-gold {{
            color: {c['gold_light']};
            background: {c['gold_bg']};
            border-color: {c['border_accent']};
        }}
        .bk-compliance {{ display: flex; gap: 6px; flex-wrap: wrap; }}
        .bk-badge {{
            padding: 4px 10px;
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {c['text_muted']};
            border: 1px solid {c['border']};
            border-radius: 3px;
            background: rgba(0, 0, 0, 0.15);
        }}

        .bk-trust-ribbon {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px 28px;
            padding: 10px 20px;
            margin-bottom: 1.25rem;
            background: rgba(15, 40, 71, 0.55);
            border: 1px solid {c['border']};
            border-radius: 6px;
        }}
        .bk-trust-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 11px;
            font-weight: 600;
            color: {c['text_secondary']};
        }}
        .bk-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
        }}
        .bk-dot-green {{ background: {c['emerald']}; box-shadow: 0 0 8px rgba(45, 138, 98, 0.6); }}
        .bk-dot-gold {{ background: {c['gold']}; box-shadow: 0 0 8px rgba(197, 165, 114, 0.5); }}

        .bk-page-intro {{
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid {c['border']};
        }}
        .bk-breadcrumb {{
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: {c['gold']};
            margin-bottom: 8px;
        }}
        .bk-page-title {{
            margin: 0;
            font-family: 'Cormorant Garamond', serif;
            font-size: 32px;
            font-weight: 700;
            color: {c['text_primary']};
        }}
        .bk-page-subtitle {{
            margin: 8px 0 0;
            font-size: 14px;
            color: {c['text_secondary']};
            max-width: 720px;
            line-height: 1.55;
        }}

        /* ========== Panels & Cards ========== */
        .bk-panel, .rt-card, .fg-premium-panel {{
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
        .rt-card-title, .bk-card-title {{
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {c['gold']};
            margin-bottom: 18px;
        }}

        .rt-decision {{
            min-height: 110px;
            display: grid;
            align-content: center;
            gap: 6px;
            padding: 20px;
            margin-top: 16px;
            border-radius: 8px;
            text-align: center;
        }}
        .rt-decision strong {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 26px;
            font-weight: 700;
        }}
        .rt-decision span {{
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: {c['text_secondary']};
        }}
        .rt-approved {{
            border: 1px solid rgba(45, 138, 98, 0.5);
            background: linear-gradient(135deg, rgba(45, 138, 98, 0.18), rgba(45, 138, 98, 0.04));
            color: #7FD4A8;
        }}
        .rt-blocked {{
            border: 1px solid rgba(196, 92, 92, 0.5);
            background: linear-gradient(135deg, rgba(196, 92, 92, 0.18), rgba(196, 92, 92, 0.04));
            color: #E8A0A0;
        }}
        .rt-score-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-top: 14px;
        }}
        .rt-score {{
            padding: 16px;
            border-radius: 6px;
            border: 1px solid {c['border']};
            background: rgba(0, 0, 0, 0.12);
        }}
        .rt-score label {{
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: {c['text_muted']};
        }}
        .rt-score strong {{
            display: block;
            margin-top: 8px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 24px;
            color: {c['text_primary']};
        }}

        /* SHAP explain */
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

        /* Sidebar brand */
        .fg-brand, .bk-sidebar-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding-bottom: 16px;
            margin-bottom: 16px;
            border-bottom: 1px solid {c['border']};
        }}
        .fg-shield, .bk-sidebar-logo {{
            width: 44px;
            height: 44px;
            display: grid;
            place-items: center;
            border-radius: 6px;
            font-family: 'Cormorant Garamond', serif;
            font-weight: 700;
            font-size: 18px;
            color: {c['gold_light']};
            background: {c['gold_bg']};
            border: 1px solid {c['border_accent']};
        }}
        .fg-brand-title, .bk-sidebar-title {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 20px;
            font-weight: 700;
        }}
        .fg-brand-subtitle, .bk-sidebar-sub {{
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: {c['gold']};
            margin-top: 2px;
        }}
        .fg-profile, .bk-officer-card {{
            display: grid;
            grid-template-columns: 48px 1fr;
            gap: 12px;
            padding: 14px;
            margin-bottom: 20px;
            background: rgba(0, 0, 0, 0.18);
            border: 1px solid {c['border']};
            border-radius: 6px;
        }}
        .fg-avatar, .bk-officer-avatar {{
            width: 48px;
            height: 48px;
            border-radius: 6px;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, rgba(197, 165, 114, 0.25), rgba(197, 165, 114, 0.05));
            border: 1px solid {c['border_accent']};
            font-size: 20px;
        }}
        .fg-profile-name, .bk-officer-name {{
            font-size: 13px;
            font-weight: 700;
        }}
        .fg-profile-meta, .bk-officer-role {{
            margin-top: 4px;
            font-size: 11px;
            color: {c['text_muted']};
        }}
        .fg-sidebar-label, .bk-nav-label {{
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: {c['text_muted']};
            margin: 8px 0 10px;
        }}
        .fg-status-box, .bk-status-box {{
            margin-top: 24px;
            padding: 14px;
            background: rgba(0, 0, 0, 0.15);
            border: 1px solid {c['border']};
            border-radius: 6px;
        }}
        .fg-model-row, .bk-model-row {{
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            font-size: 11px;
            color: {c['text_secondary']};
            border-bottom: 1px solid rgba(255,255,255,0.03);
        }}
        .fg-model-row strong, .bk-model-row strong {{
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.04em;
        }}
        .bk-online {{ color: #7FD4A8 !important; }}
        .bk-offline {{ color: {c['warning']} !important; }}

        /* KPI / Bank metrics */
        .metric-card, .bank-metric-card {{
            position: relative;
            min-height: 128px;
            padding: 20px 22px;
            background: linear-gradient(160deg, rgba(15, 40, 71, 0.98), rgba(10, 28, 50, 0.98));
            border: 1px solid {c['border']};
            border-radius: 8px;
            box-shadow: 0 14px 36px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }}
        .bank-metric-card::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: {c['gold']};
        }}
        .bank-tone-ledger::before {{ background: #5B8DEF; }}
        .bank-tone-risk::before {{ background: {c['crimson']}; }}
        .bank-tone-review::before {{ background: {c['gold']}; }}
        .bank-tone-safe::before {{ background: {c['emerald']}; }}
        .metric-label {{
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {c['text_muted']};
        }}
        .metric-value {{
            margin-top: 8px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 28px;
            font-weight: 500;
        }}
        .metric-sub {{
            margin-top: 6px;
            font-size: 11px;
            color: {c['text_muted']};
        }}

        .bank-page-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: 20px 24px;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, rgba(15, 40, 71, 0.95), rgba(11, 31, 58, 0.9));
            border: 1px solid {c['border']};
            border-radius: 8px;
        }}
        .bank-title {{
            margin: 0;
            font-family: 'Cormorant Garamond', serif;
            font-size: 26px;
            font-weight: 700;
        }}
        .bank-subtitle {{
            margin-top: 6px;
            font-size: 13px;
            color: {c['text_secondary']};
        }}
        .bank-state {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: {c['gold_light']};
            background: {c['gold_bg']};
            border: 1px solid {c['border_accent']};
        }}
        .bank-state-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: {c['emerald']};
            box-shadow: 0 0 10px rgba(45, 138, 98, 0.5);
        }}
        .bank-section-divider {{
            height: 1px;
            margin: 1.25rem 0;
            background: linear-gradient(90deg, transparent, {c['gold']}, transparent);
            opacity: 0.35;
        }}
        .section-header {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 18px;
            font-weight: 600;
            color: {c['gold_light']};
            border-bottom: 1px solid {c['border']};
            padding-bottom: 8px;
            margin-bottom: 14px;
        }}

        .status-banner {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px 24px;
            padding: 12px 18px;
            background: rgba(15, 40, 71, 0.6);
            border: 1px solid {c['border']};
            border-left: 3px solid {c['gold']};
            border-radius: 6px;
            margin-bottom: 1rem;
        }}
        .status-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 11px;
            font-weight: 600;
            color: {c['text_secondary']};
        }}
        .status-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            animation: bk-pulse 2.5s ease infinite;
        }}
        .status-dot.green {{ background: {c['emerald']}; }}
        .status-dot.orange {{ background: {c['warning']}; }}
        @keyframes bk-pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.45; }}
        }}

        .footer {{
            text-align: center;
            padding: 28px 0 12px;
            margin-top: 48px;
            border-top: 1px solid {c['border']};
        }}
        .footer-text {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 14px;
            color: {c['gold']};
        }}
        .footer-engine {{
            margin-top: 6px;
            font-size: 10px;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {c['text_muted']};
        }}

        /* Streamlit controls */
        .stButton > button[kind="primary"], .stButton > button {{
            background: linear-gradient(180deg, #D4BC8A, {c['gold']}) !important;
            color: #1A1208 !important;
            border: 1px solid {c['border_accent']} !important;
            border-radius: 6px !important;
            font-weight: 700 !important;
            letter-spacing: 0.04em !important;
            min-height: 46px !important;
            box-shadow: 0 4px 20px rgba(197, 165, 114, 0.2) !important;
        }}
        .stButton > button:hover {{
            filter: brightness(1.06);
            transform: translateY(-1px);
        }}
        .stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div {{
            background: rgba(7, 21, 37, 0.8) !important;
            border: 1px solid {c['border']} !important;
            border-radius: 6px !important;
            color: {c['text_primary']} !important;
            min-height: 48px !important;
        }}
        .stTextInput label, .stNumberInput label, .stSelectbox label, .stSlider label {{
            font-size: 10px !important;
            font-weight: 700 !important;
            letter-spacing: 0.1em !important;
            text-transform: uppercase !important;
            color: {c['text_muted']} !important;
        }}
        [data-testid="stFileUploader"] {{
            background: rgba(15, 40, 71, 0.5);
            border: 1px dashed {c['border_accent']};
            border-radius: 8px;
        }}
        [data-testid="stDataFrame"] {{
            border: 1px solid {c['border']};
            border-radius: 6px;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0;
            border-bottom: 1px solid {c['border']};
        }}
        .stTabs [data-baseweb="tab"] {{
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            color: {c['text_muted']} !important;
            font-weight: 600 !important;
            padding: 12px 20px !important;
        }}
        .stTabs [aria-selected="true"] {{
            color: {c['gold_light']} !important;
            border-bottom: 2px solid {c['gold']} !important;
            background: rgba(197, 165, 114, 0.06) !important;
        }}
        .fg-threshold-copy {{
            font-size: 13px;
            line-height: 1.55;
            color: {c['text_secondary']};
        }}
    </style>
    """
