"""
risk_engine.py — Startup Shield core logic
All sector profiles, product catalog, risk scoring, and recommendation logic lives here.
Import this module in startup_risk_app.py and retest.py.
"""
import math
import decimal
import warnings


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
# PRODUCT CATALOG — 28 ICICI Lombard products
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
    # ── 12 NEW PRODUCTS ───────────────────────────────────────────────────────
    "comprehensive_general_liability": {
        "name": "Comprehensive General Liability (CGL)",
        "il_product": "Commercial General Liability Insurance",
        "what_it_covers": (
            "Broad umbrella cover for bodily injury, property damage, and personal "
            "injury claims made against your business by third parties — customers, "
            "vendors, or the public. Wider scope than standard public liability."
        ),
        "nudge": (
            "Enterprise B2B clients and international contracts increasingly require "
            "CGL as a vendor prerequisite. Without it, you can lose deals before they start."
        ),
        "best_for": "B2B SaaS, IT services, consulting, any startup with enterprise clients.",
    },
    "business_interruption": {
        "name": "Business Interruption Insurance",
        "il_product": "Consequential Loss (Fire) / Business Interruption Policy",
        "what_it_covers": (
            "Replaces lost revenue and pays fixed costs (rent, salaries) if your "
            "business is forced to shut down or slow down due to a covered event — "
            "fire, flood, or a major cyber incident. Bridges the gap while you rebuild."
        ),
        "nudge": (
            "Post-Series A, your monthly burn is high enough that even 30 days of "
            "downtime can permanently damage the business. This is your revenue safety net."
        ),
        "best_for": "Series A+ startups, physical ops, cloud infra-dependent SaaS.",
    },
    "property_all_risk": {
        "name": "Property All Risk Insurance",
        "il_product": "Industrial All Risk Insurance / Property All Risk",
        "what_it_covers": (
            "Broadest property cover available — protects all physical assets against "
            "any accidental loss or damage not explicitly excluded. Goes beyond standard "
            "fire policies to cover accidental damage, equipment failure, and more."
        ),
        "nudge": (
            "If you have a lab, server room, or manufacturing line, standard fire "
            "insurance leaves big gaps. All-risk is the upgrade that actually covers "
            "real-world accidents."
        ),
        "best_for": "Deeptech, cleantech hardware, medical device startups, labs.",
    },
    "electronic_equipment": {
        "name": "Electronic Equipment Insurance",
        "il_product": "Electronic Equipment Insurance (EEI)",
        "what_it_covers": (
            "Covers sudden and accidental damage to computers, servers, telecom "
            "equipment, medical devices, and other electronic machinery — including "
            "electrical burnout, short circuit, and accidental operator error."
        ),
        "nudge": (
            "A server rack failure or GPU cluster burnout can cost Rs 50L+ and set "
            "your product back by months. Standard property policies exclude electrical "
            "damage — this one doesn't."
        ),
        "best_for": "Deeptech / AI, healthtech with medical devices, cloud hardware operators.",
    },
    "machinery_breakdown": {
        "name": "Machinery Breakdown Insurance",
        "il_product": "Machinery Breakdown Insurance / Boiler & Pressure Plant Insurance",
        "what_it_covers": (
            "Covers sudden mechanical or electrical breakdown of machinery and plant "
            "equipment. Pays for repair or replacement costs and consequential "
            "business loss from the breakdown."
        ),
        "nudge": (
            "If a critical machine breaks in your production line, downtime costs "
            "compound daily. This converts an unpredictable capital hit into a "
            "small, predictable premium."
        ),
        "best_for": "Cleantech / manufacturing, agritech with processing equipment, foodtech.",
    },
    "motor_fleet": {
        "name": "Motor Fleet / Goods Vehicle Insurance",
        "il_product": "Goods Carrying Vehicle Insurance / Passenger Carrying Vehicle Insurance",
        "what_it_covers": (
            "Covers your entire vehicle fleet — own damage, third-party liability, "
            "and personal accident cover for drivers. Single fleet policy is cheaper "
            "and simpler than insuring each vehicle separately."
        ),
        "nudge": (
            "Every uninsured delivery vehicle is a liability bomb. One accident "
            "without commercial vehicle cover exposes you personally to third-party "
            "claims that can run into crores."
        ),
        "best_for": "Logistics / mobility startups, agritech with farm vehicles, D2C with own fleet.",
    },
    "trade_credit": {
        "name": "Trade Credit Insurance",
        "il_product": "Trade Credit Insurance / Credit Insurance",
        "what_it_covers": (
            "Protects your accounts receivable if a B2B customer fails to pay due "
            "to insolvency, default, or political risk. Lets you extend credit "
            "confidently and protect cash flow."
        ),
        "nudge": (
            "If your top 3 customers account for 60%+ of revenue, one default "
            "can wipe out your runway. Essential for any B2B startup "
            "with payment terms of 30-90 days."
        ),
        "best_for": "B2B SaaS, logistics, D2C with wholesale channels, fintech lending platforms.",
    },
    "money_insurance": {
        "name": "Money Insurance",
        "il_product": "Money Insurance Policy",
        "what_it_covers": (
            "Covers physical cash, cheques, and negotiable instruments against "
            "loss by theft, robbery, or accident — whether in transit, in a safe, "
            "or at the premises."
        ),
        "nudge": (
            "Retail ops, cash-handling kitchens, and event businesses handle "
            "significant daily cash. One robbery without this policy means "
            "the loss comes straight out of your working capital."
        ),
        "best_for": "Foodtech / cloud kitchen, D2C retail, events, logistics cash-on-delivery ops.",
    },
    "contractors_all_risk": {
        "name": "Contractors All Risk (CAR) / Erection All Risk (EAR)",
        "il_product": "Contractors All Risk Insurance / Erection All Risk Insurance",
        "what_it_covers": (
            "Covers construction and installation projects against accidental damage, "
            "fire, flood, and third-party liability during the project period. "
            "EAR specifically covers machinery and equipment being erected or installed."
        ),
        "nudge": (
            "If you're building infrastructure, installing solar panels, or "
            "erecting hardware at a client site, your standard policies provide "
            "zero cover. CAR/EAR is the mandatory gap-filler."
        ),
        "best_for": "Cleantech, deeptech hardware, agritech with infrastructure, construction-adjacent startups.",
    },
    "drone_insurance": {
        "name": "Remotely Piloted Aircraft (Drone) Insurance",
        "il_product": "Remotely Piloted Aircraft Insurance",
        "what_it_covers": (
            "Covers drones against accidental damage, third-party liability for "
            "bodily injury or property damage, and hull loss. Required under DGCA "
            "regulations for commercial drone operations in India."
        ),
        "nudge": (
            "DGCA mandates insurance for all commercial drone operations. Flying "
            "without it is illegal, and one crash in a populated area without "
            "liability cover is a company-ending event."
        ),
        "best_for": "Agritech with drone ops, logistics / drone delivery, survey and mapping startups.",
    },
    "msme_suraksha": {
        "name": "MSME Suraksha Kavach (Complete Package)",
        "il_product": "MSME Suraksha Kavach / Complete Fire & Package Policy",
        "what_it_covers": (
            "All-in-one package for small businesses — combines fire, burglary, "
            "money, personal accident, public liability, and business interruption "
            "in a single affordable policy. IRDAI-designed for MSMEs."
        ),
        "nudge": (
            "If you're pre-Series A with physical ops, this single policy gives "
            "you 6 covers at the price of 2. It's the most capital-efficient "
            "insurance purchase a small startup can make."
        ),
        "best_for": "Pre-seed to Seed startups with physical operations, retail, food, light manufacturing.",
    },
    "enterprise_secure": {
        "name": "Enterprise Secure Package Policy",
        "il_product": "Enterprise Secure Package Policy / Business Shield",
        "what_it_covers": (
            "Comprehensive business package for mid-to-large enterprises — combines "
            "property all risk, machinery breakdown, business interruption, "
            "public liability, and fidelity in a single policy."
        ),
        "nudge": (
            "Post-Series A, managing 6 separate policies means 6 renewal dates, "
            "6 claims processes, and 6 chances for a coverage gap. One enterprise "
            "package eliminates all of that."
        ),
        "best_for": "Series A+ startups with physical assets, manufacturing, complex multi-site ops.",
    },
}


