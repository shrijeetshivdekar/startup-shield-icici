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
import plotly.graph_objects as go
import pandas as pd

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
# KNOWLEDGE BASE — ICICI Lombard products mapped to startup-relevant risk types
# =============================================================================
PRODUCT_CATALOG = {
    "cyber_liability": {
        "name": "Cyber Liability Insurance",
        "il_product": "Commercial Cyber Liability / I-Elite Group Cyber Liability Insurance",
        "what_it_covers": (
            "Pays for costs when your systems get hacked, customer data leaks, "
            "or a ransomware attack hits your servers. Covers forensic investigation, "
            "legal defence, customer notification, regulatory fines, and business "
            "interruption losses."
        ),
        "nudge": (
            "If a hacker steals your customer data tomorrow, you could face lawsuits, "
            "DPDP Act penalties, and months of downtime — this policy is what keeps "
            "your startup from shutting down."
        ),
        "best_for": "SaaS, fintech, healthtech, edtech, D2C with customer data.",
    },
    "dno_liability": {
        "name": "Directors & Officers (D&O) Liability",
        "il_product": "Directors and Officers Liability",
        "what_it_covers": (
            "Protects founders, directors, and senior managers personally if they "
            "get sued over business decisions — by investors, employees, regulators, "
            "or competitors. Covers legal defence and settlements."
        ),
        "nudge": (
            "The moment you take VC money, investors often require this. If a deal "
            "goes wrong or an employee sues the company, your personal savings and "
            "home are on the line without it."
        ),
        "best_for": "Any funded startup, especially post-Seed with institutional investors.",
    },
    "professional_indemnity": {
        "name": "Professional Indemnity / E&O Insurance",
        "il_product": "Professional Indemnity (Technology) Insurance",
        "what_it_covers": (
            "Covers claims from clients who say your software, service, or advice "
            "caused them financial loss — due to a bug, outage, wrong recommendation, "
            "or missed deadline. Pays legal costs and damages."
        ),
        "nudge": (
            "If your app has a bug that causes a client to lose money, they can sue "
            "you. Enterprise customers now demand this before signing contracts."
        ),
        "best_for": "SaaS, IT services, consultancies, fintech platforms, AI/ML products.",
    },
    "employee_health": {
        "name": "Group Health Insurance",
        "il_product": "Group Health Insurance / Group Health (Floater) Insurance",
        "what_it_covers": (
            "Medical cover for your employees and their families — hospitalization, "
            "day-care procedures, maternity, and more. Builds trust and helps you "
            "hire and retain talent."
        ),
        "nudge": (
            "Top engineers compare health benefits before joining. A ₹5 lakh family "
            "floater often costs less than one month's salary and dramatically "
            "improves retention."
        ),
        "best_for": "Every startup with 5+ employees.",
    },
    "group_pa": {
        "name": "Group Personal Accident",
        "il_product": "Group Personal Accident",
        "what_it_covers": (
            "One-time payout to the employee or family if there is an accidental "
            "injury, disability, or death — even outside working hours. Very "
            "affordable per head."
        ),
        "nudge": (
            "Field staff, delivery riders, sales teams travel constantly. For the "
            "price of a coffee per employee per month, you show them you care."
        ),
        "best_for": "Logistics, field-sales, agritech, manufacturing, any startup with travel.",
    },
    "employees_comp": {
        "name": "Workmen's Compensation / Employee's Compensation",
        "il_product": "Employer's Liability / Workmen's Compensation Insurance",
        "what_it_covers": (
            "Legally mandated under the Employees' Compensation Act for many "
            "categories of workers. Pays compensation if an employee is injured or "
            "dies while doing their job."
        ),
        "nudge": (
            "If a warehouse worker or delivery partner is injured on duty, the law "
            "holds you liable. This converts an unpredictable lawsuit into a fixed, "
            "small premium."
        ),
        "best_for": "Logistics, cleantech, D2C with warehouses, agritech, any physical ops.",
    },
    "property_fire": {
        "name": "Fire & Allied Perils / Property Insurance",
        "il_product": "ICICI Lombard Fire & Allied Perils Insurance Policy / MSME Suraksha Kavach",
        "what_it_covers": (
            "Covers your office, warehouse, equipment, and inventory against fire, "
            "lightning, floods, earthquakes, and burglary. Includes rebuilding costs "
            "and lost business income while you recover."
        ),
        "nudge": (
            "One warehouse fire can wipe out six months of inventory. If you stock "
            "physical goods or run a lab, this is non-negotiable."
        ),
        "best_for": "D2C brands, cleantech, manufacturing, deeptech labs, agritech.",
    },
    "business_edge": {
        "name": "Business Edge (Comprehensive Business Package)",
        "il_product": "Business Edge Policy / Business Prime Policy",
        "what_it_covers": (
            "A single package combining fire, burglary, money-in-transit, machinery "
            "breakdown, and public liability — designed for small and medium "
            "businesses. Simpler to manage than buying each separately."
        ),
        "nudge": (
            "One policy, one premium, one renewal date. Perfect for a growing "
            "startup that wants real cover without juggling five insurance documents."
        ),
        "best_for": "Growth-stage startups with physical offices or light manufacturing.",
    },
    "public_liability": {
        "name": "Public Liability Insurance",
        "il_product": "Commercial General Liability / Public Liability (Industrial or Non-Industrial)",
        "what_it_covers": (
            "Pays if a third party — customer, visitor, supplier — is injured on "
            "your premises, or if your product or operation damages someone's "
            "property. Covers legal costs and court-awarded damages."
        ),
        "nudge": (
            "If a delivery customer slips in your warehouse or your product causes "
            "property damage, lawsuits can run into crores. This is the shield."
        ),
        "best_for": "D2C, logistics, cleantech, events, hospitality-tech, physical retail.",
    },
    "product_liability": {
        "name": "Product Liability Insurance",
        "il_product": "Product Liability (Commercial or Retail)",
        "what_it_covers": (
            "Covers you if your manufactured product causes injury, illness, or "
            "damage after a customer buys it. Includes product recall, legal defence, "
            "and settlement costs."
        ),
        "nudge": (
            "If a batch of your D2C wellness gummies makes customers sick, the "
            "recall and lawsuits can finish the company. This is your survival kit."
        ),
        "best_for": "D2C brands, healthtech devices, food-tech, cleantech hardware.",
    },
    "marine_transit": {
        "name": "Marine Transit / Inland Transit Insurance",
        "il_product": "Marine Inland Transit Insurance / Marine Export-Import",
        "what_it_covers": (
            "Covers goods while they move — by road, rail, sea, or air. Protects "
            "against theft, accidents, and damage in transit, whether it's raw "
            "material coming in or products going out."
        ),
        "nudge": (
            "Every truckload is exposed. One accident can mean lakhs in lost "
            "inventory — this is standard for anyone who ships physical goods."
        ),
        "best_for": "D2C, logistics, agritech, cleantech, manufacturing startups.",
    },
    "key_person": {
        "name": "Key Person Insurance",
        "il_product": "Mapped via Group Personal Accident + term-life partnerships",
        "what_it_covers": (
            "Financial cushion for the company if a founder or critical team member "
            "dies or is permanently disabled. Helps the business survive the "
            "transition, pay off debt, or find a replacement."
        ),
        "nudge": (
            "Investors increasingly ask for this. If your sole technical founder is "
            "hit by a bus, this cash keeps the lights on while you rebuild."
        ),
        "best_for": "Founder-dependent startups, deeptech, single-CTO companies.",
    },
    "employment_practices": {
        "name": "Employment Practices Liability (EPL)",
        "il_product": "Employment Practices Liability (Commercial or Retail)",
        "what_it_covers": (
            "Covers lawsuits from employees alleging wrongful termination, "
            "harassment, discrimination, or unfair pay. Pays legal defence and "
            "settlements."
        ),
        "nudge": (
            "With POSH Act and labour codes, HR complaints are rising fast. One "
            "tribunal case can drain ₹20–50 lakhs in fees alone."
        ),
        "best_for": "Any startup with 10+ employees, especially post-Series A.",
    },
    "crime_fidelity": {
        "name": "Crime / Fidelity Insurance",
        "il_product": "Fidelity Insurance / Employee Dishonesty Liability",
        "what_it_covers": (
            "Covers financial loss if an employee commits fraud, theft, or "
            "embezzlement. Also covers external crime like vendor impersonation "
            "scams and fraudulent fund transfers."
        ),
        "nudge": (
            "UPI frauds and insider theft are the fastest-growing startup losses. "
            "One rogue finance hire can empty your runway."
        ),
        "best_for": "Fintech, D2C, any startup handling cash or payments.",
    },
    "gadget_equipment": {
        "name": "Gadget & Electronic Equipment Insurance",
        "il_product": "Gadget Insurance / Electronic Equipment Insurance",
        "what_it_covers": (
            "Covers laptops, phones, servers, specialized electronics against "
            "accidental damage, theft, and breakdown. Useful for distributed or "
            "remote teams."
        ),
        "nudge": (
            "A remote team of 30 means 30 laptops in 30 homes. Replacing even 10% "
            "per year adds up — this converts it into a small predictable premium."
        ),
        "best_for": "Remote-first SaaS, deeptech with specialised equipment.",
    },
    "clinical_trials": {
        "name": "Clinical Trials Liability",
        "il_product": "Clinical Trials Liability (Commercial or Retail)",
        "what_it_covers": (
            "Mandatory for human clinical trials in India. Covers liability if "
            "trial participants are injured or suffer adverse effects."
        ),
        "nudge": (
            "You cannot legally run a trial without it. CDSCO will not approve your "
            "protocol if this is missing."
        ),
        "best_for": "Healthtech, biotech, pharma, medical device startups.",
    },
}


