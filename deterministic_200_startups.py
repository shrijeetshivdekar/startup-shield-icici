"""Generate and deterministically test 200 synthetic startup profiles."""

from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

from risk_engine import (
    SECTOR_EXCLUSIONS,
    SECTOR_PROFILES,
    SUB_SECTOR_OPTIONS,
    SUB_SECTOR_PROFILES,
    analyze_profile,
    derive_physical_risk_inputs,
    priority_label,
)


ROOT = Path(__file__).resolve().parent
FIXTURES_DIR = ROOT / "fixtures"
DATASET_PATH = FIXTURES_DIR / "synthetic_startups_200.json"
REPORT_PATH = FIXTURES_DIR / "deterministic_test_report_200.json"
SEED = 20260426
PROFILE_COUNT = 200

STAGES = ["Pre-seed", "Seed", "Series A", "Series B+"]
OPERATIONS = ["Digital-only", "Physical-only", "Hybrid"]
DATA_SENSITIVITY = ["Low", "Medium", "High"]
CUSTOMER_TYPES = [
    "B2B Enterprise",
    "B2C Consumers",
    "Government / PSU",
    "D2C / Marketplace",
    "SMB / MSME",
]
DATA_HANDLED = [
    "Payments / financial transactions",
    "Health / medical records",
    "Personal identity data (KYC / Aadhaar)",
    "Physical inventory / goods",
    "Sensitive personal data (DPDP Act)",
    "None of the above",
]
REGULATORY = [
    "RBI / SEBI / IRDAI licensed",
    "FSSAI / food safety",
    "CDSCO / medical devices",
    "DPDP Act obligations",
    "DGCA / drone operations",
    "None / minimal",
]
PHYSICAL_ASSETS = [
    "Office / coworking space",
    "Warehouse / fulfilment centre",
    "Lab / R&D equipment",
    "Vehicles / delivery fleet",
    "Kitchen / food processing",
    "None — fully cloud",
]
STATE_FOOTPRINT = [
    "Karnataka",
    "Rajasthan",
    "Bihar",
    "Jharkhand",
    "Telangana",
    "Maharashtra",
    "Delhi",
    "Tamil Nadu",
    "Gujarat",
    "Other",
]
HOLDCO_DOMICILES = ["India", "DE", "SG", "Cayman", "Flip_pending"]
DATA_LOCALISATION_STATUSES = ["Unknown", "Full_onshore", "Hybrid", "Offshore"]

NAME_PREFIXES = [
    "Aegis",
    "Northstar",
    "BluePeak",
    "Signal",
    "Orbit",
    "Granite",
    "Copper",
    "Nimbus",
    "Summit",
    "Lattice",
    "Vector",
    "Pulse",
    "Anchor",
    "Atlas",
    "Foundry",
    "Praxis",
    "Helix",
    "Cinder",
    "Verve",
    "Harbor",
]
NAME_ROOTS = [
    "Labs",
    "Works",
    "Systems",
    "Grid",
    "Flow",
    "Stack",
    "Forge",
    "Nexus",
    "Mint",
    "Pilot",
    "Bridge",
    "Cloud",
    "Track",
    "Scale",
    "Core",
    "Spring",
    "Logic",
    "Loop",
    "Ledger",
    "Wave",
]
NAME_SUFFIXES = [
    "AI",
    "Health",
    "Pay",
    "Mobility",
    "Energy",
    "Foods",
    "Learn",
    "Ops",
    "Chain",
    "Metrics",
    "Care",
    "Pulse",
    "Motion",
    "Data",
    "Secure",
    "Robotics",
]

