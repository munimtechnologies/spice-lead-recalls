#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/multimyco-2018-0.1.0-result.md.

Recounts every toxin group, the 387 samples with a detection, the crackers OTA figure, the
largest group count and the DON x fumonisin tables (pooled, corn labels, other labels, and the
Mantel-Haenszel / CMH figures within the 30 product labels) from the committed per-sample table
data/multimyco_2018_samples.csv with its own code (it does not import the grader), and checks
them and the DON arithmetic against the sealed grader record data/multimyco_2018_summary.json.
Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import math
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "multimyco_2018_samples.csv")
SUMMARY = os.path.join(DATA, "multimyco_2018_summary.json")

GROUPS = ("DON", "Fumonisins", "Ergot", "Zearalenone", "OTA", "CPA", "STE", "Aflatoxins",
          "HT2T2", "NIV")
TABLE3 = {"DON": 306, "Fumonisins": 105, "Ergot": 46, "Zearalenone": 34, "OTA": 20, "CPA": 18,
          "STE": 12, "Aflatoxins": 11, "HT2T2": 8, "NIV": 7}
CORN = {"Flour - Corn", "Corn Products", "Corn Starch", "Cornmeal", "Chips - Corn"}


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_samples():
    with open(SAMPLES, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["n_groups"] = int(r["n_groups"])
        for g in GROUPS:
            r[g] = r[g] == "1"
    return rows


def cells(rows, x="DON", y="Fumonisins"):
    """(both, x only, y only, neither)."""
    t = [0, 0, 0, 0]
    for r in rows:
        t[0 if r[x] and r[y] else 1 if r[x] else 2 if r[y] else 3] += 1
    return tuple(t)


def odds(a, b, c, d):
    return a * d / (b * c)


def by_product(rows):
    out = {}
    for r in rows:
        out.setdefault(r["product"], []).append(r)
    return {k: cells(v) for k, v in sorted(out.items())}


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


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_samples()
        cls.s = load_json(SUMMARY)
        cls.a = cls.s["analysis"]


class TestTable(Base):
    def test_shape(self):
        self.assertEqual(len(self.rows), 750)
        self.assertEqual(len({r["sample"] for r in self.rows}), 750)
        for r in self.rows:
            self.assertEqual(r["n_groups"], sum(r[g] for g in GROUPS), msg=r["sample"])
        products, origins = {}, {}
        for r in self.rows:
            products[r["product"]] = products.get(r["product"], 0) + 1
            origins[r["origin"]] = origins.get(r["origin"], 0) + 1
        self.assertEqual(products, self.s["census"]["products"])
        self.assertEqual(origins, self.s["census"]["origins"])
        self.assertEqual((origins["CANADA"], origins["UNKNOWN"]), (155, 291))

    def test_gate_and_tally(self):
        self.assertTrue(all(self.s["predictions"][0]["observed"].values()))
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (10, 4))
        met = {p["id"]: p["met"] for p in self.s["predictions"]}
        self.assertEqual({k for k, v in met.items() if not v},
                         {"P1", "P2", "P3", "P4", "P7", "P8"})
        self.assertEqual({k for k, v in met.items() if v}, {"G", "C1", "P5", "P6"})


