#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/bpa-2018-2020-0.1.0-result.md.

Rebuilds, from the committed per-sample tables data/bpa_2018_samples.csv and
data/bpa_2020_samples.csv with its own code (it does not import the grader): the counts and label
maps; every printed Table 2 cell of both reports; the four extra samples that reconcile the
2018-19 report's 381 / 138 / 96 / 1.65 / 43% with the file; the BADGE, BPF and BPS figures; the
2020-21 Tables 3-5; the co-occurrence sentences (two of which fail); the 2018-19 sample-number
blocks; and the absence of identical multi-analyte profiles. Each is checked against its own copy
of the printed figures and against the sealed grader record data/bpa_2018_2020_summary.json.
Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
S18 = os.path.join(DATA, "bpa_2018_samples.csv")
S20 = os.path.join(DATA, "bpa_2020_samples.csv")
SUMMARY = os.path.join(DATA, "bpa_2018_2020_summary.json")

KEYS = ("bpa", "badge", "bpf", "bps")
PIE = ("Pie Filling - Blueberry", "Pie Filling - Cherry", "Pie Filling - Other",
       "Pie Filling - Pumpkin")
MAP18 = {"Coconut Milk": "coconut", "Infant Formula - Dairy": "formula",
         "Infant Formula - Other": "formula", "Sauces": "sauces", "Tomato Sauce": "sauces"}
MAP18.update({p: "pie" for p in PIE})
MAP20 = {"Fish/Seafood - Canned": "fish", "Meat - Canned": "meat", "Pie Filling - apple": "pie"}
MAP20.update({p: "pie" for p in PIE})
MAP20.update({f: "fruit" for f in ("Apricot", "Cherry", "Cranberry", "Grapefruit", "JackFruit",
                                   "Lychee", "Mango", "Mixed Fruit", "Orange", "Peach", "Pear",
                                   "Pineapple")})
MAP20.update({v: "veg" for v in ("Artichoke Heart", "Bean - Green/Yellow", "Bean - Kidney",
                                 "Bean - Pinto", "Beet", "Carrot", "Corn", "Lentil",
                                 "Mixed Vegetables", "Mushroom", "Mushroom - Shiitake", "Pea",
                                 "Soup", "Sprout - Bean", "Vegetable Products",
                                 "Water Chestnut")})

# Printed figures (ppb; positives only): (n, positive, minimum, maximum, average).
TABLE2_18 = {"coconut": (49, 37, "1.42", "367", "47.0"),
             "formula": (135, 17, "0.92", "2.24", "1.4"),
             "pie": (98, 62, "0.97", "101", "11.2"),
             "sauces": (95, 48, "1.01", "95.9", "9.78"),
             "all": (377, 164, "0.92", "367", "17.8")}
TABLE3_FORMULA = (138, 18, "0.92", "5.89", "1.65")
SAUCES_96 = (96, 48, "1.01", "95.9", "9.78")
ALL_381 = (381, 165, "0.92", "367", "17.8")
TABLE2_20 = {"fish": (101, 39, "0.91", "395", "43.8"),
             "fruit": (52, 15, "1.4", "21.4", "6.1"),
             "meat": (100, 42, "1.2", "479", "43.5"),
             "pie": (49, 16, "1.1", "7.1", "2.1"),
             "veg": (100, 51, "0.96", "151", "55.9"),
             "all": (402, 163, "0.91", "479", "40.0")}
# 2020-21 Tables 3-5: analyte -> type -> (positive, minimum, maximum, average).
ALT_20 = {"badge": {"fish": (5, "3.6", "1580", "330"), "meat": (11, "6.5", "372", "66.1"),
                    "veg": (1, "14.0", "14.0", "14.0")},
          "bpf": {"fish": (1, "94.8", "94.8", "94.8"), "meat": (1, "19.6", "19.6", "19.6")},
          "bps": {"fish": (1, "46.0", "46.0", "46.0"), "meat": (5, "0.96", "191", "52.1"),
                  "veg": (1, "0.98", "0.98", "0.98")}}
# 2020-21 Table 1: domestic, imported, unspecified.
TABLE1_20 = {"fish": (8, 90, 3), "fruit": (0, 50, 2), "meat": (20, 55, 25), "pie": (0, 49, 0),
             "veg": (19, 73, 8)}
# 2018-19 sample numbers: four product blocks, and the 23 numbers the file does not use.
BLOCKS_18 = (("pie", 1, 100), ("coconut", 101, 150), ("sauces", 151, 250),
             ("formula", 251, 400))