# =============================================================================
# PRODUCT RISK MAP — 28 entries
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
    # new
    "comprehensive_general_liability": {"Liability Risk": 0.9, "Compliance Risk": 0.3},
    "business_interruption":           {"Property Risk": 0.5, "Cyber Risk": 0.3, "Liability Risk": 0.2},
    "property_all_risk":               {"Property Risk": 1.0, "Liability Risk": 0.2},
    "electronic_equipment":            {"Property Risk": 0.7, "Cyber Risk": 0.2},
    "machinery_breakdown":             {"Property Risk": 0.8, "Compliance Risk": 0.1},
    "motor_fleet":                     {"Liability Risk": 0.8, "Property Risk": 0.6},
    "trade_credit":                    {"Compliance Risk": 0.4, "Liability Risk": 0.5},
    "money_insurance":                 {"Property Risk": 0.4, "Liability Risk": 0.3},
    "contractors_all_risk":            {"Property Risk": 0.9, "Liability Risk": 0.5},
    "drone_insurance":                 {"Liability Risk": 0.7, "Property Risk": 0.5, "Compliance Risk": 0.4},
    "msme_suraksha":                   {"Property Risk": 0.6, "Liability Risk": 0.4},
    "enterprise_secure":               {"Property Risk": 0.8, "Liability Risk": 0.4, "Compliance Risk": 0.2},
}