SECTOR_CONFIG = {
    "SaaS / Enterprise Software": {
        "operations": ["Digital-only", "Hybrid"],
        "data": ["Medium", "High"],
        "customers": ["B2B Enterprise", "SMB / MSME", "Government / PSU"],
        "data_handled": ["Personal identity data (KYC / Aadhaar)", "Sensitive personal data (DPDP Act)"],
        "regulatory": ["DPDP Act obligations"],
        "assets": ["Office / coworking space", "None — fully cloud"],
        "descriptions": [
            "Builds workflow automation and analytics software for finance, operations, and compliance teams.",
            "Provides enterprise API infrastructure, admin tooling, and internal controls for mid-market businesses.",
        ],
        "fears": [
            "A platform outage or data exposure that causes enterprise churn.",
            "A missed SLA leading to contractual claims from larger customers.",
        ],
    },
    "Fintech": {
        "operations": ["Digital-only", "Hybrid"],
        "data": ["High"],
        "customers": ["SMB / MSME", "B2C Consumers", "B2B Enterprise"],
        "data_handled": [
            "Payments / financial transactions",
            "Personal identity data (KYC / Aadhaar)",
            "Sensitive personal data (DPDP Act)",
        ],
        "regulatory": ["RBI / SEBI / IRDAI licensed", "DPDP Act obligations"],
        "assets": ["Office / coworking space", "None — fully cloud"],
        "descriptions": [
            "Offers regulated financial workflows including lending, payments, cards, insurance distribution, or personal finance.",
            "Runs transaction infrastructure and compliance rails for merchants, consumers, and financial institutions.",
        ],
        "fears": [
            "A fraud event or RBI action that interrupts operations during a fundraising cycle.",
            "A payments outage or KYC leak that destroys trust with users and partners.",
        ],
    },
    "Healthtech": {
        "operations": ["Digital-only", "Hybrid", "Physical-only"],
        "data": ["High"],
        "customers": ["B2B Enterprise", "B2C Consumers", "Government / PSU", "SMB / MSME"],
        "data_handled": [
            "Health / medical records",
            "Personal identity data (KYC / Aadhaar)",
            "Sensitive personal data (DPDP Act)",
        ],
        "regulatory": ["CDSCO / medical devices", "DPDP Act obligations"],
        "assets": ["Office / coworking space", "Lab / R&D equipment", "None — fully cloud"],
        "descriptions": [
            "Delivers digital care, diagnostics, medical-device software, or workflow software for healthcare providers.",
            "Builds patient-facing or provider-facing products handling clinical data and regulated healthcare workflows.",
        ],
        "fears": [
            "A clinical error allegation or device issue leading to liability claims.",
            "Improper handling of patient data causing regulatory scrutiny and reputational damage.",
        ],
    },
    "D2C / Consumer Brands": {
        "operations": ["Hybrid", "Physical-only"],
        "data": ["Low", "Medium"],
        "customers": ["B2C Consumers", "D2C / Marketplace", "SMB / MSME"],
        "data_handled": ["Physical inventory / goods", "Personal identity data (KYC / Aadhaar)"],
        "regulatory": ["DPDP Act obligations", "None / minimal"],
        "assets": ["Office / coworking space", "Warehouse / fulfilment centre", "None — fully cloud"],
        "descriptions": [
            "Sells consumer products through own channels and marketplaces with inventory, fulfilment, and marketing operations.",
            "Builds a digitally native brand with sourcing, warehousing, returns, and omnichannel retail exposure.",
        ],
        "fears": [
            "A product defect, shipment loss, or recall that goes viral online.",
            "A warehouse disruption during a major sales period that crushes margins.",
        ],
    },
    "Deeptech / AI / Robotics": {
        "operations": ["Hybrid", "Digital-only", "Physical-only"],
        "data": ["Medium", "High"],
        "customers": ["B2B Enterprise", "Government / PSU", "SMB / MSME"],
        "data_handled": ["Sensitive personal data (DPDP Act)", "Physical inventory / goods", "None of the above"],
        "regulatory": ["DGCA / drone operations", "DPDP Act obligations", "None / minimal"],
        "assets": ["Lab / R&D equipment", "Office / coworking space", "Warehouse / fulfilment centre"],
        "descriptions": [
            "Builds AI software, robotics systems, or autonomy infrastructure with a mix of IP, hardware, and enterprise delivery risk.",
            "Develops advanced models, sensors, or machine systems deployed into industrial or critical workflows.",
        ],
        "fears": [
            "An IP dispute or field failure that stalls customer deployments.",
            "A hardware incident or export-control issue that delays scale-up.",
        ],
    },
    "Edtech": {
        "operations": ["Digital-only", "Hybrid"],
        "data": ["Medium", "High"],
        "customers": ["B2C Consumers", "Government / PSU", "SMB / MSME"],
        "data_handled": ["Personal identity data (KYC / Aadhaar)", "Sensitive personal data (DPDP Act)"],
        "regulatory": ["DPDP Act obligations", "None / minimal"],
        "assets": ["Office / coworking space", "None — fully cloud"],
        "descriptions": [
            "Provides learning, assessment, tutoring, or skilling products for students, parents, schools, or employers.",
            "Runs online education workflows with learner data, teacher networks, and high consumer-trust exposure.",
        ],
        "fears": [
            "A complaints cycle around outcomes, refunds, or learner privacy.",
            "A misleading-marketing allegation or minor-data issue causing brand damage.",
        ],
    },
    "Agritech": {
        "operations": ["Physical-only", "Hybrid", "Digital-only"],
        "data": ["Low", "Medium"],
        "customers": ["SMB / MSME", "Government / PSU", "B2B Enterprise"],
        "data_handled": ["Physical inventory / goods", "None of the above"],
        "regulatory": ["DGCA / drone operations", "None / minimal"],
        "assets": ["Warehouse / fulfilment centre", "Vehicles / delivery fleet", "Lab / R&D equipment", "Office / coworking space"],
        "descriptions": [
            "Supports farm supply chains, agri-finance enablement, farm intelligence, or input distribution across rural operations.",
            "Operates products tied to crops, farm logistics, climate exposure, or agri-market infrastructure.",
        ],
        "fears": [
            "Extreme weather or field disruption wiping out operating continuity.",
            "A logistics or hardware issue that breaks trust with growers and channel partners.",
        ],
    },
    "Cleantech / Climatetech": {
        "operations": ["Hybrid", "Physical-only", "Digital-only"],
        "data": ["Low", "Medium"],
        "customers": ["B2B Enterprise", "Government / PSU", "SMB / MSME"],
        "data_handled": ["Physical inventory / goods", "None of the above"],
        "regulatory": ["None / minimal", "DGCA / drone operations"],
        "assets": ["Lab / R&D equipment", "Warehouse / fulfilment centre", "Office / coworking space"],
        "descriptions": [
            "Builds decarbonisation, energy, storage, waste, or climate-data solutions with supply-chain and policy dependence.",
            "Runs a climate or industrial sustainability business exposed to equipment, site, and customer ESG requirements.",
        ],
        "fears": [
            "A supplier or policy shock delaying deployments and revenues.",
            "A site incident or product underperformance affecting enterprise contracts.",
        ],
    },
    "Logistics / Mobility": {
        "operations": ["Physical-only", "Hybrid"],
        "data": ["Medium"],
        "customers": ["B2B Enterprise", "B2C Consumers", "SMB / MSME", "D2C / Marketplace"],
        "data_handled": ["Physical inventory / goods", "Personal identity data (KYC / Aadhaar)"],
        "regulatory": ["DPDP Act obligations", "None / minimal"],
        "assets": ["Vehicles / delivery fleet", "Warehouse / fulfilment centre", "Office / coworking space"],
        "descriptions": [
            "Runs transportation, fleet, freight, dispatch, or last-mile infrastructure with high third-party and workforce exposure.",
            "Coordinates physical movement of goods or people with field operations, vehicles, and partner networks.",
        ],
        "fears": [
            "A serious third-party accident or labour escalation hitting operations.",
            "A fleet or warehouse incident causing service disruption and liability claims.",
        ],
    },
    "Legaltech": {
        "operations": ["Digital-only", "Hybrid"],
        "data": ["High", "Medium"],
        "customers": ["B2B Enterprise", "Government / PSU", "SMB / MSME"],
        "data_handled": ["Sensitive personal data (DPDP Act)", "Personal identity data (KYC / Aadhaar)"],
        "regulatory": ["DPDP Act obligations", "None / minimal"],
        "assets": ["Office / coworking space", "None — fully cloud"],
        "descriptions": [
            "Provides contract, litigation, compliance, or legal workflow tooling where accuracy and confidentiality are critical.",
            "Builds legal operations software that handles privileged data and high-stakes enterprise use cases.",
        ],
        "fears": [
            "A confidentiality breach or bad automation outcome causing a client claim.",
            "An AI-assisted legal error leading to contractual liability and churn.",
        ],
    },
    "HRtech": {
        "operations": ["Digital-only", "Hybrid"],
        "data": ["High", "Medium"],
        "customers": ["B2B Enterprise", "SMB / MSME"],
        "data_handled": ["Personal identity data (KYC / Aadhaar)", "Sensitive personal data (DPDP Act)"],
        "regulatory": ["DPDP Act obligations", "None / minimal"],
        "assets": ["Office / coworking space", "None — fully cloud"],
        "descriptions": [
            "Builds payroll, HR operations, hiring, or workforce management software handling employee identity and compliance data.",
            "Runs employment infrastructure products touching payroll, attendance, benefits, or contractor workflows.",
        ],
        "fears": [
            "A payroll or employee-data failure causing client losses and reputational harm.",
            "A compliance miss around labour workflows escalating into client claims.",
        ],
    },
    "Gaming / Media / Content": {
        "operations": ["Digital-only", "Hybrid"],
        "data": ["Medium", "Low"],
        "customers": ["B2C Consumers", "D2C / Marketplace", "B2B Enterprise"],
        "data_handled": ["Personal identity data (KYC / Aadhaar)", "Sensitive personal data (DPDP Act)", "None of the above"],
        "regulatory": ["DPDP Act obligations", "None / minimal"],
        "assets": ["Office / coworking space", "None — fully cloud"],
        "descriptions": [
            "Builds gaming, streaming, creator, or content distribution products with consumer scale and reputation sensitivity.",
            "Operates digital entertainment workflows with moderation, IP clearance, and platform-liability exposure.",
        ],
        "fears": [
            "A moderation, IP, or consumer-safety issue triggering a public backlash.",
            "A platform or policy change sharply cutting growth and monetisation.",
        ],
    },
    "Foodtech / Cloud Kitchen": {
        "operations": ["Physical-only", "Hybrid"],
        "data": ["Low", "Medium"],
        "customers": ["B2C Consumers", "D2C / Marketplace", "SMB / MSME"],
        "data_handled": ["Physical inventory / goods", "Personal identity data (KYC / Aadhaar)"],
        "regulatory": ["FSSAI / food safety", "DPDP Act obligations"],
        "assets": ["Kitchen / food processing", "Vehicles / delivery fleet", "Warehouse / fulfilment centre", "Office / coworking space"],
        "descriptions": [
            "Runs cloud-kitchen or food-delivery operations with site, hygiene, packaging, and fleet exposure.",
            "Builds a food brand with distributed kitchens, fulfilment, and strong public reputation dependence.",
        ],
        "fears": [
            "A contamination or delivery incident damaging brand trust overnight.",
            "A kitchen shutdown during peak demand causing cascading customer complaints.",
        ],
    },
    "Crypto/VDA": {
        "operations": ["Digital-only", "Hybrid"],
        "data": ["High"],
        "customers": ["B2C Consumers", "B2B Enterprise", "SMB / MSME"],
        "data_handled": [
            "Payments / financial transactions",
            "Personal identity data (KYC / Aadhaar)",
            "Sensitive personal data (DPDP Act)",
        ],
        "regulatory": ["RBI / SEBI / IRDAI licensed", "DPDP Act obligations"],
        "assets": ["Office / coworking space", "None â€” fully cloud"],
        "descriptions": [
            "Runs VDA exchange, custody, wallet, or compliance infrastructure with AML, tax, cyber, and policy exposure.",
            "Builds crypto asset workflows for users and institutions with high trust, fraud, and regulatory sensitivity.",
        ],
        "fears": [
            "A wallet compromise, AML investigation, or policy shock interrupting customer access.",
            "A tax, compliance, or custody failure causing customer claims and regulatory scrutiny.",
        ],
    },
}


