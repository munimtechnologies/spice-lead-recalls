#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/furan-2018-0.1.0-result.md.

Rebuilds the per-type counts, every printed Table 2 row, the Figure 1 matching (and the one
dried-beverage sample that differs), the 175/176 and 9.7 ppb arithmetic, the grand average, the
Table 3 furan-only comparison, the analogue counts and shares, the canned-milk furan/2-methylfuran
ratio and the Table 1 origin counts from the committed per-sample table data/furan_2018_samples.csv
with its own code (it does not import the grader), and checks them against the sealed grader record
data/furan_2018_summary.json. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "furan_2018_samples.csv")
SUMMARY = os.path.join(DATA, "furan_2018_summary.json")

TYPES = {"canned-fish": 50, "canned-meat": 50, "canned-milk": 15, "dried-beverage": 42,
         "dried-dairy": 43, "soy-sauce": 50}
# CFIA's printed Table 2 (furans, ppb, positives only): samples, detected, min, max, average.
TABLE2 = {"canned-fish": (50, 50, "16.3", "146", "46.6"),
          "canned-meat": (50, 50, "10.8", "64", "31.1"),
          "canned-milk": (16, 10, "13.9", "33.2", "19.8"),
          "dried-beverage": (42, 15, "5.1", "22.5", "9.7"),
          "dried-dairy": (42, 0, None, None, None),
          "soy-sauce": (50, 50, "1.2", "179", "73.8")}
# Printed Table 3, CFIA rows (furan only): samples, min, max, average.
TABLE3 = {"canned-fish": (50, "1.62", "64.4", "16.9"), "canned-meat": (50, "1.19", "40", "14"),
          "canned-milk": (16, "1.27", "20.8", "6.87"),
          "dried-beverage": (43, "2.7", "8.22", "5.43"), "soy-sauce": (50, "1.09", "159", "38.5")}
# Printed Table 1 origins: domestic, imported, unspecified.
TABLE1 = {"canned-fish": (4, 45, 1), "canned-meat": (14, 35, 1), "canned-milk": (14, 0, 2),
          "dried-beverage": (10, 7, 25), "dried-dairy": (20, 5, 17), "soy-sauce": (13, 33, 4)}
# Printed Figure 1 (furans of every detected sample, ppb).
FIGURE = {
    "canned-fish": (
        "16.25 17.13 17.15 20.16 20.36 21.94 23.15 23.63 25.02 25.12 27.02 27.19 27.5 27.78 "
        "27.833 29.71 33.46 34.24 35.06 35.75 35.87 37.43 37.66 38.15 38.25 39.24 40.12 41.56 "
        "45.5 45.6 46.03 46.08 48.44 51.66 53.94 56.45 57.36 61.27 61.61 62.09 62.13 63.9 74.18 "
        "75.58 79.07 81.87 83.76 91.67 112.67 145.51").split(),
    "canned-meat": (
        "10.84 11 16.54 16.81 19.13 19.41 19.52 20.3 21.58 21.62 22.54 22.84 23.39 24.16 24.63 "
        "24.65 24.82 25.91 26.78 27.27 27.32 27.66 28.16 28.56 28.87 28.88 29.07 29.56 30.07 "
        "30.84 31.1 31.63 31.66 33.9 36.35 36.42 36.44 38.17 38 39.67 41.15 41.97 42.38 43.49 "
        "44.32 46.48 53.95 54.02 59.09 63.99").split(),
    "canned-milk": "13.9 15.15 15.84 16.74 17.15 17.92 22.2 23.01 23.31 33.23".split(),
    "dried-beverage": (
        "5.05 5.08 5.4 5.42 5.64 5.89 6.12 8.09 11.38 12.37 12.92 13.08 16.44 19.76 "
        "22.54").split(),
    "soy-sauce": (
        "1.23 7.5 8.46 10.25 11.21 11.93 12.71 13.62 15.07 15.3 15.59 17.42 18.5 24.35 31.57 "
        "45.06 49.84 55.01 64.88 65.03 66.72 67.27 71.54 74.21 78.44 78.83 83.97 85.42 87.48 "
        "91.38 96.16 97.39 98.42 98.6 99.05 99.82 102.05 110.26 112.18 113.16 116.51 117.19 "
        "126.46 126.51 127.69 131.33 145.25 149.18 164.65 179.33").split(),
}