# =============================================================================
# SECTOR OVERRIDES & EXCLUSIONS
# =============================================================================
SECTOR_OVERRIDES = {
    "Healthtech":               ["clinical_trials", "electronic_equipment"],
    "Logistics / Mobility":     ["marine_transit", "public_liability", "motor_fleet"],
    "D2C / Consumer Brands":    ["product_liability", "marine_transit", "msme_suraksha"],
    "Foodtech / Cloud Kitchen": ["product_liability", "public_liability", "money_insurance"],
    "Fintech":                  ["crime_fidelity", "dno_liability", "trade_credit"],
    "Cleantech / Climatetech":  ["property_fire", "public_liability", "contractors_all_risk"],
    "Agritech":                 ["marine_transit", "drone_insurance", "motor_fleet"],
    "Deeptech / AI / Robotics": ["electronic_equipment", "property_all_risk", "key_person"],
    "SaaS / Enterprise Software": ["cyber_liability", "professional_indemnity",
                                   "comprehensive_general_liability"],
    "Edtech":                   ["cyber_liability", "employee_health"],
    "HRtech":                   ["cyber_liability", "employment_practices"],
    "Legaltech":                ["professional_indemnity", "dno_liability"],
    "Gaming / Media / Content": ["cyber_liability", "professional_indemnity"],
}

SECTOR_EXCLUSIONS = {
    "SaaS / Enterprise Software":   ["clinical_trials", "product_liability", "marine_transit",
                                     "motor_fleet", "drone_insurance", "contractors_all_risk",
                                     "machinery_breakdown", "msme_suraksha", "money_insurance"],
    "Fintech":                      ["clinical_trials", "product_liability", "marine_transit",
                                     "motor_fleet", "drone_insurance", "contractors_all_risk",
                                     "machinery_breakdown", "msme_suraksha", "money_insurance"],
    "Edtech":                       ["clinical_trials", "product_liability", "marine_transit",
                                     "motor_fleet", "drone_insurance", "contractors_all_risk",
                                     "machinery_breakdown", "money_insurance"],
    "HRtech":                       ["clinical_trials", "product_liability", "marine_transit",
                                     "motor_fleet", "drone_insurance", "contractors_all_risk",
                                     "machinery_breakdown", "msme_suraksha", "money_insurance"],
    "Legaltech":                    ["clinical_trials", "product_liability", "marine_transit",
                                     "motor_fleet", "drone_insurance", "contractors_all_risk",
                                     "machinery_breakdown", "msme_suraksha", "money_insurance"],
    "Gaming / Media / Content":     ["clinical_trials", "marine_transit", "motor_fleet",
                                     "drone_insurance", "contractors_all_risk",
                                     "machinery_breakdown", "msme_suraksha", "money_insurance"],
    "D2C / Consumer Brands":        ["clinical_trials", "drone_insurance", "contractors_all_risk",
                                     "electronic_equipment", "motor_fleet"],
    "Healthtech":                   ["motor_fleet", "drone_insurance", "msme_suraksha",
                                     "contractors_all_risk", "money_insurance"],
    "Deeptech / AI / Robotics":     ["clinical_trials", "marine_transit", "motor_fleet",
                                     "drone_insurance", "msme_suraksha", "money_insurance"],
    "Agritech":                     ["clinical_trials", "enterprise_secure"],
    "Cleantech / Climatetech":      ["clinical_trials", "drone_insurance", "money_insurance",
                                     "trade_credit", "msme_suraksha"],
    "Logistics / Mobility":         ["clinical_trials", "product_liability",
                                     "electronic_equipment", "machinery_breakdown",
                                     "enterprise_secure"],
    "Foodtech / Cloud Kitchen":     ["clinical_trials", "marine_transit", "motor_fleet",
                                     "drone_insurance", "contractors_all_risk",
                                     "electronic_equipment", "enterprise_secure"],
}


