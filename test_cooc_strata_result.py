#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/cooc-strata-0.1.0-result.md.

Rebuilds every within-commodity ochratoxin A x deoxynivalenol 2x2 table from the two committed
per-sample tables (data/myco_don_2010_samples.csv, data/feed_myco_samples.csv) with its own code
(it does not import the grader), checks them against the committed strata CSVs and the sealed
grader record data/cooc_strata_summary.json, and recomputes the Mantel-Haenszel odds ratios, CMH
tests, between-stratum shares and Robins-Breslow-Greenland intervals quoted in the note.
Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import math
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
RETAIL = os.path.join(DATA, "myco_don_2010_samples.csv")
FEED = os.path.join(DATA, "feed_myco_samples.csv")
SUMMARY = os.path.join(DATA, "cooc_strata_summary.json")
TYPE_KEY = "feed_by_ingredient_type (sensitivity, not graded)"


def load_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def add(tabs, key, ota, don):
    t = tabs.setdefault(key, [0, 0, 0, 0])
    t[0 if ota and don else 1 if ota else 2 if don else 3] += 1


def retail_strata():
    by = {}
    for r in load_csv(RETAIL):
        s = by.setdefault(r["sample"], {"p": r["product"].strip() or "(blank)"})
        s[r["component"]] = r["detected"].strip() == "1"
    tabs = {}
    for s in by.values():
        add(tabs, s["p"], s["Ochratoxin A"], s["Deoxynivalenol"])
    return tabs


def feed_strata(key):
    tabs = {}
    for r in load_csv(FEED):
        if r["det_OTA"] == "" or r["det_DON"] == "":
            continue
        add(tabs, r[key].strip() or "(blank)", r["det_OTA"] == "1", r["det_DON"] == "1")
    return tabs


def mh(tabs):
    num = sum(a * d / (a + b + c + d) for a, b, c, d in tabs)
    den = sum(b * c / (a + b + c + d) for a, b, c, d in tabs)
    return num / den


def cmh(tabs):
    diff = var = 0.0
    for a, b, c, d in tabs:
        n = a + b + c + d
        if n < 2:
            continue
        diff += a - (a + b) * (a + c) / n
        var += (a + b) * (c + d) * (a + c) * (b + d) / (n * n * (n - 1))
    chi2 = max(0.0, abs(diff) - 0.5) ** 2 / var
    return chi2, math.erfc(math.sqrt(chi2 / 2))


def rbg_interval(tabs):
    """Robins-Breslow-Greenland 95% interval for the MH odds ratio."""
    spr = sps_qr = sqs = r_sum = s_sum = 0.0
    for a, b, c, d in tabs:
        n = a + b + c + d
        r, s, p, q = a * d / n, b * c / n, (a + d) / n, (b + c) / n
        spr += p * r
        sps_qr += p * s + q * r
        sqs += q * s
        r_sum += r
        s_sum += s
    var = spr / (2 * r_sum ** 2) + sps_qr / (2 * r_sum * s_sum) + sqs / (2 * s_sum ** 2)
    ln = math.log(r_sum / s_sum)
    half = 1.959963984540054 * math.sqrt(var)
    return math.exp(ln - half), math.exp(ln + half)


def pooled(tabs):
    return tuple(sum(t[i] for t in tabs.values()) for i in range(4))


def odds(a, b, c, d):
    if 0 in (a, b, c, d):
        return ((a + 0.5) * (d + 0.5)) / ((b + 0.5) * (c + 0.5))
    return a * d / (b * c)


def informative(t):
    a, b, c, d = t
    return bool((a + b) and (c + d) and (a + c) and (b + d))


