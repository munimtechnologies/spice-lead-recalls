#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/bpa-series-0.1.0-result.md (the five files whose gates passed).

Rebuilds, from the committed per-sample tables data/bpa_2010_samples.csv, bpa_2012, bpa_2013,
bpa_2016 and bpa_2017 with its own code (it does not import the grader): the counts and label
maps; every printed BPA row of the 2012-13 and 2013-14 Table 5, the 2016-17 Table 2 and Table 4,
and the 2017-18 Table 2 and its BADGE / BPF / BPS rows; the reconciliations reported in the result
note (2012-13: 67 pastas outside Table 5, salsa counted with curry; 2016-17: the 27 samples and 21
positives beyond the canned Table 2); the directional D1 shares; and the absence of identical
multi-analyte profiles. Each is checked against its own copy of the printed figures and against
the sealed grader record data/bpa_series_summary_0.1.0.json. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SUMMARY = os.path.join(DATA, "bpa_series_summary_0.1.0.json")
FILES = {"bpa-2010": "bpa_2010_samples.csv", "bpa-2012": "bpa_2012_samples.csv",
         "bpa-2013": "bpa_2013_samples.csv", "bpa-2016": "bpa_2016_samples.csv",
         "bpa-2017": "bpa_2017_samples.csv"}
N = {"bpa-2010": 234, "bpa-2012": 576, "bpa-2013": 391, "bpa-2016": 491, "bpa-2017": 468}
SHA256 = {
    "bpa-2010": "79652a9f76bbb099178cda28c91be67497608d11aeb861ac5e0117086c65d466",
    "bpa-2012": "d2020d42ba7d56969f559a452fd26afdd47a80a2d21b64a704e0be385a8a621d",
    "bpa-2013": "3c78983cbb5da9758a0482b6c15f2ca662f9acfff3c54d5aa14d187eb383d564",
    "bpa-2016": "dc5173a485d4acc5e9bd1651d83d82ce8d9d34c56cb12125a448edd7da70a193",
    "bpa-2017": "f3ef4b47614b8c40e240d65ab4a08cd6b8ef779d0703338f1ae6a1bab27f0f56",
}
KEYS = ("bpa", "badge", "bpf", "bps")


def group(**groups):
    return {label: g for g, labels in groups.items() for label in labels}


# The label maps fixed in docs/bpa-series-0.1.0-census.md (own copy).
FORMULA = ("Infant Formula - Dairy", "Infant Formula - Soy")
PIE = ("Pie Filling - Blueberry", "Pie Filling - Cherry", "Pie Filling - Other",
       "Pie Filling - Pumpkin", "Pie Filling - apple")