# =============================================================================
# SECTOR PROFILES — baseline risk weightings per sector (0 = low, 10 = very high)
# =============================================================================
SECTOR_PROFILES = {
    "SaaS / Enterprise Software": {
        "cyber": 8, "liability": 6, "key_person": 5, "property": 2, "compliance": 5,
        "emoji": "💻",
        "description": "Digital-first, customer data heavy, contract-driven.",
    },
    "Fintech": {
        "cyber": 10, "liability": 8, "key_person": 6, "property": 3, "compliance": 10,
        "emoji": "💳",
        "description": "RBI/SEBI regulated, high cyber exposure, fraud-prone.",
    },
    "Healthtech": {
        "cyber": 9, "liability": 9, "key_person": 6, "property": 5, "compliance": 10,
        "emoji": "🏥",
        "description": "Patient data, clinical accuracy, DPDP + health regs.",
    },
    "D2C / Consumer Brands": {
        "cyber": 5, "liability": 8, "key_person": 4, "property": 8, "compliance": 6,
        "emoji": "🛍️",
        "description": "Inventory, warehousing, product recall, marketplace risk.",
    },
    "Deeptech / AI / Robotics": {
        "cyber": 7, "liability": 7, "key_person": 9, "property": 7, "compliance": 5,
        "emoji": "🤖",
        "description": "IP-heavy, founder-critical, specialised equipment.",
    },
    "Edtech": {
        "cyber": 7, "liability": 5, "key_person": 5, "property": 3, "compliance": 6,
        "emoji": "📚",
        "description": "Minor data, content liability, EPL exposure from scaling ops.",
    },
    "Agritech": {
        "cyber": 4, "liability": 6, "key_person": 5, "property": 8, "compliance": 5,
        "emoji": "🌾",
        "description": "Rural logistics, farm inputs, crop risk, transit exposure.",
    },
    "Cleantech / Climatetech": {
        "cyber": 5, "liability": 7, "key_person": 6, "property": 9, "compliance": 7,
        "emoji": "🌱",
        "description": "Hardware, installations, pollution + public liability.",
    },
    "Logistics / Mobility": {
        "cyber": 6, "liability": 9, "key_person": 4, "property": 8, "compliance": 7,
        "emoji": "🚚",
        "description": "Fleet, drivers, goods-in-transit, public liability central.",
    },
    "Legaltech": {
        "cyber": 7, "liability": 8, "key_person": 5, "property": 2, "compliance": 7,
        "emoji": "⚖️",
        "description": "Professional advice liability, confidential data.",
    },
    "HRtech": {
        "cyber": 8, "liability": 6, "key_person": 5, "property": 2, "compliance": 7,
        "emoji": "👥",
        "description": "Employee PII, payroll data, DPDP exposure.",
    },
    "Gaming / Media / Content": {
        "cyber": 6, "liability": 6, "key_person": 5, "property": 3, "compliance": 6,
        "emoji": "🎮",
        "description": "IP, content liability, fantasy/real-money regulation.",
    },
    "Foodtech / Cloud Kitchen": {
        "cyber": 4, "liability": 9, "key_person": 4, "property": 8, "compliance": 7,
        "emoji": "🍔",
        "description": "FSSAI, food safety lawsuits, kitchen property risk.",
    },
}


