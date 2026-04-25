"""
SPARC — Startup Profiling and Risk Coverage
===================================================================
Recommends tailor-made ICICI Lombard insurance products for Indian startups.

Run locally:
    pip install streamlit plotly pandas
    streamlit run startup_risk_app.py

No API keys required. All logic is rule-based and runs fully offline.

Author: ICICI Lombard Intern Project (Proof of Concept)
"""

import json
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import pandas as pd
from risk_engine import (
    SECTOR_PROFILES,
    SUB_SECTOR_PROFILES,
    PRODUCT_CATALOG,
    REGULATORY_CITATIONS,
    RISK_CATEGORY_STATS,
    StartupInput,
    compute_risk_scores,
    recommend_products,
    check_hard_decline_by_subsector,
)

# =============================================================================
# RISK DISPLAY GROUPS — 4 clusters for grouped scorecards in results
# =============================================================================
RISK_DISPLAY_GROUPS = {
    "Digital & Data": ["Cyber Technical Risk", "Data Privacy Risk", "IP Infringement Risk"],
    "Legal & Governance": ["Liability Risk", "Governance & Fraud Risk", "Regulatory Compliance Risk"],
    "Operational": ["Key Person Risk", "Property Risk", "Gig & Labour Risk"],
    "Macro & Emerging": ["ESG & Climate Risk", "Geopolitical Risk", "Policy Velocity Risk", "Reputation Risk"],
}

# Sub-sector options keyed by sector name
SUB_SECTOR_OPTIONS = {
    "Fintech": [
        "Fintech.NBFC_Digital_Lending", "Fintech.PA_PG", "Fintech.PA_Cross_Border",
        "Fintech.WealthTech_EOP", "Fintech.Neobank_PPI", "Fintech.InsurTech",
        "Fintech.Account_Aggregator",
    ],
    "Healthtech": [
        "Healthtech.Telemedicine", "Healthtech.Diagnostics",
        "Healthtech.PharmaTech_ePharmacy", "Healthtech.MedDevice_SaMD",
        "Healthtech.Clinical_Trials_SaaS",
    ],
    "Gaming / Media / Content": [
        "Gaming.Real_Money", "Gaming.Casual_Esports", "Gaming.OTT", "Gaming.Creator_Economy",
    ],
    "Logistics / Mobility": [
        "Logistics.Last_Mile_Delivery", "Logistics.B2B_Freight", "Logistics.EV_OEM",
    ],
    "D2C / Consumer Brands": [
        "D2C.Hardware_Electronics", "D2C.Food_Beverage", "D2C.Apparel_Footwear",
    ],
    "Deeptech / AI / Robotics": [
        "Deeptech.AI_Software", "Deeptech.Hardware_Robotics",
    ],
    "Edtech": [
        "Edtech.K12_Children", "Edtech.Test_Prep_Adult",
    ],
}