MAPS = {
    "bpa-2010": group(
        formula=FORMULA, juice=("Juice - Apple", "Juice - Grape", "Nectar - Pear"),
        fruit=("Apricot", "Mixed Fruit", "Peach", "Pear", "Pineapple", "Strawberry"),
        other=("Cereal - Other", "Meat & Vegetable")),
    "bpa-2012": group(
        bev=("Beverage - Fruit", "Juice - Apple", "Juice - Blend", "Juice - Other",
             "Juice - Vegetable", "Juice - other", "Nectar - Mango", "Nectar - Other",
             "juice - pineapple"),
        coconut=("Coconut Milk",),
        fruit=("Apricot", "Grapefruit", "JackFruit", "Longan", "Lychee", "Mango", "Mixed Fruit",
               "Orange", "Orange - Organic", "Papaya", "Peach", "Pear", "Pineapple",
               "Pineapple - Organic", "Strawberry"),
        curry=("Curry",), pasta=("Pasta - Canned",), soup=("Soup",),
        veg=("Artichoke Heart", "Asparagus", "Bamboo Shoot", "Bean", "Bean - Organic", "Beet",
             "Cabbage", "Callaloo", "Chickpea products", "Corn", "Cucumber", "Heart of Palm",
             "Lentils products", "Mixed Vegetables", "Mushroom", "Okra", "Pea", "Pea - Organic",
             "Pea products", "Pepper - Pickled Hot", "Salsa", "Sauces", "Tomatillo", "Tomato",
             "Water Chestnut")),
    "bpa-2013": group(
        bev=("Beverage - Fruit", "Beverage - Other", "Beverage - Sport", "Energy Drink",
             "Soft Drink", "Juice - Apple", "Juice - Blend", "Juice - Mixed", "Juice - Other",
             "juice - pineapple"),
        coconut=("Coconut Milk",),
        fruit=("Cherry", "Gooseberry", "JackFruit", "Lychee", "Mango", "Mango - Organic",
               "Misc Fruit", "Mixed Fruit", "Orange", "Papaya", "Peach", "Pineapple"),
        formula=FORMULA, pasta=("Pasta - Canned",), pie=PIE, curry=("Sauces",), soup=("Soup",),
        veg=("Artichoke Heart", "Asparagus", "Bamboo Shoot", "Bean Products",
             "Chickpea Products", "Corn", "Heart of Palm", "Misc Vegetables", "Mixed Vegetables",
             "Mushroom")),
    "bpa-2016": group(
        bev=("Beverage - Fruit", "Beverage - Other", "Beverage - Sport", "Energy Drink",
             "Soft Drink", "Juice - Apple", "Juice - Blend", "Juice - Orange", "Juice - Other",
             "Juice - Tomato", "Juice - Vegetable", "Nectar - Guava", "Nectar - Mango",
             "Nectar - Other", "juice - pineapple"),
        coconut=("Coconut Milk",),
        fruit=("Apricot", "Grapefruit", "JackFruit", "Lychee", "Mango", "Mixed Fruit", "Orange",
               "Peach", "Pear", "Pineapple", "Pineapple - Organic"),
        formula=FORMULA, pasta=("Pasta - Canned",), pie=PIE, sauce=("Sauces", "Tomato Sauce"),
        soup=("Soup",),
        veg=("Artichoke", "Artichoke Heart", "Asparagus", "Bamboo Shoot", "Bean",
             "Bean - Green/Yellow", "Bean - wax", "Beet", "Carrot", "Corn", "Mixed Vegetables",
             "Mushroom", "Pea", "Spinach", "Yam")),
    "bpa-2017": group(
        meat=("Meat - Canned", "Chicken", "Ham", "Beef", "Pork"),
        fish=("Fish/Seafood - Canned", "Tuna", "Salmon", "Fish", "Mackerel", "Crab", "Herring",
              "Mussel", "Oyster", "Shrimp")),
}

# Printed figures (ppb; positives only): (n, positive, minimum, maximum, average).
TABLE5_2012 = {"bev": (72, 2, "5.9", "12.0", "9.0"), "coconut": (46, 17, "5.4", "381", "63.0"),
               "fruit": (73, 1, "8.6", "8.6", "8.6"), "curry": (24, 3, "88.0", "298", "227"),
               "veg": (144, 30, "5.5", "103", "34.0"), "pasta": (52, 52, "5.2", "157", "21.9"),
               "soup": (98, 39, "5.7", "277", "76.2")}
TABLE5_2013 = {"bev": (97, 34, "1.1", "190", "13.6"), "coconut": (13, 12, "4.8", "253", "84.2"),
               "fruit": (38, 19, "1.0", "53.6", "6.7"), "formula": (55, 28, "1.1", "12.5", "4.8"),
               "pasta": (45, 45, "6.7", "93.0", "19.5"), "pie": (20, 8, "3.4", "47.3", "22.3"),
               "curry": (5, 5, "6.2", "226", "75.5"), "soup": (48, 42, "1.2", "307", "42.6"),
               "veg": (70, 59, "1.1", "565", "31.8")}
TABLE2_2016 = {"bev": (135, 91, "1.7", "639", "40.8"), "coconut": (14, 12, "24.2", "1370", "306"),
               "fruit": (50, 34, "2.0", "1160", "62.1"), "formula": (66, 46, "2.3", "44.0", "8.7"),
               "pasta": (48, 39, "1.6", "270", "86.7"), "pie": (20, 16, "8.5", "2240", "281"),
               "sauce": (13, 5, "1.9", "1120", "228"), "soup": (46, 39, "2.5", "410", "107"),
               "veg": (72, 58, "5.3", "751", "139")}
# 2016-17 Table 4: analyte -> type -> (positive, minimum, maximum, average); others none.
TABLE4_2016 = {"badge": {"coconut": (4, "16.1", "224", "109"),
                         "sauce": (1, "14.3", "14.3", "14.3")},
               "bpf": {"veg": (3, "2.4", "3.8", "3.3")}, "bps": {}}