def num(s):
    return float(s) if s != "" else None


def load_rows():
    with open(SAMPLES, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["F"] = num(r["furan_ppb"])
        r["M2"] = num(r["methylfuran_2_ppb"])
        r["M3"] = num(r["methylfuran_3_ppb"])
        r["sum"] = float(r["furans_ppb"])
        r["k"] = int(r["n_detected"])
    return rows


def count(rows, key):
    out = {}
    for r in rows:
        k = key(r)
        out[k] = out.get(k, 0) + 1
    return out


def in_range(x, printed):
    half = 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5
    return abs(x - float(printed)) <= half + 1e-9


def pos(values):
    return sorted(v for v in values if v is not None and v > 0)


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_rows()
        with open(SUMMARY, encoding="utf-8") as fh:
            cls.s = json.load(fh)
        cls.a = cls.s["analysis"]
        cls.preds = {p["id"]: p for p in cls.s["predictions"]}
        cls.det = [r for r in cls.rows if r["kind"] == "det"]

    def sel(self, t):
        return [r for r in self.rows if r["category"] == t]

    def sums(self, t):
        return pos(r["sum"] for r in self.sel(t))


class TestShape(Base):
    def test_counts(self):
        self.assertEqual(len(self.rows), 250)
        self.assertEqual({r["sample"] for r in self.rows},
                         {f"C2018FRAN{i:05d}" for i in range(1, 251)})
        self.assertEqual(count(self.rows, lambda r: r["category"]), TYPES)
        self.assertEqual(count(self.rows, lambda r: r["product"]), self.s["census"]["products"])
        self.assertEqual(count(self.rows, lambda r: r["kind"]), {"det": 175, "nd": 75})
        self.assertEqual(set(r["n_rows"] for r in self.rows), {"3"})
        for r in self.rows:
            self.assertEqual(r["sum"] > 0, r["kind"] == "det", r["sample"])
        self.assertEqual([r["sample"] for r in self.rows if r["M2"] is None],
                         ["C2018FRAN00172"])
        self.assertEqual(self.s["census"]["units"], {"ng/g": 750})
        self.assertEqual(self.s["census"]["bad_shapes"], [])

    def test_gate_and_tally(self):
        self.assertTrue(self.preds["G"]["met"])
        self.assertTrue(all(self.preds["G"]["observed"].values()))
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (9, 2))
        met = {p["id"]: p["met"] for p in self.s["predictions"]}
        self.assertEqual(list(met), ["G", "C2", "C3", "CF", "CT", "P1", "P2", "P3", "P4"])
        self.assertEqual({k for k, v in met.items() if v}, {"G", "P2"})
        prov = self.s["provenance"]
        self.assertEqual(prov["sha256"],
                         "f57d7d77f73a92abb1b88d3bff15ae922ce5f1938a2c35a8a9fee51442234601")
        self.assertEqual(prov["bytes"], 133082)
        self.assertTrue(prov["md5_matches_portal"])