def pick_one(rng: random.Random, items: list[str]) -> str:
    return rng.choice(items)


def pick_some(rng: random.Random, items: list[str], min_count: int = 1, max_count: int = 2) -> list[str]:
    count = min(len(items), rng.randint(min_count, max_count))
    return rng.sample(items, count)


def pick_team_size(rng: random.Random, stage: str) -> int:
    if stage == "Pre-seed":
        return rng.randint(3, 10)
    if stage == "Seed":
        return rng.randint(8, 40)
    if stage == "Series A":
        return rng.randint(25, 120)
    return rng.randint(80, 500)


def chance(rng: random.Random, probability: float) -> bool:
    return rng.random() < probability


def build_name(index: int, rng: random.Random) -> str:
    return f"{pick_one(rng, NAME_PREFIXES)} {pick_one(rng, NAME_ROOTS)} {pick_one(rng, NAME_SUFFIXES)} {index + 1:03d}"


def choose_sub_sector(rng: random.Random, sector: str) -> str | None:
    options = SUB_SECTOR_OPTIONS.get(sector, [])
    if not options or not chance(rng, 0.70):
        return None
    filtered = [
        option for option in options
        if not SUB_SECTOR_PROFILES.get(option, {}).get("_hard_decline")
        and not SUB_SECTOR_PROFILES.get(option, {}).get("_decline_without_cdsco_licence")
    ]
    if not filtered:
        return None
    return pick_one(rng, filtered)


