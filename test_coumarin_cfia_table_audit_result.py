# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
"""Recompute every number published in docs/coumarin-cfia-table-audit-0.1.0-result.md.

Reads data/coumarin_cfia_table_audit.csv (the sealed aggregate output of job
coumarin-cfia-audit-v1: one line per Table 2 row of CFIA's 2014-15 and 2015-16 coumarin survey
reports, rebuilt from CFIA's open files, Open Government Licence - Canada) and, for the two tea
rows, the published per-sample table data/coumarin_tea_replication_samples.csv. Uses only csv,
math, statistics and unittest.
"""
import csv
import math
import os
import statistics
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIT = os.path.join(HERE, "data", "coumarin_cfia_table_audit.csv")
TEA = os.path.join(HERE, "data", "coumarin_tea_replication_samples.csv")

SURVEYS = ("2014-15", "2015-16")
ROWS = {
    "2014-15": ("Cooking sauces", "Dried beverage mixes", "Oils and extracts", "Spice mixes",
                "Tea"),
    "2015-16": ("Ground cinnamon", "Tea", "Spice mixes", "Baked goods"),
}
TOTAL = "Grand total"

# Pre-registered verdicts (docs/coumarin-cfia-table-audit-0.1.0-prereg.md).
PREDICTIONS = (
    ("Q1", "2014-15", "Cooking sauces", "all-samples"),
    ("Q2", "2014-15", "Dried beverage mixes", "all-samples"),
    ("Q3", "2014-15", "Oils and extracts", "all-samples"),
    ("Q4", "2014-15", "Spice mixes", "all-samples"),
    ("Q5", "2014-15", "Grand total", "all-samples"),
    ("Q6", "2015-16", "Spice mixes", "positives"),
    ("Q7", "2015-16", "Baked goods", "positives"),
    ("Q8", "2015-16", "Grand total", "positives"),
)
NOT_GRADED = {("2014-15", "Tea"): "all-samples", ("2015-16", "Tea"): "positives",
              ("2015-16", "Ground cinnamon"): "both"}

# Published ratios: positives-only mean / printed average, 2014-15.
RATIOS_1415 = {"Cooking sauces": 1.19, "Dried beverage mixes": 1.58, "Oils and extracts": 5.20,
               "Spice mixes": 1.17, "Tea": 1.18, "Grand total": 1.60}


def decimals(printed):
    return len(printed.split(".")[1]) if "." in printed else 0


def matches(value, printed):
    """True when `value` rounds to the printed figure at its printed precision."""
    return abs(value - float(printed)) <= 0.5 * 10 ** (-decimals(printed)) + 1e-9


def verdict(mean_pos, mean_all, printed):
    p, a = matches(mean_pos, printed), matches(mean_all, printed)
    if p and a:
        return "both"
    if p:
        return "positives"
    if a:
        return "all-samples"
    return "neither"