ABSENT_18 = {48, 98, 125, 172, 192, 193, 196, 219, 301, 305, 328, 331, 333, 334, 340, 346, 371,
             376, 378, 389, 390, 392, 398}


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["v"] = {k: float(r[k + "_ppb"]) for k in KEYS}
    return rows


def in_range(x, printed):
    half = 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5
    return x is not None and abs(x - float(printed)) <= half + 1e-9


def stats(values):
    pos = sorted(v for v in values if v > 0)
    n = len(values)
    return {"n": n, "k": len(pos), "pct": 100 * len(pos) / n if n else None,
            "min": pos[0] if pos else None, "max": pos[-1] if pos else None,
            "mean": sum(pos) / len(pos) if pos else None, "sum": sum(pos)}


def cells(printed, st):
    n, k, mn, mx, avg = printed
    return {"n": st["n"] == n, "detected": st["k"] == k, "min": in_range(st["min"], mn),
            "max": in_range(st["max"], mx), "avg": in_range(st["mean"], avg)}


def values(rows, key, kind=None):
    return [r["v"][key] for r in rows if kind is None or r["type"] == kind]


def identical_profiles(rows, min_pos=2):
    groups = {}
    for r in rows:
        prof = tuple(r["v"][k] for k in KEYS)
        if sum(1 for x in prof if x > 0) >= min_pos:
            groups.setdefault(prof, []).append(r["sample"])
    return [v for v in groups.values() if len(v) > 1]


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r18 = load(S18)
        cls.r20 = load(S20)
        with open(SUMMARY, encoding="utf-8") as fh:
            cls.s = json.load(fh)
        cls.a18 = cls.s["analysis"]["bpa-2018"]
        cls.a20 = cls.s["analysis"]["bpa-2020"]
        cls.preds = {p["id"]: p for p in cls.s["predictions"]}


class TestShape(Base):
    def test_counts_and_maps(self):
        for rows, mapping, name, n in ((self.r18, MAP18, "bpa-2018", 377),
                                       (self.r20, MAP20, "bpa-2020", 402)):
            self.assertEqual(len(rows), n)
            self.assertEqual(len({r["sample"] for r in rows}), n)
            products = {}
            for r in rows:
                products[r["product"]] = products.get(r["product"], 0) + 1
                self.assertEqual(r["type"], mapping[r["product"]], r["sample"])
            self.assertEqual(products, self.s["census"][name]["products"])
        by18 = {t: len([r for r in self.r18 if r["type"] == t]) for t in TABLE2_18 if t != "all"}
        self.assertEqual(by18, {"coconut": 49, "formula": 135, "pie": 98, "sauces": 95})

    def test_gate_and_tally(self):
        self.assertTrue(self.preds["G18"]["met"])
        self.assertTrue(self.preds["G20"]["met"])
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (8, 4))
        ids = [p["id"] for p in self.s["predictions"]]
        self.assertEqual(ids, ["G18", "G20", "B2", "B3", "B4", "B5", "B6", "C2", "C3", "C4"])
        self.assertEqual({p["id"] for p in self.s["predictions"] if not p["met"]},
                         {"B2", "B3", "B4", "C4"})
        prov = self.s["provenance"]
        self.assertEqual(prov["bpa-2018"]["sha256"],
                         "446169ddc0d1319032016853bfe1d83d4fb1c2129a305f75de9ae8d2447a60d8")
        self.assertEqual(prov["bpa-2020"]["sha256"],
                         "bf9d76bdf840a5578b7b69eeb6056cb0f65b522af6a2cec6f80874bfc5eb7dd1")
        self.assertTrue(prov["bpa-2018"]["md5_matches_portal"])
        self.assertTrue(prov["bpa-2020"]["md5_matches_portal"])