def choose_stage(rng: random.Random, sector: str) -> str:
    stage = pick_one(rng, STAGES)
    if sector in {"Fintech", "Healthtech"} and chance(rng, 0.55):
        stage = pick_one(rng, ["Seed", "Series A", "Series B+"])
    return stage


def choose_customers(rng: random.Random, sector: str) -> list[str]:
    return pick_some(rng, SECTOR_CONFIG[sector]["customers"], 1, 2)


def choose_data_handled(rng: random.Random, sector: str) -> list[str]:
    values = pick_some(rng, SECTOR_CONFIG[sector]["data_handled"], 1, 2)
    if "None of the above" in values and len(values) > 1:
        return ["None of the above"]
    return values


def choose_regulatory(rng: random.Random, sector: str) -> list[str]:
    values = pick_some(rng, SECTOR_CONFIG[sector]["regulatory"], 1, 2)
    if "None / minimal" in values and len(values) > 1:
        return ["None / minimal"]
    return values


def choose_physical_assets(rng: random.Random, sector: str, operations: str) -> list[str]:
    values = pick_some(rng, SECTOR_CONFIG[sector]["assets"], 1, 2)
    if operations == "Digital-only":
        return ["None — fully cloud"]
    if "None — fully cloud" in values and len(values) > 1:
        values = ["None — fully cloud"]
    if operations == "Physical-only" and values == ["None — fully cloud"]:
        if sector in {"Logistics / Mobility", "Foodtech / Cloud Kitchen", "D2C / Consumer Brands"}:
            return ["Office / coworking space", "Warehouse / fulfilment centre"]
        return ["Office / coworking space"]
    return values


