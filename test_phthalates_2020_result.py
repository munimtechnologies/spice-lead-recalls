#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent test for docs/phthalates-2020-0.1.0-result.md (CFIA 2020-21 phthalates in
ready-to-eat meals, vegetable fats and oils).

Does not import the grader. From the committed per-sample table data/phthalates_2020_samples.csv it
rebuilds, with its own code: Table 2 (both averaging conventions), the 464 samples without
phthalates and the single 4.2 ppm maximum, the per-phthalate counts and the 7 multi-phthalate
samples, Table 3's 2020 oil and dressing rows, the empty mayonnaise and shortening groups, and the
file's origin counts against Table 1. Each is checked against the sealed record
data/phthalates_2020_record.json where the record has it. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "phthalates_2020_samples.csv")
RECORD = os.path.join(DATA, "phthalates_2020_record.json")
SIX = ("BBP", "DBP", "DNOP", "DEHP", "DINP", "DIDP")


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["cells"] = {a: float(r[a]) for a in SIX if r[a].strip()}
        r["t"] = float(r["total"])
    return rows


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


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read(SAMPLES)
        with open(RECORD, encoding="utf-8") as fh:
            cls.rec = json.load(fh)

    def where(self, **kw):
        return [r for r in self.rows if all(r[k] == v for k, v in kw.items())]


class TestFile(Base):
    def test_shape_and_map(self):
        self.assertEqual(len(self.rows), 500)
        ids = [r["sample"] for r in self.rows]
        self.assertEqual(len(set(ids)), 500)
        self.assertEqual(ids[0], "C2020PHTH00001")
        self.assertEqual(ids[-1], "C2020PHTH00500")
        self.assertEqual((len(self.where(group="rte")), len(self.where(group="fo"))), (250, 250))
        subs = {s: len(self.where(subgroup=s)) for s in ("oil", "dressing", "shortening", "mayo")}
        self.assertEqual(subs, {"oil": 150, "dressing": 50, "shortening": 48, "mayo": 2})

    def test_total_is_sum_of_cells_and_screen_agrees(self):
        stored = 0
        for r in self.rows:
            self.assertAlmostEqual(r["t"], sum(r["cells"].values()), places=6, msg=r["sample"])
            self.assertEqual(int(r["screen_n"]), len(r["cells"]), r["sample"])
            self.assertTrue(all(v > 0 for v in r["cells"].values()), r["sample"])
            stored += len(r["cells"])
        self.assertEqual(stored, 48)
        smallest = min(v for r in self.rows for v in r["cells"].values())
        self.assertEqual(smallest, 0.2)

    def test_record_gate_and_grades(self):
        g = self.rec["gate"]
        self.assertEqual((g["md5"], g["size_in_band"], g["samples_500"], g["A1"],
                          g["G_as_written"]), (True, True, True, True, False))
        self.assertTrue(all(not v for v in g["problems"].values()))
        self.assertEqual(self.rec["md5"], "612780be14a4a571044d93aaa27f99f2")
        self.assertEqual(self.rec["bytes"], 117529)
        self.assertEqual(self.rec["held"], ["V1", "V2", "V3", "V4", "V5"])
        ci = self.rec["census_items"]
        self.assertEqual((ci["S1"]["held"], ci["S2"]["held"], ci["S3"]["held"]),
                         (True, True, False))


class TestTable2(Base):
    PRINTED = {"rte": (250, 5, "0.3", "4.2", "1.56", 2, 7.8),
               "fo": (250, 31, "0.2", "3.4", "0.86", 12, 26.8),
               "all": (500, 36, "0.2", "4.2", "0.96", 7, 34.6)}

    def group(self, g):
        return self.rows if g == "all" else self.where(group=g)

    def test_eighteen_cells(self):
        for g, (n, k, lo, hi, avg, share, total) in self.PRINTED.items():
            st = stats(self.group(g))
            self.assertEqual(st[:2], (n, k), g)
            self.assertTrue(matches(st[2], lo) and matches(st[3], hi), (g, st))
            self.assertAlmostEqual(st[4], total, places=6, msg=g)
            self.assertTrue(matches(st[4] / st[1], avg), (g, st[4] / st[1]))
            self.assertEqual(pct(st[1], st[0]), share, g)

    def test_all_sample_average_matches_nothing(self):
        for g, (_, _, _, _, avg, _, _) in self.PRINTED.items():
            rows = self.group(g)
            self.assertFalse(matches(sum(r["t"] for r in rows) / len(rows), avg), g)
        self.assertAlmostEqual(sum(r["t"] for r in self.rows) / 500, 0.0692, places=9)

    def test_record_agrees(self):
        rows = self.rec["grades"]["V1"]["rows"]
        for g in ("rte", "fo", "all"):
            st = stats(self.group(g))
            self.assertEqual((rows[g]["stats"]["n"], rows[g]["stats"]["positives"]), st[:2])
            self.assertAlmostEqual(rows[g]["stats"]["mean"], st[4] / st[1], places=5)


