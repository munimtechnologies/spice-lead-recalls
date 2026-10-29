#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/tds-ota-2008-0.1.0-result.md.

Rebuilds the census counts, the consistency checks C1-C5, the blind predictions P1, P2, P4 and P5
(the top-20 ranking and the Spearman correlation computed from scratch), and the EU reference
count from the committed per-composite table data/tds_ota_2008_samples.csv with its own code (it
does not import the grader), and checks them against the sealed grader record
data/tds_ota_2008_summary.json. P3 (the English/French agreement) is verified from the sealed
record, since the committed CSV holds the English rows only. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import math
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "tds_ota_2008_samples.csv")
SUMMARY = os.path.join(DATA, "tds_ota_2008_summary.json")

ND = "nd"
# The registered cereal-containing codes (Table 4 of the paper): every FF row plus the infant
# cereal, the cereal-plus-vegetable-plus-meat dinner and the five fast foods.
CEREAL_EXTRA = {"LL01", "LL03", "NN01", "NN03", "NN04", "NN05", "NN06"}


def load_rows():
    with open(SAMPLES, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["value"] = float(r["value"])
        r["lod"] = float(r["lod"]) if r["lod"] != "" else None
        r["loq"] = float(r["loq"]) if r["loq"] != "" else None
    return rows


def half_unit(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def matches(x, printed):
    return x is not None and abs(x - float(printed)) <= half_unit(printed) + 1e-9


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    return sxy / math.sqrt(sxx * syy)


def count(rows, col):
    out = {}
    for r in rows:
        out[r[col]] = out.get(r[col], 0) + 1
    return out


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_rows()
        with open(SUMMARY, encoding="utf-8") as fh:
            cls.s = json.load(fh)
        cls.a = cls.s["analysis"]
        cls.census = cls.s["census"]
        cls.preds = {p["id"]: p for p in cls.s["predictions"]}
        cls.det = [r for r in cls.rows if r["kind"] == "det"]


class TestShape(Base):
    def test_census(self):
        self.assertEqual(len(self.rows), 137)
        self.assertEqual(len({r["sample"] for r in self.rows}), 137)
        self.assertEqual(count(self.rows, "city"), {"Quebec City": 69, "Calgary": 68})
        self.assertEqual(self.census["cities"], {"Quebec City": 69, "Calgary": 68})
        self.assertEqual(count(self.rows, "unit"), {"ng/g": 113, "ng/ml": 24})
        self.assertEqual(count(self.rows, "kind"), {"det": 108, "below": 29})
        self.assertEqual(self.census["kinds"], {"det": 108, "below": 29})
        # Every code carries both city-years except the three the census found missing.
        by = {}
        for r in self.rows:
            by.setdefault(r["code"], set()).add(r["year"])
        shared = {c for c, ys in by.items() if ys == {"2008", "2009"}}
        self.assertEqual(len(shared), 67)
        self.assertEqual(len(shared), self.a["n_shared_foods"])

    def test_gate_and_tally(self):
        gate = self.preds["G"]
        self.assertTrue(all(gate["observed"].values()))
        self.assertEqual(len(gate["observed"]), 9)
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (11, 7))
        met = {p["id"]: p["met"] for p in self.s["predictions"]}
        self.assertEqual(list(met),
                         ["G", "C1", "C2", "C3", "C4", "C5", "P1", "P2", "P3", "P4", "P5"])
        self.assertEqual({k for k, v in met.items() if not v}, {"C1", "C4", "C5", "P1"})
        prov = self.s["provenance"]
        self.assertEqual(prov["EN"]["sha256"],
                         "3d80ade4162746fc4afac633951eead03b79a9b77a0bd37500fff7ffc06aaf79")
        self.assertEqual(prov["FR"]["sha256"],
                         "6fd5a22576fb0d1509712ecb92a6fa477c767ce5097d22e8965ab1fb59cda171")


class TestConsistency(Base):
    def test_c1_detected_vs_table3(self):
        # A mismatch: the file detects where Table 3 is n.d., or is below-limit where it prints.
        bad = [r for r in self.rows if (r["kind"] == "det") != (r["table3"] != ND)]
        self.assertEqual(len(bad), 14)
        self.assertEqual(len(self.a["c1_mismatch"]), 14)
        # Every one is a file detection against a Table 3 "n.d." between 0.001 and 0.004 ng/g.
        for r in bad:
            self.assertEqual(r["kind"], "det")
            self.assertEqual(r["table3"], ND)
            self.assertTrue(0.001 - 1e-12 <= r["value"] <= 0.004 + 1e-12)
        by_year = count(bad, "year")
        self.assertEqual(by_year, {"2008": 7, "2009": 7})

    def test_c2_values_match_table3(self):
        checked, bad = 0, []
        for r in self.det:
            if r["table3"] != ND:
                checked += 1
                if not matches(r["value"], r["table3"]):
                    bad.append(r["sample"])
        self.assertEqual(checked, 94)
        self.assertEqual(bad, [])
        self.assertEqual(checked, self.a["c2_checked"])
        self.assertEqual(self.a["c2_mismatch"], [])

    def test_c3_maxima(self):
        for year, code, printed in (("2008", "HH17", "2.3"), ("2009", "FF12", "1.7")):
            d = [r for r in self.det if r["year"] == year]
            top = max(d, key=lambda r: r["value"])
            self.assertEqual(top["code"], code)
            self.assertTrue(matches(top["value"], printed))
            self.assertEqual(self.a["maxima"][year]["code"], code)
        self.assertAlmostEqual(self.a["maxima"]["2008"]["value"], 2.348, places=9)
        self.assertAlmostEqual(self.a["maxima"]["2009"]["value"], 1.695, places=9)

    def test_c4_c5_text_counts(self):
        det_by_year = count(self.det, "year")
        self.assertEqual(det_by_year, {"2008": 56, "2009": 52})
        self.assertEqual(self.a["detected"], {"2008": 56, "2009": 52})
        above_loq = {}
        for r in self.det:
            if r["loq"] is not None and r["value"] > r["loq"] + 1e-12:
                above_loq[r["year"]] = above_loq.get(r["year"], 0) + 1
        self.assertEqual(above_loq, {"2008": 47, "2009": 40})
        self.assertEqual(self.a["above_file_loq"], {"2008": 47, "2009": 40})
        # The text's figures (51 each; 47 and 43 above the LOQ) are not reproduced except 2008.
        self.assertNotEqual(self.a["detected"], {"2008": 51, "2009": 51})


class TestPredictions(Base):
    def test_p1_follows_table3(self):
        # P1 predicted Table 3's counts (49, 45); the file has more (the 14 extra detections).
        self.assertEqual(self.a["detected"], {"2008": 56, "2009": 52})
        self.assertFalse(self.preds["P1"]["met"])

    def test_p2_ng_ml_rows(self):
        got = sorted([r["code"], r["year"]] for r in self.rows if r["unit"] == "ng/ml")
        self.assertEqual(len(got), 24)
        summ = sorted(self.a["ng_ml"])
        self.assertEqual(got, summ)
        self.assertEqual(sorted(self.a["expected_ng_ml"]), summ)

    def test_p3_en_fr_from_record(self):
        p3 = self.preds["P3"]
        self.assertTrue(p3["met"])
        self.assertEqual(p3["observed"]["paired"], 137)
        self.assertEqual(p3["observed"]["op_disagree"], [])
        self.assertEqual(p3["observed"]["value_disagree"], [])
        self.assertTrue(p3["observed"]["all_agree"])

    def test_p4_top20_cereal(self):
        by = {}
        for r in self.rows:
            by.setdefault(r["code"], {})[r["year"]] = r["value"]
        pairs = {c: (v["2008"], v["2009"]) for c, v in by.items() if len(v) == 2}
        top = sorted(pairs, key=lambda c: (-(pairs[c][0] + pairs[c][1]) / 2, c))[:20]
        cereal = sum(1 for c in top if c.startswith("FF") or c in CEREAL_EXTRA)
        self.assertEqual(cereal, 16)
        self.assertEqual(cereal, self.a["top20_cereal"])
        self.assertEqual(sorted(top), sorted(row["code"] for row in self.a["top20"]))

    def test_p5_spearman(self):
        by = {}
        for r in self.rows:
            by.setdefault(r["code"], {})[r["year"]] = r["value"]
        codes = sorted(c for c, v in by.items() if len(v) == 2)
        rho = spearman([by[c]["2008"] for c in codes], [by[c]["2009"] for c in codes])
        self.assertGreaterEqual(rho, 0.7)
        self.assertAlmostEqual(rho, self.a["spearman_2008_2009"], places=9)


class TestEU(Base):
    def test_no_eu_exceedance(self):
        self.assertEqual(self.a["eu_reference_over"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