def choose_gig_pct(rng: random.Random, sector: str) -> float:
    if sector in {"Logistics / Mobility", "Foodtech / Cloud Kitchen"}:
        return round(rng.uniform(0.25, 0.80), 2)
    if sector in {"D2C / Consumer Brands", "Agritech"}:
        return round(rng.uniform(0.00, 0.35), 2)
    return round(rng.uniform(0.00, 0.15), 2)


def choose_hardware_split(rng: random.Random, sector: str) -> float:
    if sector in {"D2C / Consumer Brands", "Deeptech / AI / Robotics", "Cleantech / Climatetech", "Agritech", "Foodtech / Cloud Kitchen"}:
        return round(rng.uniform(0.00, 0.75), 2)
    return round(rng.uniform(0.00, 0.25), 2)


def choose_climate_zone(rng: random.Random, sector: str) -> str:
    if sector in {"Agritech", "Cleantech / Climatetech", "Foodtech / Cloud Kitchen"}:
        return pick_one(rng, ["Medium", "High", "Extreme"])
    return pick_one(rng, ["Low", "Medium", "High", "Extreme"])


def choose_b2b_pct(rng: random.Random, sector: str) -> float:
    if sector in {"SaaS / Enterprise Software", "Legaltech", "HRtech", "Deeptech / AI / Robotics", "Cleantech / Climatetech"}:
        return round(rng.uniform(0.55, 0.95), 2)
    if sector in {"D2C / Consumer Brands", "Gaming / Media / Content", "Foodtech / Cloud Kitchen", "Edtech"}:
        return round(rng.uniform(0.05, 0.45), 2)
    return round(rng.uniform(0.25, 0.80), 2)


def choose_exports(rng: random.Random, sector: str) -> tuple[float, float, float]:
    export_eu = round(rng.uniform(0.00, 0.45 if sector in {"Cleantech / Climatetech", "Deeptech / AI / Robotics", "D2C / Consumer Brands"} else 0.18), 2)
    export_us = round(rng.uniform(0.00, 0.50), 2)
    export_china = round(rng.uniform(0.00, 0.25 if sector in {"Deeptech / AI / Robotics", "Agritech", "Cleantech / Climatetech"} else 0.10), 2)
    return export_eu, export_us, export_china


def choose_supplier_china_pct(rng: random.Random, sector: str) -> float:
    if sector in {"D2C / Consumer Brands", "Deeptech / AI / Robotics", "Cleantech / Climatetech"}:
        return round(rng.uniform(0.00, 0.65), 2)
    return round(rng.uniform(0.00, 0.25), 2)


