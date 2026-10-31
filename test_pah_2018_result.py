#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/pah-2018-0.1.0-result.md.

Recomputes every sample's TEQ from its 16 PAH columns, then rebuilds the counts, groups and Table 1
origins, every printed Table 2 cell, all eight Figure 1 oil lists (with the copied soybean list and
the corrected 0.27 average), the text's peanut, canola, roasted-pepper and baked-good figures and
the identical soybean/sunflower pair from the committed per-sample table
data/pah_2018_samples.csv with its own code (it does not import the grader), and checks them
against the sealed grader record data/pah_2018_summary.json. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "pah_2018_samples.csv")
SUMMARY = os.path.join(DATA, "pah_2018_summary.json")

PAH16 = ("Acenaphthene", "Acenaphthylene", "Anthracene", "Benzo[a]anthracene", "Benzo[a]pyrene",
         "Benzo[b]fluoranthene", "Benzo[g,h,i]perylene", "Benzo[k]fluoranthene", "Chrysene",
         "Dibenzo(a,h)anthracene", "Fluoranthene", "Fluorene", "Indeno(1,2,3-cd)pyrene",
         "Naphthalene", "Phenanthrene", "Pyrene")
# The report's TEQ: benzo[a]pyrene x 1 + benzo[a]anthracene x 0.1 + benzo[b]fluoranthene x 0.1 +
# chrysene x 0.01.
TEF = (("Benzo[a]pyrene", 1.0), ("Benzo[a]anthracene", 0.1), ("Benzo[b]fluoranthene", 0.1),
       ("Chrysene", 0.01))
BAKED = {"Baked Goods", "Bakery Product - Cookie", "Crackers"}
VEG = {"Pepper (roasted)", "Tomato (roasted)", "Mixed Vegetable (roasted)"}
OIL = {"Oil - Canola": "canola", "Oil - Corn": "corn", "Oil - Olive": "olive",
       "Oil - Palm": "palm", "Oil - Peanut": "peanut", "Oil - Soybean": "soybean",
       "Oil - Sunflower": "sunflower", "Oil - Other": "other", "Oil - Coconut": "other",
       "Oil - Grapeseed": "other"}
GROUPS = ("baked", "oils", "veg")
# CFIA's printed Table 1: domestic, imported, unspecified.
TABLE1 = {"baked": (18, 42, 82), "oils": (9, 59, 10), "veg": (1, 65, 1)}
# CFIA's printed Table 2 (ppb TEQ): n, detected, minimum, maximum, average of positives.
TABLE2 = {"baked": (142, 51, "0.001", "1.68", "0.16"),
          "oils": (78, 55, "0.002", "2.41", "0.27"),
          "veg": (67, 27, "0.004", "9.17", "1.16"),
          "all": (287, 133, "0.001", "9.17", "0.41")}
# CFIA's printed Figure 1 (text alternative): the detected TEQ values per oil type.
FIGURE = {
    "canola": ("0.0023", "0.033759"),
    "corn": ("0.002024", "0.002182", "0.03195", "0.032658", "0.034643", "0.045364", "0.3192",
             "0.406165"),
    "olive": ("0.004196", "0.007503", "0.007558", "0.007691", "0.01578", "0.039436", "0.047001",
              "0.056015", "0.377378"),
    "palm": ("0.04904", "0.050362", "0.108161", "0.185301", "0.441651", "0.711076"),
    "peanut": ("0.4505", "0.466762", "0.53933", "0.543899", "0.683588", "0.751593", "0.910249",
               "1.749141", "2.408304"),
    "soybean": ("0.002349", "0.0385", "0.040621", "0.053368", "0.059183", "0.074653",
                "0.459065"),
    "sunflower": ("0.002349", "0.0385", "0.040621", "0.053368", "0.059183", "0.074653",
                  "0.459065"),
    "other": ("0.002667", "0.00325", "0.034017", "0.051609", "0.146624", "0.15509", "0.3548",
              "1.882423"),
}
SOYBEAN_FILE = (0.004191, 0.036498, 0.04284, 0.045195, 0.045246, 0.059183)
TWINS = ("C2018PAHS00282", "C2018PAHS00291")
TWIN_VALUES = {"Benzo[b]fluoranthene": 0.5508, "Chrysene": 0.4103, "Fluoranthene": 0.4128,
               "Pyrene": 0.6286}


