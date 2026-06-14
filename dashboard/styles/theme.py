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
            padding: 14px 22px 12px;
            flex-wrap: wrap;
        }}
        .bk-brand-block {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .bk-logo-mark {{
            width: 46px;
            height: 46px;
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
            font-size: 25px;
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
            padding: 9px 22px 12px;
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
        }}
        .bk-page-hero {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 24px;
            align-items: center;
            margin: 0 0 1.35rem;
            padding: 24px 26px;
            border: 1px solid rgba(197, 165, 114, 0.16);
            border-radius: 10px;
            background:
                linear-gradient(135deg, rgba(15, 40, 71, 0.58), rgba(7, 21, 37, 0.18)),
                radial-gradient(circle at 94% 18%, rgba(197, 165, 114, 0.10), transparent 32%);
            box-shadow: 0 18px 46px rgba(0,0,0,0.16);
        }}
        .bk-hero-copy {{
            min-width: 0;
        }}
        .bk-breadcrumb {{
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: {c['gold']};
            margin-bottom: 10px;
        }}
        .bk-page-title {{
            margin: 0;
            font-family: 'Cormorant Garamond', serif;
            font-size: 34px;
            font-weight: 700;
            color: {c['text_primary']};
            line-height: 1;
        }}
        .bk-page-subtitle {{
            margin: 14px 0 0;
            font-size: 14px;
            color: {c['text_secondary']};
            max-width: 760px;
            line-height: 1.55;
        }}
        .bk-hero-status {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            min-width: 180px;
        }}
        .hero-chip {{
            display: flex;
            align-items: center;
            gap: 8px;
            min-height: 34px;
            padding: 0 12px;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(7, 21, 37, 0.36);
            color: {c['text_secondary']};
            font-size: 11px;
            font-weight: 700;
            white-space: nowrap;
        }}
        .hero-chip i {{
            width: 7px;
            height: 7px;
            border-radius: 999px;
            background: currentColor;
            box-shadow: 0 0 10px currentColor;
        }}
        .hero-chip-ok {{
            color: #7FD4A8;
            border-color: rgba(45, 138, 98, 0.28);
        }}
        .hero-chip-warn {{
            color: {c['warning']};
            border-color: rgba(201, 160, 74, 0.30);
        }}
        .hero-chip-soft {{
            color: {c['gold_light']};
            border-color: rgba(197, 165, 114, 0.22);
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
        .rt-action-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin-top: 14px;
        }}
        .rt-action-item {{
            min-height: 76px;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid {c['border']};
            background: rgba(7, 21, 37, 0.48);
        }}
        .rt-action-item label {{
            display: block;
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: {c['text_muted']};
            margin-bottom: 8px;
        }}
        .rt-action-item strong {{
            display: block;
            font-size: 12px;
            line-height: 1.35;
            color: {c['text_primary']};
        }}
        .rt-waiting {{
            min-height: 220px;
            display: grid;
            place-items: center;
            text-align: center;
            border: 1px dashed {c['border_accent']};
            border-radius: 8px;
            background: rgba(7, 21, 37, 0.28);
        }}
        .rt-waiting strong {{
            display: block;
            color: {c['gold_light']};
            font-size: 15px;
            margin-bottom: 6px;
        }}
        .rt-waiting span {{
            color: {c['text_muted']};
            font-size: 12px;
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
        .batch-control-panel {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) 360px;
            gap: 18px;
            align-items: end;
            padding: 20px 22px;
            margin-bottom: 18px;
            border: 1px solid rgba(197, 165, 114, 0.18);
            border-radius: 10px;
            background:
                linear-gradient(135deg, rgba(15, 40, 71, 0.70), rgba(7, 21, 37, 0.32)),
                radial-gradient(circle at 100% 0%, rgba(61, 139, 139, 0.10), transparent 34%);
        }}
        .batch-control-title {{
            font-size: 16px;
            font-weight: 800;
            color: {c['text_primary']};
            margin-bottom: 6px;
        }}
        .batch-control-copy {{
            max-width: 720px;
            color: {c['text_secondary']};
            font-size: 13px;
            line-height: 1.5;
        }}
        .batch-control-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }}
        .batch-control-meta span {{
            padding: 5px 9px;
            border-radius: 999px;
            border: 1px solid {c['border']};
            color: {c['gold_light']};
            background: rgba(0,0,0,0.14);
            font-size: 10px;
            font-family: 'IBM Plex Mono', monospace;
        }}
        .batch-result-strip {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin: 0 0 14px;
        }}
        .batch-result-item {{
            padding: 12px 14px;
            border-radius: 8px;
            border: 1px solid rgba(45, 138, 98, 0.24);
            background: rgba(45, 138, 98, 0.10);
        }}
        .batch-result-item label {{
            display: block;
            margin-bottom: 5px;
            color: {c['text_muted']};
            font-size: 9px;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }}
        .batch-result-item strong {{
            color: {c['text_primary']};
            font-family: 'IBM Plex Mono', monospace;
            font-size: 15px;
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

        .bank-alert, .alert-box {{
            margin-top: 12px;
            padding: 12px 14px;
            border-radius: 6px;
            font-size: 12px;
            line-height: 1.45;
            color: {c['text_secondary']};
            border: 1px solid {c['border']};
            background: rgba(7, 21, 37, 0.42);
        }}
        .bank-alert strong, .alert-box strong {{
            color: {c['text_primary']};
        }}
        .bank-alert-risk, .alert-warning {{
            border-color: rgba(196, 92, 92, 0.38);
            background: {c['crimson_bg']};
        }}
        .bank-alert-review {{
            border-color: rgba(201, 160, 74, 0.38);
            background: {c['warning_bg']};
        }}
        .alert-info {{
            border-color: rgba(74, 126, 184, 0.38);
            background: {c['info_bg']};
        }}

        .bk-empty-state {{
            display: grid;
            grid-template-columns: 56px 1fr;
            gap: 16px;
            align-items: center;
            padding: 22px;
            margin: 8px 0 18px;
            border: 1px dashed {c['border_accent']};
            border-radius: 8px;
            background: rgba(15, 40, 71, 0.42);
        }}
        .bk-empty-icon {{
            width: 56px;
            height: 56px;
            display: grid;
            place-items: center;
            border-radius: 8px;
            color: {c['gold_light']};
            background: {c['gold_bg']};
            border: 1px solid {c['border_accent']};
            font-family: 'Cormorant Garamond', serif;
            font-weight: 700;
        }}
        .bk-empty-title {{
            font-size: 16px;
            font-weight: 700;
            color: {c['text_primary']};
            margin-bottom: 4px;
        }}
        .bk-empty-body {{
            font-size: 13px;
            line-height: 1.5;
            color: {c['text_secondary']};
            max-width: 780px;
        }}
        .bk-empty-chips {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }}
        .bk-empty-chips span {{
            padding: 5px 9px;
            border-radius: 4px;
            border: 1px solid {c['border']};
            color: {c['gold_light']};
            background: rgba(0,0,0,0.14);
            font-family: 'IBM Plex Mono', monospace;
            font-size: 10px;
        }}
        .bk-chart-empty {{
            min-height: 300px;
            display: grid;
            place-items: center;
            text-align: center;
            border: 1px dashed {c['border']};
            border-radius: 8px;
            background: rgba(7, 21, 37, 0.24);
            color: {c['text_muted']};
            font-size: 13px;
        }}
        .bk-chart-empty strong {{
            display: block;
            color: {c['gold_light']};
            font-size: 14px;
            margin-bottom: 4px;
        }}

        .ov-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin-bottom: 14px;
        }}
        .ov-card {{
            min-height: 104px;
            padding: 18px;
            border-radius: 8px;
            border: 1px solid {c['border']};
            background: rgba(15, 40, 71, 0.72);
            box-shadow: 0 12px 28px rgba(0,0,0,0.18);
        }}
        .ov-label {{
            font-size: 11px;
            font-weight: 700;
            color: {c['text_muted']};
            margin-bottom: 8px;
        }}
        .ov-value {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 27px;
            font-weight: 600;
            color: {c['emerald']};
        }}
        .ov-sub {{
            margin-top: 6px;
            font-size: 12px;
            color: {c['text_secondary']};
        }}
        .ov-panel-grid {{
            display: grid;
            grid-template-columns: 1.2fr 0.88fr;
            gap: 14px;
            margin-top: 14px;
        }}
        .ov-panel {{
            padding: 20px;
            border-radius: 8px;
            border: 1px solid {c['border']};
            background: rgba(15, 40, 71, 0.76);
        }}
        .ov-panel-title {{
            margin-bottom: 16px;
            font-size: 14px;
            font-weight: 700;
            color: {c['gold_light']};
        }}
        .ov-bar-row {{
            display: grid;
            grid-template-columns: 112px 1fr 46px;
            align-items: center;
            gap: 12px;
            margin: 13px 0;
            font-size: 13px;
            color: {c['text_secondary']};
        }}
        .ov-bar-track {{
            height: 8px;
            border-radius: 99px;
            background: rgba(255,255,255,0.12);
            overflow: hidden;
        }}
        .ov-bar-fill {{
            height: 100%;
            border-radius: 99px;
        }}
        .ov-pill {{
            justify-self: end;
            padding: 4px 8px;
            border-radius: 999px;
            font-size: 10px;
            font-weight: 700;
            background: rgba(255,255,255,0.07);
        }}
        .ov-pill-ok {{ color: #7FD4A8; }}
        .ov-pill-warn {{ color: {c['warning']}; }}
        .ov-note {{
            margin-top: 16px;
            padding: 12px 14px;
            border-radius: 6px;
            border: 1px solid rgba(201,160,74,0.28);
            background: {c['warning_bg']};
            color: {c['text_secondary']};
            font-size: 12px;
        }}
        .insight-brief {{
            margin: 0 0 16px;
            padding: 18px;
            border-radius: 10px;
            border: 1px solid rgba(197, 165, 114, 0.18);
            background:
                linear-gradient(135deg, rgba(15, 40, 71, 0.74), rgba(7, 21, 37, 0.34)),
                radial-gradient(circle at 92% 0%, rgba(61, 139, 139, 0.12), transparent 30%);
            box-shadow: 0 14px 34px rgba(0,0,0,0.16);
        }}
        .insight-head {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 14px;
        }}
        .insight-kicker {{
            color: {c['gold']};
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }}
        .insight-head h3 {{
            margin: 5px 0 0;
            color: {c['text_primary']};
            font-size: 18px;
            line-height: 1.2;
        }}
        .insight-head > span {{
            padding: 6px 10px;
            border-radius: 999px;
            border: 1px solid rgba(45, 138, 98, 0.28);
            color: #7FD4A8;
            background: rgba(45, 138, 98, 0.10);
            font-family: 'IBM Plex Mono', monospace;
            font-size: 10px;
            white-space: nowrap;
        }}
        .insight-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 10px;
        }}
        .insight-tile {{
            min-height: 104px;
            padding: 14px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.07);
            background: rgba(7, 21, 37, 0.42);
        }}
        .insight-tile label {{
            display: block;
            margin-bottom: 8px;
            color: {c['text_muted']};
            font-size: 9px;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }}
        .insight-tile strong {{
            display: block;
            color: {c['gold_light']};
            font-size: 22px;
            line-height: 1.1;
        }}
        .insight-tile span {{
            display: block;
            margin-top: 8px;
            color: {c['text_secondary']};
            font-size: 12px;
            line-height: 1.35;
        }}
        .insight-buckets {{
            margin-top: 14px;
            padding-top: 12px;
            border-top: 1px solid rgba(255,255,255,0.06);
        }}
        .insight-bucket-title {{
            margin-bottom: 8px;
            color: {c['text_secondary']};
            font-size: 11px;
            font-weight: 800;
        }}
        .insight-bucket-row {{
            display: grid;
            grid-template-columns: 68px minmax(0, 1fr) 62px;
            align-items: center;
            gap: 10px;
            margin: 7px 0;
            color: {c['text_secondary']};
            font-size: 12px;
        }}
        .insight-bucket-row strong {{
            justify-self: end;
            color: {c['text_primary']};
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
        }}
        .insight-bucket-track {{
            height: 7px;
            border-radius: 99px;
            overflow: hidden;
            background: rgba(255,255,255,0.10);
        }}
        .insight-bucket-track div {{
            height: 100%;
            border-radius: 99px;
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
            background: rgba(7, 21, 37, 0.48);
            border: 1px dashed rgba(197, 165, 114, 0.36);
            border-radius: 10px;
            padding: 10px;
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

        [data-testid="stSidebar"] {{
            width: 220px !important;
            min-width: 220px !important;
            background: rgba(6, 18, 32, 0.98) !important;
        }}
        [data-testid="stSidebar"] > div {{
            padding: 16px 12px !important;
        }}
        .fg-side-nav {{
            display: grid;
            gap: 10px;
        }}
        .fg-side-button {{
            position: relative;
            display: grid;
            grid-template-columns: 34px 1fr;
            align-items: center;
            min-height: 58px;
            padding: 0 14px;
            border-radius: 8px;
            border: 1px solid rgba(197, 165, 114, 0.14);
            background: rgba(15, 40, 71, 0.42);
            color: {c['text_secondary']} !important;
            text-decoration: none !important;
            font-size: 13px;
            font-weight: 700;
            overflow: hidden;
            transition: transform 0.16s ease, border-color 0.16s ease, background 0.16s ease, color 0.16s ease;
        }}
        .fg-side-button::before {{
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 3px;
            background: transparent;
            transition: background 0.16s ease;
        }}
        .fg-side-button:hover {{
            transform: translateX(2px);
            border-color: {c['border_accent']};
            background: rgba(197, 165, 114, 0.10);
            color: {c['text_primary']} !important;
        }}
        .fg-side-button.is-active {{
            color: {c['gold_light']} !important;
            border-color: rgba(197, 165, 114, 0.42);
            background: linear-gradient(90deg, rgba(197, 165, 114, 0.18), rgba(15, 40, 71, 0.38));
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.22);
        }}
        .fg-side-button.is-active::before {{
            background: {c['gold']};
        }}
        .fg-side-kicker {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 10px;
            color: {c['text_muted']};
        }}
        .fg-side-button.is-active .fg-side-kicker {{
            color: {c['gold']};
        }}
        .fg-side-divider {{
            height: 1px;
            margin: 8px 0;
            background: rgba(197, 165, 114, 0.18);
        }}
        .queue-upload-link {{
            display: inline-flex;
            align-items: center;
            min-height: 42px;
            padding: 0 16px;
            border-radius: 8px;
            border: 1px solid {c['border_accent']};
            background: rgba(197, 165, 114, 0.12);
            color: {c['gold_light']} !important;
            text-decoration: none !important;
            font-weight: 800;
            margin-top: 4px;
        }}
        .queue-panel {{
            padding: 14px;
            border-radius: 10px;
            border: 1px solid rgba(197, 165, 114, 0.18);
            background: rgba(15, 40, 71, 0.70);
            box-shadow: 0 16px 34px rgba(0,0,0,0.18);
        }}
        .queue-list-panel {{
            min-height: 560px;
        }}
        .queue-detail-panel {{
            min-height: 560px;
        }}
        .queue-section-title {{
            margin-bottom: 12px;
            color: {c['gold_light']};
            font-size: 13px;
            font-weight: 800;
            letter-spacing: 0.04em;
        }}
        .queue-summary-strip {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 8px;
            margin: 8px 0 12px;
        }}
        .queue-filter-bar {{
            display: grid;
            grid-template-columns: 0.85fr 1.15fr;
            gap: 12px;
            align-items: end;
            margin: 0 0 14px;
            padding: 12px;
            border: 1px solid rgba(197, 165, 114, 0.14);
            border-radius: 10px;
            background: rgba(7, 21, 37, 0.30);
        }}
        .queue-filter-bar label {{
            display: block;
            margin-bottom: 7px;
            color: {c['text_muted']};
            font-size: 9px;
            font-weight: 900;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }}
        .queue-filter-chips {{
            display: flex;
            flex-wrap: wrap;
            gap: 7px;
        }}
        .queue-filter-chip {{
            display: inline-flex;
            align-items: center;
            min-height: 30px;
            padding: 0 11px;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(15, 40, 71, 0.54);
            color: {c['text_secondary']} !important;
            text-decoration: none !important;
            font-size: 11px;
            font-weight: 800;
        }}
        .queue-filter-chip:hover, .queue-filter-chip.is-active {{
            border-color: rgba(197, 165, 114, 0.44);
            background: rgba(197, 165, 114, 0.14);
            color: {c['gold_light']} !important;
        }}
        .queue-inbox-tabs {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin: 0 0 12px;
            padding: 8px;
            border-radius: 10px;
            border: 1px solid rgba(197, 165, 114, 0.14);
            background: rgba(7, 21, 37, 0.30);
        }}
        .queue-inbox-tab {{
            display: inline-flex;
            align-items: center;
            min-height: 36px;
            padding: 0 14px;
            border-radius: 8px;
            color: {c['text_secondary']} !important;
            text-decoration: none !important;
            font-size: 12px;
            font-weight: 800;
            border: 1px solid transparent;
        }}
        .queue-inbox-tab:hover, .queue-inbox-tab.is-active {{
            background: rgba(197, 165, 114, 0.14);
            border-color: rgba(197, 165, 114, 0.34);
            color: {c['gold_light']} !important;
        }}
        .queue-summary-strip div {{
            padding: 10px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.07);
            background: rgba(7, 21, 37, 0.42);
        }}
        .queue-summary-strip label {{
            display: block;
            color: {c['text_muted']};
            font-size: 9px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.10em;
        }}
        .queue-summary-strip strong {{
            display: block;
            margin-top: 3px;
            color: {c['text_primary']};
            font-family: 'IBM Plex Mono', monospace;
            font-size: 16px;
        }}
        .queue-items {{
            display: grid;
            gap: 7px;
            max-height: 540px;
            overflow-y: auto;
            padding-right: 4px;
        }}
        .queue-item {{
            display: grid;
            grid-template-columns: 12px minmax(0, 1fr) 70px 78px;
            align-items: center;
            gap: 10px;
            min-height: 58px;
            padding: 9px 11px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.07);
            background: linear-gradient(90deg, rgba(7, 21, 37, 0.46), rgba(15, 40, 71, 0.42));
            color: {c['text_primary']} !important;
            text-decoration: none !important;
        }}
        .queue-item:hover, .queue-item.is-selected {{
            border-color: rgba(197, 165, 114, 0.42);
            background: linear-gradient(90deg, rgba(197, 165, 114, 0.16), rgba(15, 40, 71, 0.48));
        }}
        .queue-risk-dot {{
            width: 9px;
            height: 9px;
            border-radius: 999px;
            box-shadow: 0 0 12px currentColor;
        }}
        .queue-item-main strong {{
            display: block;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 12px;
            color: {c['text_primary']};
        }}
        .queue-item-main em {{
            display: block;
            margin-top: 3px;
            font-style: normal;
            font-size: 11px;
            color: {c['text_muted']};
        }}
        .queue-score {{
            justify-self: end;
            display: grid;
            gap: 1px;
            text-align: right;
            font-family: 'IBM Plex Mono', monospace;
            color: {c['text_primary']};
        }}
        .queue-score b {{
            font-size: 15px;
            line-height: 1;
        }}
        .queue-score small {{
            color: {c['text_muted']};
            font-size: 9px;
            font-family: 'DM Sans', sans-serif;
            font-weight: 800;
            text-transform: uppercase;
        }}
        .queue-level {{
            justify-self: end;
            padding: 5px 8px;
            border-radius: 999px;
            font-size: 10px;
            font-weight: 900;
            text-transform: uppercase;
            background: rgba(255,255,255,0.07);
        }}
        .risk-high {{ color: #F28B8B !important; }}
        .risk-medium {{ color: {c['warning']} !important; }}
        .risk-low {{ color: #7FD4A8 !important; }}
        .queue-empty-mini, .queue-empty-detail {{
            min-height: 180px;
            display: grid;
            place-items: center;
            text-align: center;
            border-radius: 8px;
            border: 1px dashed {c['border']};
            color: {c['text_muted']};
        }}
        .queue-detail-head {{
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: flex-start;
            margin-bottom: 14px;
        }}
        .queue-eyebrow {{
            color: {c['gold']};
            font-size: 10px;
            font-weight: 900;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }}
        .queue-detail-head h2 {{
            margin: 4px 0 0;
            color: {c['text_primary']};
            font-size: 25px;
        }}
        .queue-status-pill {{
            padding: 7px 10px;
            border-radius: 999px;
            border: 1px solid rgba(197, 165, 114, 0.28);
            color: {c['gold_light']};
            background: rgba(197, 165, 114, 0.10);
            font-size: 11px;
            font-weight: 800;
            white-space: nowrap;
        }}
        .queue-score-hero {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            padding: 16px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(7, 21, 37, 0.44);
            margin-bottom: 14px;
        }}
        .queue-score-hero label {{
            display: block;
            color: {c['text_muted']};
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.12em;
        }}
        .queue-score-hero strong {{
            display: block;
            margin-top: 4px;
            color: {c['text_primary']};
            font-family: 'IBM Plex Mono', monospace;
            font-size: 32px;
        }}
        .queue-info-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 8px;
            margin-bottom: 16px;
        }}
        .queue-info-grid div {{
            min-height: 70px;
            padding: 11px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.07);
            background: rgba(7, 21, 37, 0.30);
        }}
        .queue-info-grid label {{
            display: block;
            margin-bottom: 6px;
            color: {c['text_muted']};
            font-size: 9px;
            font-weight: 900;
            letter-spacing: 0.10em;
            text-transform: uppercase;
        }}
        .queue-info-grid strong {{
            display: block;
            color: {c['text_primary']};
            font-size: 12px;
            line-height: 1.35;
            overflow-wrap: anywhere;
        }}
        .queue-model-policy, .queue-signals, .queue-timeline {{
            padding: 14px;
            margin-bottom: 14px;
            border-radius: 9px;
            border: 1px solid rgba(255,255,255,0.07);
            background: rgba(7, 21, 37, 0.32);
        }}
        .policy-row {{
            display: flex;
            justify-content: space-between;
            gap: 14px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            color: {c['text_secondary']};
            font-size: 13px;
        }}
        .policy-row strong {{
            color: {c['text_primary']};
            font-family: 'IBM Plex Mono', monospace;
        }}
        .policy-final {{
            border-bottom: none;
            color: {c['gold_light']};
            font-weight: 800;
        }}
        .queue-signals ul {{
            list-style: none;
            margin: 0;
            padding: 0;
            display: grid;
            gap: 8px;
        }}
        .queue-signals li {{
            display: flex;
            justify-content: space-between;
            gap: 12px;
            color: {c['text_secondary']};
            font-size: 13px;
        }}
        .queue-signals li strong {{
            color: {c['warning']};
            font-family: 'IBM Plex Mono', monospace;
            font-size: 12px;
        }}
        .timeline-row {{
            display: grid;
            grid-template-columns: 12px 1fr;
            gap: 10px;
            padding: 7px 0;
            color: {c['text_secondary']};
        }}
        .timeline-row i {{
            width: 9px;
            height: 9px;
            margin-top: 5px;
            border-radius: 999px;
            background: {c['gold']};
            box-shadow: 0 0 10px rgba(197, 165, 114, 0.5);
        }}
        .timeline-row strong {{
            display: block;
            color: {c['text_primary']};
            font-size: 12px;
        }}
        .timeline-row span {{
            display: block;
            color: {c['text_muted']};
            font-size: 11px;
            margin-top: 2px;
        }}

        @media (max-width: 900px) {{
            .bk-header-top, .bk-header-bottom, .bank-page-header {{
                align-items: stretch;
                flex-direction: column;
            }}
            .bk-header-meta, .bk-pills, .bk-compliance {{
                gap: 8px;
            }}
            .bk-page-hero {{
                grid-template-columns: 1fr;
                padding: 20px;
            }}
            .bk-hero-status {{
                flex-direction: row;
                flex-wrap: wrap;
                min-width: 0;
            }}
            .rt-score-grid, .rt-action-grid {{
                grid-template-columns: 1fr;
            }}
            .bk-empty-state {{
                grid-template-columns: 1fr;
            }}
            .bk-page-title {{
                font-size: 28px;
            }}
            .ov-grid, .ov-panel-grid, .insight-grid, .queue-info-grid, .queue-filter-bar {{
                grid-template-columns: 1fr;
            }}
            .insight-head {{
                flex-direction: column;
            }}
            .batch-control-panel, .batch-result-strip {{
                grid-template-columns: 1fr;
            }}
            .ov-bar-row {{
                grid-template-columns: 92px 1fr 42px;
            }}
        }}
    </style>
    """