# =============================================================================
# RISK SCORING ENGINE
# =============================================================================
def compute_risk_scores(sector: str, funding_stage: str, team_size: int,
                        operations: str, data_sensitivity: str) -> dict:
    """
    Rule-based risk engine. Returns dict of five risk category scores (0-100).
    Fixes applied: input validation, gradual key-person decay, log-scale liability,
    ROUND_HALF_UP for deterministic priority boundary behaviour.
    """
    # Fix 10 — Input validation
    if sector not in SECTOR_PROFILES:
        raise ValueError(f"Unknown sector: {sector!r}")
    if funding_stage not in ("Pre-seed", "Seed", "Series A", "Series B+"):
        raise ValueError(f"Unknown funding stage: {funding_stage!r}")
    if not isinstance(team_size, int) or team_size < 1:
        raise ValueError(f"team_size must be a positive integer, got {team_size!r}")
    if operations not in ("Digital-only", "Physical-only", "Hybrid"):
        raise ValueError(f"Unknown operations type: {operations!r}")
    if data_sensitivity not in ("Low", "Medium", "High"):
        raise ValueError(f"Unknown data sensitivity: {data_sensitivity!r}")

    base = SECTOR_PROFILES[sector]

    stage_multiplier = {
        "Pre-seed": 0.7, "Seed": 0.9, "Series A": 1.1, "Series B+": 1.3,
    }[funding_stage]

    if team_size <= 5:     team_mult = 0.8
    elif team_size <= 20:  team_mult = 1.0
    elif team_size <= 50:  team_mult = 1.15
    elif team_size <= 150: team_mult = 1.3
    else:                  team_mult = 1.5

    ops_mult = {
        "Digital-only":  {"property": 0.4, "liability": 0.8, "cyber": 1.2},
        "Physical-only": {"property": 1.4, "liability": 1.2, "cyber": 0.7},
        "Hybrid":        {"property": 1.0, "liability": 1.0, "cyber": 1.0},
    }[operations]

    data_mult = {
        "Low":    {"cyber": 0.6, "compliance": 0.8},
        "Medium": {"cyber": 1.0, "compliance": 1.0},
        "High":   {"cyber": 1.4, "compliance": 1.3},
    }[data_sensitivity]

    # Fix 11 — Deterministic rounding (no banker's rounding at priority boundaries)
    def to_100(x: float) -> float:
        d = decimal.Decimal(str(x * 7.5)).quantize(
            decimal.Decimal("0.1"), rounding=decimal.ROUND_HALF_UP
        )
        return float(max(decimal.Decimal("0"), min(decimal.Decimal("100"), d)))

    # Cyber
    cyber = base["cyber"] * stage_multiplier * ops_mult["cyber"] * data_mult["cyber"]

    # Fix 4 — log-scale liability: grows fast at small teams, slows at large teams, no ceiling
    team_liability_factor = 0.85 + 0.08 * math.log1p(team_size / 10)
    liability = base["liability"] * stage_multiplier * ops_mult["liability"] * team_liability_factor

    # Fix 3 — gradual key-person decay across 6 team size bands
    if team_size <= 5:     kp_mult = 1.5
    elif team_size <= 10:  kp_mult = 1.4
    elif team_size <= 20:  kp_mult = 1.2
    elif team_size <= 50:  kp_mult = 1.0
    elif team_size <= 150: kp_mult = 0.85
    else:                  kp_mult = 0.7
    key_person = base["key_person"] * kp_mult * stage_multiplier

    property_risk = base["property"] * ops_mult["property"] * team_mult
    compliance = base["compliance"] * stage_multiplier * data_mult["compliance"]

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


# =============================================================================
# PRODUCT RECOMMENDER
# =============================================================================
def _proportional_boost(score: float, pct: float, floor: float) -> float:
    """Lift score proportionally, capped at 100, guaranteed at least floor."""
    return min(100.0, max(score * (1.0 + pct), floor))