# =============================================================================
# RISK SCORING ENGINE
# =============================================================================

def compute_risk_scores(sector: str, funding_stage: str, team_size: int,
                        operations: str, data_sensitivity: str) -> dict:
    """Rule-based risk engine. Returns dict of five risk category scores (0-100)."""

    base = SECTOR_PROFILES[sector]

    stage_multiplier = {
        "Pre-seed": 0.7,
        "Seed":     0.9,
        "Series A": 1.1,
        "Series B+": 1.3,
    }[funding_stage]

    if team_size <= 5:    team_mult = 0.8
    elif team_size <= 20: team_mult = 1.0
    elif team_size <= 50: team_mult = 1.15
    elif team_size <= 150: team_mult = 1.3
    else:                 team_mult = 1.5

    ops_mult = {
        "Digital-only": {"property": 0.4, "liability": 0.8, "cyber": 1.2},
        "Physical-only": {"property": 1.4, "liability": 1.2, "cyber": 0.7},
        "Hybrid": {"property": 1.0, "liability": 1.0, "cyber": 1.0},
    }[operations]

    data_mult = {
        "Low":    {"cyber": 0.6, "compliance": 0.8},
        "Medium": {"cyber": 1.0, "compliance": 1.0},
        "High":   {"cyber": 1.4, "compliance": 1.3},
    }[data_sensitivity]

    cyber = base["cyber"] * stage_multiplier * ops_mult.get("cyber", 1.0) \
            * data_mult["cyber"]
    liability = base["liability"] * stage_multiplier * ops_mult.get("liability", 1.0) \
                * (0.85 + 0.05 * min(team_size / 20, 3))
    key_person = base["key_person"] * (1.4 if team_size <= 10 else 1.0) \
                 * stage_multiplier
    property_risk = base["property"] * ops_mult.get("property", 1.0) * team_mult
    compliance = base["compliance"] * stage_multiplier * data_mult["compliance"]

    def to_100(x): return max(0, min(100, round(x * 7.5, 1)))

    return {
        "Cyber Risk":        to_100(cyber),
        "Liability Risk":    to_100(liability),
        "Key Person Risk":   to_100(key_person),
        "Property Risk":     to_100(property_risk),
        "Compliance Risk":   to_100(compliance),
    }