def load_rows():
    with open(SAMPLES, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["v"] = {c: float(r["ppb:" + c]) for c in PAH16}
        r["teq"] = sum(f * r["v"][c] for c, f in TEF)
    return rows


def in_range(x, printed):
    half = 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5
    return x is not None and abs(x - float(printed)) <= half + 1e-9


def group_of(product):
    if product in BAKED:
        return "baked"
    if product in VEG:
        return "veg"
    return "oils" if product in OIL else None


def stats(values):
    pos = sorted(v for v in values if v > 0)
    n = len(values)
    return {"n": n, "k": len(pos), "pct": 100 * len(pos) / n if n else None,
            "min": pos[0] if pos else None, "max": pos[-1] if pos else None,
            "mean": sum(pos) / len(pos) if pos else None}


def positives(rows, oil_type):
    return sorted(r["teq"] for r in rows if OIL.get(r["product"]) == oil_type and r["teq"] > 0)


def n_matched(values, printed):
    pool = list(values)
    k = 0
    for p in printed:
        hit = [i for i, v in enumerate(pool) if in_range(v, p)]
        if hit:
            k += 1
            del pool[hit[0]]
    return k


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_rows()
        with open(SUMMARY, encoding="utf-8") as fh:
            cls.s = json.load(fh)
        cls.a = cls.s["analysis"]
        cls.preds = {p["id"]: p for p in cls.s["predictions"]}
        cls.by = {g: [r for r in cls.rows if group_of(r["product"]) == g] for g in GROUPS}


class TestShape(Base):
    def test_counts_and_groups(self):
        self.assertEqual(len(self.rows), 287)
        self.assertEqual(len({r["sample"] for r in self.rows}), 287)
        products = {}
        for r in self.rows:
            products[r["product"]] = products.get(r["product"], 0) + 1
        self.assertEqual(products, self.s["census"]["products"])
        self.assertEqual({g: len(v) for g, v in self.by.items()},
                         {"baked": 142, "oils": 78, "veg": 67})
        for r in self.rows:
            self.assertEqual(r["group"], group_of(r["product"]), r["sample"])
            self.assertEqual(r["oil_type"], OIL.get(r["product"], ""), r["sample"])

    def test_teq_recomputed(self):
        for r in self.rows:
            self.assertAlmostEqual(r["teq"], float(r["teq_ppb"]), places=9, msg=r["sample"])
            self.assertEqual(int(r["n_pah"]), sum(1 for c in PAH16 if r["v"][c] > 0), r["sample"])
        anyp = {g: sum(1 for r in self.by[g] if int(r["n_pah"]) > 0) for g in GROUPS}
        self.assertEqual(anyp, {"baked": 138, "oils": 75, "veg": 62})
        self.assertEqual(anyp, self.a["any_pah"])

    def test_gate_and_tally(self):
        self.assertTrue(self.preds["G"]["met"])
        self.assertTrue(all(self.preds["G"]["observed"].values()))
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (7, 6))
        met = {p["id"]: p["met"] for p in self.s["predictions"]}
        self.assertEqual(list(met), ["G", "P1", "P2", "P3", "P4", "P5", "P6"])
        self.assertEqual({k for k, v in met.items() if not v}, {"P2"})
        prov = self.s["provenance"]
        self.assertEqual(prov["sha256"],
                         "9b93f73381eccfd00fad91f2c8a64ff3c05a3da9651c775047314be6e1a1650e")
        self.assertEqual(prov["bytes"], 850814)
        self.assertTrue(prov["md5_matches_portal"])


class TestTable2(Base):
    def test_every_cell(self):
        groups = dict(self.by)
        groups["all"] = self.rows
        for g, (n, det, mn, mx, avg) in TABLE2.items():
            st = stats([r["teq"] for r in groups[g]])
            self.assertEqual((st["n"], st["k"]), (n, det), g)
            self.assertTrue(in_range(st["min"], mn), (g, st["min"]))
            self.assertTrue(in_range(st["max"], mx), (g, st["max"]))
            self.assertTrue(in_range(st["mean"], avg), (g, st["mean"]))
            ref = self.a["groups"][g]
            self.assertEqual((st["n"], st["k"]), (ref["n"], ref["k"]))
            for key in ("min", "max", "mean"):
                self.assertAlmostEqual(st[key], ref[key], places=9)
        self.assertTrue(in_range(100 * 133 / 287, "46"))

    def test_benzo_a_pyrene_alone(self):
        for g in GROUPS:
            st = stats([r["v"]["Benzo[a]pyrene"] for r in self.by[g]])
            ref = self.a["bap"][g]
            self.assertEqual((st["n"], st["k"]), (ref["n"], ref["k"]), g)
            self.assertAlmostEqual(st["max"], ref["max"], places=9)
        self.assertEqual([stats([r["v"]["Benzo[a]pyrene"] for r in self.by[g]])["k"]
                          for g in GROUPS], [11, 17, 23])


