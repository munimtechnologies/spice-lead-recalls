#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/aflatoxin-figs-2009-0.1.0-result.md.

Rebuilds the product and origin counts, the consistency checks C1 and C2, the blind predictions
P1-P6, the EU reference counts and the sampling-date range from the committed per-sample table
data/aflatoxin_figs_2009_samples.csv with its own code (it does not import the grader), and checks
them against the sealed grader record data/aflatoxin_figs_2009_summary.json. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "aflatoxin_figs_2009_samples.csv")
SUMMARY = os.path.join(DATA, "aflatoxin_figs_2009_summary.json")

FORMS = ("b1", "b2", "g1", "g2")
CELLS = FORMS + ("total",)
EU_B1, EU_SUM = 6.0, 10.0                 # EU 2023/915, dried figs (reference only)
PAGE_DIRECT, PAGE_FURTHER = 4.0, 10.0     # totals quoted on CFIA's 2009-10 summary page
MONTHS = {m: i for i, m in enumerate(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
                                      "Sep", "Oct", "Nov", "Dec"), start=1)}


def load_samples():
    with open(SAMPLES, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        for c in CELLS:
            r[c] = float(r[c])
    return rows


def positive(r):
    return any(r[c] > 0 for c in CELLS)


def form_sum(r):
    return sum(r[f] for f in FORMS)


def largest(r):
    best = "b1"                            # B1 wins ties, as registered
    for f in FORMS:
        if r[f] > r[best]:
            best = f
    return best


def ymd(text):
    """'19-Feb-10' -> (2010, 2, 19), without relying on the locale."""
    d, m, y = text.split("-")
    return 2000 + int(y), MONTHS[m], int(d)


def count(rows, col):
    out = {}
    for r in rows:
        out[r[col]] = out.get(r[col], 0) + 1
    return out


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_samples()
        with open(SUMMARY, encoding="utf-8") as fh:
            cls.s = json.load(fh)
        cls.a = cls.s["analysis"]
        cls.pos = [r for r in cls.rows if positive(r)]


class TestTable(Base):
    def test_shape_and_census(self):
        self.assertEqual(len(self.rows), 100)
        self.assertEqual(len({r["sample"] for r in self.rows}), 100)
        census = self.s["census"]
        self.assertEqual({k: 5 * v for k, v in count(self.rows, "product").items()},
                         census["products"])
        self.assertEqual({k: 5 * v for k, v in count(self.rows, "origin").items()},
                         census["origins"])
        self.assertEqual(count(self.rows, "product"), {"DATE": 50, "FIG": 50})
        self.assertEqual(count(self.rows, "region"), {"BC": 97, "UNKNOWN": 3})
        nonzero = sum(1 for r in self.rows for c in CELLS if r[c] > 0)
        self.assertEqual(nonzero, 14)
        self.assertEqual(nonzero, census["nonzero_cells"])
        self.assertEqual(census["value_kinds"], {"pos": 14, "zero": 486})
        self.assertEqual(census["units"], {"ppb": 500})
        self.assertTrue(all(r[c] >= 0 for r in self.rows for c in CELLS))
        pairs = {}
        for r in self.rows:
            k = f"{r['product']}|{r['origin']}"
            pairs[k] = pairs.get(k, 0) + 1
        self.assertEqual(pairs, self.a["product_origin"])

    def test_gate_and_tally(self):
        gate = self.s["predictions"][0]
        self.assertEqual(gate["id"], "G")
        self.assertEqual(len(gate["observed"]), 12)
        self.assertTrue(all(gate["observed"].values()))
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (9, 8))
        met = {p["id"]: p["met"] for p in self.s["predictions"]}
        self.assertEqual(list(met), ["G", "C1", "C2", "P1", "P2", "P3", "P4", "P5", "P6"])
        self.assertEqual({k for k, v in met.items() if not v}, {"P6"})
        prov = self.s["provenance"]["AF"]
        self.assertEqual(prov["sha256"],
                         "5d3300b7de8ab2b5a324bb8aee77ccde0ab497471693c1b44f131806b9bb055d")
        self.assertEqual(prov["bytes"], 60259)