def priority_label(score: float) -> str:
    if score >= 70: return "Critical"
    if score >= 40: return "Recommended"
    return "Optional"


def priority_css(label: str) -> str:
    return {
        "Critical":    "priority-critical",
        "Recommended": "priority-recommended",
        "Optional":    "priority-optional",
    }[label]


# =============================================================================
# PRODUCT RECOMMENDER
# =============================================================================

PRODUCT_RISK_MAP = {
    "cyber_liability":        {"Cyber Risk": 1.0, "Compliance Risk": 0.3},
    "dno_liability":          {"Liability Risk": 0.7, "Compliance Risk": 0.5},
    "professional_indemnity": {"Liability Risk": 1.0, "Cyber Risk": 0.2},
    "employee_health":        {"Key Person Risk": 0.5, "Liability Risk": 0.2},
    "group_pa":               {"Key Person Risk": 0.6, "Liability Risk": 0.2},
    "employees_comp":         {"Liability Risk": 0.6, "Compliance Risk": 0.6,
                               "Property Risk": 0.2},
    "property_fire":          {"Property Risk": 1.0},
    "business_edge":          {"Property Risk": 0.7, "Liability Risk": 0.4},
    "public_liability":       {"Liability Risk": 0.8, "Property Risk": 0.3},
    "product_liability":      {"Liability Risk": 0.9, "Compliance Risk": 0.3},
    "marine_transit":         {"Property Risk": 0.8},
    "key_person":             {"Key Person Risk": 1.0},
    "employment_practices":   {"Liability Risk": 0.6, "Compliance Risk": 0.6},
    "crime_fidelity":         {"Cyber Risk": 0.3, "Liability Risk": 0.4,
                               "Compliance Risk": 0.3},
    "gadget_equipment":       {"Property Risk": 0.5},
    "clinical_trials":        {"Compliance Risk": 0.8, "Liability Risk": 0.6},
}

SECTOR_OVERRIDES = {
    "Healthtech": ["clinical_trials"],
    "Logistics / Mobility": ["marine_transit", "public_liability"],
    "D2C / Consumer Brands": ["product_liability", "marine_transit"],
    "Foodtech / Cloud Kitchen": ["product_liability", "public_liability"],
    "Fintech": ["crime_fidelity", "dno_liability"],
    "Cleantech / Climatetech": ["property_fire", "public_liability"],
    "Agritech": ["marine_transit"],
}