class TestFigure(Base):
    def test_seven_lists_reproduce(self):
        self.assertEqual(FIGURE["soybean"], FIGURE["sunflower"])
        for t, printed in FIGURE.items():
            if t == "soybean":
                continue
            got = positives(self.rows, t)
            want = sorted(printed, key=float)
            self.assertEqual(len(got), len(want), t)
            for v, p in zip(got, want):
                self.assertTrue(in_range(v, p), (t, v, p))
            self.assertEqual(self.a["figure"][t]["full"], True, t)

    def test_soybean_is_the_copy(self):
        got = positives(self.rows, "soybean")
        self.assertEqual(len(got), 6)
        for v, w in zip(got, SOYBEAN_FILE):
            self.assertAlmostEqual(v, w, places=9)
        self.assertEqual(n_matched(got, FIGURE["soybean"]), 1)
        self.assertEqual(self.a["figure"]["soybean"]["matched"], 1)
        self.assertEqual(n_matched(positives(self.rows, "sunflower"), FIGURE["sunflower"]), 7)
        self.assertFalse(self.preds["P2"]["met"])

    def test_corrected_average(self):
        printed = [float(v) for vals in FIGURE.values() for v in vals]
        self.assertEqual(len(printed), 56)
        self.assertTrue(in_range(sum(printed) / 56, "0.28"))
        self.assertFalse(in_range(sum(printed) / 56, "0.27"))
        fixed = [float(v) for t, vals in FIGURE.items() if t != "soybean" for v in vals]
        fixed += positives(self.rows, "soybean")
        self.assertEqual(len(fixed), 55)
        self.assertTrue(in_range(sum(fixed) / 55, "0.27"))
        self.assertLessEqual(sum(SOYBEAN_FILE), 0.245)
        self.assertAlmostEqual(sum(fixed) / 55, self.a["groups"]["oils"]["mean"], places=6)


class TestText(Base):
    def test_oil_types(self):
        st = {t: stats([r["teq"] for r in self.rows if OIL.get(r["product"]) == t])
              for t in FIGURE}
        self.assertEqual(max(st, key=lambda t: st[t]["mean"]), "peanut")
        self.assertEqual(max(st, key=lambda t: st[t]["max"]), "peanut")
        self.assertTrue(in_range(st["peanut"]["mean"], "0.94"))
        self.assertTrue(in_range(st["peanut"]["max"], "2.41"))
        self.assertEqual((st["canola"]["k"], st["canola"]["n"]), (2, 11))
        for key in ("pct", "mean", "max"):
            self.assertEqual(min(st, key=lambda t: st[t][key]), "canola", key)
        self.assertTrue(in_range(st["canola"]["pct"], "18"))
        self.assertTrue(in_range(st["canola"]["mean"], "0.02"))
        self.assertTrue(in_range(st["canola"]["max"], "0.03"))

    def test_maxima(self):
        veg = sorted(self.by["veg"], key=lambda r: -r["teq"])
        self.assertEqual((veg[0]["sample"], veg[0]["product"]),
                         ("C2018PAHS00061", "Pepper (roasted)"))
        self.assertTrue(in_range(veg[0]["teq"], "9.17"))
        self.assertEqual(veg[1]["sample"], "C2018PAHS00013")
        self.assertLess(veg[1]["teq"], 2.7)
        high = [r for r in self.by["baked"] if r["teq"] >= 0.8]
        self.assertEqual([(r["sample"], r["product"]) for r in high],
                         [("C2018PAHS00118", "Bakery Product - Cookie")])
        self.assertTrue(in_range(high[0]["teq"], "1.68"))


class TestOrigin(Base):
    def test_table1(self):
        diff = {}
        for g in GROUPS:
            c = [0, 0, 0]
            for r in self.by[g]:
                c[0 if r["function"] == "Domestic" else 1 if r["function"] == "Import" else 2] += 1
            self.assertEqual(c + [len(self.by[g])], self.a["origins"][g], g)
            d = tuple(x - p for x, p in zip(c, TABLE1[g]))
            if any(d):
                diff[g] = d
        self.assertEqual(diff, {"baked": (0, -1, 1), "oils": (0, -1, 1)})


class TestTwins(Base):
    def test_identical_pair(self):
        rows = {r["sample"]: r for r in self.rows if r["sample"] in TWINS}
        a, b = rows[TWINS[0]], rows[TWINS[1]]
        self.assertEqual((a["product"], a["origin"]), ("Oil - Soybean", "UNITED STATES"))
        self.assertEqual((b["product"], b["origin"]), ("Oil - Sunflower", "TURKEY"))
        self.assertEqual(a["v"], b["v"])
        self.assertEqual({c: v for c, v in a["v"].items() if v > 0}, TWIN_VALUES)
        self.assertTrue(in_range(a["teq"], "0.059183"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
