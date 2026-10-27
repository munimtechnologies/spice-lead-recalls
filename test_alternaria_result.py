#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/alternaria-0.1.0-result.md.

Rebuilds every report category from the committed per-sample table (data/alternaria_samples.csv)
with its own label mapping (it does not import the grader), checks it against the sealed grader
record data/alternaria_summary.json, and recomputes the figures quoted in the note: the four-row
reconciliation with CFIA's report, the missing tomato extremes, the infant and pomegranate
figures, the 2018 juice arithmetic and the EU Recommendation 2022/553 exceedances. Standard
library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import os
import statistics
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "alternaria_samples.csv")
SUMMARY = os.path.join(DATA, "alternaria_summary.json")

FRESH_PEPPER = {"Pepper - Fresh", "Pepper - Hot - Fresh", "Pepper (GH)", "Pepper - Organic"}
PROCESSED_PEPPER = {"Pepper - Pickled Hot", "Pepper - Pickled", "Vegetable Products"}
TOMATO = {"Tomato Sauce", "Tomato", "Tomato - Organic"}
BARLEY = {"Grain - Barley", "Barley Products"}
CORN = {"Cereal - Corn", "Cereal - Mixed Grains"}
NAMED = {"Infant Food - Puree": "puree_", "Infant Food (non-cereal)": "meal_", "Wine": "wine_"}
BY_YEAR = {"2019": "pomegranate_2019", "2016": "fruit_2016", "2015": "juice_pom_2014_15",
           "2014": "juice_pom_2014_15"}

