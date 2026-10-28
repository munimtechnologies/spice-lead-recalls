#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/ota-grain-2018-0.1.0-result.md.

Rebuilds every report row the labels identify (C1-C10), the blind predictions P1-P6, the
exploratory reconciliation with the survey report's Table 2, and the cross-method tables (the
Mantel-Haenszel, CMH, Robins-Breslow-Greenland and cracker Fisher figures) from the committed
per-sample table data/ota_grain_2018_samples.csv and data/ota_grain_2018_crossmethod.csv with its
own code (it does not import the grader), and checks them against the sealed grader record
data/ota_grain_2018_summary.json. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import math
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "ota_grain_2018_samples.csv")
CROSS = os.path.join(DATA, "ota_grain_2018_crossmethod.csv")
SUMMARY = os.path.join(DATA, "ota_grain_2018_summary.json")

CUT = 0.8
RYE = ("Rye Products", "Flour - rye")
KAMUT = ("Kamut Products", "Grain - Kamut")
OAT = ("Bran - Oat", "Oatmeal", "Oat Products", "Flour - Oat")
GRAIN_BASED = ("Bakery Product - Cookie", "Crackers", "Baking Mixes", "Infant Food - Cereal",
               "Pasta - Dry", "Cereal - Children", "Crispbread/Crouton", "Cereal")
LESS_COMMON = RYE + KAMUT + ("Buckwheat Products", "Quinoa Products", "Flour - Other")
GRAIN_ROWS = {"buckwheat": ("Buckwheat Products",), "kamut": KAMUT, "oat": OAT,
              "quinoa": ("Quinoa Products",), "rice": ("Grain - Rice",), "rye": RYE}

# Printed rows: (labels, n, positives or percent, min, max, avg).
R20 = {
    "C1": (RYE, 25, 15, "0.050", "1.9", "0.24"),
    "C2": (("Baking Mixes",), 28, 9, "0.051", "0.46", "0.16"),
    "C3": (("Infant Food - Cereal",), 28, 5, "0.050", "0.17", "0.077"),
    "C4": (("Pasta - Dry",), 28, 21, "0.049", "0.34", "0.18"),
}
R22 = {
    "C6": (LESS_COMMON, 100, 44, "0.05", "7.6", "1.0"),
    "C7": (OAT, 97, 54, "0.05", "1.6", "0.26"),
    "C8": (("Grain - Rice",), 99, 14, "0.049", "11", "1.1"),
    "C9": (("Wheat Products",), 29, 62, "0.06", "1.5", "0.4"),
    "C10": (GRAIN_BASED, 171, 54, "0.042", "2.2", "0.24"),
}
# R20 Table 2 (n, positives) by grain row; "wheat" is every label outside GRAIN_ROWS.
R20_TABLE2 = {"buckwheat": (25, 11), "kamut": (26, 10), "oat": (100, 55), "quinoa": (25, 8),
              "rice": (98, 13), "rye": (25, 15), "wheat": (196, 107)}
