import sys, io, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from risk_engine import (
    SECTOR_PROFILES,
    compute_risk_scores,
    recommend_products,
    priority_label,
    SECTOR_OVERRIDES,
    SECTOR_EXCLUSIONS,
)

random.seed(42)
SECTORS = list(SECTOR_PROFILES.keys())
SECTOR_WEIGHTS = [0.18, 0.14, 0.10, 0.10, 0.09, 0.08, 0.07, 0.06, 0.06, 0.04, 0.04, 0.02, 0.02]
STAGES         = ["Pre-seed", "Seed", "Series A", "Series B+"]
STAGE_WEIGHTS  = [0.25, 0.40, 0.22, 0.13]
OPERATIONS     = ["Digital-only", "Physical-only", "Hybrid"]
OPS_BY_SECTOR  = {
    "SaaS / Enterprise Software":  [0.90, 0.01, 0.09],
    "Fintech":                     [0.75, 0.02, 0.23],
    "Healthtech":                  [0.40, 0.15, 0.45],
    "D2C / Consumer Brands":       [0.10, 0.30, 0.60],
    "Deeptech / AI / Robotics":    [0.30, 0.20, 0.50],
    "Edtech":                      [0.70, 0.05, 0.25],
    "Agritech":                    [0.15, 0.35, 0.50],
    "Cleantech / Climatetech":     [0.10, 0.40, 0.50],
    "Logistics / Mobility":        [0.15, 0.45, 0.40],
    "Legaltech":                   [0.75, 0.02, 0.23],
    "HRtech":                      [0.80, 0.01, 0.19],
    "Gaming / Media / Content":    [0.85, 0.02, 0.13],
    "Foodtech / Cloud Kitchen":    [0.10, 0.50, 0.40],
}
DATA_SENSITIVITY = ["Low", "Medium", "High"]
DATA_BY_SECTOR   = {
    "SaaS / Enterprise Software":  [0.10, 0.45, 0.45],
    "Fintech":                     [0.02, 0.08, 0.90],
    "Healthtech":                  [0.02, 0.08, 0.90],
    "D2C / Consumer Brands":       [0.20, 0.60, 0.20],
    "Deeptech / AI / Robotics":    [0.15, 0.50, 0.35],
    "Edtech":                      [0.20, 0.55, 0.25],
    "Agritech":                    [0.30, 0.55, 0.15],
    "Cleantech / Climatetech":     [0.30, 0.50, 0.20],
    "Logistics / Mobility":        [0.20, 0.55, 0.25],
    "Legaltech":                   [0.05, 0.30, 0.65],
    "HRtech":                      [0.05, 0.25, 0.70],
    "Gaming / Media / Content":    [0.25, 0.55, 0.20],
    "Foodtech / Cloud Kitchen":    [0.25, 0.55, 0.20],
}
TEAM_BY_STAGE = {
    "Pre-seed": (2, 8), "Seed": (5, 30),
    "Series A": (20, 120), "Series B+": (80, 500),
}

check_names = [
    "min_five_products", "overrides_respected", "exclusions_respected",
    "priority_labels_correct", "cyber_monotone", "property_ops_consistent",
    "dno_funded_stage", "health_always_present",
]
totals  = {c: 0 for c in check_names}
passing = {c: 0 for c in check_names}

for i in range(100):
    sector = random.choices(SECTORS, weights=SECTOR_WEIGHTS)[0]
    stage  = random.choices(STAGES, weights=STAGE_WEIGHTS)[0]
    ops    = random.choices(OPERATIONS, weights=OPS_BY_SECTOR[sector])[0]
    data   = random.choices(DATA_SENSITIVITY, weights=DATA_BY_SECTOR[sector])[0]
    lo, hi = TEAM_BY_STAGE[stage]
    team   = random.randint(lo, hi)
    scores = compute_risk_scores(sector, stage, team, ops, data)
    recs   = recommend_products(scores, sector, team, stage)
    rec_keys = [r["key"] for r in recs]

    checks = {}
    checks["min_five_products"] = len(recs) >= 5
    overrides = SECTOR_OVERRIDES.get(sector, [])
    checks["overrides_respected"] = all(k in rec_keys for k in overrides)
    excluded = SECTOR_EXCLUSIONS.get(sector, [])
    checks["exclusions_respected"] = not any(k in rec_keys for k in excluded)
    checks["priority_labels_correct"] = all(priority_label(r["score"]) == r["priority"] for r in recs)
    sl = compute_risk_scores(sector, stage, team, ops, "Low")
    sh = compute_risk_scores(sector, stage, team, ops, "High")
    checks["cyber_monotone"] = sh["Cyber Risk"] >= sl["Cyber Risk"]
    sp = compute_risk_scores(sector, stage, team, "Physical-only", data)
    sd = compute_risk_scores(sector, stage, team, "Digital-only",  data)
    checks["property_ops_consistent"] = sp["Property Risk"] >= sd["Property Risk"]
    if stage in ("Series A", "Series B+"):
        checks["dno_funded_stage"] = "dno_liability" in rec_keys
    else:
        checks["dno_funded_stage"] = True
    checks["health_always_present"] = "employee_health" in rec_keys

    for c in check_names:
        if c in checks:
            totals[c] += 1
            if checks[c]: passing[c] += 1