def choose_fundraising(rng: random.Random, stage: str) -> float:
    if stage == "Pre-seed":
        return round(rng.uniform(2, 20), 1)
    if stage == "Seed":
        return round(rng.uniform(15, 100), 1)
    if stage == "Series A":
        return round(rng.uniform(80, 500), 1)
    return round(rng.uniform(300, 2200), 1)


def choose_data_localisation(rng: random.Random, data_sensitivity: str) -> str:
    if data_sensitivity == "High":
        return pick_one(rng, ["Full_onshore", "Hybrid", "Offshore"])
    if data_sensitivity == "Medium":
        return pick_one(rng, ["Hybrid", "Full_onshore", "Unknown"])
    return pick_one(rng, ["Unknown", "Hybrid", "Full_onshore"])


def choose_rbi_registration(sector: str, sub_sector: str | None) -> str | None:
    if sector != "Fintech" or not sub_sector:
        return None
    if sub_sector.startswith("Fintech.NBFC_"):
        return "NBFC"
    if sub_sector.startswith("Fintech.PA_"):
        return "PA"
    if sub_sector == "Fintech.Neobank_PPI":
        return "PPI"
    if sub_sector == "Fintech.WealthTech_EOP":
        return "RIA"
    if sub_sector == "Fintech.Account_Aggregator":
        return "AA"
    return None


def build_profile(index: int, rng: random.Random) -> dict:
    sector = list(SECTOR_PROFILES)[index % len(SECTOR_PROFILES)]
    config = SECTOR_CONFIG[sector]
    stage = choose_stage(rng, sector)
    team_size = pick_team_size(rng, stage)
    operations = pick_one(rng, config["operations"])
    data_sensitivity = pick_one(rng, config["data"])
    sub_sector = choose_sub_sector(rng, sector)
    customer_type = choose_customers(rng, sector)
    data_handled = choose_data_handled(rng, sector)
    regulatory = choose_regulatory(rng, sector)
    physical_assets = choose_physical_assets(rng, sector, operations)
    raw_hardware_split = choose_hardware_split(rng, sector)
    raw_climate_zone = choose_climate_zone(rng, sector)
    physical_risk = derive_physical_risk_inputs(physical_assets, raw_hardware_split, raw_climate_zone)

    has_investors = "Yes" if stage in {"Series A", "Series B+"} or chance(rng, 0.45) else "No"
    if stage == "Series B+" and chance(rng, 0.35):
        holdco_domicile = pick_one(rng, ["India", "SG", "DE", "Cayman"])
    else:
        holdco_domicile = pick_one(rng, ["India", "India", "India", "SG", "Flip_pending"])

    if has_investors == "Yes" and chance(rng, 0.20):
        investor_cn_hk_pct = round(rng.uniform(0.00, 0.45), 2)
    else:
        investor_cn_hk_pct = round(rng.uniform(0.00, 0.08), 2)

    export_eu_pct, export_us_pct, export_china_pct = choose_exports(rng, sector)

    profile = {
        "startup_name": build_name(index, rng),
        "sector": sector,
        "sub_sector": sub_sector,
        "funding_stage": stage,
        "team_size": team_size,
        "operations": operations,
        "data_sensitivity": data_sensitivity,
        "product_description": pick_one(rng, config["descriptions"]),
        "customer_type": customer_type,
        "data_handled": data_handled,
        "regulatory": regulatory,
        "physical_assets": physical_assets,
        "has_investors": has_investors,
        "biggest_fear": pick_one(rng, config["fears"]),
        "investor_cn_hk_pct": investor_cn_hk_pct,
        "cumulative_fundraising_inr_cr": choose_fundraising(rng, stage),
        "holdco_domicile": holdco_domicile,
        "founder_concentration_index": round(rng.uniform(0.25, 0.80), 2),
        "dpiit_recognition": stage in {"Pre-seed", "Seed", "Series A"} and chance(rng, 0.65),
        "rbi_registration": choose_rbi_registration(sector, sub_sector),
        "gig_headcount_pct": choose_gig_pct(rng, sector),
        "posh_ic_constituted": team_size >= 10 and chance(rng, 0.70),
        "state_footprint": pick_some(rng, STATE_FOOTPRINT, 1 if operations == "Digital-only" else 2, 2 if operations == "Digital-only" else 4),
        "cert_in_poc_designated": (data_sensitivity == "High" or sector in {"Fintech", "Healthtech", "HRtech"}) and chance(rng, 0.55),
        "sdf_probability": round(rng.uniform(0.35, 0.90), 2) if data_sensitivity == "High" else round(rng.uniform(0.10, 0.55), 2) if data_sensitivity == "Medium" else round(rng.uniform(0.00, 0.20), 2),
        "data_localisation_status": choose_data_localisation(rng, data_sensitivity),
        "ai_in_product": sector in {"Deeptech / AI / Robotics", "Legaltech", "HRtech", "SaaS / Enterprise Software"} or chance(rng, 0.25),
        "hardware_software_split": round(physical_risk[0], 2),
        "b2b_pct": choose_b2b_pct(rng, sector),
        "export_eu_pct": export_eu_pct,
        "export_us_pct": export_us_pct,
        "export_china_pct": export_china_pct,
        "chinese_supplier_pct_cogs": choose_supplier_china_pct(rng, sector),
        "listed_customer_brsr_dependency": sector in {"Cleantech / Climatetech", "D2C / Consumer Brands", "Deeptech / AI / Robotics", "Logistics / Mobility"} and chance(rng, 0.35),
        "facility_climate_risk_zone": physical_risk[1],
        "crypto_vda_flag": sector == "Crypto/VDA",
    }
    return profile


