#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent test for docs/phthalates-series-0.1.0-result.md (CFIA 2018-19 phthalates in
flatbreads and vegan products; 2012-2018 phthalates in selected foods).

Does not import the grader. From the committed per-sample tables
data/phthalates_fv18_samples.csv and data/phthalates_ps12_samples.csv it rebuilds, with its own
code: the 2018-19 report's Table 2 in all seven rows, its text claims (526 without phthalates,
the single 24.00 tofu, the per-phthalate counts) and tofu's and mayonnaise's three positives; and,
for April 2012 to March 2015 by sampling date, every "2012-2015" row that the 2018-19 and 2020-21
reports print, part by part. It also pins the exploratory readings the note reports as not
registered. Each figure is checked against the sealed records where they have it. Standard library
only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SIX = ("BBP", "DBP", "DNOP", "DEHP", "DINP", "DIDP")
Y3 = ("2012-13", "2013-14", "2014-15")


def read(name):
    with open(os.path.join(DATA, name), newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["cells"] = {a: float(r[a]) for a in SIX if r[a].strip()}
        r["t"] = float(r["total"])
    return rows


def record(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def half(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def matches(x, printed):
    return x is not None and abs(x - float(printed)) <= half(printed) + 1e-9


def stats(rows):
    """(samples, positives, min positive, max positive, sum of positives)."""
    pos = sorted(r["t"] for r in rows if r["t"] > 0)
    return (len(rows), len(pos), pos[0] if pos else None, pos[-1] if pos else None, sum(pos))


def pct(k, n):
    return int(100.0 * k / n + 0.5)


def count_by(rows, key):
    d = {}
    for r in rows:
        d[r[key]] = d.get(r[key], 0) + 1
    return d


class F(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read("phthalates_fv18_samples.csv")
        cls.rec = record("phthalates_fv18_record.json")

    def sel(self, name):
        if name == "all":
            return self.rows
        if name in ("flatbread", "vegan"):
            return [r for r in self.rows if r["group"] == name]
        return [r for r in self.rows if r["subgroup"] == name]

    def test_shape_and_map(self):
        self.assertEqual(len(self.rows), 599)
        self.assertEqual(len({r["sample"] for r in self.rows}), 599)
        self.assertEqual(count_by(self.rows, "group"), {"flatbread": 208, "vegan": 391})
        self.assertEqual(count_by(self.rows, "subgroup"),
                         {"flatbread": 208, "dairy_alt": 76, "mayo": 53, "meat_alt": 125,
                          "tofu": 137})

    def test_cells_screen_and_totals(self):
        stored = 0
        for r in self.rows:
            self.assertAlmostEqual(r["t"], sum(r["cells"].values()), places=6, msg=r["sample"])
            self.assertEqual(int(r["screen_n"]), len(r["cells"]), r["sample"])
            self.assertTrue(all(v > 0 for v in r["cells"].values()), r["sample"])
            stored += len(r["cells"])
        self.assertEqual(stored, 81)

    def test_record_gate_and_grades(self):
        g = self.rec["gate"]
        self.assertEqual((g["md5"], g["samples_ok"], g["size_in_band_as_written"],
                          g["size_in_band_A2"], g["G_as_written"], g["A2"]),
                         (True, True, False, True, False, True))
        self.assertEqual((self.rec["bytes"], self.rec["md5"]),
                         (149790, "22dc3074e8e2c55b60fb96a666c5ff16"))
        self.assertEqual(self.rec["held"], ["F-V1", "F-V2", "F-V3", "F-V4"])

    PRINTED = {"flatbread": (208, 54, "0.57", "15.00", "2.70", 26),
               "vegan": (391, 19, "0.50", "24.00", "3.61", 5),
               "dairy_alt": (76, 6, "0.59", "2.78", "1.17", 8),
               "mayo": (53, 3, "0.72", "3.19", "1.64", 6),
               "meat_alt": (125, 7, "0.50", "7.57", "3.45", 6),
               "tofu": (137, 3, "0.54", "24.00", "10.85", 2),
               "all": (599, 73, "0.50", "24.00", "2.94", 12)}

    def test_table2_all_seven_rows(self):
        rows = self.rec["grades"]["F-V1"]["rows"]
        for name, (n, k, lo, hi, avg, share) in self.PRINTED.items():
            st = stats(self.sel(name))
            self.assertEqual(st[:2], (n, k), name)
            self.assertTrue(matches(st[2], lo) and matches(st[3], hi), (name, st))
            self.assertTrue(matches(st[4] / st[1], avg), (name, st[4] / st[1]))
            self.assertEqual(pct(k, n), share, name)
            self.assertAlmostEqual(rows[name]["stats"]["mean"], st[4] / st[1], places=5)

    def test_report_arithmetic_r2(self):
        vegan = (6 * 1.17 + 3 * 1.64 + 7 * 3.45 + 3 * 10.85) / 19
        self.assertTrue(matches(vegan, "3.61"))
        self.assertTrue(matches((54 * 2.70 + 19 * vegan) / 73, "2.94"))

    def test_text_claims(self):
        self.assertEqual(sum(1 for r in self.rows if r["t"] == 0), 526)
        top = max(r["t"] for r in self.rows)
        tops = [r for r in self.rows if r["t"] == top]
        self.assertEqual(len(tops), 1)
        self.assertEqual((tops[0]["sample"], tops[0]["product"], tops[0]["t"], tops[0]["cells"]),
                         ("C2018PHTH00718", "Tofu", 24.0, {"DBP": 24.0}))
        per = {a: sum(1 for r in self.rows if a in r["cells"]) for a in SIX}
        self.assertEqual(per, {"BBP": 0, "DBP": 4, "DNOP": 0, "DEHP": 24, "DINP": 51, "DIDP": 2})
        self.assertEqual((pct(51, 599), pct(24, 599)), (9, 4))
        self.assertEqual(sum(1 for r in self.rows if len(r["cells"]) >= 2), 8)

    def test_tofu_and_mayonnaise_positives_r3(self):
        tofu = sorted(r["t"] for r in self.sel("tofu") if r["t"] > 0)
        mayo = sorted(r["t"] for r in self.sel("mayo") if r["t"] > 0)
        self.assertEqual(tofu, [0.54, 8.0, 24.0])
        self.assertEqual(mayo, [0.72, 1.0, 3.19])
        self.assertTrue(7.985 <= tofu[1] <= 8.035)
        self.assertTrue(0.985 <= mayo[1] <= 1.035)
        eight = [r for r in self.sel("tofu") if r["t"] == 8.0][0]
        self.assertEqual((eight["sample"], eight["cells"]),
                         ("C2018PHTH00719", {"DBP": 4.0, "DEHP": 4.0}))

    def test_origin_and_positives_by_origin(self):
        self.assertEqual(count_by(self.sel("flatbread"), "function"),
                         {"Domestic": 97, "Import": 38, "Unknown": 73})
        self.assertEqual(count_by(self.sel("vegan"), "function"),
                         {"Domestic": 121, "Import": 156, "Unknown": 114})
        self.assertEqual(count_by([r for r in self.rows if r["t"] > 0], "function"),
                         {"Domestic": 34, "Import": 12, "Unknown": 27})


class P(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read("phthalates_ps12_samples.csv")
        cls.rec = record("phthalates_ps12_record.json")
        cls.y3 = [r for r in cls.rows if r["survey_year"] in Y3]

    def sel(self, name, rows=None):
        rows = self.y3 if rows is None else rows
        if name == "fats_oils":
            return [r for r in rows if r["group"] == "fats_oils"]
        return [r for r in rows if r["subgroup"] == name]

    def test_shape_screen_and_record(self):
        self.assertEqual(len(self.rows), 4517)
        self.assertEqual(len({r["sample"] for r in self.rows}), 4517)
        self.assertEqual(count_by(self.rows, "screen_n"),
                         {"0": 3540, "1": 695, "2": 204, "3": 67, "4": 11})
        per = {a: sum(1 for r in self.rows if a in r["cells"]) for a in SIX}
        self.assertEqual(per, {"BBP": 8, "DBP": 209, "DNOP": 0, "DEHP": 273, "DINP": 659,
                               "DIDP": 199})
        self.assertEqual(sum(per.values()), 1348)
        for r in self.rows:
            self.assertEqual(int(r["screen_n"]), len(r["cells"]), r["sample"])
        g = self.rec["gate"]
        self.assertEqual((g["md5"], g["samples_ok"], g["G_as_written"], g["A2"]),
                         (True, True, False, True))
        self.assertEqual((self.rec["bytes"], self.rec["md5"]),
                         (1288434, "2c80659a91013f3657519375ee33b400"))
        self.assertEqual(self.rec["held"], ["P-V1", "P-V4"])

    def test_p_v1_whole_file(self):
        st = stats(self.rows)
        self.assertEqual(st[:4], (4517, 977, 0.26, 2607.68))
        self.assertTrue(matches(st[3], "2608"))
        top = [r for r in self.rows if r["t"] == st[3]]
        self.assertEqual([(r["sample"], r["product"]) for r in top],
                         [("F2014PHTH00774", "Oil - Palm")])

    def test_y3_group_sizes_by_year(self):
        def by_year(name):
            return count_by(self.sel(name), "survey_year")
        self.assertEqual(by_year("grain"), {"2012-13": 99, "2013-14": 250, "2014-15": 110})
        self.assertEqual(by_year("rte"), {"2013-14": 171, "2014-15": 66})
        self.assertEqual(by_year("dressing"), {"2013-14": 5, "2014-15": 37})
        self.assertEqual(by_year("nut_seed"), {"2014-15": 100})
        self.assertEqual(count_by([r for r in self.sel("dressing") if r["t"] > 0],
                                  "survey_year"), {"2014-15": 8})

    def test_rows_that_match_except_their_count(self):
        # grain (2018-19 Table 3): 460 / 167 / 0.27 / 23.3 / 1.60
        st = stats(self.sel("grain"))
        self.assertEqual(st[:4], (459, 167, 0.27, 23.31))
        self.assertTrue(matches(st[3], "23.3") and matches(st[4] / st[1], "1.60"))
        self.assertEqual((pct(167, 459), pct(167, 460)), (36, 36))
        # RTE meals (2020-21 Table 3 and text): 224 / 128 (57.1%) / 0.27 / 15.4 / 1.46
        st = stats(self.sel("rte"))
        self.assertEqual(st[:4], (237, 128, 0.27, 15.4))
        self.assertTrue(matches(st[4] / st[1], "1.46"))
        self.assertEqual(round(100.0 * 128 / 224, 1), 57.1)
        self.assertEqual(round(100.0 * 128 / 237, 1), 54.0)
        # salad dressings (2020-21 Table 3 and text): 22 / 8 (36%) / 0.71 / 3.75 / 2.25
        st = stats(self.sel("dressing"))
        self.assertEqual(st[:4], (42, 8, 0.71, 3.75))
        self.assertTrue(matches(st[4] / st[1], "2.25"))
        self.assertAlmostEqual(st[4], 17.97, delta=0.001)
        self.assertEqual((pct(8, 22), pct(8, 42)), (36, 19))

    def test_nut_and_seed_butters_average(self):
        # 2018-19 Table 3: 100 / 59 (59%) / 0.5 / 315 / 17.2
        st = stats(self.sel("nut_seed"))
        self.assertEqual(st[:4], (100, 59, 0.5, 315.0))
        self.assertAlmostEqual(st[4], 1018.30, delta=0.001)
        self.assertFalse(matches(st[4] / st[1], "17.2"))
        self.assertEqual(round(st[4] / st[1], 1), 17.3)
        self.assertGreater(st[4], 17.25 * 59)

    def test_oils_and_fats_and_oils(self):
        # 2020-21 Table 3: fats and oils 327 / 0.26 / 2608 / 84.3; oil 180 / 0.26 / 2608 / 107
        oil = stats(self.sel("oil"))
        self.assertEqual(oil[:4], (160, 98, 0.26, 2607.68))
        self.assertAlmostEqual(oil[4], 10389.33, delta=0.001)
        self.assertFalse(matches(oil[4] / oil[1], "107"))
        self.assertEqual(round(oil[4] / oil[1]), 106)
        fo = stats(self.sel("fats_oils"))
        self.assertEqual(fo[:4], (248, 109, 0.26, 2607.68))
        self.assertAlmostEqual(fo[4], 10415.62, delta=0.001)
        self.assertFalse(matches(fo[4] / fo[1], "84.3"))
        self.assertEqual(round(fo[4] / fo[1], 1), 95.6)
        self.assertEqual(len(self.sel("mayo")) + len(self.sel("shortening")), 46)

    def test_p_v4_mayonnaise_and_shortening(self):
        st = stats(self.sel("mayo"))
        self.assertEqual(st[:2], (26, 3))
        self.assertEqual(pct(3, 26), 12)
        self.assertTrue(matches(st[4] / st[1], "2.77"))
        self.assertEqual(stats(self.sel("shortening"))[:2], (20, 0))

    def test_record_agrees(self):
        y3 = self.rec["year_readings"]["Y3"]
        for name in ("grain", "nut_seed", "rte", "oil", "dressing", "fats_oils", "mayo"):
            st = stats(self.sel(name))
            self.assertEqual((y3[name]["n"], y3[name]["positives"]), st[:2], name)
            self.assertAlmostEqual(y3[name]["mean"], st[4] / st[1], places=5)

    def test_exploratory_readings(self):
        # Not registered; read after the values. They pin what the note says, nothing more.
        unknown = [r for r in self.sel("dressing") if r["function"] == "Unknown"]
        self.assertEqual(stats(unknown)[:2], (22, 8))
        self.assertEqual(len(self.sel("oil")) + len(self.sel("shortening")), 180)
        butter = [r for r in self.y3 if r["product"] == "Butter"]
        bst = stats(butter)
        self.assertEqual(bst[:2], (84, 17))
        self.assertAlmostEqual(bst[4], 212.17, delta=0.001)
        fo = stats(self.sel("fats_oils"))
        self.assertTrue(matches((fo[4] + bst[4]) / (fo[1] + bst[1]), "84.3"))
        lard = [r for r in self.y3 if r["product"] in ("Lard", "Animal Fat")]
        self.assertEqual(stats(lard)[:2], (16, 0))
        self.assertEqual((fo[0] + bst[0], fo[0] + bst[0] + len(lard)), (332, 348))


if __name__ == "__main__":
    unittest.main(verbosity=2)
