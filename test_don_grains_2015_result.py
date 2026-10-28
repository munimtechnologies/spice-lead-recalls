#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/don-grains-2015-0.1.0-result.md.

Rebuilds the label groups, the consistency check C1, the blind predictions P1-P7, the
cross-method tables (the Mantel-Haenszel, CMH and Robins-Breslow-Greenland figures) and the
exploratory origin and millet figures from the committed per-sample table
data/don_grains_2015_samples.csv and data/don_grains_2015_crossmethod.csv with its own code (it
does not import the grader), and checks them against the sealed grader record
data/don_grains_2015_summary.json. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import math
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "don_grains_2015_samples.csv")
CROSS = os.path.join(DATA, "don_grains_2015_crossmethod.csv")
SUMMARY = os.path.join(DATA, "don_grains_2015_summary.json")

CUT, EU_LOW, EU_HIGH = 10.0, 400.0, 750.0
SG = ("Grain - Barley", "Barley Products", "Grain - Rye", "Rye Products", "Flour - rye",
      "Grain - Kamut", "Kamut Products", "Spelt", "Spelt Products")
PS = ("Grain - Buckwheat", "Buckwheat Products", "Grain - Quinoa", "Quinoa Products",
      "Amaranth Products", "Arrowroot Products")
OG = ("Millet", "Millet Products", "Teff Products", "Grain - Other", "Flour - Other")
MA = ("Meat Alternative",)
SHARED = ["Amaranth Products", "Arrowroot Products", "Barley Products", "Buckwheat Products",
          "Grain - Barley", "Grain - Buckwheat", "Grain - Kamut", "Grain - Other",
          "Grain - Quinoa", "Grain - Rye", "Kamut Products", "Millet", "Millet Products",
          "Quinoa Products", "Rye Products", "Spelt", "Spelt Products", "Teff Products"]


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_samples():
    with open(SAMPLES, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["detected"] = r["detected"] == "1"
        r["don"] = float(r["don_ng_g"])
    return rows


def load_cross():
    with open(CROSS, newline="", encoding="utf-8-sig") as fh:
        return {r["product"]: {k: int(v) for k, v in r.items() if k != "product"}
                for r in csv.DictReader(fh)}


def group_of(product):
    for name, labels in (("SG", SG), ("PS", PS), ("OG", OG), ("MA", MA)):
        if product in labels:
            return name
    return "PU"                                          # every other label is a pulse or soy


def pick(rows, labels):
    return [r for r in rows if r["product"] in labels]


def median(xs):
    s = sorted(xs)
    m = len(s) // 2
    return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2


def stats(rows):
    pos = [r["don"] for r in rows if r["detected"]]
    return {"n": len(rows), "pos": len(pos),
            "min": min(pos) if pos else None, "max": max(pos) if pos else None,
            "avg": sum(pos) / len(pos) if pos else None,
            "median": median(pos) if pos else None,
            "below_cut": sum(1 for v in pos if v < CUT - 1e-9),
            "ge_cut": sum(1 for v in pos if v >= CUT - 1e-9),
            "ge_400": sum(1 for v in pos if v >= EU_LOW - 1e-9),
            "ge_750": sum(1 for v in pos if v >= EU_HIGH - 1e-9)}


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

    def group(self, name):
        return [r for r in self.rows if group_of(r["product"]) == name]

    def assertStatsEqual(self, st, rec, msg):
        for k in ("n", "pos", "below_cut", "ge_cut", "ge_400", "ge_750"):
            self.assertEqual(st[k], rec[k], msg=f"{msg} {k}")
        for k in ("min", "max", "avg", "median"):
            if rec[k] is None:
                self.assertIsNone(st[k], msg=f"{msg} {k}")
            else:
                self.assertAlmostEqual(st[k], rec[k], places=9, msg=f"{msg} {k}")


class TestTable(Base):
    def test_shape(self):
        self.assertEqual(len(self.rows), 997)
        self.assertEqual(len({r["sample"] for r in self.rows}), 997)
        for r in self.rows:
            self.assertEqual(r["detected"], r["don"] > 0, msg=r["sample"])
            self.assertEqual(r["group"], group_of(r["product"]), msg=r["sample"])
        census = self.s["census"]["DG"]
        for col, key in (("product", "products"), ("origin", "origins"),
                         ("function", "functions")):
            counts = {}
            for r in self.rows:
                counts[r[col]] = counts.get(r[col], 0) + 1
            self.assertEqual(counts, census[key], msg=col)
        self.assertEqual(sum(r["detected"] for r in self.rows), 457)
        dom = [r for r in self.rows if r["function"] == "Domestic"]
        self.assertEqual(len(dom), 254)
        self.assertTrue(all(r["origin"] == "CANADA" for r in dom))

    def test_gate_and_tally(self):
        gate = self.s["predictions"][0]
        self.assertEqual(gate["id"], "G")
        self.assertEqual(len(gate["observed"]), 16)
        self.assertTrue(all(gate["observed"].values()))
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (9, 7))
        met = {p["id"]: p["met"] for p in self.s["predictions"]}
        self.assertEqual(list(met), ["G", "C1", "P1", "P2", "P3", "P4", "P5", "P6", "P7"])
        self.assertEqual({k for k, v in met.items() if not v}, {"P1", "P4"})
        dg = self.s["census"]["DG"]
        self.assertEqual(dg["units"], {"ng/g": 997})
        self.assertEqual(dg["value_kinds"], {"pos": 457, "zero": 540})
        self.assertEqual(self.s["census"]["MM"]["value_kinds"], {"pos": 306, "zero": 444})

    def test_labels_and_groups_match_sealed_record(self):
        self.assertEqual(len(self.a["labels"]), 44)
        for lab, rec in self.a["labels"].items():
            self.assertStatsEqual(stats(pick(self.rows, (lab,))), rec, lab)
        for g in ("SG", "PS", "OG", "PU", "MA"):
            self.assertStatsEqual(stats(self.group(g)), self.a["groups"][g], g)
        self.assertStatsEqual(stats(self.rows), self.a["overall"], "overall")
        grains = [r for r in self.rows if group_of(r["product"]) in ("SG", "PS", "OG")]
        self.assertStatsEqual(stats(grains), self.a["grains"], "grains")