class TestReport2018(Base):
    def test_table2_every_cell(self):
        for t, printed in TABLE2_18.items():
            st = stats(values(self.r18, "bpa", None if t == "all" else t))
            self.assertTrue(all(cells(printed, st).values()), (t, st))
            ref = self.a18["bpa"][t]
            self.assertEqual((st["n"], st["k"]), (ref["n"], ref["k"]))
            for key in ("min", "max", "mean"):
                self.assertAlmostEqual(st[key], ref[key], places=9)
        st = stats(values(self.r18, "bpa"))
        self.assertTrue(in_range(st["pct"], "44"))
        self.assertFalse(in_range(st["pct"], "43"))

    def test_failed_items_fail_only_on_the_extra_samples(self):
        formula = stats(values(self.r18, "bpa", "formula"))
        sauces = stats(values(self.r18, "bpa", "sauces"))
        everything = stats(values(self.r18, "bpa"))
        b2 = cells(TABLE3_FORMULA, formula)
        b3 = cells(SAUCES_96, sauces)
        b4 = cells(ALL_381, everything)
        self.assertEqual(b2, {"n": False, "detected": False, "min": True, "max": False,
                              "avg": False})
        self.assertEqual(b3, {"n": False, "detected": True, "min": True, "max": True,
                              "avg": True})
        self.assertEqual(b4, {"n": False, "detected": False, "min": True, "max": True,
                              "avg": True})
        self.assertEqual(b2, self.preds["B2"]["observed"]["cells"])
        self.assertEqual(b3, self.preds["B3"]["observed"]["cells"])
        self.assertEqual(b4, self.preds["B4"]["observed"]["cells"])

    def test_four_extra_samples_reconcile_every_printed_figure(self):
        formula = values(self.r18, "bpa", "formula")
        st = stats(formula)
        self.assertEqual(st["k"], 17)
        self.assertAlmostEqual(st["sum"], 23.81, places=6)
        # Registered from the report alone: Table 3's 1.65 over 18 with one extra positive at
        # 5.89 pins the 17-positive sum to 23.72-23.90.
        self.assertTrue(23.72 <= st["sum"] <= 23.90)
        lo, hi = 18 * 1.645 - st["sum"], 18 * 1.655 - st["sum"]
        self.assertTrue(lo <= 5.89 <= hi)
        self.assertLess(st["max"], 5.89)
        # Three formulas (one positive at 5.89) and one sauce with no BPA.
        self.assertTrue(all(cells(TABLE3_FORMULA, stats(formula + [5.89, 0.0, 0.0])).values()))
        self.assertTrue(all(cells(SAUCES_96,
                                  stats(values(self.r18, "bpa", "sauces") + [0.0])).values()))
        widened = stats(values(self.r18, "bpa") + [5.89, 0.0, 0.0, 0.0])
        self.assertTrue(all(cells(ALL_381, widened).values()))
        self.assertTrue(in_range(widened["pct"], "43"))
        self.assertEqual(49 + 138 + 98 + 96, 381)

    def test_badge_bpf_bps(self):
        badge = sorted((r for r in self.r18 if r["v"]["badge"] > 0), key=lambda r: -r["v"]["badge"])
        self.assertEqual(len(badge), 12)
        self.assertEqual({r["type"] for r in badge}, {"coconut"})
        self.assertTrue(all(r["v"]["bpa"] > 0 for r in badge))
        vals = [r["v"]["badge"] for r in badge]
        self.assertTrue(in_range(vals[0], "524") and in_range(vals[1], "209"))
        self.assertTrue(all(v < 63 for v in vals[2:]))
        self.assertTrue(in_range(sum(vals) / 12, "81.9"))
        for share in (100 * 12 / 377, 100 * 12 / 49, 100 * 12 / 164):
            self.assertFalse(in_range(share, "12"))
        self.assertEqual(stats(values(self.r18, "bpf"))["k"], 0)
        self.assertEqual(stats(values(self.r18, "bps"))["k"], 0)
        self.assertTrue(self.preds["B5"]["met"] and self.preds["B6"]["met"])

    def test_sample_number_blocks(self):
        used = set()
        for r in self.r18:
            m = re.match(r"^C2018BPHA(\d{5})(D?)$", r["sample"])
            self.assertIsNotNone(m, r["sample"])
            num = int(m.group(1))
            used.add(num)
            block = [t for t, a, b in BLOCKS_18 if a <= num <= b]
            self.assertEqual(block, [r["type"]], r["sample"])
        self.assertEqual(len(used), 377)
        self.assertEqual(set(range(1, 401)) - used, ABSENT_18)
        self.assertEqual(sorted(r["sample"] for r in self.r18 if r["sample"].endswith("D")),
                         ["C2018BPHA00111D", "C2018BPHA00170D", "C2018BPHA00171D"])