R20_TABLE5_RICE_POS = 14
SHARED = ["Buckwheat Products", "Crackers", "Grain - Kamut", "Kamut Products", "Pasta - Dry",
          "Quinoa Products", "Rye Products"]


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_samples():
    with open(SAMPLES, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["detected"] = r["detected"] == "1"
        r["ota"] = float(r["ota_ng_g"])
    return rows


def load_cross():
    with open(CROSS, newline="", encoding="utf-8-sig") as fh:
        return {r["product"]: {k: int(v) for k, v in r.items() if k != "product"}
                for r in csv.DictReader(fh)}


def pick(rows, labels):
    return [r for r in rows if r["product"] in labels]


def stats(rows):
    pos = [r["ota"] for r in rows if r["detected"]]
    return {"n": len(rows), "pos": len(pos), "min": min(pos) if pos else None,
            "max": max(pos) if pos else None, "avg": sum(pos) / len(pos) if pos else None,
            "ge_cut": sum(1 for v in pos if v >= CUT - 1e-9)}


def half_unit(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def matches(x, printed):
    return abs(x - float(printed)) <= half_unit(printed) + 1e-9


def pct(pos, n):
    return int(100 * pos / n + 0.5)


def mh(tabs):
    return (sum(a * d / (a + b + c + d) for a, b, c, d in tabs)
            / sum(b * c / (a + b + c + d) for a, b, c, d in tabs))


def cmh(tabs):
    diff = var = 0.0
    for a, b, c, d in tabs:
        n = a + b + c + d
        diff += a - (a + b) * (a + c) / n
        var += (a + b) * (c + d) * (a + c) * (b + d) / (n * n * (n - 1))
    chi2 = max(0.0, abs(diff) - 0.5) ** 2 / var
    return chi2, math.erfc(math.sqrt(chi2 / 2))


def rbg_interval(tabs, z=1.959964):
    """Robins-Breslow-Greenland 95% interval for the Mantel-Haenszel odds ratio."""
    sr = ss = spr = sps_qr = sqs = 0.0
    for a, b, c, d in tabs:
        n = a + b + c + d
        r, s, p, q = a * d / n, b * c / n, (a + d) / n, (b + c) / n
        sr += r
        ss += s
        spr += p * r
        sps_qr += p * s + q * r
        sqs += q * s
    var = spr / (2 * sr * sr) + sps_qr / (2 * sr * ss) + sqs / (2 * ss * ss)
    centre = math.log(sr / ss)
    return math.exp(centre - z * math.sqrt(var)), math.exp(centre + z * math.sqrt(var))


def fisher_two_sided(a, b, c, d):
    r1, c1, n = a + b, a + c, a + b + c + d

    def p(k):
        return math.comb(c1, k) * math.comb(n - c1, r1 - k) / math.comb(n, r1)

    obs = p(a)
    ks = range(max(0, c1 - (n - r1)), min(r1, c1) + 1)
    return sum(p(k) for k in ks if p(k) <= obs * (1 + 1e-7))


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_samples()
        cls.cross = load_cross()
        cls.s = load_json(SUMMARY)
        cls.a = cls.s["analysis"]


class TestTable(Base):
    def test_shape(self):
        self.assertEqual(len(self.rows), 496)
        self.assertEqual(len({r["sample"] for r in self.rows}), 496)
        for r in self.rows:
            self.assertEqual(r["detected"], r["ota"] > 0, msg=r["sample"])
        products, origins = {}, {}
        for r in self.rows:
            products[r["product"]] = products.get(r["product"], 0) + 1
            origins[r["origin"]] = origins.get(r["origin"], 0) + 1
        self.assertEqual(products, self.s["census"]["OG"]["products"])
        self.assertEqual(origins, self.s["census"]["OG"]["origins"])
        self.assertEqual((origins["CANADA"], origins["UNKNOWN"]), (92, 232))
        self.assertEqual(sum(r["detected"] for r in self.rows), 220)

    def test_gate_and_tally(self):
        self.assertTrue(all(self.s["predictions"][0]["observed"].values()))
        self.assertEqual(len(self.s["predictions"][0]["observed"]), 17)
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (17, 16))
        met = {p["id"]: p["met"] for p in self.s["predictions"]}
        self.assertEqual({k for k, v in met.items() if not v}, {"P5"})
        og = self.s["census"]["OG"]
        (token, count), = og["text_tokens"].items()     # one non-detect token
        self.assertTrue(token.startswith("Not Detected/ Non-d"), msg=token)
        self.assertEqual(count, 276)
        self.assertEqual(og["units"], {"ng/g": 496})
        self.assertEqual(og["value_kinds"], {"pos": 220, "text": 276})

    def test_labels_match_sealed_record(self):
        for lab, rec in self.a["labels"].items():
            st = stats(pick(self.rows, (lab,)))
            self.assertEqual((st["n"], st["pos"], st["ge_cut"]),
                             (rec["n"], rec["pos"], rec["ge_cut"]), msg=lab)
            for k in ("min", "max", "avg"):
                if rec[k] is None:
                    self.assertIsNone(st[k], msg=lab)
                else:
                    self.assertAlmostEqual(st[k], rec[k], places=9, msg=lab)


class TestReportRows(Base):
    def test_r20_rows(self):
        for rid, (labels, n, pos, mn, mx, avg) in R20.items():
            st = stats(pick(self.rows, labels))
            self.assertEqual((st["n"], st["pos"]), (n, pos), msg=rid)
            for k, printed in (("min", mn), ("max", mx), ("avg", avg)):
                self.assertTrue(matches(st[k], printed), msg=f"{rid} {k} {st[k]} {printed}")

    def test_r22_rows(self):
        for rid, (labels, n, percent, mn, mx, avg) in R22.items():
            st = stats(pick(self.rows, labels))
            self.assertEqual((st["n"], pct(st["pos"], st["n"])), (n, percent), msg=rid)
            for k, printed in (("min", mn), ("max", mx), ("avg", avg)):
                self.assertTrue(matches(st[k], printed), msg=f"{rid} {k} {st[k]} {printed}")
        self.assertEqual([stats(pick(self.rows, R22[k][0]))["pos"]
                          for k in ("C6", "C7", "C8", "C9", "C10")], [44, 52, 14, 18, 92])

    def test_overall_range(self):
        st = stats(self.rows)
        self.assertTrue(matches(st["min"], "0.042") and matches(st["max"], "11"))
        self.assertEqual((st["min"], st["max"]), (0.042, 11.1))

    def test_contradictions_settled(self):
        rice = stats(pick(self.rows, ("Grain - Rice",)))
        self.assertEqual((rice["n"], rice["pos"]), (99, 14))
        oat = stats(pick(self.rows, OAT))
        self.assertEqual(round(oat["avg"], 2), 0.26)
        self.assertLess(oat["max"], 2.6)                 # Table 4's 2.6 exceeds the maximum
        self.assertEqual(pct(220, 496), 44)
        for pos, n in ((219, 495), (220, 495), (220, 496)):
            self.assertNotEqual(pct(pos, n), 45)         # "45%" follows from no count

    def test_every_row_met_in_record(self):
        for rid in list(R20) + list(R22):
            self.assertTrue(self.a["rows"][rid]["ok"], msg=rid)


class TestReconciliation(Base):
    def test_r20_table2(self):
        grain_labels = {lab for labels in GRAIN_ROWS.values() for lab in labels}
        fam = {k: stats(pick(self.rows, v)) for k, v in GRAIN_ROWS.items()}
        fam["wheat"] = stats([r for r in self.rows if r["product"] not in grain_labels])
        got = {k: (v["n"], v["pos"]) for k, v in fam.items()}
        self.assertEqual(got, {"buckwheat": (23, 9), "kamut": (25, 10), "oat": (97, 52),
                               "quinoa": (24, 8), "rice": (99, 14), "rye": (25, 15),
                               "wheat": (203, 112)})
        delta = {k: (R20_TABLE2[k][0] - got[k][0], R20_TABLE2[k][1] - got[k][1]) for k in got}
        self.assertEqual(delta, {"buckwheat": (2, 2), "kamut": (1, 0), "oat": (3, 3),
                                 "quinoa": (1, 0), "rice": (-1, -1), "rye": (0, 0),
                                 "wheat": (-7, -5)})
        moved = [delta[k] for k in ("buckwheat", "kamut", "oat", "quinoa")]
        self.assertEqual((sum(m[0] for m in moved), sum(m[1] for m in moved)), (7, 5))
        self.assertEqual(sum(v[0] for v in R20_TABLE2.values()), 495)
        self.assertEqual(sum(v[1] for v in R20_TABLE2.values()), 219)
        self.assertEqual(sum(v[1] for v in R20_TABLE2.values()) - 13 + R20_TABLE5_RICE_POS,
                         sum(v[1] for v in got.values()))

    def test_crackers_crispbread(self):
        st = stats(pick(self.rows, ("Crackers", "Crispbread/Crouton")))
        self.assertEqual((st["n"], st["pos"], st["min"], st["max"]), (31, 23, 0.047, 2.21))
        self.assertEqual(round(st["avg"], 3), 0.388)
        self.assertEqual((40 - st["n"], 30 - st["pos"]), (9, 7))


class TestPredictions(Base):
    def test_p1_p2(self):
        bw = stats(pick(self.rows, ("Buckwheat Products",)))
        qu = stats(pick(self.rows, ("Quinoa Products",)))
        ka = stats(pick(self.rows, KAMUT))
        self.assertEqual((bw["max"], bw["pos"], qu["max"], qu["pos"]), (7.62, 9, 5.75, 8))
        self.assertTrue(matches(bw["max"], "7.6") and matches(qu["max"], "5.8"))
        self.assertEqual((ka["n"], ka["pos"], ka["max"]), (25, 10, 1.24))

    def test_p3_over_3(self):
        over = sorted(((r["ota"], r["product"]) for r in self.rows if r["ota"] > 3),
                      reverse=True)
        self.assertEqual(over, [(11.1, "Grain - Rice"), (7.62, "Buckwheat Products"),
                                (5.75, "Quinoa Products"), (5.68, "Buckwheat Products"),
                                (5.35, "Buckwheat Products"), (4.34, "Quinoa Products"),
                                (3.41, "Buckwheat Products")])
        outside = [o for o in over if o[1] not in ("Buckwheat Products", "Quinoa Products")]
        self.assertEqual(outside, [(11.1, "Grain - Rice")])
        self.assertEqual(sum(1 for r in pick(self.rows, ("Infant Food - Cereal",))
                             if r["ota"] > 0.5), 0)
        self.assertEqual(sum(1 for r in pick(self.rows, ("Bran - Oat",)) if r["ota"] > 7), 0)

    def test_p5_crackers_missed(self):
        ck = pick(self.rows, ("Crackers",))
        hits = sorted(r["ota"] for r in ck if r["ota"] >= CUT)
        self.assertEqual((len(ck), sum(r["detected"] for r in ck)), (29, 21))
        self.assertEqual(hits, [0.84, 0.855, 1.59, 2.21])
        self.assertGreater(len(hits), 3)                 # registered: at most 3
        self.assertEqual(max(r["ota"] for r in ck if r["ota"] < CUT), 0.74)

    def test_p6(self):
        self.assertEqual(stats(self.rows)["ge_cut"], 27)
        self.assertEqual(self.a["overall"]["ge_cut"], 27)


class TestCrossMethod(Base):
    def tables(self, at_cut):
        out = []
        for lab in SHARED:
            og = pick(self.rows, (lab,))
            hit = sum(1 for r in og if r["detected"] and (not at_cut or r["ota"] >= CUT))
            mm = self.cross[lab]
            out.append((hit, len(og) - hit, mm["mm_detected"], mm["mm_n"] - mm["mm_detected"]))
        return out

    def test_csv_matches_samples_and_record(self):
        self.assertEqual(list(self.cross), SHARED)
        for lab in SHARED:
            st = stats(pick(self.rows, (lab,)))
            c = self.cross[lab]
            self.assertEqual((c["og_n"], c["og_detected"], c["og_ge_0_8"]),
                             (st["n"], st["pos"], st["ge_cut"]), msg=lab)
        cut, own = self.tables(True), self.tables(False)
        rec = self.a["cross"]
        self.assertEqual([list(t) for t in cut], [rec["at_cut"][lab] for lab in SHARED])
        self.assertEqual([list(t) for t in own], [rec["own_limits"][lab] for lab in SHARED])
        self.assertEqual(sum(self.cross[lab]["mm_detected"] for lab in SHARED), 10)

    def test_pooled(self):
        cut, own = self.tables(True), self.tables(False)
        pooled_cut = [sum(t[i] for t in cut) for i in range(4)]
        pooled_own = [sum(t[i] for t in own) for i in range(4)]
        self.assertEqual(pooled_cut, [15, 135, 10, 237])
        self.assertEqual(pooled_own, [82, 68, 10, 237])
        self.assertEqual(pooled_cut, self.a["cross"]["at_cut_pooled"])
        a, b, c, d = pooled_cut
        self.assertEqual(round(a * d / (b * c), 2), 2.63)

    def test_p4_cmh_at_cut(self):
        tabs = self.tables(True)
        m = mh(tabs)
        chi2, p = cmh(tabs)
        rec = self.a["cross"]
        self.assertAlmostEqual(m, rec["at_cut_mh_or"], places=9)
        self.assertAlmostEqual(chi2, rec["at_cut_cmh_chi2"], places=9)
        self.assertAlmostEqual(p, rec["at_cut_cmh_p"], places=9)
        self.assertEqual((round(m, 2), round(chi2, 2), round(p, 3)), (2.09, 2.11, 0.146))
        self.assertGreaterEqual(p, 0.05)                 # P4 held
        lo, hi = rbg_interval(tabs)
        self.assertEqual((round(lo, 2), round(hi, 2)), (0.86, 5.08))

    def test_own_limits(self):
        tabs = self.tables(False)
        m = mh(tabs)
        chi2, p = cmh(tabs)
        self.assertAlmostEqual(m, self.a["cross"]["own_mh_or"], places=9)
        self.assertAlmostEqual(chi2, self.a["cross"]["own_cmh_chi2"], places=9)
        self.assertEqual((round(m, 1), round(chi2, 1)), (26.0, 129.2))
        self.assertLess(p, 1e-25)

    def test_crackers_and_pasta_at_cut(self):
        tabs = dict(zip(SHARED, self.tables(True)))
        self.assertEqual(tabs["Crackers"], (4, 25, 2, 99))
        self.assertEqual(round(4 * 99 / (25 * 2), 2), 7.92)
        self.assertEqual(round(fisher_two_sided(*tabs["Crackers"]), 4), 0.0222)
        self.assertEqual(tabs["Pasta - Dry"], (0, 28, 2, 60))
        self.assertEqual(max(r["ota"] for r in pick(self.rows, ("Pasta - Dry",))), 0.342)


if __name__ == "__main__":
    unittest.main(verbosity=2)
