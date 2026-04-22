"""
Startup Profiling and Risk Assessment using GenAI-style Rule Logic
===================================================================
Recommends tailor-made ICICI Lombard insurance products for Indian startups.

Run locally:
    pip install streamlit plotly pandas
    streamlit run startup_risk_app.py

No API keys required. All logic is rule-based and runs fully offline.

Author: ICICI Lombard Intern Project (Proof of Concept)
"""

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import pandas as pd
from risk_engine import (
    SECTOR_PROFILES,
    compute_risk_scores,
    recommend_products,
)

# =============================================================================
# PAGE CONFIGURATION — first Streamlit call, controls tab title and layout
# =============================================================================
st.set_page_config(
    page_title="Startup Shield · ICICI Lombard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
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
        yaxis=dict(title="", tickfont=dict(size=12, color="#0F172A")),
        height=320,
        margin=dict(l=20, r=60, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        bargap=0.35,
    )
    return fig


def render_risk_scorecards(scores: dict) -> str:
    """Returns HTML for 5 mini scorecard tiles — one per risk dimension."""

    def band(s):
        if s >= 70: return "#AD1E23", "#FEF2F2", "Critical"
        if s >= 40: return "#D97706", "#FFFBEB", "Watch"
        return "#059669", "#ECFDF5", "Low"

    # Inline SVG icon paths (viewBox 0 0 24 24, stroke-based)
    icons = {
        "Cyber Risk": (
            '<path d="M12 2L4 6v5c0 5.25 3.4 10.15 8 11.35C16.6 21.15 20 16.25 '
            '20 11V6L12 2z" stroke="currentColor" stroke-width="1.5" fill="none"/>'
        ),
        "Liability Risk": (
            '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" '
            'stroke="currentColor" stroke-width="1.5" fill="none"/>'
            '<path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="1.5" '
            'stroke-linecap="round" fill="none"/>'
        ),
        "Key Person Risk": (
            '<circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.5" fill="none"/>'
            '<path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="currentColor" '
            'stroke-width="1.5" stroke-linecap="round" fill="none"/>'
        ),
        "Property Risk": (
            '<path d="M3 12l9-9 9 9M5 10v9a1 1 0 001 1h4v-5h4v5h4a1 1 0 001-1v-9" '
            'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
            'stroke-linejoin="round" fill="none"/>'
        ),
        "Compliance Risk": (
            '<path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="1.5" '
            'stroke-linecap="round" fill="none"/>'
            '<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5" fill="none"/>'
        ),
    }

    cards_html = (
        '<style>body{margin:0;background:transparent;'
        "font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;}</style>"
        '<div style="display:flex;flex-direction:column;gap:10px;">'
    )
    for dim, score in scores.items():
        color, bg, label = band(score)
        icon_path = icons.get(dim, "")
        bar_pct = int(min(score, 100))
        cards_html += (
            f'<div style="background:{bg};border:1px solid {color}22;border-radius:10px;'
            f'padding:10px 14px;display:flex;align-items:center;gap:12px;">'
            f'<div style="flex-shrink:0;width:32px;height:32px;border-radius:8px;'
            f'background:{color}15;display:flex;align-items:center;'
            f'justify-content:center;color:{color};">'
            f'<svg width="16" height="16" viewBox="0 0 24 24">{icon_path}</svg>'
            f'</div>'
            f'<div style="flex:1;min-width:0;">'
            f'<div style="font-size:0.7rem;font-weight:600;color:#475569;'
            f'letter-spacing:0.03em;margin-bottom:4px;white-space:nowrap;'
            f'overflow:hidden;text-overflow:ellipsis;">{dim}</div>'
            f'<div style="background:#E5E5E0;border-radius:4px;height:5px;width:100%;">'
            f'<div style="background:{color};height:5px;border-radius:4px;'
            f'width:{bar_pct}%;"></div>'
            f'</div>'
            f'</div>'
            f'<div style="flex-shrink:0;text-align:right;min-width:42px;">'
            f'<div style="font-size:1.1rem;font-weight:800;color:{color};'
            f'line-height:1;">{score:.0f}</div>'
            f'<div style="font-size:0.6rem;font-weight:600;color:{color};'
            f'opacity:0.75;letter-spacing:0.05em;'
            f'text-transform:uppercase;">{label}</div>'
            f'</div>'
            f'</div>'
        )
    cards_html += "</div>"
    return cards_html


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
        Startup Shield &nbsp;·&nbsp; ICICI Lombard
      </div>
      <p class="hero-tagline">Tailored insurance recommendations for Indian startups —
        powered by sector-aware GenAI risk logic.</p>
      <hr class="hero-rule"/>
      <p class="hero-micro">Powered by GenAI &nbsp;·&nbsp; Built for Indian startups &nbsp;·&nbsp; No data leaves your browser</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# UI — Sidebar
# =============================================================================
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:0.55rem;margin-bottom:1rem;">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <rect x="3" y="2" width="12" height="14" rx="2" stroke="#AD1E23" stroke-width="1.5" fill="none"/>
            <path d="M6 6h6M6 9h6M6 12h4" stroke="#AD1E23" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <span style="font-size:0.95rem;font-weight:700;color:#0F172A;letter-spacing:-0.01em;">
            Your startup profile
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Company ──────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section first">Company</div>', unsafe_allow_html=True)

    startup_name = st.text_input("Startup name", value="Acme Labs",
                                 help="Just a label, used in the report.")

    sector = st.selectbox(
        "Sector",
        list(SECTOR_PROFILES.keys()),
        help="Pick the sector that describes most of your revenue.",
    )
    st.caption(f"{SECTOR_PROFILES[sector]['emoji']}  {SECTOR_PROFILES[sector]['description']}")

    # ── Team & Stage ─────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">Team &amp; Stage</div>', unsafe_allow_html=True)

    funding_stage = st.selectbox(
        "Funding stage",
        ["Pre-seed", "Seed", "Series A", "Series B+"],
    )

    _team_val = st.session_state.get("team_size_slider", 15)
    st.markdown(
        f'<div class="slider-label-row">'
        f'<span>Team size (FTEs)</span>'
        f'<span class="value-pill">{_team_val}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    team_size = st.slider(
        "", min_value=1, max_value=500, value=15, step=1,
        key="team_size_slider", label_visibility="collapsed",
    )

    # ── Risk Profile ─────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">Risk Profile</div>', unsafe_allow_html=True)

    operations = st.radio(
        "Primary operations",
        ["Digital-only", "Physical-only", "Hybrid"],
        horizontal=True,
        help="Digital-only = cloud/SaaS. Physical-only = warehouse/factory. Hybrid = both.",
    )

    data_sensitivity = st.select_slider(
        "Customer data sensitivity",
        options=["Low", "Medium", "High"],
        value="Medium",
        help="High = financial, health, or identity data. Low = basic user accounts only.",
    )

    st.markdown("---")
    analyse = st.button("Analyse my startup", type="primary", use_container_width=True)

    st.markdown(
        """
        <div class="privacy-badge">
          <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
            <rect x="2" y="5.5" width="9" height="6" rx="1.5" stroke="#94A3B8" stroke-width="1.2" fill="none"/>
            <path d="M4.5 5.5V4a2 2 0 014 0v1.5" stroke="#94A3B8" stroke-width="1.2" stroke-linecap="round" fill="none"/>
          </svg>
          All inputs stay on your machine. No data is sent anywhere.
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# UI — Main panel (empty state)
# =============================================================================
if not analyse:
    st.markdown(
        """
        <div class="info-card">
          <div class="info-card-icon">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 2C5.58 2 2 5.58 2 10s3.58 8 8 8 8-3.58 8-8-3.58-8-8-8zm1 12H9v-2h2v2zm0-4H9V6h2v4z" fill="#AD1E23"/>
            </svg>
          </div>
          <div class="info-card-body">
            Fill in your startup details on the left and click
            <strong>Analyse my startup</strong> to see your customised risk
            profile and recommended ICICI Lombard policies.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-heading">What this tool does</div>'
        '<div class="section-sub">Three steps from profile to policy — all offline, no API keys.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="feature-grid">

          <div class="feature-card">
            <div class="feature-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <circle cx="10" cy="10" r="7" stroke="#AD1E23" stroke-width="1.6" fill="none"/>
                <circle cx="10" cy="10" r="3.5" stroke="#AD1E23" stroke-width="1.4" fill="none"/>
                <circle cx="10" cy="10" r="1" fill="#AD1E23"/>
              </svg>
            </div>
            <div class="feature-title">Sector-aware profiling</div>
            <div class="feature-desc">We match your sector against known risk patterns from 13+ Indian startup categories — from fintech to agritech.</div>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <rect x="3" y="11" width="3" height="6" rx="1" fill="#AD1E23"/>
                <rect x="8.5" y="7" width="3" height="10" rx="1" fill="#AD1E23" opacity=".7"/>
                <rect x="14" y="3" width="3" height="14" rx="1" fill="#AD1E23" opacity=".4"/>
              </svg>
            </div>
            <div class="feature-title">5-dimension risk score</div>
            <div class="feature-desc">Cyber, Liability, Key Person, Property, and Compliance — each scored 0–100 using a transparent rule engine.</div>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10 2L3 5.5v4.75C3 14.1 6.07 17.8 10 19c3.93-1.2 7-4.9 7-8.75V5.5L10 2z"
                      stroke="#AD1E23" stroke-width="1.5" fill="none" stroke-linejoin="round"/>
                <path d="M7 10l2 2 4-4" stroke="#AD1E23" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="feature-title">Plain-language policy plan</div>
            <div class="feature-desc">Top 5 ICICI Lombard policies explained as if talking to a first-time founder — no jargon, no upsell.</div>
          </div>

        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# =============================================================================
# UI — Results
# =============================================================================
scores = compute_risk_scores(sector, funding_stage, team_size,
                             operations, data_sensitivity)
recommendations = recommend_products(scores, sector, team_size, funding_stage)

# Profile strip
st.markdown(
    f"## {SECTOR_PROFILES[sector]['emoji']} Profile: **{startup_name}**"
)
meta_col1, meta_col2, meta_col3, meta_col4 = st.columns(4)
meta_col1.metric("Sector", sector.split(" /")[0])
meta_col2.metric("Stage", funding_stage)
meta_col3.metric("Team", f"{team_size} people")
meta_col4.metric("Ops", operations)

st.markdown("---")

# Risk dashboard
st.markdown(
    '<div class="section-heading">Your Risk Dashboard</div>'
    '<div class="section-sub">Five-dimension exposure profile based on your inputs.</div>',
    unsafe_allow_html=True,
)
dash_col1, dash_col2, dash_col3 = st.columns([1.1, 1.2, 0.9])
with dash_col1:
    st.plotly_chart(render_risk_radar(scores), use_container_width=True)
with dash_col2:
    st.plotly_chart(render_risk_bars(scores), use_container_width=True)
with dash_col3:
    components.html(render_risk_scorecards(scores), height=340, scrolling=False)

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

# Product recommendations
st.markdown(
    '<div class="section-heading">Recommended ICICI Lombard Products</div>'
    '<div class="section-sub">Top recommendations ranked by fit score. Group Health Insurance is always included as a baseline.</div>',
    unsafe_allow_html=True,
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

# Explainers
with st.expander("Founder's explainer — what each of these actually means", expanded=False):
    st.markdown("""
        **No jargon. Just what you need to know as a founder.**

        - **Cyber Liability** — if your systems are hacked, this pays legal
          bills, ransom response, customer notifications, and regulatory fines.
        - **D&O Liability** — if somebody sues *you personally* (investor,
          employee, regulator) over a business decision, this protects your
          savings and home.
        - **Professional Indemnity** — if a paying customer says your product
          caused them loss (a bug, wrong advice, missed SLA), this covers
          defence and damages.
        - **Group Health + GPA** — standard employee benefits. Retention tool
          first, compliance fallback second.
        - **Fire / Property / Marine Transit** — for anyone with physical
          things: offices, stock, equipment, shipments.
        - **Product Liability** — for anyone selling physical products. Handles
          the nightmare scenario: your product hurt a customer.
        - **Employment Practices Liability** — for HR complaints (wrongful
          termination, harassment, discrimination). Becomes essential past 25
          employees.
        - **Crime / Fidelity** — covers internal fraud, UPI scams, vendor
          impersonation. Rising fast in India.
    """)

with st.expander("How we scored you — the logic behind the numbers"):
    st.markdown("""
        We combine **six inputs** into **five risk dimensions**:

        1. **Sector baseline** — each sector has a characteristic risk shape
           drawn from CB Insights failure analysis and Stanford's Startup
           Genome work.
        2. **Funding stage** — later stages attract higher investor scrutiny,
           regulatory attention, and litigation exposure.
        3. **Team size** — larger teams raise HR, key-person, and compliance risk.
        4. **Operations type** — digital-only amplifies cyber risk; physical
           raises property/liability.
        5. **Data sensitivity** — handling PII, health, or financial data pushes
           cyber and compliance scores up sharply under DPDP Act 2023.

        Scores are normalised to 0–100. Products are matched from a pool of 28 insurance types using a
        weighted-risk mapping, plus sector-specific legal requirements (e.g.
        clinical trials liability is near-mandatory for healthtech running
        human studies).
    """)

st.markdown("---")
st.caption(
    "This prototype is a proof-of-concept built for ICICI Lombard. "
    "All product names are mapped to real ICICI Lombard offerings. "
    "Scores are indicative and meant to start a conversation with a "
    "licensed broker or relationship manager — they do not replace "
    "formal underwriting."
)
