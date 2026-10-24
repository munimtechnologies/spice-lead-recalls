# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
"""Recompute every number published in docs/coumarin-tea-0.1.0-result.md.

Reads data/coumarin_tea_samples.csv (the sealed per-sample output of job coumarin-tea-v1, CFIA
2013-14 coumarin survey, Open Government Licence - Canada), data/coumarin-tea.csv (the published
per-cup exposure table) and, for the parse gate (G0), the 749-row data/coumarin_eu_limits_samples.csv
already published with coumarin-eu-limits 0.1.1. Uses only csv, math, statistics and unittest.
"""
import csv
import math
import os
import statistics
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TEA = os.path.join(HERE, "data", "coumarin_tea_samples.csv")
TABLE = os.path.join(HERE, "data", "coumarin-tea.csv")
EU = os.path.join(HERE, "data", "coumarin_eu_limits_samples.csv")

TDI_MG_PER_KG_BW = 0.1  # EFSA coumarin TDI, mg per kg body weight per day

# Pre-registered thresholds (docs/coumarin-tea-0.1.0-prereg.md), unchanged.
G0_N_ROWS = (740, 749)
G0_POOLED_MAX = (2200.0, 2800.0)
G0_TEA_MAX = (2300.0, 2500.0)
G0_TEA_DETECTED = (112, 115)
P1_A1_COUNT = 0
P2_A2_SHARE = (0.005, 0.12)
P3_C1_SHARE = (0.07, 0.40)
P4_C2_SHARE = (0.25, 0.70)

# Per-cup scenarios (fixed in the pre-registration): id -> (body weight kg, dry tea g/cup).
SCENARIOS = {"A1": (60.0, 2.0), "A2": (60.0, 4.0), "C1": (15.0, 2.0), "C2": (15.0, 4.0)}
# Flag column in the per-sample table for each scenario.
FLAG = {"A1": "over_tdi_a1", "A2": "over_tdi_a2", "C1": "over_tdi_c1", "C2": "over_tdi_c2"}
# % of day budget column for each scenario.
PCT = {"A1": "pct_budget_a1", "A2": "pct_budget_a2", "C1": "pct_budget_c1", "C2": "pct_budget_c2"}


def threshold_ppm(bw_kg, dry_g):
    # TDI (mg/kg bw/day) * bw (kg) = mg/day budget; / dry (kg/cup, transfer 1.0) = mg/kg in tea.
    return TDI_MG_PER_KG_BW * bw_kg / (dry_g / 1000.0)


def pct_budget(ppm, bw_kg, dry_g):
    return ppm / threshold_ppm(bw_kg, dry_g) * 100.0


def nearest_rank(sorted_vals, q):
    if not sorted_vals:
        return None
    return sorted_vals[max(1, math.ceil(q * len(sorted_vals))) - 1]