# CFIA's report, by the year tables (Tables 3-11) plus the two derived groups of the
# report-check note: (samples, positives) per file category. 2020 rice 53/37 + wheat 1/1 +
# nut/seed 113/65; 2021 wheat 122/99 + sorghum 121/111; 2014-15 juices 75/15 + 147/72 and
# 2015 pomegranate 51/50.
REPORT = {
    "fresh_pepper_2020": (79, 0), "barley_2021": (123, 78), "wheat_sorghum_2021": (243, 210),
    "corn_2020": (52, 37), "rice_wheat_nutseed_2020": (167, 103),
    "processed_pepper_2020": (48, 6), "wheat_2017": (283, 247), "sunseed_2017": (34, 31),
    "sunoil_2017": (41, 31), "puree_2019": (108, 94), "puree_2016": (58, 42),
    "meal_2019": (90, 60), "meal_2016": (2, 1), "pomegranate_2019": (187, 124),
    "fruit_2016": (333, 109), "tomato_2016": (100, 41), "tomato_2015": (101, 36),
    "juice_pom_2014_15": (273, 137), "wine_2014": (75, 26), "wine_2015": (200, 141),
}


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_samples():
    with open(SAMPLES, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["aoh"] = float(r["aoh_ng_g"])
        r["ame"] = float(r["ame_ng_g"])
        r["total"] = float(r["total_ng_g"])
    return rows


def category(r):
    p, y = r["product"], r["plan"][:4]
    if r["file"] == "F2":
        if p == "Beer":
            return "f2_beer"
        if p == "Juice - Pomegranate":
            return "f2_pomegranate_juice"
        for prefix, cat in (("Oil - ", "f2_oil"), ("Seed - ", "f2_seed")):
            if p.startswith(prefix):
                return cat
        return "f2_juice"
    if p in FRESH_PEPPER:
        return "fresh_pepper_" + y
    if p in NAMED:
        return NAMED[p] + y
    if p in TOMATO and y in ("2015", "2016"):
        return "tomato_" + y
    if y == "2021":
        return "barley_2021" if p in BARLEY else "wheat_sorghum_2021"
    if y == "2020":
        if p in CORN:
            return "corn_2020"
        if p in PROCESSED_PEPPER:
            return "processed_pepper_2020"
        return "rice_wheat_nutseed_2020"
    if y == "2017":
        return {"Seed - Sunflower": "sunseed_2017",
                "Oil - Sunflower": "sunoil_2017"}.get(p, "wheat_2017")
    return BY_YEAR[y]


def stats(recs):
    totals = [r["total"] for r in recs]
    pos = [t for t in totals if t > 0]
    return {"n": len(totals), "pos": len(pos), "min": min(pos) if pos else None,
            "max": max(totals) if totals else None,
            "avg": statistics.fmean(pos) if pos else None}


def aoh_share(recs):
    a = sum(r["aoh"] for r in recs)
    m = sum(r["ame"] for r in recs)
    return a / (a + m)


def over(recs, aoh_level, ame_level):
    return [r for r in recs if r["aoh"] > aoh_level or r["ame"] > ame_level]


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_samples()
        cls.s = load_json(SUMMARY)
        cls.by = {}
        for r in cls.rows:
            cls.by.setdefault(category(r), []).append(r)

    def cat(self, *names):
        return [r for n in names for r in self.by.get(n, [])]


class TestTable(Base):
    def test_shape(self):
        self.assertEqual(len(self.rows), 2994)
        self.assertEqual(sum(1 for r in self.rows if r["file"] == "F1"), 2595)
        self.assertEqual(sum(1 for r in self.rows if r["file"] == "F2"), 399)
        self.assertEqual(len({(r["file"], r["sample"]) for r in self.rows}), 2994)
        for r in self.rows:
            self.assertEqual(r["total"], r["aoh"] + r["ame"], msg=r["sample"])
            self.assertGreaterEqual(min(r["aoh"], r["ame"]), 0.0)

    def test_own_mapping_matches_column(self):
        for r in self.rows:
            self.assertEqual(category(r), r["category"], msg=r["sample"])

    def test_categories_match_sealed_record(self):
        rec = self.s["analysis"]["categories"]
        self.assertEqual(set(rec), set(self.by))
        for cat, recs in self.by.items():
            st, want = stats(recs), rec[cat]
            self.assertEqual((st["n"], st["pos"]), (want["n"], want["pos"]), msg=cat)
            for k in ("min", "max", "avg"):
                if want[k] is None:
                    self.assertIsNone(st[k], msg=(cat, k))
                else:
                    self.assertAlmostEqual(st[k], want[k], places=9, msg=(cat, k))
            self.assertEqual(sum(1 for r in recs if r["aoh"] > 0), want["aoh_pos"], msg=cat)
            self.assertEqual(sum(1 for r in recs if r["ame"] > 0), want["ame_pos"], msg=cat)

    def test_gate_and_tally(self):
        self.assertTrue(all(self.s["predictions"][0]["observed"].values()))
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (29, 17))
        met = {p["id"]: p["met"] for p in self.s["predictions"]}
        missed = {"C9", "C12", "C14", "C15", "C16", "C17", "P3", "P4", "P5", "P6", "E1", "E2"}
        self.assertEqual({k for k, v in met.items() if not v}, missed)
        self.assertEqual(len(met), 29)


