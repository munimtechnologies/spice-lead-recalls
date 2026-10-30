#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/cfp-afm1-trend-0.1.0-result.md.

Rebuilds the per-year counts, the consistency checks C1-C6, the blind predictions P1-P5 (the Wilson
intervals and the one-sided Fisher exact p computed from scratch) and the exploratory origin table
from the committed per-sample table data/cfp_afm1_trend_samples.csv with its own code (it does not
import the grader), and checks them against the sealed grader record
data/cfp_afm1_trend_summary.json. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import math
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "cfp_afm1_trend_samples.csv")
SUMMARY = os.path.join(DATA, "cfp_afm1_trend_summary.json")

YEARS = ["2012-13", "2014-15", "2016", "2018", "2020", "2022"]
EARLIER = ["2012-13", "2014-15", "2016", "2018"]
CUT = 0.02


def load_rows():
    with open(SAMPLES, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["value"] = float(r["value_stored"])
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

    def year(self, y, cls_=None):
        return [r for r in self.rows if r["year"] == y and (cls_ is None or r["class"] == cls_)]

    def dvals(self, y, cls_=None):
        return sorted(r["value"] for r in self.year(y, cls_) if r["kind"] == "det")


class TestShape(Base):
    def test_counts(self):
        self.assertEqual(count(self.rows, lambda r: r["year"]),
                         {"2012-13": 101, "2014-15": 32, "2016": 114, "2018": 52, "2020": 76,
                          "2022": 93})
        self.assertEqual(len(self.rows), 468)
        self.assertEqual(len({(r["year"], r["sample"]) for r in self.rows}), 468)
        self.assertEqual(count(self.det, lambda r: r["year"]),
                         {"2012-13": 12, "2014-15": 4, "2016": 8, "2018": 10, "2022": 1})
        self.assertEqual(len(self.det), 35)
        self.assertEqual(set(r["kind"] for r in self.rows), {"det", "nd"})
        for y in YEARS:
            self.assertEqual(count(self.year(y), lambda r: r["class"]),
                             self.s["census"][y]["classes"])
            self.assertEqual(len(self.year(y)), self.s["census"][y]["samples"])
        # 2020: two AFM1 rows per sample, both zero.
        for r in self.year("2020"):
            self.assertEqual(r["n_rows"], "2")
            self.assertEqual(r["kind"], "nd")

    def test_gate_and_tally(self):
        self.assertTrue(self.preds["G"]["met"])
        for y in YEARS:
            self.assertTrue(all(self.preds["G"]["observed"]["per_year"][y].values()))
            self.assertEqual(self.s["census"][y]["bad_shapes"], [])
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (12, 10))
        met = {p["id"]: p["met"] for p in self.s["predictions"]}
        self.assertEqual(list(met), ["G", "C1", "C2", "C3", "C4", "C5", "C6",
                                     "P1", "P2", "P3", "P4", "P5"])
        self.assertEqual({k for k, v in met.items() if not v}, {"P1", "P4"})
        self.assertEqual(self.s["provenance"]["2014-15"]["sha256"],
                         "d2cfa733ff78e3cdc04f92e47a4b9e578e7cab8839fe1778972ecd6f98f7da59")


class TestConsistency(Base):
    def test_c1_2012(self):
        v = self.dvals("2012-13")
        self.assertEqual(len(v), 12)
        self.assertEqual(round(100 * 12 / 101), 12)
        self.assertLess(v[-1], 0.5)
        self.assertAlmostEqual(v[-1], 0.136, places=9)
        self.assertAlmostEqual(v[0], 0.01, places=9)

    def test_c2_2014(self):
        self.assertEqual(len(self.dvals("2014-15", "formula")), 4)
        self.assertEqual(len(self.dvals("2014-15")), 4)

    def test_c3_2016(self):
        f = self.dvals("2016", "formula")
        self.assertEqual(len(f), 7)
        self.assertTrue(in_range(f[0], "0.018") and in_range(f[-1], "0.080"))
        other = [r for r in self.year("2016", "other") if r["kind"] == "det"]
        self.assertEqual([r["product"] for r in other], ["Infant Biscuit"])
        self.assertTrue(in_range(other[0]["value"], "0.022"))
        self.assertEqual(self.dvals("2016", "dairy-dessert"), [])

    def test_c4_2018(self):
        f = self.dvals("2018")
        self.assertEqual(len(f), 10)
        self.assertTrue(in_range(f[0], "0.01") and in_range(f[-1], "0.086"))

    def test_c5_c6(self):
        self.assertEqual(self.dvals("2020"), [])
        d = [r for r in self.year("2022") if r["kind"] == "det"]
        self.assertEqual(len(d), 1)
        self.assertEqual(d[0]["class"], "formula")
        self.assertTrue(in_range(d[0]["value"], "0.0566"))


