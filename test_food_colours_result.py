#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent test for docs/food-colours-0.1.0-result.md (CFIA food colours 2009-10 and 2018-19).

Does not import the grader. From the committed tables data/food_colours_c18_samples.csv,
data/food_colours_c18_detections.csv and data/food_colours_c09_rows.csv it rebuilds, with its own
code: Table 2 by product type; Table 3 per colour; V3-V8; the Orange II reading (the one sub-LQ
result explains Table 2's 336); the origin split; the ID numbers; the dates; and the twin scan.
Each is checked against the sealed record data/food_colours_summary.json. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import datetime
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "food_colours_c18_samples.csv")
DETECTIONS = os.path.join(DATA, "food_colours_c18_detections.csv")
C09 = os.path.join(DATA, "food_colours_c09_rows.csv")
SUMMARY = os.path.join(DATA, "food_colours_summary.json")

TYPES = ("essence", "oil", "veg", "sweets")
# Table 2 of the 2018-19 report: (samples, samples with a colour, colour detections).
TABLE2 = {"essence": (50, 9, 23), "oil": (99, 13, 13), "veg": (50, 28, 40),
          "sweets": (200, 131, 260)}
FILE_TABLE2 = {"essence": (50, 9, 23), "oil": (99, 13, 13), "veg": (50, 28, 40),
               "sweets": (200, 131, 261)}
# Table 3: colour -> (samples, printed maximum, printed average); Orange II average "< LQ 0.13".
TABLE3 = {"Allura Red": (101, "539", "78.7"), "Tartrazine": (100, "144", "27.1"),
          "Brilliant Blue FCF": (61, "85", "9.5"), "Sunset Yellow FCF": (44, "98.6", "20.5"),
          "Erythrosin B": (13, "124", "39.3"), "Amaranth": (12, "83.5", "26.9"),
          "Indigo Carmine": (3, "50.6", "21.3"), "Orange II": (2, "0.221", None),
          "Rhodamine B": (1, "10.8", "10.8")}
ORANGE_LQ = 0.13
# Function split (domestic, import, unknown) in the file; Table 1 prints sweets as 23 / 81 / 96.
FILE_SPLIT = {"essence": (10, 14, 26), "oil": (15, 51, 33), "veg": (8, 38, 4),
              "sweets": (23, 80, 97)}
