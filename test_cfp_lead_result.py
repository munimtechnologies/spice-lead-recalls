#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/cfp-lead-0.1.0-result.md.

Rebuilds the per-year counts, every printed lead table row and text figure (C2017-C2022), the blind
predictions P1-P6 (the Wilson intervals and the one-sided Fisher exact p computed from scratch), the
FDA reference table and the exploratory origin counts from the committed per-sample table
data/cfp_lead_samples.csv with its own code (it does not import the grader), and checks them
against the sealed grader record data/cfp_lead_summary.json. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import math
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "cfp_lead_samples.csv")
SUMMARY = os.path.join(DATA, "cfp_lead_summary.json")

YEARS = ["2017", "2018", "2019", "2020", "2021", "2022"]

# CFIA's printed lead tables: type -> (tested, negative, positive, maximum, mean), ppm.
PRINTED = {
    "2017": {"juice": (51, 49, 2, "0.009", "0.000")},
    "2018": {"puree": (38, 38, 0, None, None), "formula-dairy": (52, 49, 3, "0.019", "0.02"),
             "formula-soy": (7, 7, 0, None, None), "meal": (11, 11, 0, None, None),
             "pasta": (35, 34, 1, "0.03", "0.03")},
    "2019": {"yogurt-beverage": (11, 11, 0, None, None),
             "infant-cereal": (48, 37, 11, "0.093", "0.01"),
             "puree": (98, 97, 1, "0.015", "0.0002"), "snack": (78, 71, 7, "0.04", "0.0025"),
             "yogurt": (16, 16, 0, None, None)},
    "2020": {"children-cereal": (50, 47, 3, "0.10", "0.003"),
             "fruit-snack": (20, 19, 1, "0.03", "0.001"),
             "granola-bar": (29, 28, 1, "0.03", "0.001"), "pudding": (36, 36, 0, None, None)},
    "2021": {"puree-meal": (177, 174, 3, None, None), "pasta": (47, 44, 3, "0.05", "0.002"),
             "juice": (67, 67, 0, None, None)},
    "2022": {"infant-cereal": (39, 16, 23, "0.0211", "0.0089"),
             "snack": (69, 28, 41, "0.196", "0.0152")},
}
CONVENTION = {"2017": "all", "2018": "positives", "2019": "all", "2020": "all", "2021": "all",
              "2022": "positives"}


def report_type(year, product):
    """The report's product type for a file label (own rules, written for this test)."""
    if year == "2017":
        return "juice"
    if year == "2018":
        if product.startswith("Pasta"):
            return "pasta"
        return {"Infant Formula - Dairy": "formula-dairy", "Infant Formula - Soy": "formula-soy",
                "Infant Food - Puree": "puree", "Meal - Toddler/Baby": "meal"}[product]
    if year == "2019":
        return {"Infant Food - Puree": "puree", "Infant Food - Snack": "snack",
                "Infant Food - Cereal": "infant-cereal", "Yogurt": "yogurt",
                "Beverage - Yogurt": "yogurt-beverage"}[product]
    if year == "2020":
        return {"Cereal - Children": "children-cereal", "Oatmeal": "children-cereal",
                "Pudding": "pudding", "Granola/Cereal Bar": "granola-bar",
                "Fruit Snacks": "fruit-snack", "Raisin": "fruit-snack"}[product]
    if year == "2021":
        if "Pur" in product or product.startswith("Meal"):
            return "puree-meal"
        if product.startswith("Pasta"):
            return "pasta"
        assert product.startswith("Juice") or product == "Beverage - Fruit", product
        return "juice"
    return "infant-cereal" if product == "Infant Food - Cereal" else "snack"


def load_rows():
    with open(SAMPLES, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["value"] = float(r["value_ppm"])
    return rows


def count(rows, key):
    out = {}
    for r in rows:
        k = key(r)
        out[k] = out.get(k, 0) + 1
    return out


def wilson(k, n, z=1.959963984540054):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, c - h), min(1.0, c + h)]


def fisher_at_most(k1, n1, k2, n2):
    """P(X <= k1): X = successes in group 1 when k1 + k2 successes fall among n1 + n2."""
    k, n = k1 + k2, n1 + n2
    return sum(math.comb(n1, x) * math.comb(n2, k - x)
               for x in range(max(0, k - n2), k1 + 1)) / math.comb(n, k)