print("=" * 65)
print("  STARTUP RISK APP -- ACCURACY REPORT (AFTER FIXES)")
print("=" * 65)
overall_pass = overall_total = 0
for c in check_names:
    t = totals[c]; p = passing[c]
    pct = (p / t * 100) if t else 0
    status = "[PASS]" if pct == 100 else ("[WARN]" if pct >= 80 else "[FAIL]")
    print(f"  {status}  {c.replace('_',' ').title():<38} {p:>3}/{t:<3}  ({pct:.1f}%)")
    overall_pass += p; overall_total += t
print("-" * 65)
print(f"  OVERALL SCORE:  {overall_pass}/{overall_total}  ->  {overall_pass/overall_total*100:.1f}%")
print("=" * 65)

# =============================================================================
# DETERMINISTIC BOUNDARY TESTS (Fix 9)
# =============================================================================
BOUNDARY_CASES = [
    ("SaaS / Enterprise Software", "Pre-seed",  1,   "Digital-only",  "Low",    "min team, digital"),
    ("SaaS / Enterprise Software", "Series B+", 500, "Hybrid",        "High",   "max team, high data"),
    ("Fintech",                    "Series A",  10,  "Digital-only",  "High",   "team=10 boundary"),
    ("Fintech",                    "Series A",  11,  "Digital-only",  "High",   "just above team=10"),
    ("Healthtech",                 "Seed",      25,  "Hybrid",        "High",   "team=25 boundary"),
    ("Healthtech",                 "Seed",      26,  "Hybrid",        "High",   "just above team=25"),
    ("Logistics / Mobility",       "Series B+", 150, "Physical-only", "Medium", "large physical ops"),
    ("D2C / Consumer Brands",      "Seed",      8,   "Hybrid",        "Medium", "D2C small team"),
    ("Deeptech / AI / Robotics",   "Series A",  45,  "Hybrid",        "High",   "deeptech mid-stage"),
    ("Agritech",                   "Seed",      12,  "Physical-only", "Low",    "agritech physical"),
    ("Foodtech / Cloud Kitchen",   "Seed",      30,  "Physical-only", "Medium", "foodtech kitchen"),
    ("Gaming / Media / Content",   "Pre-seed",  5,   "Digital-only",  "Medium", "gaming tiny team"),
]

print("\n" + "=" * 65)
print("  BOUNDARY TESTS")
print("=" * 65)
boundary_pass = boundary_total = 0
for sector, stage, team, ops, data, desc in BOUNDARY_CASES:
    scores   = compute_risk_scores(sector, stage, team, ops, data)
    recs     = recommend_products(scores, sector, team, stage)
    rec_keys = [r["key"] for r in recs]
    ok = True
    fail_reason = ""
    if len(recs) < 5:
        ok = False; fail_reason = f"only {len(recs)} products"
    elif any(k in rec_keys for k in SECTOR_EXCLUSIONS.get(sector, [])):
        ok = False; fail_reason = "excluded product surfaced"
    elif any(priority_label(r["score"]) != r["priority"] for r in recs):
        ok = False; fail_reason = "priority label mismatch"
    elif "employee_health" not in rec_keys:
        ok = False; fail_reason = "employee_health missing"
    status = "[PASS]" if ok else f"[FAIL: {fail_reason}]"
    boundary_total += 1
    if ok: boundary_pass += 1
    print(f"  {status:<36} {desc}")
print(f"\n  Boundary score: {boundary_pass}/{boundary_total}")
print("=" * 65)