class TestPredictions(Base):
    def test_p1_two_values_at_or_above_0_1(self):
        high = [r for r in self.det if r["year"] != "2014-15" and r["value"] >= 0.1]
        self.assertEqual(sorted(r["value"] for r in high), [0.13, 0.136])
        self.assertEqual({r["year"] for r in high}, {"2012-13"})
        self.assertEqual({r["formula_type"] for r in high}, {"milk"})
        self.assertAlmostEqual(self.a["p1"]["max_ppb"], 0.136, places=9)
        self.assertFalse(self.preds["P1"]["met"])

    def test_p2_unit_label(self):
        f = self.dvals("2014-15", "formula")
        self.assertEqual(f, [0.011, 0.022, 0.052, 0.061])
        self.assertTrue(in_range(f[0], "0.011") and in_range(f[-1], "0.061"))
        self.assertEqual({r["unit"] for r in self.year("2014-15")}, {"µg/g"})
        self.assertEqual({r["unit"] for r in self.rows if r["year"] != "2014-15"}, {"ng/g"})
        self.assertEqual(self.a["unit_2014_15"]["reading"], "stored")
        self.assertEqual(self.a["ppb_factor"]["2014-15"], 1.0)

    def test_p3_dairy_desserts(self):
        dd = [r for r in self.rows if r["class"] == "dairy-dessert"]
        self.assertEqual(len(dd), 160)
        self.assertEqual(sum(1 for r in dd if r["kind"] == "det"), 0)
        hi = wilson(0, 160)[1]
        self.assertAlmostEqual(hi, self.a["dairy_dessert"]["ci95"][1], places=9)
        self.assertAlmostEqual(hi, 0.0234, places=3)

    def test_p4_2012_types(self):
        d = [r for r in self.year("2012-13") if r["kind"] == "det"]
        self.assertEqual(count(d, lambda r: r["formula_type"]), {"milk": 9, "specialized": 3})
        self.assertEqual(count(self.year("2012-13"), lambda r: r["formula_type"]),
                         {"milk": 87, "specialized": 13, "soy": 1})
        spec = sorted(r["value"] for r in d if r["formula_type"] == "specialized")
        self.assertEqual(spec, [0.021, 0.023, 0.055])

    def test_p5_common_cut(self):
        cut = {}
        for y in EARLIER + ["2022"]:
            f = self.year(y, "formula")
            k = sum(1 for r in f if r["kind"] == "det" and r["value"] >= CUT - 1e-12)
            cut[y] = (k, len(f))
            self.assertEqual(k, self.a["formula_at_cut"][y]["k"])
            self.assertEqual(len(f), self.a["formula_at_cut"][y]["n"])
        self.assertEqual(cut, {"2012-13": (10, 101), "2014-15": (3, 22), "2016": (6, 63),
                               "2018": (9, 52), "2022": (1, 34)})
        pk = sum(cut[y][0] for y in EARLIER)
        pn = sum(cut[y][1] for y in EARLIER)
        self.assertEqual((pk, pn), (28, 238))
        p = fisher_at_most(1, 34, pk, pn)
        self.assertAlmostEqual(p, self.a["p5"]["fisher_one_sided_p"], places=9)
        self.assertAlmostEqual(p, 0.094, places=3)
        for got, want in zip(wilson(pk, pn), self.a["p5"]["pooled_ci95"]):
            self.assertAlmostEqual(got, want, places=9)
        for got, want in zip(wilson(1, 34), self.a["p5"]["y2022"]["ci95"]):
            self.assertAlmostEqual(got, want, places=9)
        self.assertLess(1 / 34, pk / pn)


class TestOriginExploratory(Base):
    """Not registered: reported in the result note as a hypothesis only."""

    def test_origin_table(self):
        f = [r for r in self.rows if r["class"] == "formula"]
        self.assertEqual(len(f), 272)

        def group(r):
            if r["origin"] == "UNITED STATES":
                return "us"
            return "unknown" if r["origin"] in ("UNKNOWN", "") else "other"

        n = count(f, group)
        k = count([r for r in f if r["kind"] == "det"], group)
        self.assertEqual(n, {"us": 195, "other": 50, "unknown": 27})
        self.assertEqual(k, {"us": 30, "unknown": 4})
        self.assertEqual({r["origin"] for r in f if group(r) == "other"},
                         {"IRELAND", "SWITZERLAND", "CANADA", "NETHERLANDS"})
        p = fisher_at_most(0, 50, 30, 195)
        self.assertTrue(0.0004 < p < 0.0009, p)
        f12 = [r for r in f if r["year"] == "2012-13"]
        self.assertEqual(count(f12, group), {"us": 69, "other": 32})
        p12 = fisher_at_most(0, 32, 12, 69)
        self.assertTrue(0.006 < p12 < 0.009, p12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