class TestPredictions(Base):
    def test_c1(self):
        pos = sum(r["detected"] for r in self.rows)
        self.assertEqual((len(self.rows), pos), (997, 457))
        self.assertEqual(int(100 * pos / 997 + 0.5), 46)
        self.assertTrue(454 <= pos <= 463)

    def test_headline_at_cut(self):
        st = stats(self.rows)
        self.assertEqual((st["below_cut"], st["ge_cut"]), (243, 214))
        self.assertEqual(st["min"], 0.412)
        self.assertEqual(round(100 * 214 / 997), 21)
        self.assertEqual(st["median"], 7.8)

    def test_p1_missed_by_one(self):
        pu = stats(self.group("PU"))
        self.assertEqual((pu["n"], pu["pos"], pu["ge_cut"], pu["max"]), (189, 29, 8, 33.8))
        self.assertGreater(pu["pos"], 0.15 * pu["n"])    # registered: at most 15% (28)
        self.assertEqual(int(0.15 * 189), 28)
        self.assertLess(pu["max"], 100.0)                # the level part held
        by_label = {}
        for r in self.group("PU"):
            by_label.setdefault(r["product"], []).append(r["detected"])
        pos = {lab: sum(v) for lab, v in by_label.items()}
        self.assertEqual(len(pos), 23)
        self.assertEqual(sum(1 for v in pos.values() if v > 0), 16)
        self.assertEqual((pos["Lentil"], pos["Infant Formula - Soy"], pos["Bean - Kidney"],
                          pos["Bean - Other"], pos["Flour - Soy"], pos["Soy Products"]),
                         (5, 4, 3, 3, 2, 2))
        formula = sorted(r["don"] for r in pick(self.rows, ("Infant Formula - Soy",))
                         if r["detected"])
        self.assertEqual(formula, [1.55, 2.7, 4.3, 13.3])

    def test_p2_p3(self):
        sg, ps = stats(self.group("SG")), stats(self.group("PS"))
        self.assertEqual((sg["n"], sg["pos"], ps["n"], ps["pos"]), (353, 304, 252, 38))
        ratio = (sg["pos"] / sg["n"]) / (ps["pos"] / ps["n"])
        self.assertEqual(round(ratio, 2), 5.71)
        self.assertGreaterEqual(sg["pos"] / sg["n"], 0.60)
        for lab in ("Arrowroot Products", "Quinoa Products"):
            self.assertEqual(stats(pick(self.rows, (lab,)))["pos"], 0, msg=lab)

    def test_p4_missed(self):
        top = sorted(((r["don"], r["product"]) for r in self.rows if r["detected"]),
                     reverse=True)[:5]
        self.assertEqual(top, [(5720.0, "Grain - Rye"), (4690.0, "Grain - Rye"),
                               (3330.0, "Rye Products"), (3010.0, "Rye Products"),
                               (1110.0, "Grain - Rye")])
        self.assertEqual(group_of(top[0][1]), "SG")      # the label part held
        self.assertGreaterEqual(top[0][0], 2000.0)       # registered: below 2,000 ppb
        self.assertEqual(self.a["max_sample"]["sample"], "C2015DEOV00249")

    def test_p5(self):
        grains = [r for r in self.rows if group_of(r["product"]) in ("SG", "PS", "OG")]
        st = stats(grains)
        self.assertEqual((st["n"], st["ge_750"], st["ge_400"]), (802, 9, 30))
        self.assertTrue(st["ge_750"] <= 16 and st["ge_400"] <= 40)
        high = [r for r in grains if r["don"] >= EU_LOW]
        self.assertTrue(all(group_of(r["product"]) == "SG" for r in high))
        over750 = {}
        for r in grains:
            if r["don"] >= EU_HIGH:
                over750[r["product"]] = over750.get(r["product"], 0) + 1
        self.assertEqual(over750, {"Grain - Rye": 3, "Rye Products": 2, "Spelt": 2,
                                   "Spelt Products": 1, "Grain - Barley": 1})