class TestCounts(Base):
    def test_any_detected_387(self):
        n_any = sum(1 for r in self.rows if r["n_groups"] > 0)
        self.assertEqual(n_any, 387)
        self.assertEqual(n_any, self.a["any_detected"])
        self.assertEqual(sum(1 for r in self.rows if r["n_groups"] == 0), 363)
        self.assertNotIn(n_any, (386, 388))

    def test_groups_against_table3(self):
        groups = {g: sum(1 for r in self.rows if r[g]) for g in GROUPS}
        self.assertEqual(groups, self.a["groups"])
        self.assertEqual(groups, {"DON": 306, "Fumonisins": 106, "Ergot": 46, "Zearalenone": 38,
                                  "OTA": 20, "CPA": 18, "STE": 12, "Aflatoxins": 10,
                                  "HT2T2": 8, "NIV": 7})
        off = {g: groups[g] - TABLE3[g] for g in GROUPS if groups[g] != TABLE3[g]}
        self.assertEqual(off, {"Fumonisins": 1, "Zearalenone": 4, "Aflatoxins": -1})

    def test_labels_detected(self):
        self.assertEqual(self.a["n_detected_analytes"], 18)
        self.assertIn("?-Zearalenol(ppb)", self.a["detected_analytes"])
        self.assertEqual(sorted(self.a["never_detected"]),
                         sorted(["15-acetyldeoxynivalenol", "3-acetyldeoxynivalenol",
                                 "Aflatoxin G2", "Diacetoxyscirpenol", "Fusarenon-X",
                                 "Neosolaniol"]))

    def test_don_average(self):
        don = self.a["analytes"]["DON"]
        self.assertEqual((don["n_detected"], don["max"]), (306, 2570.0))
        total = don["avg_pos"] * 306
        self.assertAlmostEqual(total, don["avg_all"] * 750, places=6)
        self.assertEqual(round(total), 55480)
        self.assertEqual(round(don["avg_pos"], 1), 181.3)
        self.assertLess(total, 281.5 * 306)                  # printed 282 is out of reach
        self.assertEqual(round(282 * 306 - total), 30812)

    def test_ota(self):
        self.assertEqual(self.a["ota_over_3"], 7)
        self.assertEqual(round(100 * (750 - 7) / 750, 1), 99.1)
        crackers = [r for r in self.rows if r["product"] == "Crackers"]
        self.assertEqual((len(crackers), sum(1 for r in crackers if r["OTA"])), (101, 2))
        self.assertEqual((self.a["crackers_n"], self.a["crackers_ota_n"]), (101, 2))
        ota = self.a["analytes"]["OTA"]
        self.assertEqual((ota["max"], ota["n_detected"]), (33.8, 20))

    def test_most_groups(self):
        top = max(r["n_groups"] for r in self.rows)
        self.assertEqual(top, 6)
        best = [r for r in self.rows if r["n_groups"] == top]
        self.assertEqual([(r["sample"], r["product"]) for r in best],
                         [("C2018MUMY00663", "Flour - Corn")])
        self.assertEqual({g for g in GROUPS if best[0][g]},
                         {"DON", "Fumonisins", "Zearalenone", "CPA", "Aflatoxins", "NIV"})


class TestCooccurrence(Base):
    def test_pooled_and_corn(self):
        pooled = cells(self.rows)
        self.assertEqual(pooled, (63, 243, 43, 401))
        self.assertEqual(list(pooled), self.a["don_fumonisin"]["pooled"])
        self.assertEqual(round(odds(*pooled), 2), 2.42)
        corn = cells([r for r in self.rows if r["product"] in CORN])
        other = cells([r for r in self.rows if r["product"] not in CORN])
        self.assertEqual((corn, other), ((51, 10, 36, 53), (12, 233, 7, 348)))
        self.assertEqual((round(odds(*corn), 2), round(odds(*other), 2)), (7.51, 2.56))
        self.assertEqual(corn[0] + corn[2], 87)
        starch = [r for r in self.rows if r["product"] == "Corn Starch"]
        self.assertEqual(len(starch), 25)
        self.assertFalse(any(r["DON"] or r["Fumonisins"] for r in starch))

    def test_within_labels(self):
        tabs = by_product(self.rows)
        self.assertEqual(len(tabs), 30)
        m = mh(list(tabs.values()))
        chi2, p = cmh(list(tabs.values()))
        rec = self.a["don_fumonisin"]
        self.assertEqual(rec["n_strata"], 30)
        self.assertAlmostEqual(m, rec["mh_or"], places=9)
        self.assertAlmostEqual(chi2, rec["cmh_chi2"], places=9)
        self.assertAlmostEqual(p, rec["cmh_p"], places=9)
        self.assertEqual((round(m, 2), round(chi2, 1), round(p, 4)), (2.48, 10.0, 0.0016))
        self.assertGreater(abs(math.log(m)), abs(math.log(odds(*cells(self.rows)))))  # P7 missed


if __name__ == "__main__":
    unittest.main(verbosity=2)