C09_FIVE = ("Sunset, yellow", "Tartrazine, yellow", "Brilliant blue", "Allura, red", "Amaranth")
ID_RE = re.compile(r"^C2018FCOL(\d{5})(D?)$")


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def half(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def in_range(x, printed):
    return x is not None and abs(x - float(printed)) <= half(printed) + 1e-9


def day(text):
    for fmt in ("%d-%b-%y", "%m/%d/%Y"):
        try:
            return datetime.datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError(text)


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.samples = read(SAMPLES)
        cls.dets = read(DETECTIONS)
        cls.c09 = read(C09)
        for d in cls.dets:
            d["v"] = float(d["ppm"])
        for r in cls.c09:
            r["v"] = float(r["ppm"])
        cls.by = {s["sample"]: s for s in cls.samples}
        cls.det_by_sample = {}
        for d in cls.dets:
            cls.det_by_sample.setdefault(d["sample"], []).append(d)
        with open(SUMMARY, encoding="utf-8") as fh:
            cls.s = json.load(fh)
        cls.preds = {p["id"]: p for p in cls.s["predictions"]}
        cls.c18 = cls.s["files"]["c18"]
        cls.c09rec = cls.s["files"]["c09"]


class TestTable2(Base):
    def test_by_type_and_the_one_sweets_cell(self):
        got = {t: [0, 0, 0] for t in TYPES}
        for s in self.samples:
            n_col = int(s["n_colours"])
            got[s["type"]][0] += 1
            if n_col:
                got[s["type"]][1] += 1
                got[s["type"]][2] += n_col
        got = {t: tuple(v) for t, v in got.items()}
        self.assertEqual(got, FILE_TABLE2)
        per_type = {}
        for d in self.dets:
            per_type[d["type"]] = per_type.get(d["type"], 0) + 1
        self.assertEqual(per_type, {t: FILE_TABLE2[t][2] for t in TYPES})
        off = [t for t in TYPES if got[t] != TABLE2[t]]
        self.assertEqual(off, ["sweets"])
        self.assertEqual(got["sweets"][2] - TABLE2["sweets"][2], 1)
        self.assertEqual(sum(v[1] for v in got.values()), 181)
        self.assertEqual(sum(v[2] for v in got.values()), 337)
        oil_pos = [s for s in self.samples if s["type"] == "oil" and int(s["n_colours"])]
        self.assertEqual(len(oil_pos), 13)
        self.assertTrue(all(int(s["n_colours"]) == 1 for s in oil_pos))
        self.assertEqual(self.preds["V1"]["observed"]["by_type"],
                         {t: list(v) for t, v in got.items()})
        self.assertFalse(self.preds["V1"]["met"])

    def test_samples_table_agrees_with_detections(self):
        self.assertEqual(len(self.samples), 399)
        self.assertEqual(len(self.dets), 337)
        for s in self.samples:
            mine = self.det_by_sample.get(s["sample"], [])
            self.assertEqual(int(s["n_colours"]), len(mine), s["sample"])
            if mine:
                self.assertEqual(float(s["top_ppm"]), max(d["v"] for d in mine), s["sample"])
            else:
                self.assertEqual((s["top_colour"], s["top_ppm"]), ("", ""), s["sample"])
        self.assertTrue(all(d["v"] > 0 for d in self.dets))
        self.assertTrue(all(d["rows_above_zero"] == "1" for d in self.dets))


class TestTable3AndOrange(Base):
    def test_nine_colours(self):
        levels = {}
        for d in self.dets:
            levels.setdefault(d["colour"], []).append(d["v"])
        self.assertEqual(set(levels), set(TABLE3))
        for c, (n, pmax, pavg) in TABLE3.items():
            v = levels[c]
            mean = sum(v) / len(v)
            self.assertEqual(len(v), n, c)
            self.assertTrue(in_range(max(v), pmax), (c, max(v)))
            if pavg is not None:
                self.assertTrue(in_range(mean, pavg), (c, mean))
            rec = self.c18["descriptive"]["colour_stats"][c]
            self.assertEqual(rec["n"], n, c)
            self.assertAlmostEqual(rec["mean"], mean, places=9)
            self.assertEqual(rec["max"], max(v), c)
        self.assertFalse(self.preds["V2"]["met"])
        self.assertEqual(self.preds["V2"]["observed"]["other_colours_detected"], {})

    def test_orange_ii_settles_v2_v3_and_fits_table2(self):
        orange = sorted((d for d in self.dets if d["colour"] == "Orange II"),
                        key=lambda d: d["v"])
        self.assertEqual([(d["sample"], d["product"], d["type"], d["v"]) for d in orange],
                         [("C2018FCOL00376", "Pudding", "sweets", 0.042),
                          ("C2018FCOL00293", "Candy - Soft", "sweets", 0.221)])
        self.assertEqual((orange[0]["function"], orange[0]["origin"]),
                         ("Import", "UNITED STATES"))
        mean = (orange[0]["v"] + orange[1]["v"]) / 2
        self.assertAlmostEqual(mean, 0.1315, places=9)
        self.assertGreater(mean, ORANGE_LQ)
        self.assertTrue(in_range(mean, "0.13"))
        self.assertGreater(orange[0]["v"], 0.039)
        self.assertLess(orange[0]["v"], ORANGE_LQ)
        self.assertGreater(orange[1]["v"], ORANGE_LQ)
        sub_lq_orange = [d for d in orange if d["v"] < ORANGE_LQ]
        self.assertEqual(len(sub_lq_orange), 1)
        sweets = sum(1 for d in self.dets if d["type"] == "sweets")
        self.assertEqual(sweets - len(sub_lq_orange), TABLE2["sweets"][2])
        self.assertEqual(len(self.dets) - len(sub_lq_orange), 336)
        low_other = [d for d in self.dets if d["v"] < ORANGE_LQ and d["colour"] != "Orange II"]
        self.assertTrue(low_other)
        v3 = self.preds["V3"]["observed"]
        self.assertEqual((v3["detections"], v3["orange_ii_levels"], v3["orange_ii_low"]),
                         (337, [0.042, 0.221], []))
        self.assertEqual(v3["type_cells_off"], {"sweets": 1})
        self.assertFalse(self.preds["V3"]["met"])


class TestTextItems(Base):
    def test_v4_v5(self):
        hist = {}
        for s in self.samples:
            k = int(s["n_colours"])
            hist[k] = hist.get(k, 0) + 1
        self.assertEqual(hist, {0: 218, 1: 80, 2: 64, 3: 23, 4: 11, 5: 2, 6: 1})
        self.assertEqual(sum(n for k, n in hist.items() if 1 <= k <= 4), 178)
        self.assertEqual(self.preds["V4"]["observed"]["without_colour"], 218)
        self.assertEqual(self.preds["V5"]["observed"]["one_to_four"], 178)
        self.assertTrue(self.preds["V4"]["met"])
        self.assertTrue(self.preds["V5"]["met"])

    def test_v6_v7(self):
        top = max(self.dets, key=lambda d: d["v"])
        self.assertEqual((top["sample"], top["colour"], top["v"], top["product"]),
                         ("C2018FCOL00366", "Allura Red", 539.0, "Candy - Hard"))
        second = sorted((d["v"] for d in self.dets), reverse=True)[1]
        self.assertEqual(second, 475.0)
        rb = [d for d in self.dets if d["colour"] == "Rhodamine B"]
        self.assertEqual([(d["sample"], d["v"], d["product"], d["origin"]) for d in rb],
                         [("C2018FCOL00263", 10.8, "Pickled Vegetable - Misc", "LEBANON")])
        self.assertFalse(any(d["colour"] == "Chrysoidine G" for d in self.dets))
        dr = self.c18["descriptive"]["double_rows"]
        self.assertEqual([dr[c]["both_rows"] for c in ("Chrysoidine G", "Orange II",
                                                      "Rhodamine B")], [0, 0, 0])
        self.assertTrue(self.preds["V6"]["met"])
        self.assertTrue(self.preds["V7"]["met"])


class TestFile2009(Base):
    def test_v8_rows_and_shares(self):
        self.assertEqual(len(self.c09), 176)
        self.assertEqual(len({r["sample"] for r in self.c09}), 100)
        fat = [r for r in self.c09 if r["test"] == "FOOD COLOURS (FAT)"]
        water = [r for r in self.c09 if r["test"] == "FOOD COLOURS (WATER)"]
        self.assertEqual((len(fat), len(water)), (100, 76))
        self.assertEqual({r["colour"] for r in fat}, {"Fat-Soluble Dyes"})
        self.assertTrue(all(r["v"] == 0 for r in fat))
        self.assertTrue(all(r["v"] > 0 for r in water))
        pos = {r["sample"] for r in water}
        self.assertEqual(len(pos), 41)
        counts = {}
        for r in water:
            counts[r["colour"]] = counts.get(r["colour"], 0) + 1
        self.assertEqual(counts, {"Tartrazine, yellow": 18, "Sunset, yellow": 17,
                                  "Brilliant blue": 16, "Allura, red": 15, "Amaranth": 8,
                                  "Erythrosine": 1, "Indigotine": 1})
        five = sum(counts[c] for c in C09_FIVE)
        self.assertEqual(five, 74)
        share = five / len(water)
        self.assertFalse(0.925 <= share <= 0.935)
        self.assertAlmostEqual(share, 74 / 76, places=12)
        with_five = {r["sample"] for r in water if r["colour"] in C09_FIVE}
        self.assertEqual(with_five, pos)
        obs = self.preds["V8"]["observed"]
        self.assertEqual((obs["with_colour"], obs["results"], obs["five_colours"]), (41, 76, 74))
        self.assertEqual(obs["checks"], {"forty_one_with_colour": True, "no_fat_soluble": True,
                                         "five_share_92.5_93.5": False})
        self.assertFalse(self.preds["V8"]["met"])

    def test_largest_values_dates_and_twins(self):
        top2 = sorted(self.c09, key=lambda r: -r["v"])[:2]
        self.assertEqual([(r["sample"], r["colour"], r["v"]) for r in top2],
                         [("2009COL0012", "Tartrazine, yellow", 3836.7),
                          ("2009COL0012", "Allura, red", 2174.7)])
        self.assertEqual(top2[0]["product"], "Spices/flavours")
        dates = {}
        for r in self.c09:
            dates.setdefault(r["sample"], set()).add(r["date"])
        self.assertTrue(all(len(v) == 1 for v in dates.values()))
        per = {}
        for v in dates.values():
            d = day(next(iter(v)))
            per[d] = per.get(d, 0) + 1
        self.assertEqual((len(per), min(per), max(per)),
                         (16, datetime.date(2009, 9, 1), datetime.date(2010, 1, 8)))
        self.assertEqual(per[datetime.date(2009, 11, 9)], 25)
        self.assertEqual(max(per.values()), 25)
        profiles = {}
        for r in self.c09:
            if r["test"] == "FOOD COLOURS (WATER)":
                profiles.setdefault(r["sample"], []).append((r["colour"], r["v"]))
        seen = {}
        for sid, prof in profiles.items():
            if len(prof) >= 2:
                seen.setdefault(tuple(sorted(prof)), []).append(sid)
        self.assertEqual([v for v in seen.values() if len(v) > 1], [])
        self.assertEqual(self.c09rec["descriptive"]["twins"], [])


class TestDescriptive2018(Base):
    def test_origin_split_and_regions(self):
        got = {t: [0, 0, 0] for t in TYPES}
        regions = {}
        for s in self.samples:
            got[s["type"]][{"Domestic": 0, "Import": 1}.get(s["function"], 2)] += 1
            regions[s["region"]] = regions.get(s["region"], 0) + 1
        self.assertEqual({t: tuple(v) for t, v in got.items()}, FILE_SPLIT)
        self.assertEqual(self.c18["census_checks"]["S2b"],
                         {t: list(v) for t, v in FILE_SPLIT.items()})
        self.assertEqual(regions, {"ATLANTIC": 23, "ONTARIO": 151, "QUEBEC": 95, "WEST": 130})

    def test_ids(self):
        nums, suffixed = set(), []
        for s in self.samples:
            m = ID_RE.match(s["sample"])
            self.assertIsNotNone(m, s["sample"])
            nums.add(int(m.group(1)))
            if m.group(2):
                suffixed.append(s["sample"])
        self.assertEqual(nums, set(range(1, 401)) - {2})
        self.assertEqual(suffixed, ["C2018FCOL00008D"])
        self.assertNotIn("C2018FCOL00008", self.by)
        ids = self.c18["descriptive"]["ids_dates"]
        self.assertEqual((ids["gaps"], ids["id_range"]), ([2], [1, 400]))

    def test_dates_mixed_sample_and_twins(self):
        days = {s["sample"]: day(s["date"]) for s in self.samples}
        per = {}
        for d in days.values():
            per[d] = per.get(d, 0) + 1
        self.assertEqual((min(per), max(per), len(per), max(per.values())),
                         (datetime.date(2018, 4, 4), datetime.date(2019, 3, 26), 133, 17))
        order = sorted(days)
        first = min(per)
        fits = sum(1 for i, sid in enumerate(order)
                   if days[sid] == first + datetime.timedelta(days=i))
        self.assertEqual(fits, self.c18["descriptive"]["ids_dates"]["text_rank_fits"])
        self.assertLess(fits, 10)
        mixed = self.c18["descriptive"]["mixed"]
        self.assertEqual([m["sample"] for m in mixed], ["C2018FCOL00400"])
        self.assertEqual(mixed[0]["fields"], ["date"])
        self.assertEqual({day(x) for x in mixed[0]["values"]["date"]},
                         {datetime.date(2019, 2, 1)})
        seen = {}
        for sid, ds in self.det_by_sample.items():
            if len(ds) >= 2:
                seen.setdefault(tuple(sorted((d["colour"], d["v"]) for d in ds)), []).append(sid)
        self.assertEqual([v for v in seen.values() if len(v) > 1], [])
        self.assertEqual(self.c18["descriptive"]["twins"], [])


class TestRecord(Base):
    def test_gates_and_four_of_eight(self):
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (8, 4))
        met = {pid: p["met"] for pid, p in self.preds.items()}
        self.assertEqual(met, {"V1": False, "V2": False, "V3": False, "V4": True, "V5": True,
                               "V6": True, "V7": True, "V8": False, "V9": None})
        self.assertFalse(self.preds["V9"]["graded"])
        self.assertTrue(all(self.c18["gate"].values()))
        self.assertTrue(all(self.c09rec["gate"].values()))
        self.assertEqual(self.c18["facts"]["md5"], "7651427618a70aa3ad2a51ab90bcae8c")
        self.assertEqual(self.c09rec["facts"]["md5"], "dc558d850720b90610da2c75424d1cd7")
        self.assertEqual((self.c18["facts"]["rows"], self.c09rec["facts"]["rows"]),
                         (18354, 176))
        coding = self.c18["descriptive"]["coding"]
        self.assertEqual((coding["rows_zero"], coding["rows_above_zero"]), (18017, 337))


if __name__ == "__main__":
    unittest.main(verbosity=2)