class TestCrossMethod(Base):
    def tables(self, at_cut):
        out = []
        for lab in SHARED:
            dg = pick(self.rows, (lab,))
            hit = sum(1 for r in dg if r["detected"] and (not at_cut or r["don"] >= CUT - 1e-9))
            mm = self.cross[lab]                         # every MM positive is >= 10 ppb
            out.append((hit, len(dg) - hit, mm["mm_detected"], mm["mm_n"] - mm["mm_detected"]))
        return out

    def test_csv_matches_samples_and_record(self):
        self.assertEqual(list(self.cross), SHARED)
        for lab in SHARED:
            st = stats(pick(self.rows, (lab,)))
            c = self.cross[lab]
            self.assertEqual((c["dg_n"], c["dg_detected"], c["dg_ge_10"]),
                             (st["n"], st["pos"], st["ge_cut"]), msg=lab)
        rec = self.a["cross"]
        self.assertEqual([list(t) for t in self.tables(True)],
                         [rec["at_cut"][lab] for lab in SHARED])
        self.assertEqual([list(t) for t in self.tables(False)],
                         [rec["own_limits"][lab] for lab in SHARED])
        self.assertEqual((sum(self.cross[lab]["mm_n"] for lab in SHARED),
                          sum(self.cross[lab]["mm_detected"] for lab in SHARED)), (297, 75))

    def test_p6_own_limits(self):
        tabs = self.tables(False)
        pooled = [sum(t[i] for t in tabs) for i in range(4)]
        self.assertEqual(pooled, [404, 350, 75, 222])
        self.assertEqual(pooled, self.a["cross"]["own_pooled"])
        m = mh(tabs)
        chi2, p = cmh(tabs)
        self.assertAlmostEqual(m, self.a["cross"]["own_mh_or"], places=9)
        self.assertAlmostEqual(chi2, self.a["cross"]["own_cmh_chi2"], places=9)
        self.assertEqual((round(m, 2), round(chi2, 1)), (6.44, 98.2))
        self.assertLess(p, 1e-20)
        a, b, c, d = pooled
        self.assertEqual(round(a * d / (b * c), 2), 3.42)
        shared = stats(pick(self.rows, SHARED))
        self.assertEqual((shared["pos"], shared["below_cut"]), (404, 208))
        self.assertGreaterEqual(shared["below_cut"], 0.25 * shared["pos"])

    def test_p7_common_cut(self):
        tabs = self.tables(True)
        pooled = [sum(t[i] for t in tabs) for i in range(4)]
        self.assertEqual(pooled, [196, 558, 75, 222])
        self.assertEqual(pooled, self.a["cross"]["at_cut_pooled"])
        m = mh(tabs)
        chi2, p = cmh(tabs)
        rec = self.a["cross"]
        self.assertAlmostEqual(m, rec["at_cut_mh_or"], places=9)
        self.assertAlmostEqual(chi2, rec["at_cut_cmh_chi2"], places=9)
        self.assertAlmostEqual(p, rec["at_cut_cmh_p"], places=9)
        self.assertEqual((round(m, 2), round(chi2, 2), round(p, 3)), (1.28, 1.40, 0.237))
        self.assertTrue(0.5 <= m <= 2.0)                 # P7 held
        a, b, c, d = pooled
        self.assertEqual(round(a * d / (b * c), 2), 1.04)
        lo, hi = rbg_interval(tabs)
        self.assertAlmostEqual(lo, 0.8651, delta=0.002)  # printed 0.87
        self.assertAlmostEqual(hi, 1.9021, delta=0.002)  # printed 1.90
        self.assertTrue(lo < 1.0 < hi < 2.0)

    def test_millet_at_cut(self):
        tabs = dict(zip(SHARED, self.tables(True)))
        self.assertEqual(tabs["Millet"], (0, 45, 3, 12))
        self.assertEqual(round(fisher_two_sided(*tabs["Millet"]), 4), 0.0133)
        self.assertEqual(stats(pick(self.rows, ("Millet",)))["max"], 8.38)
        self.assertEqual(tabs["Grain - Kamut"], (27, 25, 3, 10))