class StrataCase(unittest.TestCase):
    csv_name = None
    summary_key = None

    def check_csv(self, tabs):
        rows = load_csv(os.path.join(DATA, self.csv_name))
        self.assertEqual(len(rows), len(tabs))
        for r in rows:
            t = tabs[r["stratum"]]
            cells = [int(r[k]) for k in ("ota_and_don", "ota_only", "don_only", "neither")]
            self.assertEqual(cells, t, msg=r["stratum"])
            self.assertEqual(int(r["n"]), sum(t))
            self.assertLess(abs(float(r["odds_ratio"]) - odds(*t)), 1e-6, msg=r["stratum"])
            self.assertEqual(int(r["haldane_corrected"]), int(0 in t))
            self.assertEqual(int(r["informative"]), int(informative(t)))

    def check_summary(self, tabs):
        rec = load_json(SUMMARY)[self.summary_key]
        self.assertEqual(rec["n_strata"], len(tabs))
        inf = [t for t in tabs.values() if informative(t)]
        self.assertEqual(rec["n_informative"], len(inf))
        self.assertEqual(rec["n_in_informative"], sum(sum(t) for t in inf))
        self.assertAlmostEqual(rec["mh_or"], mh(list(tabs.values())), places=9)
        chi2, p = cmh(list(tabs.values()))
        self.assertAlmostEqual(rec["cmh_chi2"], chi2, places=9)
        self.assertAlmostEqual(rec["cmh_p"], p, places=9)
        self.assertEqual(rec["large_strata"], {k: v for k, v in tabs.items() if sum(v) >= 10})


class TestFeed(StrataCase):
    csv_name = "cooc_strata_feed.csv"
    summary_key = "feed_by_ingredient"

    @classmethod
    def setUpClass(cls):
        cls.tabs = feed_strata("ingredient_name")
        cls.inf = [t for t in cls.tabs.values() if informative(t)]

    def test_gate_and_strata(self):
        self.assertEqual(pooled(self.tabs), (136, 60, 2312, 711))
        self.assertEqual(len(load_csv(FEED)), 3258)
        self.assertEqual((len(self.tabs), len(self.inf), sum(sum(t) for t in self.inf)),
                         (101, 14, 2867))
        self.assertIn("Wheat Shorts", self.tabs)   # no merging, as registered
        self.assertIn("Wheat shorts", self.tabs)
        self.check_csv(self.tabs)
        self.check_summary(self.tabs)

    def test_m3_m4(self):
        m = mh(list(self.tabs.values()))
        chi2, p = cmh(list(self.tabs.values()))
        self.assertEqual((round(m, 2), round(chi2, 2), round(p, 2)), (0.90, 0.23, 0.63))
        self.assertTrue(0.5 <= m <= 1.5 and p >= 0.05)
        po = odds(*pooled(self.tabs))
        self.assertEqual(round(po, 2), 0.70)
        self.assertLess(abs(math.log(m)), abs(math.log(po)))
        self.assertEqual(round(100 * (1 - math.log(m) / math.log(po))), 72)

    def test_interval(self):
        lo, hi = rbg_interval(self.inf)
        self.assertAlmostEqual(lo, 0.6375, delta=0.001)   # printed 0.64
        self.assertAlmostEqual(hi, 1.2780, delta=0.002)   # printed 1.28

    def test_corn_versus_small_grains(self):
        t = self.tabs
        self.assertEqual(t["Corn"], [11, 2, 1188, 96])
        self.assertEqual(t["Barley"], [42, 22, 277, 135])
        self.assertEqual(t["Wheat"], [18, 13, 190, 129])
        self.assertEqual(t["Oats"], [4, 8, 75, 56])
        self.assertEqual(t["(blank)"], [33, 8, 244, 71])

        def rates(x):
            n = sum(x)
            return round(100 * (x[0] + x[1]) / n, 1), round(100 * (x[0] + x[2]) / n, 1)
        self.assertEqual(rates(t["Corn"]), (1.0, 92.4))
        self.assertEqual(rates(t["Barley"]), (13.4, 67.0))
        self.assertEqual(rates(t["Wheat"]), (8.9, 59.4))
        self.assertEqual(rates(t["Oats"]), (8.4, 55.2))
        self.assertEqual(rates(t["(blank)"]), (11.5, 77.8))
        self.assertEqual(round(100 * 1297 / 3219), 40)
        self.assertEqual([round(odds(*t[k]), 2) for k in ("Corn", "Barley", "(blank)", "Wheat",
                                                           "Oats")],
                         [0.44, 0.93, 1.20, 0.94, 0.37])