def generate_profiles() -> list[dict]:
    rng = random.Random(SEED)
    profiles = [build_profile(index, rng) for index in range(PROFILE_COUNT)]
    names = {profile["startup_name"] for profile in profiles}
    if len(names) != PROFILE_COUNT:
        raise ValueError("Synthetic startup names must be unique.")
    if any(profile["sub_sector"] == "Gaming.Real_Money" for profile in profiles):
        raise ValueError("Hard-decline Gaming.Real_Money profiles must not be generated.")
    if any(profile["sub_sector"] == "Healthtech.MedDevice_SaMD" for profile in profiles):
        raise ValueError("CDSCO referral-only SaMD profiles must not be generated.")
    return profiles


def run_deterministic_tests(profiles: list[dict]) -> dict:
    failures: list[dict] = []
    sector_counter: Counter[str] = Counter()
    stage_counter: Counter[str] = Counter()

    for profile in profiles:
        sector_counter[profile["sector"]] += 1
        stage_counter[profile["funding_stage"]] += 1

        try:
            analysis = analyze_profile(profile)
        except Exception as exc:  # pragma: no cover - explicit failure capture
            failures.append({"startup_name": profile["startup_name"], "reason": f"analyze_profile raised: {exc}"})
            continue

        scores = analysis["scores"]
        recommendations = analysis["recommendations"]
        rec_keys = [rec["key"] for rec in recommendations]
        excluded = set(SECTOR_EXCLUSIONS.get(profile["sector"], []))

        checks = {
            "score_count": len(scores) == 13,
            "score_range": all(0.0 <= value <= 100.0 for value in scores.values()),
            "min_recommendations": len(recommendations) >= 5,
            "employee_health_present": "employee_health" in rec_keys,
            "priority_labels_match": all(priority_label(rec["score"]) == rec["priority"] for rec in recommendations),
            "sector_exclusions_respected": not any(key in excluded for key in rec_keys),
            "funded_has_dno": profile["funding_stage"] not in {"Series A", "Series B+"} or "dno_liability" in rec_keys,
        }

        failed_checks = [name for name, passed in checks.items() if not passed]
        if failed_checks:
            failures.append(
                {
                    "startup_name": profile["startup_name"],
                    "sector": profile["sector"],
                    "funding_stage": profile["funding_stage"],
                    "failed_checks": failed_checks,
                }
            )

    return {
        "seed": SEED,
        "profile_count": len(profiles),
        "passed": len(failures) == 0,
        "failure_count": len(failures),
        "failures": failures,
        "sector_distribution": dict(sector_counter),
        "stage_distribution": dict(stage_counter),
    }


def main() -> None:
    FIXTURES_DIR.mkdir(exist_ok=True)
    profiles = generate_profiles()
    report = run_deterministic_tests(profiles)

    DATASET_PATH.write_text(json.dumps(profiles, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Generated {len(profiles)} startup profiles: {DATASET_PATH}")
    print(f"Wrote deterministic test report: {REPORT_PATH}")
    print(f"Passed: {report['passed']}")
    print(f"Failures: {report['failure_count']}")


if __name__ == "__main__":
    main()
