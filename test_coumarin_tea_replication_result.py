# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
"""Recompute every number published in docs/coumarin-tea-replication-0.1.1-result.md.

Reads data/coumarin_tea_replication_samples.csv (the sealed per-sample output of job
coumarin-cfia-audit-v1: all 622 "Tea - *" rows of CFIA's 2013-14, 2014-15 and 2015-16 coumarin
surveys, Open Government Licence - Canada), data/coumarin_tea_replication_by_type.csv and, for the
measured-row counts in the parse gate (G0), the grand-total rows of data/coumarin_cfia_table_audit.csv.
Uses only csv, math, statistics and unittest.
"""
import csv
import math
import os
import statistics
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.join(HERE, "data", "coumarin_tea_replication_samples.csv")
BY_TYPE = os.path.join(HERE, "data", "coumarin_tea_replication_by_type.csv")
AUDIT = os.path.join(HERE, "data", "coumarin_cfia_table_audit.csv")

TDI_MG_PER_KG_BW = 0.1  # EFSA coumarin TDI, mg per kg body weight per day
SURVEYS = ("2013-14", "2014-15", "2015-16")
LATER = ("2014-15", "2015-16")
TEA_TYPES = ("Tea - Black", "Tea - Green", "Tea - Herbal", "Tea - Oolong", "Tea - White",
             "Tea - Other")
HERBAL = "Tea - Herbal"

# Per-cup scenarios (fixed in coumarin-tea 0.1.0): id -> (body weight kg, dry tea g/cup).
SCENARIOS = {"A1": (60.0, 2.0), "A2": (60.0, 4.0), "C1": (15.0, 2.0), "C2": (15.0, 4.0)}

# Gate G0 as registered in 0.1.0, with the one 0.1.1 change: the 2014-15 printed average is
# compared with the mean of all teas. "mean" = (which mean, bounds).
GATE = {
    "2014-15": {
        "n_rows": (730, 739), "n_tea": 210,
        "types": {"Tea - Black": 77, "Tea - Green": 30, "Tea - Herbal": 60, "Tea - Oolong": 7,
                  "Tea - White": 15, "Tea - Other": 21},
        "tea_max": (1910.0, 1930.0), "detected": (178, 178), "mean": ("all", (285.0, 320.0)),
    },
    "2015-16": {
        "n_rows": (740, 747), "n_tea": 297,
        "types": {"Tea - Black": 81, "Tea - Green": 31, "Tea - Herbal": 86, "Tea - Oolong": 32,
                  "Tea - White": 42, "Tea - Other": 25},
        "tea_max": (2220.0, 2240.0), "detected": (245, 245),
        "mean": ("detected", (420.0, 465.0)),
    },
}
REF_1314 = {"n": 115, "A1": 0, "A2": 7, "C1": 33, "C2": 45}

# Pre-registered thresholds (docs/coumarin-tea-replication-0.1.0-prereg.md), unchanged.
P3_C1_1415 = (0.04, 0.22)
P4_C1_1516 = (0.10, 0.32)
P5_C2_1415 = (0.12, 0.40)
P6_C2_1516 = (0.18, 0.45)
P7_A2_1415_N = (1, 12)
P8_A2_1516_N = (2, 30)

# Published figures: survey -> (n, detected, median, mean, mean of detected, p90, max,
# over A1, A2, C1, C2).
PUBLISHED = {
    "2013-14": (115, 114, 240.0, 495.6669565, 500.0149123, 1420.0, 2430.0, 0, 7, 33, 45),
    "2014-15": (210, 178, 124.0, 301.9380952, 356.2191011, 944.0, 1920.0, 0, 5, 28, 54),
    "2015-16": (297, 245, 191.0, 364.3013468, 441.6224490, 1180.0, 2230.0, 0, 14, 41, 97),
    "later two": (507, 423, 172.0, 338.4704142, 405.6843972, 1030.0, 2230.0, 0, 19, 69, 151),
    "all three": (622, 537, 180.5, 367.5340836, 425.7098696, 1130.0, 2430.0, 0, 26, 102, 196),
}


def threshold_ppm(bw_kg, dry_g):
    # TDI (mg/kg bw/day) * bw (kg) = mg/day budget; / dry (kg/cup, transfer 1.0) = mg/kg in tea.
    return TDI_MG_PER_KG_BW * bw_kg / (dry_g / 1000.0)


def pct_budget(ppm, bw_kg, dry_g):
    return ppm / threshold_ppm(bw_kg, dry_g) * 100.0


def nearest_rank(sorted_vals, q):
    return sorted_vals[max(1, math.ceil(q * len(sorted_vals))) - 1]


def over(ppms, sid):
    return sum(1 for p in ppms if p > threshold_ppm(*SCENARIOS[sid]))