class TestOrigin(Base):
    def test_small_grains_by_function(self):
        sg = self.group("SG")
        got = {}
        for f in ("Domestic", "Import", "Unknown"):
            st = stats([r for r in sg if r["function"] == f])
            got[f] = (st["n"], st["pos"], st["ge_cut"], st["ge_400"], st["ge_750"])
            self.assertStatsEqual(st, self.a["by_function"][f"SG|{f}"], f)
        self.assertEqual(got, {"Domestic": (129, 124, 106, 24, 8),
                               "Import": (119, 97, 41, 0, 0),
                               "Unknown": (105, 83, 41, 6, 1)})
        imp = stats([r for r in sg if r["function"] == "Import"])
        self.assertEqual((imp["max"], imp["median"]), (130.0, 6.6))
        dom = stats([r for r in sg if r["function"] == "Domestic"])
        self.assertEqual((dom["max"], dom["median"]), (5720.0, 76.25))
        self.assertGreater(dom["median"], 10 * imp["median"])
        self.assertLess(fisher_two_sided(24, 129 - 24, 0, 119), 1e-6)
        high = [r for r in self.rows if r["don"] >= EU_LOW]
        self.assertEqual(len(high), 30)
        self.assertFalse(any(r["function"] == "Import" for r in high))


if __name__ == "__main__":
    unittest.main(verbosity=2)