def load_tea():
    with open(TEA, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["ppm"] = float(r["coumarin_ppm"])
    return rows


def eu_measured():
    with open(EU, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return [float(r["coumarin_ppm"]) for r in rows if r["coumarin_ppm"].strip() != ""]


class TestTeaSamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_tea()
        cls.ppms = sorted(r["ppm"] for r in cls.rows)

    def test_counts(self):
        self.assertEqual(len(self.rows), 115)
        self.assertEqual(sum(1 for p in self.ppms if p > 0), 114)  # detected
        self.assertAlmostEqual(sum(1 for p in self.ppms if p > 0) / 115, 0.9913043, places=6)

    def test_distribution(self):
        self.assertAlmostEqual(min(self.ppms), 0.0)
        self.assertAlmostEqual(statistics.median(self.ppms), 240.0)
        self.assertAlmostEqual(statistics.mean(self.ppms), 495.6669565217391, places=6)
        self.assertAlmostEqual(nearest_rank(self.ppms, 0.9), 1420.0)
        self.assertAlmostEqual(max(self.ppms), 2430.0)

    def test_unit_census(self):
        self.assertEqual({r["unit"] for r in self.rows}, {"ug/g"})
        self.assertEqual(sum(1 for r in self.rows if r["unit"] == "ug/g"), 115)

    def test_pct_budget_columns_recompute(self):
        for r in self.rows:
            for sid, (bw, g) in SCENARIOS.items():
                self.assertAlmostEqual(
                    float(r[PCT[sid]]), pct_budget(r["ppm"], bw, g), places=1, msg=r
                )

    def test_over_tdi_flags_match(self):
        for r in self.rows:
            for sid, (bw, g) in SCENARIOS.items():
                want = "yes" if r["ppm"] > threshold_ppm(bw, g) else "no"
                self.assertEqual(r[FLAG[sid]], want, msg=(sid, r))


class TestExposureTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ppms = [r["ppm"] for r in load_tea()]
        with open(TABLE, newline="", encoding="utf-8") as fh:
            cls.table = {r["scenario"]: r for r in csv.DictReader(fh)}

    def test_every_row_recomputes(self):
        self.assertEqual(set(self.table), {"A1", "A2", "C1", "C2"})
        median = statistics.median(self.ppms)
        mx = max(self.ppms)
        n = len(self.ppms)
        for sid, t in self.table.items():
            bw, g = float(t["bw_kg"]), float(t["dry_g_per_cup"])
            self.assertEqual((bw, g), SCENARIOS[sid])
            self.assertAlmostEqual(float(t["transfer"]), 1.0)
            thr = threshold_ppm(bw, g)
            over = sum(1 for p in self.ppms if p > thr)
            with self.subTest(scenario=sid):
                self.assertAlmostEqual(float(t["threshold_ppm"]), thr, places=4)
                self.assertEqual(int(t["n"]), n)
                self.assertEqual(int(t["n_over_tdi"]), over)
                self.assertAlmostEqual(float(t["share_over_tdi"]), over / n, places=9)
                self.assertAlmostEqual(float(t["median_pct_budget"]), pct_budget(median, bw, g), places=3)
                self.assertAlmostEqual(float(t["max_pct_budget"]), pct_budget(mx, bw, g), places=3)

    def test_headline_counts(self):
        self.assertEqual(self.table["A1"]["n_over_tdi"], "0")
        self.assertEqual(self.table["A2"]["n_over_tdi"], "7")
        self.assertEqual(self.table["C1"]["n_over_tdi"], "33")
        self.assertEqual(self.table["C2"]["n_over_tdi"], "45")


class TestGradesHold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_tea()
        cls.ppms = sorted(r["ppm"] for r in cls.rows)

    def test_g0_gate(self):
        measured = eu_measured()
        self.assertTrue(G0_N_ROWS[0] <= len(measured) <= G0_N_ROWS[1])
        self.assertEqual(len(measured), 749)
        self.assertTrue(G0_POOLED_MAX[0] <= max(measured) <= G0_POOLED_MAX[1])
        self.assertEqual(max(measured), 2510.0)
        # Tea subset (the per-sample table is already the 115 "tea" rows).
        self.assertEqual(len(self.rows), 115)
        self.assertTrue(G0_TEA_MAX[0] <= max(self.ppms) <= G0_TEA_MAX[1])
        detected = sum(1 for p in self.ppms if p > 0)
        self.assertTrue(G0_TEA_DETECTED[0] <= detected <= G0_TEA_DETECTED[1])
        self.assertEqual({r["unit"] for r in self.rows}, {"ug/g"})

    def test_p1_primary_met(self):
        count = sum(1 for p in self.ppms if p > threshold_ppm(*SCENARIOS["A1"]))
        self.assertEqual(count, P1_A1_COUNT)

    def test_p2_met(self):
        share = sum(1 for p in self.ppms if p > threshold_ppm(*SCENARIOS["A2"])) / 115
        self.assertTrue(P2_A2_SHARE[0] <= share <= P2_A2_SHARE[1])

    def test_p3_met(self):
        share = sum(1 for p in self.ppms if p > threshold_ppm(*SCENARIOS["C1"])) / 115
        self.assertTrue(P3_C1_SHARE[0] <= share <= P3_C1_SHARE[1])

    def test_p4_met(self):
        share = sum(1 for p in self.ppms if p > threshold_ppm(*SCENARIOS["C2"])) / 115
        self.assertTrue(P4_C2_SHARE[0] <= share <= P4_C2_SHARE[1])


if __name__ == "__main__":
    unittest.main()