class TestTable2(Base):
    def test_rows(self):
        for t, (n, det, mn, mx, avg) in TABLE2.items():
            d = self.sums(t)
            self.assertEqual(len(d), det, t)
            if det:
                self.assertTrue(in_range(d[-1], mx), (t, d[-1], mx))
                if t != "dried-beverage":
                    self.assertTrue(in_range(d[0], mn), (t, d[0], mn))
                    self.assertTrue(in_range(sum(d) / len(d), avg), (t, avg))
                st = self.a["cats"][t]["furans_stats"]
                self.assertAlmostEqual(st["mean"], sum(d) / len(d), places=9)
                self.assertEqual((st["min"], st["max"]), (d[0], d[-1]))
        # Sample counts: only canned milk and dried dairy differ, by one each way.
        diff = {t: len(self.sel(t)) - TABLE2[t][0] for t in TABLE2}
        self.assertEqual({t: v for t, v in diff.items() if v},
                         {"canned-milk": -1, "dried-dairy": 1})
        self.assertEqual(sum(r[1] for r in TABLE2.values()), 175)

    def test_dairy_alternatives(self):
        da = [r for r in self.rows if r["product"] == "Dairy Alternative"]
        self.assertEqual(len(da), 5)
        self.assertTrue(all(r["kind"] == "nd" and r["category"] == "dried-dairy" for r in da))
        self.assertEqual(count(da, lambda r: r["function"]), {"Import": 3, "Unknown": 2})
        self.assertEqual([r["sample"] for r in self.sel("dried-dairy") if r["kind"] == "det"], [])

    def test_grand_and_beverage(self):
        d = pos(r["sum"] for r in self.rows)
        m = sum(d) / len(d)
        self.assertEqual(len(d), 175)
        self.assertTrue(in_range(d[0], "1.23") and in_range(d[-1], "179"))
        self.assertTrue(45.0 <= m <= 45.4)
        self.assertFalse(in_range(m, "45.5"))
        self.assertAlmostEqual(m, self.a["grand"]["mean"], places=9)
        self.assertAlmostEqual(sum(d), 7928.733, places=6)
        bev = self.sums("dried-beverage")
        self.assertAlmostEqual(sum(bev), 152.29, places=6)
        self.assertFalse(in_range(sum(bev) / 15, "9.7"))
        self.assertFalse(in_range(sum(bev) / 16, "9.7"))
        self.assertTrue(in_range(sum(bev) / 15, "10.15"))
        fig = sum(float(v) for v in FIGURE["dried-beverage"])
        self.assertAlmostEqual(fig, 155.18, places=6)
        self.assertTrue(in_range(fig / 16, "9.7"))
        self.assertFalse(in_range(fig / 15, "9.7"))
        self.assertFalse(any(v <= 0.82 for v in bev))


class TestFigure(Base):
    def test_four_types_match_exactly(self):
        for t in ("canned-fish", "canned-meat", "canned-milk", "soy-sauce"):
            printed = sorted(FIGURE[t], key=float)
            d = self.sums(t)
            self.assertEqual(len(d), len(printed), t)
            for v, p in zip(d, printed):
                self.assertTrue(in_range(v, p), (t, v, p))

    def test_beverage_one_differs(self):
        d = self.sums("dried-beverage")
        printed = sorted(FIGURE["dried-beverage"], key=float)
        self.assertEqual(len(d), 15)
        self.assertEqual(d[0], 3.0)
        self.assertFalse(any(in_range(3.0, p) for p in printed))
        self.assertFalse(any(in_range(v, "5.89") for v in d))
        rest_p = [p for p in printed if p != "5.89"]
        for v, p in zip(d[1:], rest_p):
            self.assertTrue(in_range(v, p), (v, p))
        r170 = [r for r in self.rows if r["sample"] == "C2018FRAN00170"][0]
        self.assertEqual((r170["product"], r170["function"], r170["F"], r170["M2"], r170["M3"]),
                         ("Beverage - Powdered Mixes - Hot", "Domestic", 3.0, 0.0, 0.0))
        self.assertEqual([r["sample"] for r in self.det if r["sum"] == 3.0], ["C2018FRAN00170"])
        f = self.a["figure"]["dried-beverage"]
        self.assertEqual((f["matched"], f["unmatched"], f["extras"]), (14, ["5.89"], [3.0]))
        self.assertEqual(sum(v["matched"] for v in self.a["figure"].values()), 174)