def in_range(x, printed):
    half = 0.5 * 10 ** -len(printed.split(".")[1])
    return abs(x - float(printed)) <= half + 1e-9


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_rows()
        with open(SUMMARY, encoding="utf-8") as fh:
            cls.s = json.load(fh)
        cls.a = cls.s["analysis"]
        cls.preds = {p["id"]: p for p in cls.s["predictions"]}
        cls.det = [r for r in cls.rows if r["kind"] == "det"]

    def sel(self, y, t=None):
        return [r for r in self.rows if r["year"] == y and (t is None or r["category"] == t)]

    def dvals(self, y, t=None):
        return sorted(r["value"] for r in self.sel(y, t) if r["kind"] == "det")


class TestShape(Base):
    def test_counts(self):
        self.assertEqual(count(self.rows, lambda r: r["year"]),
                         {"2017": 51, "2018": 143, "2019": 251, "2020": 135, "2021": 291,
                          "2022": 108})
        self.assertEqual(len(self.rows), 979)
        self.assertEqual(len({(r["year"], r["sample"]) for r in self.rows}), 979)
        self.assertEqual(count(self.det, lambda r: r["year"]),
                         {"2017": 2, "2018": 4, "2019": 19, "2020": 5, "2021": 6, "2022": 64})
        self.assertEqual(len(self.det), 100)
        self.assertEqual(set(r["kind"] for r in self.rows), {"det", "nd"})
        self.assertEqual(set(r["n_rows"] for r in self.rows), {"1"})
        for r in self.rows:
            self.assertEqual(r["value"] > 0, r["kind"] == "det")
        for y in YEARS:
            census = self.s["census"][y]
            self.assertEqual(count(self.sel(y), lambda r: r["product"]), census["products"])
            self.assertEqual(len(census["units"]), 1)
            self.assertEqual({r["unit"] for r in self.sel(y)}, set(census["units"]))
            self.assertEqual(census["bad_shapes"], [])

    def test_report_types(self):
        for r in self.rows:
            self.assertEqual(r["category"], report_type(r["year"], r["product"]), r["sample"])

    def test_gate_and_tally(self):
        self.assertTrue(self.preds["G"]["met"])
        for y in YEARS:
            self.assertTrue(all(self.preds["G"]["observed"]["per_year"][y].values()))
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (13, 12))
        met = {p["id"]: p["met"] for p in self.s["predictions"]}
        self.assertEqual(list(met), ["G", "C2017", "C2018", "C2019", "C2020", "C2021", "C2022",
                                     "P1", "P2", "P3", "P4", "P5", "P6"])
        self.assertEqual({k for k, v in met.items() if not v}, {"C2021"})
        self.assertEqual(self.s["provenance"]["2021"]["sha256"],
                         "5364b9cd385d25428868c3f1354d6f1d5eccf5e4f58a3143e263c10aa7f1c544")


class TestConsistency(Base):
    def test_every_table_row(self):
        for y, table in PRINTED.items():
            for t, (n, neg, pos, mx, _mean) in table.items():
                got = self.sel(y, t)
                d = self.dvals(y, t)
                self.assertEqual((len(got), len(got) - len(d), len(d)), (n, neg, pos), (y, t))
                if mx is not None:
                    self.assertTrue(in_range(d[-1], mx), (y, t, d[-1], mx))

    def test_text_figures(self):
        f = sorted(self.dvals("2018", "formula-dairy") + self.dvals("2018", "formula-soy"))
        n_formula = len(self.sel("2018", "formula-dairy")) + len(self.sel("2018", "formula-soy"))
        self.assertEqual(n_formula, 59)
        self.assertEqual(f, [0.016, 0.018, 0.019])
        self.assertEqual(len(self.dvals("2019")), 19)
        self.assertEqual(len(self.sel("2020")) - len(self.dvals("2020")), 130)
        d22 = self.dvals("2022")
        self.assertEqual(len(self.sel("2022")) - len(d22), 44)
        self.assertTrue(in_range(d22[0], "0.0050") and in_range(d22[-1], "0.196"))
        top = max((r for r in self.det if r["year"] == "2022"), key=lambda r: r["value"])
        self.assertEqual(top["product"], "Crackers")
        for t in ("infant-cereal", "snack"):
            self.assertTrue(in_range(self.dvals("2022", t)[0], "0.0050"))
        for k in ("formula_det", "formula_n", "formula_range"):
            self.assertTrue(self.a["text"]["2018"][k])

    def test_c2021_one_miss(self):
        d = self.dvals("2021")
        self.assertEqual(len(self.sel("2021")) - len(d), 285)
        top = max((r for r in self.det if r["year"] == "2021"), key=lambda r: r["value"])
        self.assertEqual((top["value"], top["category"]), (0.047, "pasta"))
        # The text's lower end, 0.015, is the only printed figure the file does not give.
        self.assertEqual(d[0], 0.016)
        self.assertFalse(in_range(d[0], "0.015"))
        self.assertEqual(self.a["text"]["2021"], {"max_category": True, "nd": True,
                                                  "range": False})
        self.assertFalse(self.preds["C2021"]["met"])