# =============================================================================
# PAGE CONFIGURATION — first Streamlit call, controls tab title and layout
# =============================================================================
st.set_page_config(
    page_title="SPARC · ICICI Lombard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# CSS — premium fintech aesthetic (Inter font, ICICI red as accent only)
# =============================================================================
st.markdown(
    """
    <style>
    /* ── Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Design tokens ── */
    :root {
      --red:        #AD1E23;
      --red-dark:   #7A1419;
      --red-tint:   rgba(173, 30, 35, 0.08);
      --ink:        #0F172A;
      --ink-muted:  #475569;
      --ink-faint:  #94A3B8;
      --bg:         #FAFAF7;
      --surface:    #F4F4F0;
      --border:     #E5E5E0;
      --white:      #FFFFFF;
      --shadow-sm:  0 1px 2px rgba(15,23,42,.04), 0 4px 12px rgba(15,23,42,.04);
      --shadow-md:  0 2px 4px rgba(15,23,42,.06), 0 8px 24px rgba(15,23,42,.08);
      --r-card:     12px;
      --r-input:    8px;
      --r-btn:      10px;
    }

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--ink);
    }
    .stApp { background-color: var(--bg) !important; }
    .main .block-container {
        max-width: 1200px !important;
        padding: 1.75rem 2.5rem 4rem !important;
        margin: 0 auto !important;
    }

    /* ── Hide Streamlit chrome ── */
    #MainMenu                          { visibility: hidden !important; }
    footer                             { visibility: hidden !important; }
    [data-testid="stToolbar"]          { visibility: hidden !important; }
    [data-testid="stDecoration"]       { display: none !important; }
    [data-testid="stHeader"]           { background: transparent !important; }
    [data-testid="stStatusWidget"]     { display: none !important; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--white) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebarContent"] {
        padding: 1.75rem 1.25rem 1.5rem !important;
    }

    /* ── Sidebar section labels ── */
    .sidebar-section {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--ink-faint);
        margin: 1.5rem 0 0.65rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border);
    }
    .sidebar-section.first { margin-top: 0.5rem; }

    /* ── Privacy badge ── */
    .privacy-badge {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.55rem 0.8rem;
        margin-top: 1.25rem;
        font-size: 0.72rem;
        color: var(--ink-muted);
        line-height: 1.4;
    }

    /* ── Text inputs ── */
    .stTextInput > div > div > input {
        border-radius: var(--r-input) !important;
        border: 1px solid var(--border) !important;
        background: var(--white) !important;
        color: var(--ink) !important;
        font-size: 0.88rem !important;
        padding: 0.5rem 0.75rem !important;
        transition: border-color .15s, box-shadow .15s !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--red) !important;
        box-shadow: 0 0 0 3px rgba(173,30,35,.12) !important;
        outline: none !important;
    }

    /* ── Selectbox ── */
    [data-testid="stSelectbox"] > div > div {
        border-radius: var(--r-input) !important;
        border: 1px solid var(--border) !important;
        background: var(--white) !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stSelectbox"] > div > div:focus-within {
        border-color: var(--red) !important;
        box-shadow: 0 0 0 3px rgba(173,30,35,.12) !important;
    }

    /* ── Slider (recolor thumb + filled track) ── */
    [data-testid="stSlider"] [role="slider"] {
        background-color: var(--red) !important;
        border-color: var(--red) !important;
    }
    [data-testid="stSlider"] [data-baseweb="slider"] > div > div > div:first-child {
        background: var(--red) !important;
    }

    /* ── Slider label + value pill ── */
    .slider-label-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.82rem;
        font-weight: 500;
        color: var(--ink);
        margin-bottom: 0.2rem;
    }
    .value-pill {
        background: var(--red-tint);
        color: var(--red);
        font-weight: 700;
        font-size: 0.72rem;
        padding: 2px 9px;
        border-radius: 20px;
        min-width: 34px;
        text-align: center;
    }

    /* ── Select slider ── */
    [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
        background: var(--red) !important;
        border-color: var(--red) !important;
    }

    /* ── Radio ── */
    [data-testid="stRadio"] label { font-size: 0.85rem !important; }

    /* ── Button ── */
    [data-testid="stButton"] > button,
    .stButton > button {
        background: var(--red) !important;
        border: none !important;
        border-radius: var(--r-btn) !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
        padding: 0.65rem 1.25rem !important;
        height: auto !important;
        min-height: 0 !important;
        transition: background .15s, transform .1s !important;
        width: 100% !important;
    }
    [data-testid="stButton"] > button:hover,
    .stButton > button:hover {
        background: var(--red-dark) !important;
        transform: translateY(-1px) !important;
    }
    [data-testid="stButton"] > button:active,
    .stButton > button:active { transform: none !important; }

    /* ── Widget labels ── */
    [data-testid="stWidgetLabel"] > label,
    .stSlider label,
    .stSelectbox label,
    .stTextInput label,
    [data-testid="stRadio"] > label,
    [data-testid="stSelectSlider"] > label {
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        color: var(--ink) !important;
    }

    /* ── Captions ── */
    [data-testid="stCaptionContainer"],
    .stCaption {
        font-size: 0.74rem !important;
        color: var(--ink-faint) !important;
    }

    /* ── Metrics ── */
    [data-testid="stMetric"] {
        background: var(--white) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r-card) !important;
        padding: 0.85rem 1rem !important;
        box-shadow: var(--shadow-sm) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.07em !important;
        text-transform: uppercase !important;
        color: var(--ink-faint) !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1rem !important;
        font-weight: 700 !important;
        color: var(--ink) !important;
    }

    /* ── Horizontal rule ── */
    hr {
        border: none !important;
        border-top: 1px solid var(--border) !important;
        margin: 2rem 0 !important;
    }

    /* ── Expanders ── */
    [data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--r-card) !important;
        background: var(--white) !important;
        box-shadow: none !important;
        margin-bottom: 0.65rem !important;
    }
    [data-testid="stExpander"] summary {
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        color: var(--ink) !important;
    }

    /* ══════════════ CUSTOM HTML COMPONENTS ══════════════ */

    /* Hero */
    .hero-block {
        background: linear-gradient(135deg, #AD1E23 0%, #7A1419 100%);
        padding: 2.25rem 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2.25rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 24px rgba(173,30,35,.22);
    }
    .hero-block::before {
        content: '';
        position: absolute;
        top: -80px; right: -80px;
        width: 340px; height: 340px;
        background: radial-gradient(circle, rgba(255,255,255,.07) 0%, transparent 65%);
        pointer-events: none;
    }
    .hero-block::after {
        content: '';
        position: absolute;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg width='52' height='52' viewBox='0 0 52 52' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.035' fill-rule='evenodd'%3E%3Cpath d='M10 10h4v4h-4zM26 10h4v4h-4zM42 10h4v4h-4zM10 26h4v4h-4zM26 26h4v4h-4zM42 26h4v4h-4zM10 42h4v4h-4zM26 42h4v4h-4zM42 42h4v4h-4z'/%3E%3C/g%3E%3C/svg%3E");
        pointer-events: none;
    }
    .hero-eyebrow {
        font-size: 0.63rem;
        font-weight: 700;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: rgba(255,255,255,.65);
        margin-bottom: 0.65rem;
        display: flex;
        align-items: center;
        gap: 0.45rem;
        position: relative;
        z-index: 1;
    }
    .hero-title {
        font-size: 2.25rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.15;
        color: white;
        margin: 0 0 0.55rem 0;
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        gap: 0.55rem;
    }
    .hero-tagline {
        font-size: 0.95rem;
        color: rgba(255,255,255,.8);
        line-height: 1.55;
        margin: 0;
        position: relative;
        z-index: 1;
    }
    .hero-rule {
        border: none;
        border-top: 1px solid rgba(255,255,255,.18);
        margin: 1rem 0 0.75rem 0;
        position: relative;
        z-index: 1;
    }
    .hero-micro {
        font-size: 0.7rem;
        color: rgba(255,255,255,.45);
        letter-spacing: 0.03em;
        position: relative;
        z-index: 1;
    }

    /* Info card */
    .info-card {
        background: var(--white);
        border: 1px solid var(--border);
        border-left: 4px solid var(--red);
        border-radius: var(--r-card);
        padding: 1.1rem 1.3rem;
        margin-bottom: 1.75rem;
        display: flex;
        align-items: flex-start;
        gap: 0.8rem;
        box-shadow: var(--shadow-sm);
    }
    .info-card-icon { flex-shrink: 0; margin-top: 1px; }
    .info-card-body {
        font-size: 0.88rem;
        color: var(--ink-muted);
        line-height: 1.65;
    }
    .info-card-body strong { color: var(--red); font-weight: 600; }

    /* Feature cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.25rem;
        margin: 1.25rem 0 2.5rem 0;
    }
    .feature-card {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: var(--r-card);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
        transition: box-shadow .2s ease, transform .2s ease;
    }
    .feature-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    .feature-icon {
        width: 40px;
        height: 40px;
        background: var(--red-tint);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.9rem;
    }
    .feature-title {
        font-size: 0.93rem;
        font-weight: 600;
        color: var(--ink);
        margin-bottom: 0.35rem;
        letter-spacing: -0.01em;
    }
    .feature-desc {
        font-size: 0.82rem;
        color: var(--ink-muted);
        line-height: 1.6;
    }

    /* Section headings */
    .section-heading {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--ink);
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }
    .section-sub {
        font-size: 0.82rem;
        color: var(--ink-muted);
        margin-bottom: 0.75rem;
    }

    /* Verdict card */
    .verdict-card {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: var(--r-card);
        padding: 0.9rem 1.2rem;
        margin: 0.75rem 0 1.25rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        box-shadow: var(--shadow-sm);
        font-size: 0.88rem;
        color: var(--ink);
        line-height: 1.55;
    }
    .verdict-dot { font-size: 1.1rem; flex-shrink: 0; line-height: 1; }

    /* Product cards */
    .product-card {
        background: var(--white);
        border: 1px solid var(--border);
        border-left: 4px solid var(--red);
        border-radius: var(--r-card);
        padding: 1.2rem 1.4rem;
        margin: 0.6rem 0;
        box-shadow: var(--shadow-sm);
        transition: box-shadow .2s ease, transform .2s ease;
    }
    .product-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    .product-card h4 {
        margin: 0 0 0.3rem 0;
        font-size: 0.98rem;
        font-weight: 600;
        color: var(--ink);
        letter-spacing: -0.01em;
    }

    /* Priority badges — soft semantic tokens */
    .priority-critical {
        background: #FEE2E2;
        color: #991B1B;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .priority-recommended {
        background: #FEF3C7;
        color: #92400E;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .priority-optional {
        background: #D1FAE5;
        color: #065F46;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* Nudge box */
    .nudge-box {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-left: 3px solid #F59E0B;
        padding: 0.6rem 0.9rem;
        margin-top: 0.7rem;
        border-radius: 8px;
        font-style: italic;
        font-size: 0.82rem;
        color: #78350F;
        line-height: 1.55;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# GENAI — locked to gemini-2.5-flash-lite (free tier, lowest cost model)
# Do NOT change _GEMINI_MODEL to flash, pro, or ultra variants — they are paid.
# =============================================================================
_GEMINI_MODEL = "gemini-2.5-flash-lite"   # cheapest available; do not upgrade
_GEMINI_MAX_TOKENS = 2048                  # fits full JSON response; still within free tier

_GENAI_AVAILABLE = False
_GEMINI_CLIENT = None

try:
    from google import genai as _genai  # type: ignore[import]
    from google.genai import types as _genai_types  # type: ignore[import]

    try:
        _GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        _GEMINI_KEY = ""

    if _GEMINI_KEY:
        _GEMINI_CLIENT = _genai.Client(api_key=_GEMINI_KEY)
        _GENAI_AVAILABLE = True
except ImportError:
    pass


# =============================================================================
# UI HELPERS
# =============================================================================
def priority_css(label: str) -> str:
    return {
        "Critical":    "priority-critical",
        "Recommended": "priority-recommended",
        "Optional":    "priority-optional",
    }.get(label, "priority-optional")


# =============================================================================
# VISUALIZATION
# =============================================================================
def render_risk_radar(scores: dict):
    categories = list(scores.keys()) + [list(scores.keys())[0]]
    values = list(scores.values()) + [list(scores.values())[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=categories, fill='toself',
        line=dict(color='#AD1E23', width=2),
        fillcolor='rgba(173,30,35,0.15)', name='Risk profile'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100],
                                   tickfont=dict(size=10, color='#94A3B8'),
                                   gridcolor='#E5E5E0'),
                   angularaxis=dict(tickfont=dict(size=11, color='#0F172A'))),
        showlegend=False, height=400,
        margin=dict(l=60, r=60, t=30, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig


def render_risk_bars(scores: dict):
    """Horizontal bar chart with color-band backgrounds and threshold reference lines."""
    df = pd.DataFrame({
        "Category": list(scores.keys()),
        "Score": list(scores.values()),
    }).sort_values("Score", ascending=True)

    def band_color(s):
        if s >= 70: return "#AD1E23"
        if s >= 40: return "#F59E0B"
        return "#10B981"

    fig = go.Figure()

    # Faint background bands for each priority zone
    fig.add_shape(type="rect", x0=0,  x1=40,  y0=-0.5, y1=len(df) - 0.5,
                  fillcolor="rgba(16,185,129,0.04)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=40, x1=70,  y0=-0.5, y1=len(df) - 0.5,
                  fillcolor="rgba(245,158,11,0.05)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=70, x1=100, y0=-0.5, y1=len(df) - 0.5,
                  fillcolor="rgba(173,30,35,0.05)", line_width=0, layer="below")

    # Threshold lines with labels
    for x_val, label, color in [(40, "Recommended", "#F59E0B"), (70, "Critical", "#AD1E23")]:
        fig.add_vline(x=x_val, line_dash="dot", line_color=color,
                      line_width=1.2, opacity=0.6)
        fig.add_annotation(x=x_val, y=len(df) - 0.1, text=label,
                           showarrow=False,
                           font=dict(size=9, color=color),
                           xanchor="center", yanchor="bottom")

    # Bars
    fig.add_trace(go.Bar(
        x=df["Score"],
        y=df["Category"],
        orientation="h",
        marker=dict(color=[band_color(s) for s in df["Score"]], line=dict(width=0)),
        text=[f"<b>{s:.0f}</b>" for s in df["Score"]],
        textposition="outside",
        textfont=dict(size=12, color="#0F172A"),
        hovertemplate="%{y}: %{x:.1f}/100<extra></extra>",
    ))

    fig.update_layout(
        xaxis=dict(range=[0, 115], showgrid=False, zeroline=False,
                   tickfont=dict(color="#94A3B8", size=10),
                   title=dict(text="Risk Score (0–100)",
                              font=dict(size=10, color="#94A3B8"))),
        yaxis=dict(title="", tickfont=dict(size=11, color="#0F172A")),
        height=550,
        margin=dict(l=20, r=60, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        bargap=0.35,
    )
    return fig


def render_risk_scorecards(scores: dict) -> str:
    """Returns HTML for mini scorecard tiles — one per risk dimension (handles 13 categories)."""

    def band(s):
        if s >= 70: return "#AD1E23", "#FEF2F2", "Critical"
        if s >= 40: return "#D97706", "#FFFBEB", "Watch"
        return "#059669", "#ECFDF5", "Low"

    # Generic shield icon used for all categories
    _shield_path = (
        '<path d="M12 2L4 5.5v5.25C4 15.36 7.53 19.9 12 21.25'
        ' 16.47 19.9 20 15.36 20 10.75V5.5L12 2z"'
        ' stroke="currentColor" stroke-width="1.5" fill="none"/>'
    )

    cards_html = (
        '<style>body{margin:0;background:transparent;'
        "font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;}</style>"
        '<div style="display:flex;flex-direction:column;gap:8px;">'
    )
    for dim, score in scores.items():
        color, bg, label = band(score)
        bar_pct = int(min(score, 100))
        cards_html += (
            f'<div style="background:{bg};border:1px solid {color}22;border-radius:10px;'
            f'padding:9px 12px;display:flex;align-items:center;gap:10px;">'
            f'<div style="flex-shrink:0;width:28px;height:28px;border-radius:7px;'
            f'background:{color}15;display:flex;align-items:center;'
            f'justify-content:center;color:{color};">'
            f'<svg width="14" height="14" viewBox="0 0 24 24">{_shield_path}</svg>'
            f'</div>'
            f'<div style="flex:1;min-width:0;">'
            f'<div style="font-size:0.67rem;font-weight:600;color:#475569;'
            f'letter-spacing:0.02em;margin-bottom:4px;white-space:nowrap;'
            f'overflow:hidden;text-overflow:ellipsis;">{dim}</div>'
            f'<div style="background:#E5E5E0;border-radius:4px;height:4px;width:100%;">'
            f'<div style="background:{color};height:4px;border-radius:4px;'
            f'width:{bar_pct}%;"></div>'
            f'</div>'
            f'</div>'
            f'<div style="flex-shrink:0;text-align:right;min-width:38px;">'
            f'<div style="font-size:1rem;font-weight:800;color:{color};'
            f'line-height:1;">{score:.0f}</div>'
            f'<div style="font-size:0.58rem;font-weight:600;color:{color};'
            f'opacity:0.75;letter-spacing:0.05em;'
            f'text-transform:uppercase;">{label}</div>'
            f'</div>'
            f'</div>'
        )
    cards_html += "</div>"
    return cards_html


# =============================================================================
# GENAI HELPERS
# =============================================================================
def _catalog_for_prompt() -> str:
    lines = []
    for key, p in PRODUCT_CATALOG.items():
        snippet = p["what_it_covers"][:110].replace("\n", " ")
        lines.append(f"  {key}: {p['name']} — {snippet}...")
    return "\n".join(lines)


def generate_bundles(
    startup_name: str,
    sector: str,
    stage: str,
    team_size: int,
    operations: str,
    data_sensitivity: str,
    scores: dict,
    product_description: str = "",
    customer_type=None,
    data_handled=None,
    regulatory=None,
    physical_assets=None,
    has_investors: str = "No",
    biggest_fear: str = "",
) -> dict:
    """Calls Gemini 1.5 Flash to produce 1–2 insurance bundles. Returns parsed JSON or None."""
    if not _GENAI_AVAILABLE:
        return None

    profile_parts = [
        f"Startup name: {startup_name}",
        f"Sector: {sector}",
        f"Funding stage: {stage}",
        f"Team size: {team_size} people",
        f"Primary operations: {operations}",
        f"Customer data sensitivity: {data_sensitivity}",
        f"Institutional investors: {has_investors}",
    ]
    if product_description.strip():
        profile_parts.append(f"What they build/do: {product_description.strip()}")
    if customer_type:
        profile_parts.append(f"Customer types: {', '.join(customer_type)}")
    if data_handled:
        profile_parts.append(f"Data / assets handled: {', '.join(data_handled)}")
    if regulatory:
        profile_parts.append(f"Regulatory exposure: {', '.join(regulatory)}")
    if physical_assets:
        profile_parts.append(f"Physical assets owned: {', '.join(physical_assets)}")
    if biggest_fear.strip():
        profile_parts.append(f"Founder's biggest fear: {biggest_fear.strip()}")

    score_lines = [f"  {k}: {v}/100" for k, v in scores.items()]

    prompt = (
        "You are an expert insurance advisor specialising in Indian startups "
        "and ICICI Lombard products. Analyse the startup profile and risk scores "
        "below, then recommend 1–2 coherent insurance bundles.\n\n"
        "Each bundle groups products that address a shared risk theme "
        "(e.g. 'Digital Risk Bundle', 'Physical Ops Bundle').\n"
        "For every product inside a bundle, write a 'why_for_you' field "
        "that is SPECIFIC to this startup — mention their sector, data type, "
        "team size, regulatory exposure, or stated fear. Do NOT write generic text.\n\n"
        "Return ONLY valid JSON — no markdown fences, no explanation:\n"
        "{\n"
        '  "risk_narrative": "2-3 sentences interpreting the overall risk profile specific to this startup",\n'
        '  "top_risks": [\n'
        "    {\n"
        '      "dimension": "exact dimension name e.g. Cyber Risk",\n'
        '      "score": 100,\n'
        '      "why": "2-3 sentences explaining why this score is high for THIS specific startup",\n'
        '      "mitigation": "one concrete non-insurance action to reduce this risk (process, certification, tool, or policy)"\n'
        "    }\n"
        "  ],\n"
        '  "bundles": [\n'
        "    {\n"
        '      "name": "bundle name",\n'
        '      "tagline": "one-line description of what this bundle protects",\n'
        '      "priority": "Critical or Recommended",\n'
        '      "buy_timeline": "e.g. Before your next funding round",\n'
        '      "bundle_summary": "2-3 sentence justification specific to this startup",\n'
        '      "products": [\n'
        "        {\n"
        '          "key": "exact product key from catalog",\n'
        '          "name": "product name",\n'
        '          "why_for_you": "2-3 startup-specific sentences"\n'
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ],\n"
        '  "bottom_line": "one sentence of overall advice for this founder"\n'
        "}\n\n"
        "STARTUP PROFILE:\n"
        + "\n".join(profile_parts)
        + "\n\nRISK SCORES (70+ = Critical, 40–69 = Recommended, <40 = Optional):\n"
        + "\n".join(score_lines)
        + "\n\nPRODUCT CATALOG (use ONLY these exact keys):\n"
        + _catalog_for_prompt()
        + "\n\nRules:\n"
        "- top_risks: include only dimensions with score >= 40, max 3 entries, ordered by score descending\n"
        "- top_risks.why must mention specific details from this startup's profile (sector, data, team, fear)\n"
        "- top_risks.mitigation must be a non-insurance action — never mention buying a policy here\n"
        "- Each bundle must contain 3–5 products\n"
        "- Use only product keys listed in the catalog above\n"
        "- why_for_you must reference specific details from this startup's profile\n"
        "- Do not include clinical_trials unless regulatory exposure mentions CDSCO\n"
        "- employee_health must be included in at least one bundle\n"
        "- Assign priority 'Critical' if any risk score is 70 or above\n"
    )

    try:
        response = _GEMINI_CLIENT.models.generate_content(
            model=_GEMINI_MODEL,
            contents=prompt,
            config=_genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.4,
                max_output_tokens=_GEMINI_MAX_TOKENS,
            ),
        )
        # Detect truncation before attempting JSON parse
        try:
            finish_reason = response.candidates[0].finish_reason
            if str(finish_reason) in ("FinishReason.MAX_TOKENS", "MAX_TOKENS", "2"):
                st.warning(
                    "⚠️ AI response was cut short (output limit reached). "
                    "Showing rule-based recommendations instead."
                )
                return None
        except (AttributeError, IndexError):
            pass

        result = json.loads(response.text)
        # Sanitize: remove any product keys not in catalog
        valid_keys = set(PRODUCT_CATALOG.keys())
        for bundle in result.get("bundles", []):
            bundle["products"] = [
                p for p in bundle.get("products", [])
                if p.get("key") in valid_keys
            ]
            # Normalise priority to Critical / Recommended only
            if bundle.get("priority") not in ("Critical", "Recommended"):
                bundle["priority"] = "Recommended"
        return result
    except json.JSONDecodeError:
        st.warning(
            "⚠️ AI returned malformed output. "
            "Showing rule-based recommendations instead."
        )
        return None
    except Exception as exc:
        st.warning(
            f"⚠️ AI unavailable ({exc}). "
            "Showing rule-based recommendations instead."
        )
        return None


def render_bundle_card(bundle: dict) -> str:
    """Returns the HTML string for one insurance bundle card."""
    priority = bundle.get("priority", "Recommended")
    border_color = "#AD1E23" if priority == "Critical" else "#F59E0B"
    priority_class = "priority-critical" if priority == "Critical" else "priority-recommended"

    products_html = ""
    for p in bundle.get("products", []):
        products_html += (
            '<div style="background:#FAFAF7;border:1px solid #E5E5E0;border-radius:8px;'
            "padding:0.9rem 1.1rem;margin-bottom:0.55rem;\">"
            f'<div style="font-size:0.9rem;font-weight:600;color:#0F172A;'
            f'margin-bottom:0.35rem;">{p.get("name", "")}</div>'
            f'<div style="font-size:0.83rem;color:#475569;line-height:1.65;">'
            f'<strong style="color:#AD1E23;">Why for you:</strong> '
            f'{p.get("why_for_you", "")}</div>'
            "</div>"
        )

    timeline = bundle.get("buy_timeline", "")
    timeline_html = (
        f'<div style="margin-top:0.85rem;font-size:0.78rem;color:#64748B;'
        f'display:flex;align-items:center;gap:0.4rem;">'
        f'<svg width="13" height="13" viewBox="0 0 24 24" fill="none">'
        f'<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5"/>'
        f'<path d="M12 7v5l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>'
        f"</svg><span>{timeline}</span></div>"
    ) if timeline else ""

    return (
        f'<div style="background:#FFFFFF;border:1px solid {border_color}33;'
        f"border-left:4px solid {border_color};border-radius:12px;"
        f"padding:1.4rem 1.6rem;margin:0.75rem 0;"
        f'box-shadow:0 2px 8px rgba(15,23,42,0.06);">'
        f'<div style="display:flex;justify-content:space-between;'
        f'align-items:flex-start;margin-bottom:0.75rem;">'
        f'<div style="flex:1;min-width:0;padding-right:1rem;">'
        f'<div style="font-size:1.1rem;font-weight:700;color:#0F172A;'
        f'letter-spacing:-0.02em;margin-bottom:0.2rem;">'
        f'{bundle.get("name", "Insurance Bundle")}</div>'
        f'<div style="font-size:0.82rem;color:#475569;">'
        f'{bundle.get("tagline", "")}</div></div>'
        f'<span class="{priority_class}">{priority}</span></div>'
        f'<div style="background:#F4F4F0;border-radius:8px;padding:0.75rem 1rem;'
        f'margin-bottom:0.9rem;font-size:0.86rem;color:#0F172A;line-height:1.65;">'
        f'{bundle.get("bundle_summary", "")}</div>'
        f'<div style="font-size:0.72rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;color:#94A3B8;margin-bottom:0.55rem;">'
        "Products in this bundle</div>"
        f"{products_html}"
        f"{timeline_html}"
        "</div>"
    )


# =============================================================================
# UI — Hero
# =============================================================================
st.markdown(
    """
    <div class="hero-block">
      <div class="hero-eyebrow">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
          <rect width="12" height="12" rx="2" fill="rgba(255,255,255,0.25)"/>
          <path d="M6 1.5L2 3.5v3c0 2.07 1.65 4 4 4.58C8.35 10.5 10 8.57 10 6.5v-3L6 1.5z" fill="white"/>
        </svg>
        Insurance Advisory
      </div>
      <div class="hero-title">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
          <path d="M12 2L4 5.5v5.25C4 15.36 7.53 19.9 12 21.25 16.47 19.9 20 15.36 20 10.75V5.5L12 2z" fill="white"/>
          <path d="M9 12l2 2 4-4" stroke="#AD1E23" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        SPARC &nbsp;·&nbsp; ICICI Lombard
      </div>
      <p class="hero-tagline">Startup Profiling and Risk Coverage — GenAI-powered insurance recommendations tailored to your startup's unique risk profile.</p>
      <hr class="hero-rule"/>
      <p class="hero-micro">Powered by GenAI &nbsp;·&nbsp; Built for Indian startups &nbsp;·&nbsp; ICICI Lombard</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# UI — Sidebar (minimal — all inputs live in the main panel)
# =============================================================================
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:1.25rem 0 1.75rem;">
          <svg width="38" height="38" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L4 5.5v5.25C4 15.36 7.53 19.9 12 21.25 16.47 19.9 20 15.36 20 10.75V5.5L12 2z" fill="#AD1E23"/>
            <path d="M9 12l2 2 4-4" stroke="white" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <div style="font-size:0.95rem;font-weight:700;color:#0F172A;margin-top:0.65rem;letter-spacing:-0.01em;">
            SPARC
          </div>
          <div style="font-size:0.72rem;color:#94A3B8;margin-top:0.15rem;">ICICI Lombard</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section first">How it works</div>', unsafe_allow_html=True)
    st.markdown("""
1. **Fill the form** with your startup details
2. **Click Analyse** to compute your 5-dimension risk scores
3. **AI** groups your coverage needs into named bundles with startup-specific reasoning
4. **Review & act** — speak to an ICICI Lombard RM to bind cover
    """)

    if _GENAI_AVAILABLE:
        st.markdown(
            '<div class="privacy-badge" style="margin-top:1.5rem;">'
            '<svg width="13" height="13" viewBox="0 0 13 13" fill="none">'
            '<path d="M6.5 1.5L2 3.8v3.2c0 2.8 1.9 5.4 4.5 6.1 2.6-.7 4.5-3.3 4.5-6.1V3.8L6.5 1.5z"'
            ' fill="#AD1E23" opacity="0.8"/></svg>'
            " AI-powered bundles are active. Inputs are processed via a secure API."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="privacy-badge" style="margin-top:1.5rem;">'
            '<svg width="13" height="13" viewBox="0 0 13 13" fill="none">'
            '<rect x="2" y="5.5" width="9" height="6" rx="1.5" stroke="#94A3B8" stroke-width="1.2" fill="none"/>'
            '<path d="M4.5 5.5V4a2 2 0 014 0v1.5" stroke="#94A3B8" stroke-width="1.2" stroke-linecap="round" fill="none"/>'
            "</svg>"
            " No GEMINI_API_KEY — rule-based recommendations. All inputs stay local."
            "</div>",
            unsafe_allow_html=True,
        )


# =============================================================================
# UI — Form (landing) or Results, driven by session_state
# =============================================================================

if not st.session_state.get("show_results"):

    # ── FORM ─────────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-heading">Startup Profile</div>'
        '<div class="section-sub">Tell us about your company — takes about 60 seconds.</div>',
        unsafe_allow_html=True,
    )

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        startup_name = st.text_input("Startup name", value="Acme Labs",
                                     help="Used as a label in your report.")
    with fc2:
        sector = st.selectbox("Sector", list(SECTOR_PROFILES.keys()),
                              help="Pick the sector that describes most of your revenue.")
    with fc3:
        funding_stage = st.selectbox("Funding stage",
                                     ["Pre-seed", "Seed", "Series A", "Series B+"])

    st.caption(f"{SECTOR_PROFILES[sector]['emoji']}  {SECTOR_PROFILES[sector]['description']}")

    _sub_opts = SUB_SECTOR_OPTIONS.get(sector, [])
    sub_sector: str | None = None
    if _sub_opts:
        _sub_raw = st.selectbox(
            "Sub-sector (optional — refines risk scores)",
            ["— General —"] + _sub_opts,
            help="Select your specific business model for a more precise regulatory risk assessment.",
        )
        sub_sector = None if _sub_raw == "— General —" else _sub_raw

    if sub_sector:
        _decline_msg = check_hard_decline_by_subsector(sub_sector)
        if _decline_msg:
            st.error(f"**Coverage unavailable for this sub-sector.** {_decline_msg}")
            st.stop()

    fr1, fr2, fr3 = st.columns([1.2, 1, 1])
    with fr1:
        team_size = st.slider("Team size (FTEs)", 1, 500, 15)
    with fr2:
        operations = st.radio(
            "Primary operations",
            ["Digital-only", "Physical-only", "Hybrid"],
            horizontal=True,
            help="Digital-only = cloud/SaaS · Physical = warehouse/factory · Hybrid = both.",
        )
    with fr3:
        data_sensitivity = st.select_slider(
            "Customer data sensitivity",
            options=["Low", "Medium", "High"],
            value="Medium",
            help="High = financial, health, or identity data.",
        )

    st.markdown("---")
    st.markdown(
        '<div class="section-heading">Tell Us More '
        '<span style="font-size:0.68rem;background:#EEF2FF;color:#3730A3;'
        'padding:2px 8px;border-radius:10px;margin-left:6px;font-weight:600;">'
        "Powers AI bundles</span></div>"
        '<div class="section-sub">The more detail you give, the more specific the AI\'s reasoning.</div>',
        unsafe_allow_html=True,
    )

    fa, fb = st.columns([1.3, 1])
    with fa:
        product_description = st.text_area(
            "What does your product / service do?",
            placeholder="e.g. We build a UPI payment gateway for SMBs, processing 10k+ txns/day…",
            height=110,
            help="Be specific — what you build, who it's for, how it works.",
        )
    with fb:
        customer_type = st.multiselect(
            "Who are your customers?",
            ["B2B Enterprise", "B2C Consumers", "Government / PSU",
             "D2C / Marketplace", "SMB / MSME"],
        )
        has_investors = st.radio(
            "Institutional investors on board?",
            ["Yes", "No"],
            index=1,
            horizontal=True,
            help="VCs / angels often require D&O and other policies.",
        )

    fd, fe, ff = st.columns(3)
    with fd:
        data_handled = st.multiselect(
            "Sensitive data / assets you handle",
            [
                "Payments / financial transactions",
                "Health / medical records",
                "Personal identity data (KYC / Aadhaar)",
                "Physical inventory / goods",
                "Sensitive personal data (DPDP Act)",
                "None of the above",
            ],
        )
    with fe:
        regulatory = st.multiselect(
            "Regulatory exposure",
            [
                "RBI / SEBI / IRDAI licensed",
                "FSSAI / food safety",
                "CDSCO / medical devices",
                "DPDP Act obligations",
                "DGCA / drone operations",
                "None / minimal",
            ],
        )
    with ff:
        physical_assets = st.multiselect(
            "Physical assets you own",
            [
                "Office / coworking space",
                "Warehouse / fulfilment centre",
                "Lab / R&D equipment",
                "Vehicles / delivery fleet",
                "Kitchen / food processing",
                "None — fully cloud",
            ],
        )

    biggest_fear = st.text_area(
        "Biggest fear for your startup? (optional)",
        placeholder="e.g. A data breach that kills customer trust, or a product recall that goes viral…",
        height=80,
    )

    st.markdown("---")
    st.markdown(
        '<div class="section-heading">Advanced Risk Inputs '
        '<span style="font-size:0.68rem;background:#F0FDF4;color:#166534;'
        'padding:2px 8px;border-radius:10px;margin-left:6px;font-weight:600;">'
        "Optional — sharpens 13-category scoring</span></div>"
        '<div class="section-sub">Expand any section that applies to your startup.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("Governance & Capital"):
        gc1, gc2, gc3 = st.columns(3)
        with gc1:
            investor_cn_hk_pct = st.slider(
                "China / HK investor BO %", 0, 100, 0,
                help="Beneficial ownership from China/Hong Kong — triggers DPIIT Press Note 3 government-route FDI.",
            ) / 100
            cumulative_fundraising_inr_cr = st.number_input(
                "Total fundraising (₹ Cr)", min_value=0.0, value=0.0, step=10.0,
                help="Cumulative raise in INR crore. ₹2,000cr+ triggers Competition Act DVT.",
            )
        with gc2:
            holdco_domicile = st.selectbox(
                "Holdco domicile",
                ["India", "DE", "SG", "Cayman", "Flip_pending"],
                help="Where your ultimate parent entity is incorporated.",
            )
            founder_concentration_index = st.slider(
                "Founder concentration index", 0.0, 1.0, 0.5,
                help="(founder equity %) × (1 − independent director %). "
                     "0 = fully distributed, 1 = sole founder with no independent board.",
            )
        with gc3:
            dpiit_recognition = st.checkbox("DPIIT recognised startup", value=False)
            _rbi_raw = st.selectbox(
                "RBI registration (if any)",
                ["None", "NBFC", "PA", "PPI", "RIA", "AA"],
            )
            rbi_registration = None if _rbi_raw == "None" else _rbi_raw

    with st.expander("Workforce & Gig Risk"):
        wf1, wf2 = st.columns(2)
        with wf1:
            gig_headcount_pct = st.slider(
                "Gig / contractor workforce %", 0, 100, 0,
                help="% of total headcount that are gig workers or contractors. "
                     "Triggers Social Security Code §113-114 aggregator levy.",
            ) / 100
            posh_ic_constituted = st.checkbox(
                "POSH Act Internal Committee constituted", value=False,
                help="POSH Act 2013 §4 — mandatory once you have 10+ employees.",
            )
        with wf2:
            state_footprint = st.multiselect(
                "States with significant operations",
                ["Karnataka", "Rajasthan", "Bihar", "Jharkhand", "Telangana",
                 "Maharashtra", "Delhi", "Tamil Nadu", "Gujarat", "Other"],
                help="Gig worker legislation is most aggressive in Karnataka, Rajasthan, Bihar, Jharkhand, Telangana.",
            )
            cert_in_poc_designated = st.checkbox(
                "CERT-In POC designated", value=False,
                help="CERT-In Directions 28-Apr-2022 — mandatory for qualifying entities (6-hr breach reporting).",
            )

    with st.expander("Data & AI Risk"):
        da1, da2 = st.columns(2)
        with da1:
            sdf_probability = st.slider(
                "SDF designation likelihood %", 0, 100, 0,
                help="DPDPA §10 Significant Data Fiduciary. High if you process data of 10M+ users "
                     "or handle sensitive personal data at scale (₹250cr breach penalty).",
            ) / 100
            data_localisation_status = st.selectbox(
                "Data localisation status",
                ["Unknown", "Full_onshore", "Hybrid", "Offshore"],
                help="Where customer data is stored and processed.",
            )
        with da2:
            ai_in_product = st.checkbox(
                "AI / ML in core product", value=False,
                help="Triggers MeitY AI Advisory (15-Mar-2024) and SGI Rules (10-Feb-2026) compliance obligations.",
            )
            hardware_software_split = st.slider(
                "Hardware revenue %", 0, 100, 0,
                help="% of revenue from physical hardware or manufactured products (BIS QCO, BEE compliance).",
            ) / 100

    with st.expander("Market & Supply Chain"):
        ms1, ms2 = st.columns(2)
        with ms1:
            b2b_pct = st.slider(
                "B2B revenue %", 0, 100, 50,
                help="Higher B2B % elevates professional indemnity and contractual liability exposure.",
            ) / 100
            export_eu_pct = st.slider(
                "EU revenue %", 0, 100, 0,
                help="EU exports trigger CBAM (1-Jan-2026) and EU AI Act extraterritorial reach.",
            ) / 100
            export_us_pct = st.slider("US revenue %", 0, 100, 0) / 100
        with ms2:
            export_china_pct = st.slider("China revenue %", 0, 100, 0) / 100
            chinese_supplier_pct_cogs = st.slider(
                "Chinese supplier % of COGS", 0, 100, 0,
                help="Supply-chain PN3 / geopolitical exposure.",
            ) / 100
            listed_customer_brsr_dependency = st.checkbox(
                "Listed customers requiring BRSR value-chain data", value=False,
                help="SEBI BRSR Core Circular (28-Mar-2025) pushes ESG obligations to supplier startups.",
            )

    with st.expander("Physical & Environmental"):
        pe1, pe2 = st.columns(2)
        with pe1:
            facility_climate_risk_zone = st.selectbox(
                "Facility climate risk zone",
                ["Low", "Medium", "High", "Extreme"],
                help="IMD / NDMA climate hazard classification for your primary facility location.",
            )
        with pe2:
            st.caption(
                "**Zone guide** — Low: metro/plains · Medium: coastal/semi-arid · "
                "High: flood-prone/cyclone belt · Extreme: high-altitude or delta region."
            )

    st.markdown("")
    btn_col, _ = st.columns([1, 2])
    with btn_col:
        if st.button("Analyse my startup →", type="primary", use_container_width=True):
            # Map physical_assets → hardware_software_split and facility_climate_risk_zone.
            # Take the higher-risk value between the user's explicit advanced input and
            # what the asset list implies — never silently downgrade.
            _zone_rank = {"Low": 0, "Medium": 1, "High": 2, "Extreme": 3}
            _rank_zone = {0: "Low", 1: "Medium", 2: "High", 3: "Extreme"}
            _pa_hw_boost = 0.0
            _pa_zone_floor = 0
            for _asset in physical_assets:
                if _asset == "Warehouse / fulfilment centre":
                    _pa_hw_boost = max(_pa_hw_boost, 0.30)
                    _pa_zone_floor = max(_pa_zone_floor, 1)   # at least Medium
                elif _asset == "Vehicles / delivery fleet":
                    _pa_hw_boost = max(_pa_hw_boost, 0.20)
                    _pa_zone_floor = max(_pa_zone_floor, 1)
                elif _asset == "Lab / R&D equipment":
                    _pa_hw_boost = max(_pa_hw_boost, 0.25)
                elif _asset == "Kitchen / food processing":
                    _pa_hw_boost = max(_pa_hw_boost, 0.20)
                    _pa_zone_floor = max(_pa_zone_floor, 1)
                elif _asset == "Office / coworking space":
                    _pa_hw_boost = max(_pa_hw_boost, 0.05)
                # "None — fully cloud" → no boost
            _effective_hw_split = min(1.0, max(hardware_software_split, _pa_hw_boost))
            _effective_climate_zone = _rank_zone[
                max(_zone_rank[facility_climate_risk_zone], _pa_zone_floor)
            ]

            st.session_state["profile"] = {
                "startup_name": startup_name,
                "sector": sector,
                "sub_sector": sub_sector,
                "funding_stage": funding_stage,
                "team_size": team_size,
                "operations": operations,
                "data_sensitivity": data_sensitivity,
                "product_description": product_description,
                "customer_type": customer_type,
                "data_handled": data_handled,
                "regulatory": regulatory,
                "physical_assets": physical_assets,
                "has_investors": has_investors,
                "biggest_fear": biggest_fear,
                # advanced fields
                "investor_cn_hk_pct": investor_cn_hk_pct,
                "cumulative_fundraising_inr_cr": cumulative_fundraising_inr_cr,
                "holdco_domicile": holdco_domicile,
                "founder_concentration_index": founder_concentration_index,
                "dpiit_recognition": dpiit_recognition,
                "rbi_registration": rbi_registration,
                "gig_headcount_pct": gig_headcount_pct,
                "posh_ic_constituted": posh_ic_constituted,
                "state_footprint": state_footprint,
                "cert_in_poc_designated": cert_in_poc_designated,
                "sdf_probability": sdf_probability,
                "data_localisation_status": data_localisation_status,
                "ai_in_product": ai_in_product,
                "hardware_software_split": _effective_hw_split,
                "b2b_pct": b2b_pct,
                "export_eu_pct": export_eu_pct,
                "export_us_pct": export_us_pct,
                "export_china_pct": export_china_pct,
                "chinese_supplier_pct_cogs": chinese_supplier_pct_cogs,
                "listed_customer_brsr_dependency": listed_customer_brsr_dependency,
                "facility_climate_risk_zone": _effective_climate_zone,
            }
            st.session_state["show_results"] = True
            st.session_state["_bundle_data"] = None
            st.rerun()

    st.stop()


# =============================================================================
# UI — Results
# =============================================================================
_p               = st.session_state["profile"]
startup_name     = _p["startup_name"]
sector           = _p["sector"]
funding_stage    = _p["funding_stage"]
team_size        = _p["team_size"]
operations       = _p["operations"]
data_sensitivity = _p["data_sensitivity"]
product_description = _p.get("product_description", "")
customer_type    = _p.get("customer_type", [])
data_handled     = _p.get("data_handled", [])
regulatory       = _p.get("regulatory", [])
physical_assets  = _p.get("physical_assets", [])
has_investors    = _p.get("has_investors", "No")
biggest_fear     = _p.get("biggest_fear", "")

if st.button("← Edit profile"):
    st.session_state["show_results"] = False
    st.session_state["_bundle_data"] = None
    st.rerun()

_inp = StartupInput(
    sector=sector,
    funding_stage=funding_stage,
    team_size=team_size,
    operations=operations,
    data_sensitivity=data_sensitivity,
    sub_sector=_p.get("sub_sector"),
    export_eu_pct=_p.get("export_eu_pct", 0.0),
    export_us_pct=_p.get("export_us_pct", 0.0),
    export_china_pct=_p.get("export_china_pct", 0.0),
    b2b_pct=_p.get("b2b_pct", 0.5),
    gig_headcount_pct=_p.get("gig_headcount_pct", 0.0),
    posh_ic_constituted=_p.get("posh_ic_constituted", False),
    cert_in_poc_designated=_p.get("cert_in_poc_designated", False),
    investor_cn_hk_pct=_p.get("investor_cn_hk_pct", 0.0),
    cumulative_fundraising_inr_cr=_p.get("cumulative_fundraising_inr_cr", 0.0),
    holdco_domicile=_p.get("holdco_domicile", "India"),
    founder_concentration_index=_p.get("founder_concentration_index", 0.5),
    sdf_probability=_p.get("sdf_probability", 0.0),
    data_localisation_status=_p.get("data_localisation_status", "Unknown"),
    ai_in_product=_p.get("ai_in_product", False),
    hardware_software_split=_p.get("hardware_software_split", 0.0),
    rbi_registration=_p.get("rbi_registration"),
    dpiit_recognition=_p.get("dpiit_recognition", False),
    state_footprint=_p.get("state_footprint", []),
    chinese_supplier_pct_cogs=_p.get("chinese_supplier_pct_cogs", 0.0),
    listed_customer_brsr_dependency=_p.get("listed_customer_brsr_dependency", False),
    facility_climate_risk_zone=_p.get("facility_climate_risk_zone", "Low"),
)
scores = compute_risk_scores(_inp)
recommendations = recommend_products(scores, sector, team_size, funding_stage, inp=_inp)

# Profile strip
st.markdown(f"## {SECTOR_PROFILES[sector]['emoji']} Profile: **{startup_name}**")
meta_col1, meta_col2, meta_col3, meta_col4 = st.columns(4)
meta_col1.metric("Sector", sector.split(" /")[0])
meta_col2.metric("Stage", funding_stage)
meta_col3.metric("Team", f"{team_size} people")
meta_col4.metric("Ops", operations)

st.markdown("---")

# Risk dashboard
st.markdown(
    '<div class="section-heading">Your Risk Dashboard</div>'
    '<div class="section-sub">Thirteen-category exposure profile across digital, legal, operational, and macro risk dimensions.</div>',
    unsafe_allow_html=True,
)
dash_col1, dash_col2, dash_col3 = st.columns([1.1, 1.2, 0.9])
with dash_col1:
    st.plotly_chart(render_risk_radar(scores), use_container_width=True)
with dash_col2:
    st.plotly_chart(render_risk_bars(scores), use_container_width=True)
with dash_col3:
    components.html(render_risk_scorecards(scores), height=680, scrolling=True)

# Verdict
overall = sum(scores.values()) / len(scores)
if overall >= 70:
    v_color = "#EF4444"
    v_text  = "<strong>High overall exposure.</strong> Several risk categories are at critical level — you likely need a bundled cover now."
elif overall >= 45:
    v_color = "#F59E0B"
    v_text  = "<strong>Moderate overall exposure.</strong> Cover the critical categories first, revisit the rest every 6 months."
else:
    v_color = "#10B981"
    v_text  = "<strong>Low overall exposure.</strong> Start with the essentials and layer on as you scale."

st.markdown(
    f'<div class="verdict-card">'
    f'<span class="verdict-dot" style="color:{v_color};">&#9679;</span>'
    f'<span>{v_text}</span>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Grouped risk breakdown (4 clusters) ─────────────────────────────────
st.markdown(
    '<div class="section-heading">Risk Breakdown by Category</div>'
    '<div class="section-sub">Scores grouped across four risk themes — hover for values.</div>',
    unsafe_allow_html=True,
)
for group_name, group_keys in RISK_DISPLAY_GROUPS.items():
    group_scores = {k: scores[k] for k in group_keys if k in scores}
    if not group_scores:
        continue
    max_score = max(group_scores.values())
    if max_score >= 70:
        g_color = "#AD1E23"
    elif max_score >= 40:
        g_color = "#D97706"
    else:
        g_color = "#059669"
    cols = st.columns(len(group_scores))
    st.markdown(
        f'<div style="font-size:0.72rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;color:{g_color};margin:-0.4rem 0 0.5rem 0;">'
        f'{group_name}</div>',
        unsafe_allow_html=True,
    )
    for col, (cat, val) in zip(cols, group_scores.items()):
        col.metric(cat, f"{val:.0f}/100")

# ── Risk Intelligence panel ──────────────────────────────────────────────
st.markdown(
    '<div class="section-heading" style="margin-top:1.25rem;">Risk Intelligence</div>'
    '<div class="section-sub">Statistics and forecasts behind your scores — '
    'only categories scoring 40+ are shown.</div>',
    unsafe_allow_html=True,
)

_active_cats = [cat for cat, val in scores.items() if val >= 40]
for cat in _active_cats:
    stat_data = RISK_CATEGORY_STATS.get(cat, {})
    cite_list = REGULATORY_CITATIONS.get(cat, [])
    score_val = scores[cat]
    if score_val >= 70:
        badge_bg, badge_color = "#FEE2E2", "#991B1B"
    else:
        badge_bg, badge_color = "#FEF3C7", "#92400E"

    with st.expander(f"{cat}  —  {score_val:.0f}/100"):
        if stat_data:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(
                    f'<div style="background:#F0F9FF;border-left:3px solid #0EA5E9;'
                    f'border-radius:8px;padding:0.8rem 1rem;margin-bottom:0.6rem;">'
                    f'<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;'
                    f'text-transform:uppercase;color:#0369A1;margin-bottom:0.4rem;">Current scenario</div>'
                    f'<p style="font-size:0.84rem;color:#0F172A;line-height:1.65;margin:0;">'
                    f'{stat_data.get("headline","")}</p>'
                    f'<div style="font-size:0.7rem;color:#64748B;margin-top:0.5rem;">'
                    f'📎 {stat_data.get("source","")}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f'<div style="background:#F0FDF4;border-left:3px solid #22C55E;'
                    f'border-radius:8px;padding:0.8rem 1rem;margin-bottom:0.6rem;">'
                    f'<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;'
                    f'text-transform:uppercase;color:#15803D;margin-bottom:0.4rem;">Forecast</div>'
                    f'<p style="font-size:0.84rem;color:#0F172A;line-height:1.65;margin:0;">'
                    f'{stat_data.get("forecast","")}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            sector_note = stat_data.get("sector_notes", {}).get(sector)
            if sector_note:
                st.markdown(
                    f'<div style="background:{badge_bg};border-left:3px solid {badge_color};'
                    f'border-radius:8px;padding:0.65rem 1rem;margin-bottom:0.6rem;">'
                    f'<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;'
                    f'text-transform:uppercase;color:{badge_color};margin-bottom:0.3rem;">'
                    f'Why this matters for {sector}</div>'
                    f'<p style="font-size:0.84rem;color:#0F172A;line-height:1.6;margin:0;">'
                    f'{sector_note}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        if cite_list:
            st.markdown(
                '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;'
                'text-transform:uppercase;color:#94A3B8;margin:0.4rem 0 0.3rem 0;">'
                'Statutes &amp; regulations</div>',
                unsafe_allow_html=True,
            )
            for cite in cite_list:
                st.markdown(f"- {cite}")

st.markdown("---")

# ── Trigger Gemini (single call covers narrative + top_risks + bundles) ──
if st.session_state.get("_bundle_data") is None and _GENAI_AVAILABLE:
    with st.spinner("✨ Analysing your risk profile and crafting your insurance plan…"):
        st.session_state["_bundle_data"] = generate_bundles(
            startup_name=startup_name, sector=sector, stage=funding_stage,
            team_size=team_size, operations=operations,
            data_sensitivity=data_sensitivity, scores=scores,
            product_description=product_description, customer_type=customer_type,
            data_handled=data_handled, regulatory=regulatory,
            physical_assets=physical_assets, has_investors=has_investors,
            biggest_fear=biggest_fear,
        )

bundle_result = st.session_state.get("_bundle_data")

# ── GenAI Risk Narrative ─────────────────────────────────────────────────
if bundle_result and bundle_result.get("risk_narrative"):
    st.markdown(
        '<div class="section-heading">GenAI Risk Analysis</div>'
        '<div class="section-sub">AI interpretation of your specific risk profile.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="background:#F0F4FF;border:1px solid #C7D2FE;border-left:4px solid #6366F1;'
        f'border-radius:12px;padding:1.1rem 1.4rem;margin-bottom:1.25rem;">'
        f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.55rem;">'
        f'<svg width="14" height="14" viewBox="0 0 24 24" fill="none">'
        f'<path d="M12 2L9.5 9.5H2L8 14l-2.5 7.5L12 17l6.5 4.5L16 14l6-4.5H14.5L12 2z" '
        f'fill="#6366F1"/></svg>'
        f'<span style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;color:#6366F1;">AI Risk Assessment</span></div>'
        f'<p style="font-size:0.92rem;color:#0F172A;line-height:1.7;margin:0;">'
        f'{bundle_result["risk_narrative"]}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Top Risk Dimensions ──────────────────────────────────────────────────
if bundle_result and bundle_result.get("top_risks"):
    top_risks = bundle_result["top_risks"]
    st.markdown(
        '<div class="section-heading" style="margin-top:0.5rem;">Top Risk Dimensions</div>'
        '<div class="section-sub">What\'s driving your scores — and one action to reduce each risk.</div>',
        unsafe_allow_html=True,
    )
    risk_cols = st.columns(min(len(top_risks), 3))
    for i, risk in enumerate(top_risks[:3]):
        score = risk.get("score", 0)
        if score >= 70:
            badge_bg, badge_color, border_color = "#FEE2E2", "#991B1B", "#EF4444"
        else:
            badge_bg, badge_color, border_color = "#FEF3C7", "#92400E", "#F59E0B"
        with risk_cols[i]:
            st.markdown(
                f'<div style="background:#FFFFFF;border:1px solid {border_color}44;'
                f'border-top:3px solid {border_color};border-radius:12px;'
                f'padding:1.2rem 1.3rem;box-shadow:0 2px 8px rgba(15,23,42,0.06);">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'margin-bottom:0.75rem;">'
                f'<div style="font-size:0.88rem;font-weight:600;color:#0F172A;">'
                f'{risk.get("dimension", "")}</div>'
                f'<div style="background:{badge_bg};color:{badge_color};font-size:0.85rem;'
                f'font-weight:800;padding:3px 10px;border-radius:20px;">{score}</div>'
                f'</div>'
                f'<div style="font-size:0.72rem;font-weight:700;letter-spacing:0.06em;'
                f'text-transform:uppercase;color:#94A3B8;margin-bottom:0.35rem;">Why</div>'
                f'<p style="font-size:0.84rem;color:#475569;line-height:1.65;margin:0 0 0.85rem 0;">'
                f'{risk.get("why", "")}</p>'
                f'<div style="background:#F1F5F9;border-radius:8px;padding:0.7rem 0.85rem;">'
                f'<div style="font-size:0.72rem;font-weight:700;letter-spacing:0.06em;'
                f'text-transform:uppercase;color:#6366F1;margin-bottom:0.3rem;">Non-insurance action</div>'
                f'<p style="font-size:0.83rem;color:#0F172A;line-height:1.6;margin:0;">'
                f'{risk.get("mitigation", "")}</p>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")

# ── Insurance Plan ───────────────────────────────────────────────────────
st.markdown(
    '<div class="section-heading">Your Insurance Plan</div>'
    '<div class="section-sub">AI groups your needs into coherent bundles — '
    "each product comes with a reason specific to your startup.</div>",
    unsafe_allow_html=True,
)

if bundle_result and "bundles" in bundle_result:
    for bundle in bundle_result["bundles"]:
        st.markdown(render_bundle_card(bundle), unsafe_allow_html=True)
    if bundle_result.get("bottom_line"):
        st.markdown(
            f'<div class="verdict-card" style="margin-top:1rem;">'
            f'<span style="font-size:1.1rem;flex-shrink:0;">💡</span>'
            f'<span><strong>Bottom line:</strong> {bundle_result["bottom_line"]}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
else:
    if not _GENAI_AVAILABLE:
        st.info(
            "Add your **GEMINI_API_KEY** to `.streamlit/secrets.toml` to get "
            "AI-powered bundle recommendations. Showing rule-based results below."
        )
    for rec in recommendations:
        priority     = rec["priority"]
        css_class    = priority_css(priority)
        is_mandatory = rec.get("mandatory", False)
        mandatory_badge = (
            '<span style="background:#DCFCE7;color:#166534;font-size:0.65rem;'
            'font-weight:700;padding:2px 9px;border-radius:20px;letter-spacing:0.05em;'
            'text-transform:uppercase;margin-left:8px;">Baseline</span>'
        ) if is_mandatory else ""
        st.markdown(
            f"""
            <div class="product-card">
              <div style="display:flex;justify-content:space-between;align-items:center;
                          margin-bottom:0.4rem;">
                <h4>{rec['name']}{mandatory_badge}</h4>
                <span class="{css_class}">{priority}</span>
              </div>
              <div style="color:#94A3B8;font-size:0.8rem;margin-bottom:0.5rem;">
                <strong style="color:#475569;">ICICI Lombard:</strong> {rec['il_product']}
              </div>
              <div style="font-size:0.86rem;color:#0F172A;line-height:1.6;">
                <strong>What it covers:</strong> {rec['what_it_covers']}
              </div>
              <div class="nudge-box">
                <strong>Why you need this:</strong> {rec['nudge']}
              </div>
              <div style="margin-top:0.6rem;font-size:0.78rem;color:#94A3B8;">
                Best for: {rec['best_for']} &nbsp;&middot;&nbsp;
                Fit score: <strong style="color:#475569;">{rec['score']:.0f}/100</strong>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")

with st.expander("Founder's explainer — what each of these actually means", expanded=False):
    st.markdown("""
        **No jargon. Just what you need to know as a founder.**

        - **Cyber Liability** — if your systems are hacked, this pays legal bills, ransom response, customer notifications, and regulatory fines.
        - **D&O Liability** — if somebody sues *you personally* over a business decision, this protects your savings and home.
        - **Professional Indemnity** — if a client says your product caused them loss, this covers defence and damages.
        - **Group Health + GPA** — standard employee benefits. Retention tool first, compliance fallback second.
        - **Fire / Property / Marine Transit** — for anyone with physical things: offices, stock, equipment, shipments.
        - **Product Liability** — for anyone selling physical products. Handles the nightmare scenario: your product hurt a customer.
        - **Employment Practices Liability** — for HR complaints. Becomes essential past 25 employees.
        - **Crime / Fidelity** — covers internal fraud, UPI scams, vendor impersonation. Rising fast in India.
    """)

with st.expander("How we scored you — the logic behind the numbers"):
    st.markdown("""
        We combine **up to 25 inputs** into **13 risk dimensions** across four themes:

        **Digital & Data** — Cyber Technical, Data Privacy, IP Infringement
        **Legal & Governance** — Liability, Governance & Fraud, Regulatory Compliance
        **Operational** — Key Person, Property, Gig & Labour
        **Macro & Emerging** — ESG & Climate, Geopolitical, Policy Velocity, Reputation

        Key scoring inputs:
        1. **Sector baseline** — each sector has a characteristic risk profile calibrated to Indian regulatory filings.
        2. **Sub-sector overrides** — e.g. Fintech.NBFC_Digital_Lending forces compliance → 10 per RBI Digital Lending Directions 8-May-2025.
        3. **Funding stage** — later stages attract higher investor scrutiny, D&O exposure, and Competition Act DVT risk.
        4. **Team size** — larger teams raise key-person, gig labour, and compliance risk.
        5. **Operations type** — digital-only amplifies cyber risk; physical raises property and liability.
        6. **Data sensitivity** — High sensitivity pushes cyber and data privacy scores sharply (DPDPA ₹250cr penalty cap).
        7. **SDF probability** — DPDPA §10 Significant Data Fiduciary designation further elevates data privacy scores.
        8. **Gig headcount %** — Social Security Code §113-114 aggregator levy; state gig Acts (KA/RJ/BR/JH/TG).
        9. **China/HK investor BO %** — DPIIT Press Note 3 government-route FDI exposure.
        10. **EU revenue % (CBAM)** — Carbon Border Adjustment Mechanism from 1-Jan-2026 elevates ESG & climate scores.
        11. **AI in product** — MeitY AI Advisory (Mar-2024) and SGI Rules (Feb-2026) elevate policy velocity and compliance.
        12. **Climate risk zone** — IMD/NDMA hazard classification elevates property and ESG scores.

        Scores are normalised to 0–100. Products are matched from a pool of 28 insurance types using a weighted-risk mapping.
    """)

st.markdown("---")
st.caption(
    "Proof-of-concept built for ICICI Lombard. All product names are mapped to real ICICI Lombard offerings. "
    "Scores are indicative and meant to start a conversation with a licensed broker — they do not replace formal underwriting."
)