TABLE2_2017 = {"meat": (231, 170, "1.20", "407", "35.6"),
               "fish": (237, 159, "1.29", "1480", "54.7"),
               "all": (468, 329, "1.20", "1480", "44.8")}
ALT_2017 = {"badge": {"meat": (53, "0.98", "46.2", "10.8"), "fish": (19, "0.97", "53.2", "8.02")},
            "bpf": {"meat": (68, "1.01", "63.6", "15.3")},
            "bps": {"meat": (1, "1.79", "1.79", "1.79")}}
CANNED_2016 = (340, "91.6")
OTHER_2016 = (21, "15.2")
D1_CUT = 5.2
D1_OF = {"veg": "veg", "fruit": "fruit", "bev": "bev", "pasta": "pastasoup",
         "soup": "pastasoup", "coconut": "coconut", "curry": "curry"}
D1_LEFT_OUT_2013 = ("Beverage - Sport", "Energy Drink", "Soft Drink")


def load(name):
    with open(os.path.join(DATA, FILES[name]), newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["v"] = {k: float(r[k + "_ppb"]) if (k + "_ppb") in r else 0.0 for k in KEYS}
    return rows


def half(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def in_range(x, printed):
    return x is not None and abs(x - float(printed)) <= half(printed) + 1e-9


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


def values(rows, key="bpa", kind=None):
    return [r["v"][key] for r in rows if kind is None or r["type"] == kind]


def ranked(rows, key="bpa", kind=None):
    return sorted((r for r in rows if r["v"][key] > 0 and (kind is None or r["type"] == kind)),
                  key=lambda r: -r["v"][key])


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
        cls.rows = {name: load(name) for name in FILES}
        with open(SUMMARY, encoding="utf-8") as fh:
            cls.s = json.load(fh)
        cls.an = cls.s["analysis"]
        cls.preds = {p["id"]: p for p in cls.s["predictions"]}


class TestShape(Base):
    def test_counts_types_and_products(self):
        for name, rows in self.rows.items():
            self.assertEqual(len(rows), N[name], name)
            self.assertEqual(len({r["sample"] for r in rows}), N[name], name)
            products = {}
            for r in rows:
                products[r["product"]] = products.get(r["product"], 0) + 1
                self.assertEqual(r["type"], MAPS[name][r["product"]], (name, r["sample"]))
            self.assertEqual(products, self.s["census"][name]["products"], name)

    def test_record(self):
        ids = [p["id"] for p in self.s["predictions"]]
        self.assertEqual(ids, ["G09", "G10", "G11", "G12", "G13", "G16", "G17", "V1", "V2",
                               "V3", "V4", "V5", "V6", "V7", "D1", "T1", "X6", "X7"])
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (6, 4))
        gates_failed = {p["id"] for p in self.s["predictions"]
                        if p["kind"] == "gate" and not p["met"]}
        self.assertEqual(gates_failed, {"G09", "G11"})
        graded = {p["id"]: p["met"] for p in self.s["predictions"]
                  if p["kind"] == "prediction" and p["graded"]}
        self.assertEqual(graded, {"V2": True, "V4": False, "V5": True, "V6": False, "V7": True,
                                  "D1": True})
        self.assertFalse(self.preds["V1"]["graded"])
        self.assertFalse(self.preds["V3"]["graded"])
        # The two failed gates failed only on the sample-ID pattern.
        for name, n_bad in (("bpa-2009", 8), ("bpa-2011", 3)):
            gate = self.preds["G" + name[-2:]]["observed"]
            self.assertEqual({k for k, v in gate.items() if not v}, {"samples"}, name)
            self.assertEqual(len(self.s["census"][name]["ids_bad"]), n_bad, name)
        self.assertEqual(self.s["census"]["bpa-2011"]["ids_bad"],
                         ["2011BPA0086-2", "2011BPA0270-2", "2011BPA0272-2"])
        self.assertEqual(self.s["census"]["bpa-2009"]["ids_bad"],
                         ["2009BPA%d" % n for n in range(176, 184)])
        for name, sha in SHA256.items():
            self.assertEqual(self.s["provenance"][name]["sha256"], sha, name)


class Test2010(Base):
    def test_no_positive(self):
        st = stats(values(self.rows["bpa-2010"]))
        self.assertEqual((st["n"], st["k"]), (234, 0))
        self.assertTrue(self.preds["V2"]["met"])


class Test2012(Base):
    def test_table5_cells(self):
        rows = self.rows["bpa-2012"]
        got = {t: cells(p, stats(values(rows, kind=t))) for t, p in TABLE5_2012.items()}
        self.assertEqual(got, self.an["bpa-2012"]["table5"])
        ok = {"n": True, "detected": True, "min": True, "max": True, "avg": True}
        self.assertEqual(got["bev"], ok)
        self.assertEqual(got["fruit"], ok)
        self.assertEqual(got["soup"], ok)
        self.assertEqual(got["coconut"], dict(ok, avg=False))
        self.assertEqual(got["curry"], dict(ok, n=False))
        self.assertEqual(got["veg"], dict(ok, n=False, avg=False))
        self.assertEqual(got["pasta"], dict(ok, n=False, detected=False, avg=False))

    def test_totals_and_extremes(self):
        rows = self.rows["bpa-2012"]
        st = stats(values(rows))
        self.assertEqual((st["n"], st["k"]), (576, 145))
        pos = ranked(rows)
        self.assertTrue(in_range(pos[0]["v"]["bpa"], "381"))
        self.assertEqual(pos[0]["product"], "Coconut Milk")
        self.assertTrue(in_range(pos[-1]["v"]["bpa"], "5.2"))
        self.assertEqual(pos[-1]["type"], "pasta")
        self.assertEqual(stats(values(rows, kind="pasta"))["k"]
                         + stats(values(rows, kind="soup"))["k"], 92)

    def test_67_pastas_outside_table5(self):
        rows = self.rows["bpa-2012"]
        self.assertEqual(sum(p[0] for p in TABLE5_2012.values()), 509)
        self.assertEqual(sum(p[1] for p in TABLE5_2012.values()), 144)
        pasta = values(rows, kind="pasta")
        st = stats(pasta)
        self.assertEqual((st["n"], st["k"]), (119, 53))
        self.assertEqual(576 - 509, st["n"] - TABLE5_2012["pasta"][0])
        # 52 positives averaging 21.9 = the file's 53 less one value in this band.
        lo, hi = st["sum"] - 52 * 21.95, st["sum"] - 52 * 21.85
        band = [v for v in pasta if v > 0 and lo <= v <= hi]
        self.assertEqual(len(band), 11)
        for v in band:
            rest = list(pasta)
            rest.remove(v)
            r = stats(rest)
            self.assertEqual(r["k"], 52)
            self.assertTrue(in_range(r["mean"], "21.9"))
            self.assertTrue(in_range(r["min"], "5.2") and in_range(r["max"], "157"))

    def test_salsa_counted_with_curry(self):
        rows = self.rows["bpa-2012"]
        curry = [r["v"]["bpa"] for r in rows if r["type"] == "curry" or r["product"] == "Salsa"]
        veg = [r["v"]["bpa"] for r in rows if r["type"] == "veg" and r["product"] != "Salsa"]
        self.assertEqual(sum(1 for r in rows if r["product"] == "Salsa"), 3)
        c = cells(TABLE5_2012["curry"], stats(curry))
        v = cells(TABLE5_2012["veg"], stats(veg))
        self.assertTrue(all(c.values()), c)
        self.assertEqual(v, {"n": True, "detected": True, "min": True, "max": True,
                             "avg": False})
        self.assertTrue(in_range(stats(veg)["mean"], "34.7"))

    def test_coconut_average(self):
        st = stats(values(self.rows["bpa-2012"], kind="coconut"))
        self.assertEqual(st["k"], 17)
        self.assertAlmostEqual(st["sum"], 1111.2, places=6)
        self.assertTrue(in_range(st["mean"], "65.4"))
        self.assertFalse(17 * 62.95 <= st["sum"] <= 17 * 63.05)


class Test2013(Base):
    def test_table5_every_cell(self):
        rows = self.rows["bpa-2013"]
        for t, p in TABLE5_2013.items():
            c = cells(p, stats(values(rows, kind=t)))
            self.assertTrue(all(c.values()), (t, c))
            self.assertEqual(c, self.an["bpa-2013"]["table5"][t])
        st = stats(values(rows))
        self.assertEqual((st["n"], st["k"]), (391, 252))
        pos = ranked(rows)
        self.assertEqual(pos[0]["product"], "Corn")
        self.assertTrue(in_range(pos[0]["v"]["bpa"], "565"))
        self.assertEqual(pos[-1]["type"], "fruit")
        self.assertTrue(in_range(pos[-1]["v"]["bpa"], "1.0"))
        self.assertEqual([r["sample"] for r in rows if r["sample"].endswith("D")],
                         ["C2013BHPA00319D"])


class Test2016(Base):
    def test_table2(self):
        rows = self.rows["bpa-2016"]
        got = {t: cells(p, stats(values(rows, kind=t))) for t, p in TABLE2_2016.items()}
        self.assertEqual(got, self.an["bpa-2016"]["table2"])
        for t in ("coconut", "fruit", "pie", "veg"):
            self.assertTrue(all(got[t].values()), t)
        veg = stats(values(rows, kind="veg"))["mean"]
        self.assertTrue(in_range(veg, "139"))
        self.assertFalse(in_range(veg, "138"))
        st = stats(values(rows))
        self.assertEqual((st["n"], st["k"]), (491, 361))
        self.assertTrue(in_range(st["mean"], "87.2"))

    def test_surplus_is_the_non_canned_part(self):
        rows = self.rows["bpa-2016"]
        dn, dk = {}, {}
        for t, p in TABLE2_2016.items():
            st = stats(values(rows, kind=t))
            dn[t], dk[t] = st["n"] - p[0], st["k"] - p[1]
        self.assertEqual(dn, {"bev": 14, "coconut": 0, "fruit": 0, "formula": 8, "pasta": 1,
                              "pie": 0, "sauce": 2, "soup": 2, "veg": 0})
        self.assertEqual(dk, {"bev": 11, "coconut": 0, "fruit": 0, "formula": 7, "pasta": 0,
                              "pie": 0, "sauce": 2, "soup": 1, "veg": 0})
        self.assertEqual(sum(p[1] for p in TABLE2_2016.values()), CANNED_2016[0])
        self.assertEqual(sum(dk.values()), OTHER_2016[0])
        self.assertEqual(sum(dn.values()), 27)
        total = stats(values(rows))["sum"]
        expect = CANNED_2016[0] * float(CANNED_2016[1]) + OTHER_2016[0] * float(OTHER_2016[1])
        slack = CANNED_2016[0] * half(CANNED_2016[1]) + OTHER_2016[0] * half(OTHER_2016[1])
        self.assertLessEqual(abs(total - expect), slack + 1e-6)

    def test_maxima_and_next(self):
        rows = self.rows["bpa-2016"]
        tops = {t: ranked(rows, kind=t)[:2] for t in ("pie", "coconut", "fruit", "sauce")}
        vals = {t: [r["v"]["bpa"] for r in v] for t, v in tops.items()}
        self.assertEqual(vals, {"pie": [2240.0, 530.0], "coconut": [1370.0, 478.0],
                                "fruit": [1160.0, 186.0], "sauce": [1120.0, 188.0]})
        self.assertEqual(tops["pie"][0]["product"], "Pie Filling - Pumpkin")
        self.assertEqual(tops["fruit"][0]["product"], "Pineapple - Organic")
        # Table 2's canned sauces: 5 positives averaging 228 with maximum 1120 leave 17.5-22.5
        # ppb for the other four, so the 188 sauce cannot be one of them.
        k, _, _, mx, avg = TABLE2_2016["sauce"]
        lo = k * (float(avg) - half(avg)) - float(mx)
        hi = k * (float(avg) + half(avg)) - float(mx)
        self.assertAlmostEqual(lo, 17.5, places=9)
        self.assertAlmostEqual(hi, 22.5, places=9)
        self.assertGreater(vals["sauce"][1], hi)
        checks = self.preds["V6"]["observed"]["checks"]
        self.assertEqual({k for k, v in checks.items() if not v},
                         {"fruit_top_1160_next_186", "sauce_top_1120_next_7.5"})

    def test_table4_and_text(self):
        rows = self.rows["bpa-2016"]
        for key, printed in TABLE4_2016.items():
            for t in TABLE2_2016:
                st = stats(values(rows, key, t))
                if t not in printed:
                    self.assertEqual(st["k"], 0, (key, t))
                    continue
                k, mn, mx, avg = printed[t]
                self.assertEqual(st["k"], k, (key, t))
                for got, want in ((st["min"], mn), (st["max"], mx), (st["mean"], avg)):
                    self.assertTrue(in_range(got, want), (key, t, got, want))
        badge = ranked(rows, "badge")
        self.assertEqual((badge[0]["product"], badge[0]["v"]["bpa"]), ("Coconut Milk", 0.0))
        self.assertTrue(in_range(badge[0]["v"]["badge"], "224"))
        bpf = ranked(rows, "bpf")
        self.assertEqual(len(bpf), 3)
        self.assertTrue(all(r["product"] == "Bamboo Shoot" and r["v"]["bpa"] > 0 for r in bpf))
        self.assertEqual(ranked(rows, "bps"), [])
        self.assertEqual(identical_profiles(rows), [])


class Test2017(Base):
    def test_table2_and_text(self):
        rows = self.rows["bpa-2017"]
        for t, p in TABLE2_2017.items():
            c = cells(p, stats(values(rows, kind=None if t == "all" else t)))
            self.assertTrue(all(c.values()), (t, c))
            self.assertEqual(c, self.an["bpa-2017"]["table2"][t])
        meat = stats(values(rows, kind="meat"))["mean"]
        self.assertFalse(in_range(meat, "34.6") or in_range(meat, "46.6"))
        top = ranked(rows)[:2]
        self.assertTrue(in_range(top[0]["v"]["bpa"], "1480") and in_range(top[1]["v"]["bpa"], "567"))
        self.assertEqual((top[0]["type"], top[0]["function"]), ("fish", "Import"))
        bps = ranked(rows, "bps")
        self.assertEqual([(r["sample"], r["type"]) for r in bps], [("C2017BPHA00076", "meat")])
        self.assertTrue(in_range(bps[0]["v"]["bps"], "1.79"))
        badge = [r for r in rows if r["v"]["badge"] > 0]
        bpf = [r for r in rows if r["v"]["bpf"] > 0]
        self.assertEqual((len(badge), sum(1 for r in badge if r["v"]["bpa"] > 0)), (72, 69))
        self.assertEqual((len(bpf), sum(1 for r in bpf if r["v"]["bpa"] > 0)), (68, 68))
        self.assertTrue(in_range(stats(values(rows, "badge"))["mean"], "10.1"))

    def test_alternatives(self):
        rows = self.rows["bpa-2017"]
        for key, printed in ALT_2017.items():
            for t in ("meat", "fish"):
                st = stats(values(rows, key, t))
                if t not in printed:
                    self.assertEqual(st["k"], 0, (key, t))
                    continue
                k, mn, mx, avg = printed[t]
                self.assertEqual(st["k"], k, (key, t))
                for got, want in ((st["min"], mn), (st["max"], mx), (st["mean"], avg)):
                    self.assertTrue(in_range(got, want), (key, t, got, want))
        self.assertEqual(identical_profiles(rows), [])


class TestD1(Base):
    @staticmethod
    def shares(rows, name):
        groups = {}
        for r in rows:
            if name == "bpa-2013" and r["product"] in D1_LEFT_OUT_2013:
                continue
            g = D1_OF.get(r["type"])
            if g is None:
                continue
            row = groups.setdefault(g, [0, 0, 0])
            v = r["v"]["bpa"]
            row[0] += 1
            row[1] += int(v > 0)
            row[2] += int(v >= D1_CUT - 1e-6)
        n = sum(x[0] for x in groups.values())
        k = sum(x[2] for x in groups.values())
        return groups, k / n

    def test_common_cut(self):
        a, sa = self.shares(self.rows["bpa-2012"], "bpa-2012")
        b, sb = self.shares(self.rows["bpa-2013"], "bpa-2013")
        rec = self.an["d1"]
        self.assertEqual(a, rec["2012-13"]["groups"])
        self.assertEqual(b, rec["2013-14"]["groups"])
        self.assertAlmostEqual(sb / sa, rec["ratio"], places=9)
        self.assertGreaterEqual(sb / sa, 1.5)
        self.assertEqual(sum(x[0] for x in b.values()), 274)
        for g in a:
            self.assertGreater(b[g][2] / b[g][0], a[g][2] / a[g][0], g)


if __name__ == "__main__":
    unittest.main(verbosity=2)