class TestPredictions(Base):
    def test_p1_p2_decimal_slip(self):
        pm = self.dvals("2021", "puree-meal")
        self.assertEqual(pm, [0.016, 0.018, 0.022])
        self.assertFalse(any(in_range(v, "0.18") for v in self.dvals("2021")))
        self.assertLess(pm[-1], 0.05)
        self.assertEqual([v for v in pm if in_range(v, "0.018")], [0.018])
        # The reading that fits every printed 2021 figure: meals {0.016, 0.018} (2 positives,
        # max 0.018 printed as 0.18, mean over 53 printed 0.001), puree {0.022} (1 positive,
        # max printed 0.02, mean over 124 printed 0).
        self.assertTrue(in_range((0.016 + 0.018) / 53, "0.001"))
        self.assertTrue(in_range(0.022, "0.02"))
        self.assertEqual(round(0.022 / 124), 0)
        self.assertTrue(self.preds["P1"]["met"] and self.preds["P2"]["met"])

    def test_p3_minimum_detected(self):
        mins = {y: self.dvals(y)[0] for y in YEARS}
        self.assertEqual(mins, {"2017": 0.007, "2018": 0.016, "2019": 0.015, "2020": 0.027,
                                "2021": 0.016, "2022": 0.005})
        self.assertTrue(all(mins[y] >= 0.010 for y in ("2018", "2019", "2020", "2021")))
        self.assertEqual(self.a["p3"], mins)
        self.assertEqual(sum(1 for r in self.det if r["year"] != "2022" and r["value"] < 0.015),
                         2)

    def test_p4_fda_cereal(self):
        c19 = [v for v in self.dvals("2019", "infant-cereal") if v > 0.020]
        self.assertEqual(c19, [0.026, 0.031, 0.038, 0.039, 0.07, 0.093])
        c22 = [v for v in self.dvals("2022", "infant-cereal") if v > 0.020]
        self.assertEqual(c22, [0.0211])
        self.assertTrue(self.preds["P4"]["met"])

    def test_p5_mean_conventions(self):
        rows = 0
        for y, table in PRINTED.items():
            for t, (n, _neg, pos, _mx, mean) in table.items():
                if not pos or mean is None:
                    continue
                rows += 1
                d = self.dvals(y, t)
                m_all, m_pos = sum(d) / n, sum(d) / len(d)
                want, other = (m_all, m_pos) if CONVENTION[y] == "all" else (m_pos, m_all)
                self.assertTrue(in_range(want, mean), (y, t, want, mean))
                self.assertFalse(in_range(other, mean), (y, t, other, mean))
                s = self.a["means"][y][t]
                self.assertAlmostEqual(s["mean_all"], m_all, places=12)
                self.assertAlmostEqual(s["mean_positives"], m_pos, places=12)
        self.assertEqual(rows, 12)
        # 2017's note says positives only; its positives average 0.008, not the printed 0.000.
        self.assertAlmostEqual(sum(self.dvals("2017")) / 2, 0.008, places=12)

    def test_p6_common_cut(self):
        def at_cut(y, t):
            return sum(1 for v in self.dvals(y, t) if v >= 0.015 - 1e-12), len(self.sel(y, t))

        self.assertEqual(at_cut("2019", "infant-cereal"), (11, 48))
        self.assertEqual(at_cut("2022", "infant-cereal"), (3, 39))
        p = fisher_at_most(3, 39, 11, 48)
        self.assertAlmostEqual(p, self.a["p6"]["fisher_one_sided_p"], places=9)
        self.assertAlmostEqual(p, 0.049, places=3)
        for got, want in zip(wilson(11, 48), self.a["p6"]["y2019"]["ci95"]):
            self.assertAlmostEqual(got, want, places=9)
        for got, want in zip(wilson(3, 39), self.a["p6"]["y2022"]["ci95"]):
            self.assertAlmostEqual(got, want, places=9)
        self.assertEqual(at_cut("2019", "snack"), (7, 78))
        self.assertEqual(at_cut("2022", "snack"), (8, 69))
        ps = fisher_at_most(7, 78, 8, 69)
        self.assertAlmostEqual(ps, self.a["snack_cut_fisher_greater_p"], places=9)
        self.assertAlmostEqual(ps, 0.40, places=2)