class TestReconciliation(Base):
    def test_totals(self):
        self.assertEqual(sum(n for n, _ in REPORT.values()), 2597)
        self.assertEqual(sum(p for _, p in REPORT.values()), 1554)
        f1 = stats([r for r in self.rows if r["file"] == "F1"])
        self.assertEqual((f1["n"], f1["pos"]), (2595, 1551))
        self.assertEqual(set(REPORT), {c for c in self.by if not c.startswith("f2_")})

    def test_gap_sits_in_four_rows(self):
        diffs = {}
        for cat, (n, pos) in REPORT.items():
            st = stats(self.by[cat])
            if (st["n"], st["pos"]) != (n, pos):
                diffs[cat] = (st["n"] - n, st["pos"] - pos)
        self.assertEqual(diffs, {"juice_pom_2014_15": (-1, -1), "tomato_2015": (-1, 0),
                                 "tomato_2016": (0, -1), "wine_2014": (0, -1)})

    def test_largest_totals(self):
        f1 = [r for r in self.rows if r["file"] == "F1"]
        big = [r for r in f1 if r["total"] > 700]
        self.assertEqual([(r["sample"], r["product"], r["total"]) for r in big],
                         [("C2019ALTN00289", "Juice - Pomegranate", 871.0)])
        self.assertAlmostEqual(stats(self.by["tomato_2016"])["max"], 6.72, places=9)
        self.assertAlmostEqual(stats(self.by["tomato_2015"])["max"], 3.91, places=9)
        y2016 = [r["total"] for r in f1 if r["plan"].startswith("2016")]
        self.assertAlmostEqual(max(y2016), 146.31, places=9)

    def test_row_sums(self):
        def gap(cat, pos, lo_avg, hi_avg):
            fsum = sum(r["total"] for r in self.by[cat])
            return pos * lo_avg - fsum, pos * hi_avg - fsum
        lo, hi = gap("tomato_2016", 41, 9.35, 9.45)          # printed 9.4, max 350
        self.assertEqual((round(lo, 1), round(hi, 1)), (342.4, 346.5))
        self.assertTrue(lo < 355 and hi > 345)
        lo, hi = gap("tomato_2015", 36, 24.5, 25.5)          # printed 25, max 880
        self.assertEqual((round(lo, 1), round(hi, 1)), (855.8, 891.8))
        lo, hi = gap("wine_2014", 26, 2.55, 2.65)            # printed 2.6, max 11
        self.assertEqual((round(lo, 1), round(hi, 1)), (15.2, 17.8))
        self.assertGreater(lo, 11.5)
        self.assertAlmostEqual(stats(self.by["wine_2014"])["max"], 6.0, places=9)
        self.assertAlmostEqual(stats(self.by["wine_2015"])["max"], 10.6, places=9)

    def test_juices_2018_include_pomegranate(self):
        juice, pomj = self.by["f2_juice"], self.by["f2_pomegranate_juice"]
        js, ps = stats(juice), stats(pomj)
        self.assertEqual((js["n"], js["pos"], ps["n"], ps["pos"]), (174, 120, 5, 5))
        both = [r["total"] for r in juice + pomj if r["total"] > 0]
        self.assertEqual(len(both), 125)
        avg = statistics.fmean(both)
        self.assertLessEqual(abs(avg - 17), 0.5)             # printed 17
        self.assertEqual(round(avg, 1), 17.1)
        self.assertGreater(abs(js["avg"] - 17), 0.5)
        self.assertEqual(round(sum(r["total"] for r in juice), 1), 896.9)
        self.assertEqual(round(sum(r["total"] for r in pomj), 1), 1246.5)
        f2 = stats([r for r in self.rows if r["file"] == "F2"])
        beer = stats(self.by["f2_beer"])
        self.assertEqual((f2["n"], f2["pos"]), (399, 232))
        self.assertEqual((beer["n"], beer["pos"]), (80, 21))
        self.assertEqual(232, 125 + stats(self.by["f2_seed"])["pos"]
                         + stats(self.by["f2_oil"])["pos"] + beer["pos"])
        self.assertAlmostEqual(beer["max"], 1.174, places=9)

    def test_small_misses(self):
        sun = stats(self.by["sunseed_2017"])
        self.assertEqual(round(sun["avg"], 1), 5.7)          # printed 5.6
        excess = sum(r["total"] for r in self.by["sunseed_2017"]) - 31 * 5.65
        self.assertTrue(0 < excess < 0.05)
        self.assertAlmostEqual(stats(self.by["f2_seed"])["min"], 0.113, places=9)
        self.assertAlmostEqual(stats(self.by["rice_wheat_nutseed_2020"])["min"], 0.091, places=9)
        self.assertAlmostEqual(stats([r for r in self.rows if r["file"] == "F1"])["min"], 0.05,
                               places=9)