def load():
    with open(SAMPLES, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["ppm"] = float(r["coumarin_ppm"])
    return rows


def select(rows, surveys, tea_type=None):
    return sorted(r["ppm"] for r in rows if r["survey"] in surveys
                  and (tea_type is None or r["tea_type"] == tea_type))


def grand_totals():
    with open(AUDIT, newline="", encoding="utf-8") as fh:
        return {r["survey"]: int(r["n"]) for r in csv.DictReader(fh) if r["row"] == "Grand total"}


GROUPS = {"2013-14": ("2013-14",), "2014-15": ("2014-15",), "2015-16": ("2015-16",),
          "later two": LATER, "all three": SURVEYS}


class TestSamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load()

    def test_rows_and_units(self):
        self.assertEqual(len(self.rows), 622)
        self.assertEqual({r["unit"] for r in self.rows}, {"ug/g"})
        self.assertEqual({r["survey"] for r in self.rows}, set(SURVEYS))
        self.assertTrue({r["tea_type"] for r in self.rows} <= set(TEA_TYPES))

    def test_pct_budget_columns_recompute(self):
        for r in self.rows:
            for sid, (bw, g) in SCENARIOS.items():
                self.assertAlmostEqual(float(r["pct_budget_" + sid.lower()]),
                                       pct_budget(r["ppm"], bw, g), places=1, msg=r)

    def test_over_tdi_flags_match(self):
        for r in self.rows:
            for sid in SCENARIOS:
                want = "yes" if r["ppm"] > threshold_ppm(*SCENARIOS[sid]) else "no"
                self.assertEqual(r["over_tdi_" + sid.lower()], want, msg=(sid, r))

    def test_published_distributions_and_counts(self):
        for name, surveys in GROUPS.items():
            n, det, med, mean, mean_det, p90, mx, a1, a2, c1, c2 = PUBLISHED[name]
            ps = select(self.rows, surveys)
            with self.subTest(group=name):
                self.assertEqual(len(ps), n)
                detected = [p for p in ps if p > 0]
                self.assertEqual(len(detected), det)
                self.assertAlmostEqual(min(ps), 0.0)
                self.assertAlmostEqual(statistics.median(ps), med)
                self.assertAlmostEqual(statistics.fmean(ps), mean, places=5)
                self.assertAlmostEqual(statistics.fmean(detected), mean_det, places=5)
                self.assertAlmostEqual(nearest_rank(ps, 0.9), p90)
                self.assertAlmostEqual(max(ps), mx)
                self.assertEqual([over(ps, s) for s in ("A1", "A2", "C1", "C2")],
                                 [a1, a2, c1, c2])

    def test_reproduction_2013_14(self):
        ps = select(self.rows, ("2013-14",))
        got = {"n": len(ps)}
        got.update({s: over(ps, s) for s in SCENARIOS})
        self.assertEqual(got, REF_1314)

    def test_headline_percentages(self):
        # Highest standard adult cup, % of the adult day budget, per survey.
        for survey, want in (("2013-14", 81.0), ("2014-15", 64.0), ("2015-16", 74.333)):
            ps = select(self.rows, (survey,))
            self.assertAlmostEqual(pct_budget(max(ps), *SCENARIOS["A1"]), want, places=2)
        allp = select(self.rows, SURVEYS)
        self.assertAlmostEqual(pct_budget(statistics.median(allp), *SCENARIOS["A1"]), 6.0167,
                               places=3)
        self.assertEqual(round(28 / 210, 3), 0.133)
        self.assertEqual(round(41 / 297, 3), 0.138)
        self.assertEqual(round(33 / 115, 3), 0.287)
        self.assertEqual(round(over(allp, "A2") / 622 * 100, 1), 4.2)
        self.assertEqual(round(over(allp, "C1") / 622 * 100, 1), 16.4)
        self.assertEqual(round(over(allp, "C2") / 622 * 100, 1), 31.5)

    def test_herbal_carries_the_exceedances(self):
        herbal = [r["ppm"] for r in self.rows if r["tea_type"] == HERBAL]
        other = [r["ppm"] for r in self.rows if r["tea_type"] != HERBAL]
        self.assertEqual((len(herbal), len(other)), (218, 404))
        self.assertEqual(over(herbal, "C1"), 90)
        self.assertEqual(over(other, "C1"), 12)
        self.assertEqual(over(herbal, "A2"), 24)
        self.assertEqual(over(other, "A2"), 2)
        self.assertEqual(round(90 / 218 * 100, 1), 41.3)
        self.assertEqual(round(12 / 404 * 100, 1), 3.0)
        self.assertEqual(round(90 / 102 * 100), 88)
        # The twelve non-herbal child standard-cup exceedances, by survey and type.
        thr = threshold_ppm(*SCENARIOS["C1"])
        found = {}
        for r in self.rows:
            if r["tea_type"] != HERBAL and r["ppm"] > thr:
                key = (r["survey"], r["tea_type"])
                found[key] = found.get(key, 0) + 1
        self.assertEqual(found, {("2014-15", "Tea - Black"): 4, ("2014-15", "Tea - Other"): 1,
                                 ("2015-16", "Tea - Black"): 3, ("2015-16", "Tea - Oolong"): 2,
                                 ("2015-16", "Tea - Other"): 2})


class TestByTypeTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load()
        with open(BY_TYPE, newline="", encoding="utf-8") as fh:
            cls.table = list(csv.DictReader(fh))

    def test_every_row_recomputes(self):
        self.assertEqual(len(self.table), 17)
        for t in self.table:
            ps = select(self.rows, (t["survey"],), t["tea_type"])
            with self.subTest(survey=t["survey"], tea_type=t["tea_type"]):
                self.assertEqual(int(t["n"]), len(ps))
                self.assertEqual(int(t["n_detected"]), sum(1 for p in ps if p > 0))
                self.assertAlmostEqual(float(t["ppm_median"]), statistics.median(ps), places=3)
                self.assertAlmostEqual(float(t["ppm_mean"]), statistics.fmean(ps), places=3)
                self.assertAlmostEqual(float(t["ppm_max"]), max(ps), places=3)
                for sid in SCENARIOS:
                    self.assertEqual(int(t["n_over_tdi_" + sid.lower()]), over(ps, sid))

    def test_rows_cover_every_sample(self):
        self.assertEqual(sum(int(t["n"]) for t in self.table), 622)


class TestGradesHold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load()
        cls.ps = {s: select(cls.rows, (s,)) for s in SURVEYS}
        cls.totals = grand_totals()

    def share(self, survey, sid):
        return over(self.ps[survey], sid) / len(self.ps[survey])

    def test_g0_gate_as_amended(self):
        for survey in LATER:
            g = GATE[survey]
            ps = self.ps[survey]
            with self.subTest(survey=survey):
                lo, hi = g["n_rows"]
                self.assertTrue(lo <= self.totals[survey] <= hi)
                self.assertEqual(len(ps), g["n_tea"])
                types = {}
                for r in self.rows:
                    if r["survey"] == survey:
                        types[r["tea_type"]] = types.get(r["tea_type"], 0) + 1
                self.assertEqual(types, g["types"])
                self.assertEqual({r["unit"] for r in self.rows if r["survey"] == survey},
                                 {"ug/g"})
                self.assertTrue(g["tea_max"][0] <= max(ps) <= g["tea_max"][1])
                det = [p for p in ps if p > 0]
                self.assertTrue(g["detected"][0] <= len(det) <= g["detected"][1])
                which, (lo, hi) = g["mean"]
                mean = statistics.fmean(ps if which == "all" else det)
                self.assertTrue(lo <= mean <= hi, msg=(survey, which, mean))
        # The one check the amendment changed: under the 0.1.0 reading it fails.
        det_1415 = [p for p in self.ps["2014-15"] if p > 0]
        self.assertFalse(285.0 <= statistics.fmean(det_1415) <= 320.0)

    def test_p1(self):
        self.assertEqual(over(self.ps["2014-15"], "A1"), 0)
        self.assertEqual(over(self.ps["2015-16"], "A1"), 0)

    def test_p2_primary(self):
        ref = REF_1314["C1"] / REF_1314["n"]
        self.assertLess(self.share("2014-15", "C1"), ref)
        self.assertLess(self.share("2015-16", "C1"), ref)

    def test_p3_to_p8(self):
        self.assertTrue(P3_C1_1415[0] <= self.share("2014-15", "C1") <= P3_C1_1415[1])
        self.assertTrue(P4_C1_1516[0] <= self.share("2015-16", "C1") <= P4_C1_1516[1])
        self.assertTrue(P5_C2_1415[0] <= self.share("2014-15", "C2") <= P5_C2_1415[1])
        self.assertTrue(P6_C2_1516[0] <= self.share("2015-16", "C2") <= P6_C2_1516[1])
        self.assertTrue(P7_A2_1415_N[0] <= over(self.ps["2014-15"], "A2") <= P7_A2_1415_N[1])
        self.assertTrue(P8_A2_1516_N[0] <= over(self.ps["2015-16"], "A2") <= P8_A2_1516_N[1])

    def test_p9_direction(self):
        self.assertGreater(self.share("2015-16", "C1"), self.share("2014-15", "C1"))

    def test_p10_herbal_highest_median_2015_16(self):
        meds = {t: statistics.median(select(self.rows, ("2015-16",), t)) for t in TEA_TYPES}
        want = {"Tea - Black": 184.0, "Tea - Green": 147.0, "Tea - Herbal": 392.0,
                "Tea - Oolong": 198.5, "Tea - White": 23.65, "Tea - Other": 320.0}
        self.assertEqual(set(meds), set(want))
        for t, m in want.items():
            self.assertAlmostEqual(meds[t], m, places=6, msg=t)
        self.assertTrue(all(meds[HERBAL] > m for t, m in meds.items() if t != HERBAL))


if __name__ == "__main__":
    unittest.main()
