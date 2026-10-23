# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
"""Recompute every number published in docs/coumarin-infant-0.1.0-result.md.

Reads data/coumarin_infant_samples.csv (the sealed per-sample output of job coumarin-infant-v1,
CFIA 2013-14 coumarin survey, Open Government Licence - Canada), data/coumarin-infant.csv (the
published exposure table) and, for the children's-cereal comparison (P3) and the parse gate (G0),
the 749-row data/coumarin_eu_limits_samples.csv already published with coumarin-eu-limits 0.1.1.
Uses only csv, math, statistics and unittest.
"""
import csv
import math
import os
import statistics
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
INFANT = os.path.join(HERE, "data", "coumarin_infant_samples.csv")
TABLE = os.path.join(HERE, "data", "coumarin-infant.csv")
EU = os.path.join(HERE, "data", "coumarin_eu_limits_samples.csv")

TDI_MG_PER_KG_BW = 0.1  # EFSA coumarin TDI, mg per kg body weight per day

# Pre-registered thresholds (docs/coumarin-infant-0.1.0-prereg.md), unchanged.
G0_N_ROWS = (740, 749)
G0_MAX_PPM = (2200.0, 2800.0)
P1_S1_SHARE = (0.00, 0.10)
P2_S2_SHARE = (0.02, 0.30)
P4_DETECT_SHARE = (0.80, 1.00)
EU_CEREAL_LIMIT = 20.0  # EU breakfast-cereal row, reference only


def threshold_ppm(bw_kg, dry_g):
    # TDI (mg/kg bw/day) * bw (kg) = mg/day budget; / dry (kg/day) = mg/kg in cereal.
    return TDI_MG_PER_KG_BW * bw_kg / (dry_g / 1000.0)


def pct_tdi(ppm, bw_kg, dry_g):
    return ppm / threshold_ppm(bw_kg, dry_g) * 100.0


def nearest_rank(sorted_vals, q):
    if not sorted_vals:
        return None
    return sorted_vals[max(1, math.ceil(q * len(sorted_vals))) - 1]


def load_infant():
    with open(INFANT, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["ppm"] = float(r["coumarin_ppm"])
    return rows


def eu_measured():
    with open(EU, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return [(r, float(r["coumarin_ppm"])) for r in rows if r["coumarin_ppm"].strip() != ""]


def children_cereal():
    vals = [p for r, p in eu_measured()
            if r["subcat"] == "cereal" and r["product"] == "Cereal - Children"]
    return len(vals), statistics.median(vals)


class TestInfantSamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_infant()
        cls.ppms = sorted(r["ppm"] for r in cls.rows)

    def test_counts(self):
        self.assertEqual(len(self.rows), 52)
        self.assertEqual(sum(1 for p in self.ppms if p > 0), 51)   # detected
        self.assertAlmostEqual(sum(1 for p in self.ppms if p > 0) / 52, 0.9807692, places=6)

    def test_distribution(self):
        self.assertAlmostEqual(statistics.median(self.ppms), 1.25)
        self.assertAlmostEqual(nearest_rank(self.ppms, 0.9), 2.4)
        self.assertAlmostEqual(max(self.ppms), 18.3)

    def test_over_eu_cereal_20(self):
        self.assertEqual(sum(1 for p in self.ppms if p > EU_CEREAL_LIMIT), 0)

    def test_unit_census(self):
        self.assertEqual({r["unit"] for r in self.rows}, {"ug/g"})
        self.assertEqual(sum(1 for r in self.rows if r["unit"] == "ug/g"), 52)

    def test_over_tdi_flags_match(self):
        for r in self.rows:
            s1 = "yes" if r["ppm"] > threshold_ppm(8.0, 30.0) else "no"
            s2 = "yes" if r["ppm"] > threshold_ppm(8.0, 60.0) else "no"
            self.assertEqual(r["over_tdi_s1"], s1, r)
            self.assertEqual(r["over_tdi_s2"], s2, r)


class TestExposureTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ppms = [r["ppm"] for r in load_infant()]
        with open(TABLE, newline="", encoding="utf-8") as fh:
            cls.table = {r["scenario"]: r for r in csv.DictReader(fh)}

    def test_every_row_recomputes(self):
        self.assertEqual(set(self.table), {"S1", "S2", "S3"})
        median = statistics.median(self.ppms)
        mx = max(self.ppms)
        for sid, t in self.table.items():
            bw, g = float(t["bw_kg"]), float(t["dry_g_per_day"])
            thr = threshold_ppm(bw, g)
            over = sum(1 for p in self.ppms if p > thr)
            with self.subTest(scenario=sid):
                self.assertAlmostEqual(float(t["threshold_ppm"]), thr, places=4)
                self.assertEqual(int(t["n"]), len(self.ppms))
                self.assertEqual(int(t["n_over_tdi"]), over)
                self.assertAlmostEqual(float(t["share_over_tdi"]), over / 52, places=5)
                self.assertAlmostEqual(float(t["median_pct_tdi"]), pct_tdi(median, bw, g), places=3)
                self.assertAlmostEqual(float(t["max_pct_tdi"]), pct_tdi(mx, bw, g), places=3)

    def test_headline_counts(self):
        self.assertEqual(self.table["S1"]["n_over_tdi"], "0")
        self.assertEqual(self.table["S2"]["n_over_tdi"], "2")
        self.assertEqual(self.table["S3"]["n_over_tdi"], "0")


class TestGradesHold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ppms = sorted(r["ppm"] for r in load_infant())

    def test_g0_gate(self):
        measured = eu_measured()
        self.assertTrue(G0_N_ROWS[0] <= len(measured) <= G0_N_ROWS[1])
        self.assertEqual(len(measured), 749)
        self.assertEqual(max(p for _, p in measured), 2510.0)
        self.assertTrue(G0_MAX_PPM[0] <= max(p for _, p in measured) <= G0_MAX_PPM[1])

    def test_p1_primary_met(self):
        share = sum(1 for p in self.ppms if p > threshold_ppm(8.0, 30.0)) / 52
        self.assertEqual(share, 0.0)
        self.assertTrue(P1_S1_SHARE[0] <= share <= P1_S1_SHARE[1])

    def test_p2_met(self):
        share = sum(1 for p in self.ppms if p > threshold_ppm(8.0, 60.0)) / 52
        self.assertTrue(P2_S2_SHARE[0] <= share <= P2_S2_SHARE[1])

    def test_p3_direction_met(self):
        n_child, child_median = children_cereal()
        self.assertEqual(n_child, 65)
        self.assertAlmostEqual(child_median, 3.4)
        self.assertLess(statistics.median(self.ppms), child_median)

    def test_p4_detected_met(self):
        share = sum(1 for p in self.ppms if p > 0) / 52
        self.assertTrue(P4_DETECT_SHARE[0] <= share <= P4_DETECT_SHARE[1])


if __name__ == "__main__":
    unittest.main()