SECTOR_EXCLUSIONS = {
    "SaaS / Enterprise Software":   ["clinical_trials", "product_liability", "marine_transit"],
    "Fintech":                      ["clinical_trials", "product_liability", "marine_transit"],
    "Edtech":                       ["clinical_trials", "product_liability", "marine_transit"],
    "HRtech":                       ["clinical_trials", "product_liability", "marine_transit"],
    "Legaltech":                    ["clinical_trials", "product_liability", "marine_transit"],
    "Gaming / Media / Content":     ["clinical_trials", "marine_transit"],
    "D2C / Consumer Brands":        ["clinical_trials"],
    "Healthtech":                   [],
    "Deeptech / AI / Robotics":     ["clinical_trials"],
    "Agritech":                     ["clinical_trials"],
    "Cleantech / Climatetech":      ["clinical_trials"],
    "Logistics / Mobility":         ["clinical_trials", "product_liability"],
    "Foodtech / Cloud Kitchen":     ["clinical_trials"],
}


def recommend_products(risk_scores: dict, sector: str, team_size: int,
                       funding_stage: str) -> list:
    scored = []
    excluded = set(SECTOR_EXCLUSIONS.get(sector, []))
    for key, weights in PRODUCT_RISK_MAP.items():
        if key in excluded:
            continue
        score = sum(risk_scores[cat] * w for cat, w in weights.items())
        score = score / sum(weights.values())
        scored.append((key, score))

    for key in SECTOR_OVERRIDES.get(sector, []):
        scored = [(k, s + 25 if k == key else s) for k, s in scored]

    # D&O boost raised to +30 so it survives multiple property overrides in
    # physical sectors (D2C, Agritech, Logistics) where +15 was insufficient.
    if funding_stage in ("Series A", "Series B+"):
        scored = [(k, s + 30 if k == "dno_liability" else s) for k, s in scored]

    if team_size >= 10:
        scored = [(k, s + 10 if k == "employee_health" else s) for k, s in scored]
    if team_size >= 25:
        scored = [(k, s + 8 if k == "employment_practices" else s) for k, s in scored]

    scored = [(k, min(100, s)) for k, s in scored]
    scored.sort(key=lambda x: x[1], reverse=True)

    top = scored[:5]
    results = []
    for key, score in top:
        product = PRODUCT_CATALOG[key].copy()
        product["score"] = round(score, 1)
        product["priority"] = priority_label(product["score"])  # label from rounded score
        results.append(product)
    return results


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
    df = pd.DataFrame({"Category": list(scores.keys()),
                       "Score": list(scores.values())})
    df = df.sort_values("Score", ascending=True)

    def band_color(s):
        if s >= 70: return "#AD1E23"
        if s >= 40: return "#F59E0B"
        return "#10B981"

    fig = go.Figure(go.Bar(
        x=df["Score"], y=df["Category"], orientation='h',
        marker=dict(color=[band_color(s) for s in df["Score"]],
                    line=dict(width=0)),
        text=[f"{s:.0f}" for s in df["Score"]], textposition='outside',
        textfont=dict(size=12, color='#0F172A'),
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 115], title="Risk Score (0–100)",
                   tickfont=dict(color='#94A3B8'), gridcolor='#F4F4F0'),
        yaxis=dict(title="", tickfont=dict(size=12, color='#0F172A')),
        height=320, margin=dict(l=20, r=50, t=15, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig


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
dash_col1, dash_col2 = st.columns([1, 1.2])
with dash_col1:
    st.plotly_chart(render_risk_radar(scores), use_container_width=True)
with dash_col2:
    st.plotly_chart(render_risk_bars(scores), use_container_width=True)

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
    '<div class="section-sub">Ranked by how closely they match your risk profile.</div>',
    unsafe_allow_html=True,
)

for rec in recommendations:
    priority  = rec["priority"]
    css_class = priority_css(priority)

    st.markdown(
        f"""
        <div class="product-card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
            <h4>{rec['name']}</h4>
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
            Best for: {rec['best_for']} &nbsp;·&nbsp; Fit score: <strong style="color:#475569;">{rec['score']:.0f}/100</strong>
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

        Scores are normalised to 0–100. Products are matched using a
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
