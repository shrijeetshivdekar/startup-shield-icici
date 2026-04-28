import json
import unittest
from pathlib import Path

from risk_engine import SECTOR_PROFILES, StartupInput, compute_risk_scores


class RiskEngineSectorExamplesTest(unittest.TestCase):
    def sample_input(self, **overrides):
        data = {
            "sector": "Fintech",
            "funding_stage": "Seed",
            "team_size": 40,
            "operations": "Hybrid",
            "data_sensitivity": "Medium",
            "posh_ic_constituted": False,
            "cert_in_poc_designated": False,
            "data_localisation_status": "Unknown",
        }
        data.update(overrides)
        return StartupInput(**data)

    def test_one_example_startup_per_sector_scores_cleanly(self):
        sectors = list(SECTOR_PROFILES)
        self.assertEqual(14, len(sectors))

        for sector in sectors:
            with self.subTest(sector=sector):
                inp = StartupInput(
                    sector=sector,
                    funding_stage="Series A",
                    team_size=42,
                    operations="Hybrid",
                    data_sensitivity="High",
                    ai_tier="Applied",
                    b2b_pct=0.6,
                    sdf_probability=0.4,
                    state_footprint=["Karnataka"],
                    gig_headcount_pct=0.2,
                    hs_basket="steel",
                    export_eu_pct=0.15,
                    top1000_listed_customer_rev_pct=0.3,
                    crypto_vda_flag=(sector == "Crypto/VDA"),
                )
                scores = compute_risk_scores(inp)

                self.assertEqual(13, len(scores))
                self.assertTrue(all(0 <= score <= 100 for score in scores.values()))
                self.assertIn("Cyber Technical Risk", scores)
                self.assertIn("Regulatory Compliance Risk", scores)

    def test_crypto_flag_routes_to_crypto_vda_vector(self):
        flagged = StartupInput(
            sector="Fintech",
            funding_stage="Seed",
            team_size=20,
            operations="Digital-only",
            data_sensitivity="High",
            crypto_vda_flag=True,
        )
        direct = StartupInput(
            sector="Crypto/VDA",
            funding_stage="Seed",
            team_size=20,
            operations="Digital-only",
            data_sensitivity="High",
        )

        self.assertEqual(compute_risk_scores(direct), compute_risk_scores(flagged))

    def test_real_money_gaming_subsector_amplifies_scores(self):
        base = StartupInput(
            sector="Gaming / Media / Content",
            funding_stage="Seed",
            team_size=12,
            operations="Digital-only",
            data_sensitivity="Medium",
        )
        rmg = StartupInput(
            sector="Gaming / Media / Content",
            sub_sector="RMG",
            funding_stage="Seed",
            team_size=12,
            operations="Digital-only",
            data_sensitivity="Medium",
        )

        self.assertGreater(
            compute_risk_scores(rmg)["Policy Velocity Risk"],
            compute_risk_scores(base)["Policy Velocity Risk"],
        )

    def test_new_stage_aliases_and_high_stacked_are_accepted(self):
        inp = StartupInput(
            sector="Healthtech",
            funding_stage="Pre_IPO_or_Listed",
            team_size=220,
            operations="Hybrid",
            data_sensitivity="High_stacked",
            founder_controversy_flag=True,
            facility_in_ndma_flood_tier1=True,
        )
        scores = compute_risk_scores(inp)

        self.assertGreaterEqual(scores["Liability Risk"], 90)
        self.assertGreaterEqual(scores["Property Risk"], 90)

    def test_new_adjusters_default_vs_filled_move_expected_categories(self):
        self.assertGreater(
            compute_risk_scores(self.sample_input(holdco_domicile="Cayman_BVI"))["Geopolitical Risk"],
            compute_risk_scores(self.sample_input(holdco_domicile="India_or_GIFT"))["Geopolitical Risk"],
        )
        self.assertLess(
            compute_risk_scores(self.sample_input(posh_ic_constituted=True))["Liability Risk"],
            compute_risk_scores(self.sample_input(posh_ic_constituted=False))["Liability Risk"],
        )
        self.assertLess(
            compute_risk_scores(self.sample_input(cert_in_poc_designated=True))["Cyber Technical Risk"],
            compute_risk_scores(self.sample_input(cert_in_poc_designated=False))["Cyber Technical Risk"],
        )
        self.assertLess(
            compute_risk_scores(self.sample_input(institutional_investors_on_board=True))["Governance & Fraud Risk"],
            compute_risk_scores(self.sample_input(institutional_investors_on_board=False))["Governance & Fraud Risk"],
        )
        self.assertGreater(
            compute_risk_scores(self.sample_input(data_localisation_status="Offshore"))["Data Privacy Risk"],
            compute_risk_scores(self.sample_input(data_localisation_status="Full_onshore"))["Data Privacy Risk"],
        )
        self.assertLess(
            compute_risk_scores(self.sample_input(dpiit_recognition=True))["IP Infringement Risk"],
            compute_risk_scores(self.sample_input(dpiit_recognition=False))["IP Infringement Risk"],
        )
        self.assertGreater(
            compute_risk_scores(self.sample_input(export_us_pct=0.8))["Geopolitical Risk"],
            compute_risk_scores(self.sample_input(export_us_pct=0.0))["Geopolitical Risk"],
        )
        self.assertGreater(
            compute_risk_scores(self.sample_input(ai_tier="Foundational"))["Policy Velocity Risk"],
            compute_risk_scores(self.sample_input(ai_tier="None"))["Policy Velocity Risk"],
        )
        self.assertGreater(
            compute_risk_scores(self.sample_input(top1000_listed_customer_rev_pct=0.9))["ESG & Climate Risk"],
            compute_risk_scores(self.sample_input(top1000_listed_customer_rev_pct=0.0))["ESG & Climate Risk"],
        )

    def test_cumulative_adjuster_cap_stays_under_sector_vector_ceiling(self):
        inp = self.sample_input(
            sector="Logistics / Mobility",
            funding_stage="Pre-IPO / Listed",
            team_size=500,
            operations="Physical-only",
            data_sensitivity="High_stacked",
            posh_ic_constituted=False,
            cert_in_poc_designated=False,
            holdco_domicile="Land_border_BO_>10%",
            data_localisation_status="Offshore",
            ai_tier="Foundational",
            investor_cn_hk_pct=0.9,
            chinese_supplier_pct_cogs=0.9,
            top1000_listed_customer_rev_pct=1.0,
            facility_climate_risk_zone="Extreme",
            facility_in_ndma_flood_tier1=True,
            gig_headcount_pct=1.0,
            state_footprint=["Karnataka"],
            b2b_pct=1.0,
        )
        scores = compute_risk_scores(inp)
        emitted_keys = {
            "Cyber Technical Risk": "cyber_technical",
            "Data Privacy Risk": "data_privacy_regulatory",
            "Liability Risk": "liability",
            "IP Infringement Risk": "ip_infringement",
            "Key Person Risk": "key_person",
            "Governance & Fraud Risk": "governance_fraud",
            "Property Risk": "property",
            "Regulatory Compliance Risk": "compliance",
            "ESG & Climate Risk": "esg_climate",
            "Geopolitical Risk": "geopolitical",
            "Gig & Labour Risk": "gig_labour",
            "Policy Velocity Risk": "policy_velocity",
            "Reputation Risk": "reputation",
        }
        raw_score_sum = sum(scores.values()) / 7.5
        ceiling = sum(SECTOR_PROFILES[inp.sector][k] * 3.5 for k in emitted_keys.values())

        self.assertLessEqual(raw_score_sum, ceiling)

    def test_sector_stage_ai_tier_matrix_smoke(self):
        stages = ["Pre-seed", "Seed", "Series A", "Series B+", "Series C", "Pre-IPO / Listed"]
        tiers = ["None", "Embedded", "Applied", "Foundational"]
        for sector in SECTOR_PROFILES:
            for stage in stages:
                for tier in tiers:
                    with self.subTest(sector=sector, stage=stage, tier=tier):
                        scores = compute_risk_scores(
                            self.sample_input(sector=sector, funding_stage=stage, ai_tier=tier)
                        )
                        self.assertEqual(13, len(scores))

    def test_existing_fixture_profiles_remain_analyzable(self):
        path = Path(__file__).resolve().parent / "fixtures" / "synthetic_startups_200.json"
        if not path.exists():
            self.skipTest("deterministic fixture is not present")

        profiles = json.loads(path.read_text(encoding="utf-8"))[:20]
        self.assertTrue(profiles)
        for profile in profiles:
            with self.subTest(profile=profile["startup_name"]):
                inp = StartupInput(
                    sector=profile["sector"],
                    funding_stage=profile["funding_stage"],
                    team_size=profile["team_size"],
                    operations=profile["operations"],
                    data_sensitivity=profile["data_sensitivity"],
                    sub_sector=profile.get("sub_sector"),
                    institutional_investors_on_board=profile.get("has_investors") == "Yes",
                    holdco_domicile=profile.get("holdco_domicile", "India_or_GIFT"),
                    posh_ic_constituted=profile.get("posh_ic_constituted"),
                    cert_in_poc_designated=profile.get("cert_in_poc_designated"),
                    data_localisation_status=profile.get("data_localisation_status", "Unknown"),
                    dpiit_recognition=profile.get("dpiit_recognition", False),
                    export_us_pct=profile.get("export_us_pct", 0.0),
                    ai_tier=profile.get("ai_tier", "Applied" if profile.get("ai_in_product") else "None"),
                    listed_customer_brsr_dependency=profile.get("listed_customer_brsr_dependency", False),
                    top1000_listed_customer_rev_pct=profile.get("top1000_listed_customer_rev_pct", 0.0),
                    crypto_vda_flag=profile.get("crypto_vda_flag", False),
                )
                scores = compute_risk_scores(inp)
                self.assertTrue(all(0 <= score <= 100 for score in scores.values()))


if __name__ == "__main__":
    unittest.main()