class TestFeedByType(StrataCase):
    csv_name = "cooc_strata_feed_by_type.csv"
    summary_key = TYPE_KEY

    def test_sensitivity(self):
        tabs = feed_strata("ingredient_type")
        self.check_csv(tabs)
        self.check_summary(tabs)
        m = mh(list(tabs.values()))
        chi2, p = cmh(list(tabs.values()))
        self.assertEqual(round(m, 2), 0.64)
        self.assertEqual(round(p, 4), 0.0066)
        self.assertEqual(tabs["Cereals"], [82, 47, 1788, 429])
        self.assertEqual(round(odds(*tabs["Cereals"]), 2), 0.42)


class TestRetail(StrataCase):
    csv_name = "cooc_strata_retail.csv"
    summary_key = "retail_by_product"

    @classmethod
    def setUpClass(cls):
        cls.tabs = retail_strata()
        cls.inf = [t for t in cls.tabs.values() if informative(t)]

    def test_gate_and_strata(self):
        self.assertEqual(len(load_csv(RETAIL)), 1886)
        self.assertEqual(pooled(self.tabs), (275, 40, 280, 348))
        self.assertEqual(sum(sum(t) for t in self.tabs.values()), 943)
        self.assertEqual((len(self.tabs), len(self.inf), sum(sum(t) for t in self.inf)),
                         (21, 8, 517))
        self.assertEqual(sum(t[1] for t in self.inf), 16)
        self.check_csv(self.tabs)
        self.check_summary(self.tabs)

    def test_m1_m2(self):
        m = mh(list(self.tabs.values()))
        chi2, p = cmh(list(self.tabs.values()))
        po = odds(*pooled(self.tabs))
        self.assertEqual((round(po, 2), round(m, 2), round(chi2, 2), round(p, 2)),
                         (8.54, 1.40, 0.77, 0.38))
        self.assertLessEqual(m, math.sqrt(po))       # M1 met
        self.assertGreaterEqual(p, 0.05)             # M2 missed
        self.assertEqual(round(100 * (1 - math.log(m) / math.log(po))), 84)

    def test_interval(self):
        lo, hi = rbg_interval(self.inf)
        self.assertAlmostEqual(lo, 0.7248, delta=0.001)   # printed 0.72
        self.assertAlmostEqual(hi, 2.702, delta=0.002)    # printed 2.70
        self.assertLess(hi, odds(*pooled(self.tabs)))

    def test_composition(self):
        t = self.tabs
        self.assertEqual(t["Flour - Wheat"], [55, 0, 5, 0])
        self.assertEqual(t["Cereal - Adult"], [107, 3, 49, 3])
        neither = {k: t[k][3] for k in ("Wine", "Infant Formula - Dairy", "Fig", "Date",
                                        "Apricot", "Raisin")}
        self.assertEqual(neither, {"Wine": 136, "Infant Formula - Dairy": 88, "Fig": 28,
                                   "Date": 27, "Apricot": 10, "Raisin": 10})
        self.assertEqual(sum(neither.values()), 299)
        self.assertEqual([round(odds(*t[k]), 2) for k in ("Cereal - Adult", "Beer",
                                                           "Infant Food - Cereal",
                                                           "Chips - Corn")],
                         [2.18, 0.78, 2.03, 0.24])


class TestSealedRecord(unittest.TestCase):
    def test_tally(self):
        s = load_json(SUMMARY)
        self.assertEqual((s["n_graded"], s["n_met"]), (5, 4))
        met = {p["id"]: p["met"] for p in s["predictions"]}
        self.assertEqual(met, {"G": True, "M1": True, "M2": False, "M3": True, "M4": True})
        self.assertTrue(all(s["predictions"][0]["observed"].values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