class TestTextClaims(Base):
    def test_464_without_and_single_top(self):
        self.assertEqual(sum(1 for r in self.rows if r["t"] == 0), 464)
        top = max(r["t"] for r in self.rows)
        tops = [r for r in self.rows if r["t"] == top]
        self.assertEqual(len(tops), 1)
        t = tops[0]
        self.assertEqual((t["sample"], t["product"], t["group"], t["t"]),
                         ("C2020PHTH00482", "Meal - Toddler/Baby", "rte", 4.2))
        self.assertEqual(t["cells"], {"DBP": 0.9, "DNOP": 0.9, "DEHP": 0.9, "DINP": 0.6,
                                      "DIDP": 0.9})

    def test_per_phthalate_and_multi(self):
        per = {a: sum(1 for r in self.rows if a in r["cells"]) for a in SIX}
        self.assertEqual(per, {"BBP": 1, "DBP": 9, "DNOP": 2, "DEHP": 23, "DINP": 8, "DIDP": 5})
        self.assertAlmostEqual(100.0 * per["DEHP"] / 500, 4.6, places=9)
        multi = sorted(r["sample"][-3:] for r in self.rows if len(r["cells"]) >= 2)
        self.assertEqual(multi, ["030", "050", "120", "129", "268", "392", "482"])

    def test_children_meals(self):
        kids = self.where(product="Meal - Toddler/Baby")
        self.assertEqual(len(kids), 53)
        pos = sorted((r["t"], r["sample"]) for r in kids if r["t"] > 0)
        self.assertEqual(pos, [(2.2, "C2020PHTH00050"), (4.2, "C2020PHTH00482")])
        other = [r for r in self.where(group="rte") if r["product"] != "Meal - Toddler/Baby"]
        self.assertEqual(stats(other)[:2], (197, 3))
        self.assertTrue(all(len(r["cells"]) == 1 for r in other if r["t"] > 0))


class TestTable3AndV5(Base):
    def test_oils(self):
        st = stats(self.where(subgroup="oil"))
        self.assertEqual(st[:4], (150, 29, 0.2, 3.4))
        self.assertAlmostEqual(st[4], 25.9, places=6)
        self.assertTrue(matches(st[4] / st[1], "0.89"))

    def test_dressings(self):
        dress = self.where(subgroup="dressing")
        pos = sorted((r["t"], r["sample"]) for r in dress if r["t"] > 0)
        self.assertEqual(pos, [(0.3, "C2020PHTH00416"), (0.6, "C2020PHTH00402")])
        self.assertEqual(len(dress), 50)
        self.assertEqual(pct(2, 50), 4)
        self.assertAlmostEqual((0.3 + 0.6) / 2, 0.45, places=9)

    def test_no_mayo_or_shortening(self):
        for s in ("mayo", "shortening"):
            self.assertEqual(stats(self.where(subgroup=s))[1], 0, s)

    def test_fats_and_oils_split_from_the_report_arithmetic(self):
        # R2: (29 x 0.89 + 2 x 0.45) / 31 = 0.862 -> 0.86; the file's exact sums give 26.8 / 31.
        self.assertTrue(matches((29 * 0.89 + 2 * 0.45) / 31, "0.86"))
        self.assertAlmostEqual(stats(self.where(group="fo"))[4], 25.9 + 0.9, places=6)


class TestOrigin(Base):
    def test_table1_off_by_one_or_two(self):
        got = {}
        for g in ("rte", "fo"):
            d = {}
            for r in self.where(group=g):
                d[r["function"]] = d.get(r["function"], 0) + 1
            got[g] = d
        self.assertEqual(got, {"rte": {"Domestic": 56, "Import": 166, "Unknown": 28},
                               "fo": {"Domestic": 28, "Import": 159, "Unknown": 63}})
        printed = {"rte": {"Domestic": 56, "Import": 165, "Unknown": 29},
                   "fo": {"Domestic": 27, "Import": 161, "Unknown": 62}}
        self.assertNotEqual(got, printed)
        for g in got:
            self.assertEqual(sum(got[g].values()), sum(printed[g].values()))
        canada = {g: sum(1 for r in self.where(group=g) if r["origin"] == "CANADA")
                  for g in ("rte", "fo")}
        self.assertEqual(canada, {"rte": 56, "fo": 28})

    def test_positives_by_function(self):
        d = {}
        for r in self.rows:
            if r["t"] > 0:
                d[r["function"]] = d.get(r["function"], 0) + 1
        self.assertEqual(d, {"Import": 31, "Domestic": 2, "Unknown": 3})


if __name__ == "__main__":
    unittest.main(verbosity=2)