class TestChecks(Base):
    def test_c1(self):
        by = {p: sum(1 for r in self.pos if r["product"] == p) for p in ("DATE", "FIG")}
        self.assertEqual(by, {"DATE": 0, "FIG": 4})
        self.assertEqual((self.a["date_pos"], self.a["fig_pos"]), (0, 4))
        # L1: both splits print as 92% of figs without aflatoxin.
        self.assertEqual(round(100 * 47 / 51), 92)
        self.assertEqual(round(100 * 46 / 50), 92)

    def test_c2(self):
        totals = [r["total"] for r in self.pos]
        lo, hi = min(totals), max(totals)
        self.assertEqual((lo, hi), (7.46, 78.66))
        self.assertLessEqual(abs(lo - 7.5), 0.05 + 1e-9)
        self.assertLessEqual(abs(hi - 78.7), 0.05 + 1e-9)
        self.assertAlmostEqual(lo, self.a["total_min"], places=9)
        self.assertAlmostEqual(hi, self.a["total_max"], places=9)


class TestPredictions(Base):
    def test_p1_total_is_sum(self):
        gaps = {r["sample"]: abs(r["total"] - form_sum(r)) for r in self.rows}
        worst = max(gaps, key=gaps.get)
        self.assertEqual(worst, "2009ATX0027")
        self.assertAlmostEqual(gaps[worst], 0.01, delta=1e-6)
        self.assertAlmostEqual(gaps[worst], self.a["max_sum_gap"], places=9)
        self.assertTrue(all(g < 1e-6 for s, g in gaps.items() if s != worst))
        self.assertLessEqual(gaps[worst], 0.25)

    def test_p2_p3(self):
        self.assertTrue(all(r["b1"] > 0 for r in self.pos))
        top = {r["sample"]: largest(r) for r in self.pos}
        self.assertEqual(top, {"2009ATX0003": "b1", "2009ATX0012": "b1", "2009ATX0027": "b1",
                               "2009ATX0043": "g1"})
        self.assertEqual(sum(1 for v in top.values() if v == "b1"), self.a["b1_largest"])
        greek = next(r for r in self.pos if r["sample"] == "2009ATX0043")
        self.assertEqual(greek["origin"], "GREECE")
        self.assertEqual(round(100 * greek["g1"] / greek["total"]), 68)

    def test_p4_origins(self):
        got = {}
        for r in self.pos:
            got[r["origin"]] = got.get(r["origin"], 0) + 1
        self.assertEqual(got, {"TURKEY": 2, "GREECE": 1, "UNITED STATES": 1})
        self.assertEqual(got["TURKEY"], self.a["origin_hits"])
        figs = [r for r in self.rows if r["product"] == "FIG"]
        n = count(figs, "origin")
        self.assertEqual((n["TURKEY"], n["GREECE"], n["UNITED STATES"]), (20, 15, 10))

    def test_p5_eu_levels(self):
        over_b1 = [r["sample"] for r in self.pos if r["b1"] > EU_B1]
        over_sum = [r["sample"] for r in self.pos if form_sum(r) > EU_SUM]
        self.assertEqual(sorted(over_b1), ["2009ATX0012", "2009ATX0027", "2009ATX0043"])
        self.assertEqual(sorted(over_sum), sorted(over_b1))
        self.assertEqual((len(over_b1), len(over_sum)), (self.a["eu_b1"], self.a["eu_sum"]))
        self.assertGreaterEqual(min(form_sum(r) for r in self.pos if r["sample"] in over_sum),
                                7 * EU_SUM)
        us = next(r for r in self.pos if r["origin"] == "UNITED STATES")
        self.assertEqual((us["b1"], us["total"]), (5.18, 7.46))
        # The totals CFIA's page quoted for 2009-10 (reference only).
        self.assertEqual(sum(1 for r in self.pos if r["total"] > PAGE_DIRECT), 4)
        self.assertEqual(sum(1 for r in self.pos if r["total"] > PAGE_FURTHER), 3)

    def test_p6_missed(self):
        g1 = [r["sample"] for r in self.pos if r["g1"] > 0]
        g2 = [r["sample"] for r in self.pos if r["g2"] > 0]
        self.assertEqual((g1, g2), (["2009ATX0043"], ["2009ATX0043"]))
        self.assertEqual(len(g1), self.a["g1_pos"])
        self.assertLess(len(g1), 2)                      # registered: at least 2


class TestDates(Base):
    def test_sampling_range_and_text_order(self):
        dates = [r["date"] for r in self.rows]
        self.assertEqual(min(ymd(d) for d in dates), (2009, 11, 2))
        self.assertEqual(max(ymd(d) for d in dates), (2010, 3, 10))
        # The pre-registration's "to 2010-01-27" is the text-order maximum.
        self.assertEqual((min(dates), max(dates)), ("02-Nov-09", "27-Jan-10"))
        pos_dates = sorted(ymd(r["date"]) for r in self.pos)
        self.assertEqual(pos_dates, [(2010, 1, 22), (2010, 2, 4), (2010, 2, 19), (2010, 3, 5)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