class TestPredictions(Base):
    def test_infant_row_is_2019_only(self):
        allyrs = stats(self.cat("puree_2016", "puree_2019", "meal_2016", "meal_2019"))
        self.assertEqual((allyrs["n"], allyrs["pos"]), (258, 197))
        self.assertAlmostEqual(allyrs["max"], 37.1, places=9)
        self.assertTrue(4.95 <= allyrs["avg"] < 5.15)
        self.assertEqual(round(allyrs["avg"], 2), 5.04)
        y2019 = stats(self.cat("puree_2019", "meal_2019"))
        self.assertEqual(y2019["pos"], 154)
        self.assertAlmostEqual(y2019["max"], 25.94, places=9)
        self.assertEqual((round(y2019["avg"], 2), round(y2019["avg"], 1)), (5.23, 5.2))

    def test_table1_swap(self):
        pom = self.by["pomegranate_2019"]
        self.assertEqual((len(pom), sum(1 for r in pom if r["origin"] == "CANADA")), (187, 13))

    def test_eu_levels(self):
        eu = self.s["analysis"]["eu"]
        f2 = [r for r in self.rows if r["file"] == "F2"]
        tomato = self.cat("tomato_2015", "tomato_2016")
        self.assertEqual((len(tomato), len(over(tomato, 10, 5))), (200, 0))
        self.assertAlmostEqual(max(r["aoh"] for r in tomato), 6.22, places=9)
        self.assertAlmostEqual(max(r["ame"] for r in tomato), 0.9, places=9)

        sunseed = self.by["sunseed_2017"] + [r for r in f2 if r["product"] == "Seed - Sunflower"]
        self.assertEqual((len(sunseed), len(over(sunseed, 30, 30))), (51, 0))
        sesame = [r for r in f2 if r["product"] == "Seed - Sesame"]
        self.assertEqual(len(sesame), 3)
        self.assertEqual({(r["sample"], r["origin"], r["aoh"], r["ame"])
                          for r in over(sesame, 30, 30)},
                         {("C2018ALTN00379", "CANADA", 1.4, 53.7),
                          ("C2018ALTN00397", "INDIA", 34.7, 16.1)})

        sunoil = self.by["sunoil_2017"] + [r for r in f2 if r["product"] == "Oil - Sunflower"]
        self.assertEqual(len(sunoil), 51)
        self.assertEqual({(r["sample"], r["origin"], r["aoh"], r["ame"])
                          for r in over(sunoil, 10, 10)},
                         {("C2017ALTN00049", "CANADA", 11.4, 8.88),
                          ("C2017ALTN00296", "CANADA", 11.9, 50.4),
                          ("C2017ALTN00309", "CANADA", 10.2, 43.0)})
        self.assertEqual(sum(1 for r in sunoil if r["aoh"] > 10), 3)
        self.assertEqual(sum(1 for r in sunoil if r["ame"] > 10), 2)

        sf = aoh_share(sunseed + sunoil)
        fr = aoh_share(self.cat("pomegranate_2019", "wine_2014", "wine_2015", "tomato_2015",
                                "tomato_2016"))
        self.assertEqual((round(sf, 3), round(fr, 3)), (0.389, 0.75))
        self.assertAlmostEqual(sf, eu["sunflower_aoh_share"], places=9)
        self.assertAlmostEqual(fr, eu["fruit_aoh_share"], places=9)

        purees = self.cat("puree_2016", "puree_2019")
        self.assertEqual((len(purees), len(over(purees, 2, 2))), (166, 79))
        self.assertEqual(round(100 * 79 / 166, 1), 47.6)

        self.assertEqual((eu["tomato_n"], eu["tomato_exceed"], eu["sunseed_n"],
                          eu["sunseed_exceed"], eu["sesame_n"], eu["sesame_exceed"],
                          eu["sunoil_n"], eu["sunoil_exceed"], eu["puree_n"],
                          eu["puree_over_2"]),
                         (200, 0, 51, 0, 3, 2, 51, 3, 166, 79))


if __name__ == "__main__":
    unittest.main(verbosity=2)
