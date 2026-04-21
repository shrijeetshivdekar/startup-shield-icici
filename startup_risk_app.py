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
# CUSTOM CSS — light theming to give the prototype a polished, distinct look
# =============================================================================
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(90deg, #8B1A1A 0%, #C8102E 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(139,26,26,0.2);
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p  { margin: 0.3rem 0 0 0; opacity: 0.95; font-size: 1rem; }

    .product-card {
        background: #ffffff;
        border: 1px solid #e6e6e6;
        border-left: 6px solid #C8102E;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        margin: 0.7rem 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .product-card h4 { margin: 0 0 0.4rem 0; color: #1a1a1a; }

    .priority-critical    { background:#C8102E; color:white;  padding:3px 10px;
                            border-radius:12px; font-size:0.78rem; font-weight:600; }
    .priority-recommended { background:#F59E0B; color:white;  padding:3px 10px;
                            border-radius:12px; font-size:0.78rem; font-weight:600; }
    .priority-optional    { background:#059669; color:white;  padding:3px 10px;
                            border-radius:12px; font-size:0.78rem; font-weight:600; }

    .nudge-box {
        background: #FFF7E6;
        border-left: 4px solid #F59E0B;
        padding: 0.7rem 1rem;
        margin-top: 0.6rem;
        border-radius: 6px;
        font-style: italic;
        color: #5c4a00;
    }

    .score-label { font-size: 0.85rem; color: #555; margin-top: 0.3rem; }
    .stMetric { background:#F8F9FB; padding:0.6rem; border-radius:8px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# KNOWLEDGE BASE — ICICI Lombard products mapped to startup-relevant risk types
# Each product has plain-language copy written for a first-time founder.
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
# Derived from academic research on startup failure modes, CB Insights post-mortems,
# and the ICICI Lombard product taxonomy. Each sector has a different risk shape.
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
# ---------------------------------------------------------------------------
# The engine combines six inputs into risk scores across five categories.
# Logic inspired by:
#   - CB Insights "Top Reasons Startups Fail" (2019, 2021)
#   - Marmer et al. Startup Genome Report (Stanford, 2012)
#   - Shepherd & Wiklund venture risk framework (Journal of Business Venturing)
#   - Insurance underwriting severity × frequency model (standard actuarial)
#
# Each category output is in 0–100 scale. Thresholds:
#   >= 70  → Critical
#   40–69  → Recommended
#   < 40   → Optional
# =============================================================================

def compute_risk_scores(sector: str, funding_stage: str, team_size: int,
                        operations: str, data_sensitivity: str) -> dict:
    """Rule-based risk engine. Returns dict of five risk category scores (0-100)."""

    base = SECTOR_PROFILES[sector]

    # --- modifiers: multiply sector baseline based on inputs ---
    stage_multiplier = {
        "Pre-seed": 0.7,     # less to lose, fewer regulators watching
        "Seed":     0.9,
        "Series A": 1.1,     # investors now demand cover
        "Series B+": 1.3,    # board governance, scale exposure
    }[funding_stage]

    # team size amplifies people-risk (EPL, group health, key person)
    if team_size <= 5:    team_mult = 0.8
    elif team_size <= 20: team_mult = 1.0
    elif team_size <= 50: team_mult = 1.15
    elif team_size <= 150: team_mult = 1.3
    else:                 team_mult = 1.5

    # operations affects property/liability heavily
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

    # --- compute each category (0-100) ---
    cyber = base["cyber"] * stage_multiplier * ops_mult.get("cyber", 1.0) \
            * data_mult["cyber"]
    liability = base["liability"] * stage_multiplier * ops_mult.get("liability", 1.0) \
                * (0.85 + 0.05 * min(team_size / 20, 3))
    key_person = base["key_person"] * (1.4 if team_size <= 10 else 1.0) \
                 * stage_multiplier
    property_risk = base["property"] * ops_mult.get("property", 1.0) * team_mult
    compliance = base["compliance"] * stage_multiplier * data_mult["compliance"]

    # scale base (0-10) to 0-100 and clamp
    def to_100(x): return max(0, min(100, round(x * 7.5, 1)))

    return {
        "Cyber Risk":        to_100(cyber),
        "Liability Risk":    to_100(liability),
        "Key Person Risk":   to_100(key_person),
        "Property Risk":     to_100(property_risk),
        "Compliance Risk":   to_100(compliance),
    }


def priority_label(score: float) -> str:
    """Convert numeric score to a priority tag used on product cards."""
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
# ---------------------------------------------------------------------------
# For each product, we define which risk buckets it addresses and with what
# weight. We then score each product by summing (risk_score * weight), pick
# the top 5, and label each by priority.
# =============================================================================

PRODUCT_RISK_MAP = {
    # product_key: {risk_category: weight}
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


# Sector-specific hard requirements — certain products are mandatory/near-mandatory
SECTOR_OVERRIDES = {
    "Healthtech": ["clinical_trials"],
    "Logistics / Mobility": ["marine_transit", "public_liability"],
    "D2C / Consumer Brands": ["product_liability", "marine_transit"],
    "Foodtech / Cloud Kitchen": ["product_liability", "public_liability"],
    "Fintech": ["crime_fidelity", "dno_liability"],
    "Cleantech / Climatetech": ["property_fire", "public_liability"],
    "Agritech": ["marine_transit"],
}

# Sector-irrelevant products — hide products that make no operational sense
# for a given sector, even if the abstract risk score pulls them in.
SECTOR_EXCLUSIONS = {
    "SaaS / Enterprise Software":   ["clinical_trials", "product_liability", "marine_transit"],
    "Fintech":                      ["clinical_trials", "product_liability", "marine_transit"],
    "Edtech":                       ["clinical_trials", "product_liability", "marine_transit"],
    "HRtech":                       ["clinical_trials", "product_liability", "marine_transit"],
    "Legaltech":                    ["clinical_trials", "product_liability", "marine_transit"],
    "Gaming / Media / Content":     ["clinical_trials", "marine_transit"],
    "D2C / Consumer Brands":        ["clinical_trials"],
    "Healthtech":                   [],  # healthtech can need all of them
    "Deeptech / AI / Robotics":     ["clinical_trials"],
    "Agritech":                     ["clinical_trials"],
    "Cleantech / Climatetech":      ["clinical_trials"],
    "Logistics / Mobility":         ["clinical_trials", "product_liability"],
    "Foodtech / Cloud Kitchen":     ["clinical_trials"],
}


def recommend_products(risk_scores: dict, sector: str, team_size: int,
                       funding_stage: str) -> list:
    """Score each product, return top 5 with priority label and rationale."""

    scored = []
    excluded = set(SECTOR_EXCLUSIONS.get(sector, []))
    for key, weights in PRODUCT_RISK_MAP.items():
        if key in excluded:
            continue
        score = sum(risk_scores[cat] * w for cat, w in weights.items())
        # normalise by sum of weights so products with fewer links aren't penalised
        score = score / sum(weights.values())
        scored.append((key, score))

    # Apply sector overrides — boost mandatory products
    for key in SECTOR_OVERRIDES.get(sector, []):
        scored = [(k, s + 25 if k == key else s) for k, s in scored]

    # Funding-stage overrides
    if funding_stage in ("Series A", "Series B+"):
        scored = [(k, s + 15 if k == "dno_liability" else s) for k, s in scored]

    # Team-size overrides
    if team_size >= 10:
        scored = [(k, s + 10 if k == "employee_health" else s) for k, s in scored]
    if team_size >= 25:
        scored = [(k, s + 8 if k == "employment_practices" else s) for k, s in scored]

    # Cap at 100 after overrides so priority labels stay meaningful
    scored = [(k, min(100, s)) for k, s in scored]
    scored.sort(key=lambda x: x[1], reverse=True)

    top = scored[:5]
    results = []
    for key, score in top:
        product = PRODUCT_CATALOG[key].copy()
        product["score"] = round(score, 1)
        product["priority"] = priority_label(score)
        results.append(product)
    return results


# =============================================================================
# VISUALIZATION — plotly radar + horizontal bar dashboard
# =============================================================================

def render_risk_radar(scores: dict):
    """Radar chart giving an at-a-glance risk shape of the startup."""
    categories = list(scores.keys()) + [list(scores.keys())[0]]
    values = list(scores.values()) + [list(scores.values())[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=categories, fill='toself',
        line=dict(color='#C8102E', width=2),
        fillcolor='rgba(200,16,46,0.25)', name='Risk profile'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100],
                                   tickfont=dict(size=10))),
        showlegend=False, height=420,
        margin=dict(l=60, r=60, t=30, b=30),
    )
    return fig


def render_risk_bars(scores: dict):
    """Horizontal bar chart, color-coded by priority band."""
    df = pd.DataFrame({"Category": list(scores.keys()),
                       "Score": list(scores.values())})
    df = df.sort_values("Score", ascending=True)

    def band_color(s):
        if s >= 70: return "#C8102E"
        if s >= 40: return "#F59E0B"
        return "#059669"

    fig = go.Figure(go.Bar(
        x=df["Score"], y=df["Category"], orientation='h',
        marker=dict(color=[band_color(s) for s in df["Score"]]),
        text=[f"{s:.0f}" for s in df["Score"]], textposition='outside',
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 110], title="Risk Score (0–100)"),
        yaxis=dict(title=""),
        height=340, margin=dict(l=20, r=40, t=20, b=40),
        plot_bgcolor='white',
    )
    return fig


# =============================================================================
# UI — sidebar inputs, main panel outputs
# =============================================================================

# --- Header ---
st.markdown(
    """
    <div class="main-header">
      <h1>🛡️ Startup Shield · ICICI Lombard</h1>
      <p>Tailored insurance recommendations for Indian startups — powered by
      sector-aware GenAI risk logic.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar: inputs ---
with st.sidebar:
    st.markdown("### 📋 Tell us about your startup")
    st.caption("All inputs stay on your machine. No data is sent anywhere.")

    startup_name = st.text_input("Startup name", value="Acme Labs",
                                 help="Just a label, used in the report.")

    sector = st.selectbox(
        "Sector",
        list(SECTOR_PROFILES.keys()),
        help="Pick the sector that describes most of your revenue.",
    )
    st.caption(f"{SECTOR_PROFILES[sector]['emoji']} "
               f"{SECTOR_PROFILES[sector]['description']}")

    funding_stage = st.selectbox(
        "Funding stage",
        ["Pre-seed", "Seed", "Series A", "Series B+"],
    )

    team_size = st.slider(
        "Team size (full-time equivalents)",
        min_value=1, max_value=500, value=15, step=1,
    )

    operations = st.radio(
        "Primary operations",
        ["Digital-only", "Physical-only", "Hybrid"],
        horizontal=True,
        help="Digital-only = cloud/SaaS. Physical-only = warehouse/factory. "
             "Hybrid = both.",
    )

    data_sensitivity = st.select_slider(
        "Customer data sensitivity",
        options=["Low", "Medium", "High"],
        value="Medium",
        help="High = financial, health, or identity data. Low = basic user "
             "accounts only.",
    )

    st.markdown("---")
    analyse = st.button("🔍 Analyse my startup",
                        type="primary", use_container_width=True)


# --- Main panel ---
if not analyse:
    st.info("👈 Fill in your startup details on the left and click **Analyse "
            "my startup** to see your customised risk profile and "
            "recommended ICICI Lombard policies.")
    st.markdown("### What this tool does")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🎯 Sector-aware profiling**\n\nWe match your sector against "
                    "known risk patterns from 13+ startup categories.")
    with col2:
        st.markdown("**📊 5-dimension risk score**\n\nCyber, Liability, Key Person, "
                    "Property, and Compliance — scored 0–100.")
    with col3:
        st.markdown("**🛡️ Plain-language plan**\n\nTop 5 ICICI Lombard policies "
                    "explained as if talking to a first-time founder.")
    st.stop()


# ============ ANALYSE PATH ============
scores = compute_risk_scores(sector, funding_stage, team_size,
                             operations, data_sensitivity)
recommendations = recommend_products(scores, sector, team_size, funding_stage)

# Profile header strip
st.markdown(f"## {SECTOR_PROFILES[sector]['emoji']} Profile: **{startup_name}**")
meta_col1, meta_col2, meta_col3, meta_col4 = st.columns(4)
meta_col1.metric("Sector", sector.split(" /")[0])
meta_col2.metric("Stage", funding_stage)
meta_col3.metric("Team", f"{team_size} people")
meta_col4.metric("Ops", operations)

st.markdown("---")

# Risk dashboard
st.markdown("### 📊 Your Risk Dashboard")
dash_col1, dash_col2 = st.columns([1, 1.2])
with dash_col1:
    st.plotly_chart(render_risk_radar(scores), use_container_width=True)
with dash_col2:
    st.plotly_chart(render_risk_bars(scores), use_container_width=True)

# Interpretation strip
overall = sum(scores.values()) / len(scores)
if overall >= 70:
    verdict = ("🔴 **High overall exposure.** Several risk categories are at "
               "critical level — you likely need a bundled cover now.")
elif overall >= 45:
    verdict = ("🟠 **Moderate overall exposure.** Cover the critical categories "
               "first, revisit the rest every 6 months.")
else:
    verdict = ("🟢 **Low overall exposure.** Start with the essentials and "
               "layer on as you scale.")
st.info(verdict)

st.markdown("---")

# Product recommendations
st.markdown("### 🎯 Recommended ICICI Lombard Products")
st.caption("Ranked by how closely they match **your** risk profile. "
           "Tap any card to understand what it covers in plain language.")

for rec in recommendations:
    priority = rec["priority"]
    css_class = priority_css(priority)

    st.markdown(
        f"""
        <div class="product-card">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <h4>{rec['name']}</h4>
            <span class="{css_class}">{priority}</span>
          </div>
          <div style="color:#666; font-size:0.88rem; margin-bottom:0.4rem;">
            <strong>ICICI Lombard product:</strong> {rec['il_product']}
          </div>
          <div style="margin-top:0.5rem;">
            <strong>What it covers:</strong> {rec['what_it_covers']}
          </div>
          <div class="nudge-box">
            💡 <strong>Why you need this:</strong> {rec['nudge']}
          </div>
          <div style="margin-top:0.6rem; font-size:0.82rem; color:#888;">
            Best for: {rec['best_for']} · Fit score:
            <strong>{rec['score']:.0f}/100</strong>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# Plain-language founder explainer
with st.expander("📘 Founder's explainer — what each of these actually means",
                 expanded=False):
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

with st.expander("🧠 How we scored you — the logic behind the numbers"):
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
st.caption("This prototype is a proof-of-concept built for ICICI Lombard. "
           "All product names are mapped to real ICICI Lombard offerings. "
           "Scores are indicative and meant to start a conversation with a "
           "licensed broker or relationship manager — they do not replace "
           "formal underwriting.")