def recommend_products(risk_scores: dict, sector: str, team_size: int,
                       funding_stage: str) -> list:
    """
    Returns the top 5 by fit score, then appends required products that were
    displaced by ranking ties or stronger competitors.
    Each product dict has keys: name, il_product, what_it_covers, nudge,
    best_for, key, score, priority, and optionally mandatory=True.
    """
    scored = []
    excluded = set(SECTOR_EXCLUSIONS.get(sector, []))

    for key, weights in PRODUCT_RISK_MAP.items():
        if key in excluded:
            continue
        raw = sum(risk_scores[cat] * w for cat, w in weights.items())
        score = raw / sum(weights.values())
        scored.append((key, score))

    # Fix 1 — proportional sector override boosts (replaces flat +25)
    for key in SECTOR_OVERRIDES.get(sector, []):
        scored = [
            (k, _proportional_boost(s, pct=0.40, floor=50.0)) if k == key else (k, s)
            for k, s in scored
        ]

    # Fix 7 — D&O boost: stage-aware AND compliance-aware (replaces flat +30)
    if funding_stage in ("Series A", "Series B+"):
        compliance_factor = 1.0 + (risk_scores["Compliance Risk"] / 200.0)
        scored = [
            (k, _proportional_boost(s, pct=0.45 * compliance_factor, floor=55.0))
            if k == "dno_liability" else (k, s)
            for k, s in scored
        ]

    # Fix 1 — proportional team-size boosts (replaces flat +10 / +8)
    if team_size >= 10:
        scored = [
            (k, _proportional_boost(s, pct=0.20, floor=40.0)) if k == "employee_health" else (k, s)
            for k, s in scored
        ]
    if team_size >= 25:
        scored = [
            (k, _proportional_boost(s, pct=0.15, floor=38.0)) if k == "employment_practices" else (k, s)
            for k, s in scored
        ]

    scored = [(k, min(100.0, s)) for k, s in scored]
    scored.sort(key=lambda x: x[1], reverse=True)
    scored_lookup = dict(scored)

    # Fix 5 — warn if pool is thin
    if len(scored) < 5:
        warnings.warn(
            f"Only {len(scored)} eligible products for sector '{sector}'. "
            "Consider reviewing SECTOR_EXCLUSIONS.",
            stacklevel=2,
        )

    top5 = scored[:5]
    top5_keys = {k for k, _ in top5}

    # Fix 2 — priority label always computed AFTER rounding
    results = []
    result_keys = set()
    for key, score in top5:
        product = PRODUCT_CATALOG[key].copy()
        product["key"] = key
        product["score"] = round(score, 1)
        product["priority"] = priority_label(product["score"])
        product["mandatory"] = False
        results.append(product)
        result_keys.add(key)

    # Mandatory employee_health baseline — always surface if not in top 5
    def append_mandatory(key: str, fallback_score: float = 0.0) -> None:
        if key in excluded or key in result_keys or key not in PRODUCT_CATALOG:
            return
        score = round(scored_lookup.get(key, fallback_score), 1)
        product = PRODUCT_CATALOG[key].copy()
        product["key"] = key
        product["score"] = score
        product["priority"] = priority_label(score)
        product["mandatory"] = True
        results.append(product)
        result_keys.add(key)

    for key in SECTOR_OVERRIDES.get(sector, []):
        if key not in top5_keys:
            append_mandatory(key)

    if funding_stage in ("Series A", "Series B+") and "dno_liability" not in top5_keys:
        append_mandatory("dno_liability")

    append_mandatory("employee_health", fallback_score=40.0)

    return results


# =============================================================================
# CONFIG VALIDATOR — Fix 6, runs at import time
# =============================================================================
def validate_config() -> None:
    """
    Raises ValueError on startup if:
    - Any product key is in both OVERRIDES and EXCLUSIONS for the same sector
    - Any override/exclusion key doesn't exist in PRODUCT_CATALOG
    """
    errors = []
    all_keys = set(PRODUCT_CATALOG.keys())

    for sector, overrides in SECTOR_OVERRIDES.items():
        exclusions = set(SECTOR_EXCLUSIONS.get(sector, []))
        conflicts = [k for k in overrides if k in exclusions]
        if conflicts:
            errors.append(
                f"  CONFLICT in '{sector}': {conflicts} are in both OVERRIDES and EXCLUSIONS."
            )
        for k in overrides:
            if k not in all_keys:
                errors.append(f"  OVERRIDE key '{k}' in '{sector}' missing from PRODUCT_CATALOG.")

    for sector, excl_keys in SECTOR_EXCLUSIONS.items():
        for k in excl_keys:
            if k not in all_keys:
                errors.append(f"  EXCLUSION key '{k}' in '{sector}' missing from PRODUCT_CATALOG.")

    if errors:
        raise ValueError("Risk engine config errors found:\n" + "\n".join(errors))


validate_config()  # runs once at import time — catches config bugs immediately