def load():
    with open(AUDIT, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return {(r["survey"], r["row"]): r for r in rows}


def f(r, key):
    return float(r[key])


class TestTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = load()

    def test_rows_present(self):
        want = {(s, name) for s in SURVEYS for name in ROWS[s] + (TOTAL,)}
        self.assertEqual(set(self.t), want)

    def test_counts_min_max_match_cfia(self):
        for key, r in self.t.items():
            with self.subTest(row=key):
                self.assertEqual(int(r["n"]), int(r["cfia_n"]))
                self.assertEqual(int(r["n_detected"]), int(r["cfia_n_detected"]))
                self.assertAlmostEqual(f(r, "min_detected"), float(r["cfia_min"]))
                self.assertAlmostEqual(f(r, "max"), float(r["cfia_max"]))

    def test_rows_add_up_to_grand_totals(self):
        for s in SURVEYS:
            parts = [self.t[(s, name)] for name in ROWS[s]]
            tot = self.t[(s, TOTAL)]
            with self.subTest(survey=s):
                self.assertEqual(sum(int(r["n"]) for r in parts), int(tot["n"]))
                self.assertEqual(sum(int(r["n_detected"]) for r in parts), int(tot["n_detected"]))
                self.assertAlmostEqual(max(f(r, "max") for r in parts), f(tot, "max"))
                self.assertAlmostEqual(min(f(r, "min_detected") for r in parts),
                                       f(tot, "min_detected"))
                # Total coumarin implied by each kind of mean (non-detects are 0, so both
                # readings must give the same total; the tables are rounded to 4 decimals).
                sum_all = sum(int(r["n"]) * f(r, "mean_all") for r in parts)
                sum_pos = sum(int(r["n_detected"]) * f(r, "mean_positives") for r in parts)
                self.assertAlmostEqual(sum_all, int(tot["n"]) * f(tot, "mean_all"), delta=0.5)
                self.assertAlmostEqual(sum_pos, int(tot["n_detected"]) * f(tot, "mean_positives"),
                                       delta=0.5)
                self.assertAlmostEqual(sum_all, sum_pos, delta=0.5)

    def test_every_verdict_recomputes(self):
        for key, r in self.t.items():
            with self.subTest(row=key):
                self.assertEqual(r["verdict"], verdict(f(r, "mean_positives"), f(r, "mean_all"),
                                                       r["cfia_average"]))

    def test_whole_tables(self):
        for name in ROWS["2014-15"] + (TOTAL,):
            self.assertEqual(self.t[("2014-15", name)]["verdict"], "all-samples", msg=name)
        for name in ("Tea", "Spice mixes", "Baked goods", TOTAL):
            self.assertEqual(self.t[("2015-16", name)]["verdict"], "positives", msg=name)
        self.assertEqual(self.t[("2015-16", "Ground cinnamon")]["verdict"], "both")

    def test_published_ratios_and_headline(self):
        for name, want in RATIOS_1415.items():
            r = self.t[("2014-15", name)]
            self.assertAlmostEqual(f(r, "mean_positives") / float(r["cfia_average"]), want,
                                   delta=0.005, msg=name)
        oils = self.t[("2014-15", "Oils and extracts")]
        self.assertEqual(round(f(oils, "mean_positives"), 1), 240.2)
        self.assertEqual(round(f(self.t[("2014-15", TOTAL)], "mean_positives"), 1), 238.3)

    def test_no_graded_near_tie(self):
        # The losing mean misses the printed figure by more than twice the half-unit rounding
        # window in every graded row (closest: 2015-16 baked goods, 16.87 against 18), and in
        # 2014-15 by at least 17 times the window.
        multiples = {}
        for _, s, name, want in PREDICTIONS:
            r = self.t[(s, name)]
            loser = f(r, "mean_positives") if want == "all-samples" else f(r, "mean_all")
            window = 0.5 * 10 ** (-decimals(r["cfia_average"]))
            multiples[(s, name)] = abs(loser - float(r["cfia_average"])) / window
        self.assertGreater(min(multiples.values()), 2.0)
        self.assertEqual(min(multiples, key=multiples.get), ("2015-16", "Baked goods"))
        self.assertGreaterEqual(min(m for (s, _), m in multiples.items() if s == "2014-15"), 17)


class TestGradesHold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = load()

    def test_q1_to_q8(self):
        for pid, s, name, want in PREDICTIONS:
            r = self.t[(s, name)]
            with self.subTest(pid=pid):
                self.assertEqual(verdict(f(r, "mean_positives"), f(r, "mean_all"),
                                         r["cfia_average"]), want)

    def test_not_graded_rows_as_reported(self):
        for (s, name), want in NOT_GRADED.items():
            self.assertEqual(self.t[(s, name)]["verdict"], want)


class TestTeaRowsFromSamples(unittest.TestCase):
    """Both tea rows rebuilt from the published per-sample tea table."""

    @classmethod
    def setUpClass(cls):
        cls.t = load()
        with open(TEA, newline="", encoding="utf-8") as fh:
            cls.samples = list(csv.DictReader(fh))

    def test_tea_rows(self):
        for s in SURVEYS:
            ps = sorted(float(r["coumarin_ppm"]) for r in self.samples if r["survey"] == s)
            det = [p for p in ps if p > 0]
            r = self.t[(s, "Tea")]
            with self.subTest(survey=s):
                self.assertEqual(int(r["n"]), len(ps))
                self.assertEqual(int(r["n_detected"]), len(det))
                self.assertAlmostEqual(f(r, "min_detected"), det[0])
                self.assertAlmostEqual(f(r, "max"), ps[-1])
                self.assertAlmostEqual(f(r, "mean_all"), statistics.fmean(ps), places=3)
                self.assertAlmostEqual(f(r, "mean_positives"), statistics.fmean(det), places=3)


class TestPrintedArithmetic(unittest.TestCase):
    """The pre-registered reasoning, from CFIA's printed figures only."""

    @classmethod
    def setUpClass(cls):
        cls.t = load()

    def readings(self, s):
        parts = [self.t[(s, name)] for name in ROWS[s]]
        n = sum(int(r["cfia_n"]) for r in parts)
        det = sum(int(r["cfia_n_detected"]) for r in parts)
        all_reading = sum(int(r["cfia_n"]) * float(r["cfia_average"]) for r in parts) / n
        pos_reading = sum(int(r["cfia_n_detected"]) * float(r["cfia_average"]) for r in parts) / det
        return all_reading, pos_reading

    def test_2014_15_total_only_under_all_samples(self):
        a, p = self.readings("2014-15")
        self.assertEqual(round(a, 1), 148.9)
        self.assertEqual(round(p, 1), 186.5)
        printed = self.t[("2014-15", TOTAL)]["cfia_average"]
        self.assertTrue(matches(a, printed))
        self.assertFalse(matches(p, printed))

    def test_2015_16_total_only_under_positives(self):
        a, p = self.readings("2015-16")
        self.assertEqual(round(p, 1), 391.8)
        self.assertEqual(round(a, 1), 387.8)
        printed = self.t[("2015-16", TOTAL)]["cfia_average"]
        self.assertTrue(matches(p, printed))
        self.assertFalse(matches(a, printed))

    def test_like_for_like_positives(self):
        # The 2014 tea and spice-mix figures reprinted in CFIA's 2016-2018 report, on a
        # positives basis.
        self.assertEqual(round(f(self.t[("2014-15", "Tea")], "mean_positives")), 356)
        self.assertEqual(round(f(self.t[("2014-15", "Spice mixes")], "mean_positives")), 385)
        self.assertTrue(math.isclose(float(self.t[("2014-15", "Tea")]["cfia_average"]), 302.0))


if __name__ == "__main__":
    unittest.main()