class TestFdaTable(Base):
    def test_rows(self):
        want = {("2018", "puree"): 0, ("2018", "meal"): 0, ("2019", "puree"): 1,
                ("2019", "infant-cereal"): 6, ("2019", "yogurt"): 0, ("2020", "pudding"): 0,
                ("2021", "puree-meal"): 3, ("2022", "infant-cereal"): 1}
        self.assertEqual(len(self.a["fda"]), len(want))
        for row in self.a["fda"]:
            y, t, level = row["year"], row["category"], row["level_ppm"]
            k = sum(1 for v in self.dvals(y, t) if v > level + 1e-12)
            n = len(self.sel(y, t))
            self.assertEqual(k, want[(y, t)], (y, t))
            self.assertEqual((row["above"], row["n"]), (k, n))
            for got, exp in zip(wilson(k, n), row["ci95"]):
                self.assertAlmostEqual(got, exp, places=9)
            if t in ("puree", "puree-meal"):
                self.assertEqual(row["above_0_020"],
                                 sum(1 for v in self.dvals(y, t) if v > 0.020 + 1e-12))
        self.assertEqual(self.a["fda"][6]["above_0_020"], 1)


class TestOriginExploratory(Base):
    """Not registered: reported in the result note as a hypothesis only."""

    @staticmethod
    def group(r):
        if r["origin"] in ("UNITED STATES", "CANADA", "UNKNOWN"):
            return r["origin"]
        return "other"

    def test_2019_cereal(self):
        c = self.sel("2019", "infant-cereal")
        self.assertEqual(count(c, self.group),
                         {"UNITED STATES": 9, "CANADA": 12, "UNKNOWN": 20, "other": 7})
        self.assertEqual(count([r for r in c if self.group(r) == "other"], lambda r: r["origin"]),
                         {"AUSTRIA": 2, "SWITZERLAND": 5})
        high = [r for r in c if r["value"] > 0.020]
        self.assertEqual(count(high, self.group), {"UNITED STATES": 4, "UNKNOWN": 2})
        self.assertEqual(sorted(r["sample"] for r in high if r["origin"] == "UNITED STATES"),
                         ["CFP2019-0107", "CFP2019-0108", "CFP2019-0109", "CFP2019-0110"])

    def test_2022_cereal_and_canadian_cut(self):
        c22 = self.sel("2022", "infant-cereal")
        self.assertEqual(count(c22, self.group), {"CANADA": 8, "UNKNOWN": 31})
        ca22 = [r for r in c22 if r["origin"] == "CANADA"]
        self.assertTrue(all(r["kind"] == "det" for r in ca22))
        cut22 = [r for r in c22 if r["value"] >= 0.015 - 1e-12]
        self.assertEqual({r["origin"] for r in cut22}, {"CANADA"})
        self.assertEqual(len(cut22), 3)
        c19 = self.sel("2019", "infant-cereal")
        ca19 = [r for r in c19 if r["origin"] == "CANADA"]
        self.assertEqual(sum(1 for r in ca19 if r["value"] >= 0.015 - 1e-12), 4)
        rest19 = [r for r in c19 if r["origin"] != "CANADA"]
        self.assertEqual((sum(1 for r in rest19 if r["value"] >= 0.015 - 1e-12), len(rest19)),
                         (7, 36))

    def test_top_snack(self):
        s22 = sorted((r for r in self.sel("2022", "snack") if r["kind"] == "det"),
                     key=lambda r: r["value"])
        self.assertEqual((s22[-1]["value"], s22[-1]["product"], s22[-1]["origin"]),
                         (0.196, "Crackers", "CANADA"))
        self.assertEqual(s22[-2]["value"], 0.0475)


if __name__ == "__main__":
    unittest.main(verbosity=2)