class TestReport2020(Base):
    def test_table1_and_table2(self):
        for t, (dom, imp, uns) in TABLE1_20.items():
            fn = [r["function"] for r in self.r20 if r["type"] == t]
            got = (fn.count("Domestic"), fn.count("Import"),
                   len(fn) - fn.count("Domestic") - fn.count("Import"))
            self.assertEqual(got, (dom, imp, uns), t)
            self.assertEqual(list(got) + [len(fn)], self.a20["origins"][t])
        for t, printed in TABLE2_20.items():
            st = stats(values(self.r20, "bpa", None if t == "all" else t))
            self.assertTrue(all(cells(printed, st).values()), (t, st))
            self.assertAlmostEqual(st["mean"], self.a20["bpa"][t]["mean"], places=9)
        self.assertEqual(stats(values(self.r20, "bpa", "veg"))["k"], 51)
        self.assertTrue(in_range(stats(values(self.r20, "bpa"))["pct"], "41"))

    def test_tables_3_to_5(self):
        for key, printed in ALT_20.items():
            self.assertEqual(sum(p[0] for p in printed.values()),
                             stats(values(self.r20, key))["k"], key)
            for t in ("fish", "fruit", "meat", "pie", "veg"):
                st = stats(values(self.r20, key, t))
                if t not in printed:
                    self.assertEqual(st["k"], 0, (key, t))
                    continue
                k, mn, mx, avg = printed[t]
                self.assertEqual(st["k"], k, (key, t))
                for got, want in ((st["min"], mn), (st["max"], mx), (st["mean"], avg)):
                    self.assertTrue(in_range(got, want), (key, t, got, want))
        badge = stats(values(self.r20, "badge"))
        self.assertEqual((badge["k"], stats(values(self.r20, "bpf"))["k"],
                          stats(values(self.r20, "bps"))["k"]), (17, 2, 7))
        self.assertTrue(in_range(badge["mean"], "141"))

    def test_co_occurrence_text(self):
        badge = [r for r in self.r20 if r["v"]["badge"] > 0]
        both = [r for r in badge if r["v"]["bpa"] > 0]
        self.assertEqual(len(both), 8)
        self.assertEqual(sum(1 for r in badge if r["function"] == "Import"), 14)
        not_imported = sorted((r["sample"], r["type"], r["function"], r["origin"]) for r in both
                              if r["function"] != "Import")
        self.assertEqual(not_imported,
                         [("C2020BPHA00133", "meat", "Domestic", "CANADA"),
                          ("C2020BPHA00314", "meat", "Unknown", "CANADA")])
        self.assertTrue(all(r["type"] in ("meat", "fish") for r in both))
        bps_meat = [r for r in self.r20 if r["type"] == "meat" and r["v"]["bps"] > 0]
        self.assertEqual(len(bps_meat), 5)
        self.assertTrue(all(r["function"] == "Import" for r in bps_meat))
        no_bpa = [(r["sample"], r["origin"], r["v"]["bps"]) for r in bps_meat
                  if r["v"]["bpa"] == 0]
        self.assertEqual(len(no_bpa), 1)
        self.assertEqual(no_bpa[0][:2], ("C2020BPHA00130", "BRAZIL"))
        self.assertTrue(in_range(no_bpa[0][2], "0.96"))
        fish = sorted((r["v"]["badge"] for r in self.r20 if r["type"] == "fish"
                       and r["v"]["badge"] > 0), reverse=True)
        self.assertTrue(in_range(fish[1], "51"))
        fruit_pie = [r for r in self.r20 if r["type"] in ("fruit", "pie") and r["v"]["bpa"] > 0]
        self.assertEqual(len(fruit_pie), 31)
        self.assertTrue(all(r["function"] == "Import" for r in fruit_pie))
        bpf = sorted((r["sample"], r["type"], r["function"]) for r in self.r20
                     if r["v"]["bpf"] > 0)
        self.assertEqual(bpf, [("C2020BPHA00119", "meat", "Unknown"),
                               ("C2020BPHA00141", "fish", "Import")])
        self.assertEqual(self.a20["c4"], {
            "badge_imported_14": True, "badge_with_bpa_8": True,
            "bpa_fruit_pie_all_imported": True, "bps_meat_all_with_bpa": False,
            "fish_badge_second_51": True, "with_bpa_all_imported_meat_or_fish": False})
        self.assertFalse(self.preds["C4"]["met"])


class TestTwins(Base):
    def test_no_identical_multi_analyte_profiles(self):
        self.assertEqual(identical_profiles(self.r18), [])
        self.assertEqual(identical_profiles(self.r20), [])
        self.assertEqual(self.a18["twins"], [])
        self.assertEqual(self.a20["twins"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