class TestTable3(Base):
    def test_furan_only(self):
        hits = []
        for t, (n, mn, mx, avg) in TABLE3.items():
            f = pos(r["F"] for r in self.sel(t))
            st = self.a["cats"][t]["furan_stats"]
            self.assertEqual((st["k"], st["min"], st["max"]), (len(f), f[0], f[-1]), t)
            self.assertAlmostEqual(st["mean"], sum(f) / len(f), places=9)
            for name, x, p in (("min", f[0], mn), ("max", f[-1], mx),
                               ("mean", sum(f) / len(f), avg)):
                if in_range(x, p):
                    hits.append((t, name))
        self.assertEqual(hits, [("soy-sauce", "max")])
        self.assertEqual(len(pos(r["F"] for r in self.sel("dried-beverage"))), 13)
        milk = pos(r["F"] for r in self.sel("canned-milk"))
        self.assertEqual((milk[0], milk[-1]), (13.83, 31.02))
        self.assertTrue(in_range(sum(milk) / len(milk), "18.53"))
        self.assertEqual(len(self.sel("dried-beverage")), TABLE3["dried-beverage"][0] - 1)


class TestText(Base):
    def test_analogue_counts(self):
        self.assertEqual(count(self.det, lambda r: r["k"]), {1: 15, 2: 101, 3: 59})
        all3 = [r for r in self.det if r["k"] == 3]
        self.assertEqual(count(all3, lambda r: r["category"]),
                         {"canned-fish": 33, "canned-meat": 26})
        f2 = [r for r in self.det if (r["F"] or 0) > 0 and (r["M2"] or 0) > 0]
        self.assertEqual(len(f2), 160)
        self.assertEqual((self.a["n_one"], self.a["n_f_2mf"]), (15, 160))
        self.assertEqual(self.a["all3"], {"canned_meat": 26, "n": 59})
        for k, printed in ((15, "52"), (160, "38")):
            self.assertFalse(in_range(100 * k / 175, printed))
            self.assertFalse(in_range(100 * k / 250, printed))

    def test_no_3mf_cut_makes_meat_lead(self):
        cuts = sorted({r["M3"] for r in self.rows if (r["M3"] or 0) > 0})
        for c in [0.0] + cuts:
            def n(t):
                return sum(1 for r in self.sel(t) if (r["F"] or 0) > 0 and (r["M2"] or 0) > 0
                           and (r["M3"] or 0) > c)
            self.assertGreaterEqual(n("canned-fish"), n("canned-meat"), c)

    def test_analyte_sums(self):
        def tot(key, t=None):
            return sum(r[key] or 0 for r in self.rows if t is None or r["category"] == t)

        self.assertAlmostEqual(tot("F", "canned-milk"), 185.32, places=6)
        self.assertAlmostEqual(tot("M2", "canned-milk"), 13.13, places=6)
        self.assertGreater(tot("F", "canned-milk"), 14 * tot("M2", "canned-milk"))
        self.assertAlmostEqual(tot("F"), 5056.34, places=6)
        self.assertAlmostEqual(tot("M2"), 2699.083, places=6)
        self.assertAlmostEqual(tot("M3"), 173.31, places=6)
        self.assertGreater(tot("F"), tot("M2"))
        self.assertGreater(tot("M2"), tot("M3"))
        self.assertAlmostEqual(tot("F") + tot("M2") + tot("M3"), self.a["grand"]["sum"],
                               places=6)


class TestOrigin(Base):
    def test_table1(self):
        names = ("Domestic", "Import", "Unknown")
        diff = {}
        for t, printed in TABLE1.items():
            c = count(self.sel(t), lambda r: r["function"])
            self.assertEqual(set(c) - set(names), set(), t)
            got = tuple(c.get(k, 0) for k in names)
            self.assertEqual({k: v for k, v in c.items()}, self.a["origin"][t])
            d = tuple(g - p for g, p in zip(got, printed))
            if any(d):
                diff[t] = d
        self.assertEqual(diff, {"canned-milk": (-1, 0, 0), "dried-dairy": (1, 0, 0)})


if __name__ == "__main__":
    unittest.main(verbosity=2)
