#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent test for docs/fumonisin-0.1.0-result.md (CFIA's open 2010-11, 2011-12 and
2012-2018 fumonisin files).

Does not import the grader. From the committed per-sample tables data/fumonisin_fum10_samples.csv,
data/fumonisin_fum11_samples.csv and data/fumonisin_fum1218_samples.csv it rebuilds, with its own
code, every graded figure the note reports and every exploratory reading it gives (B1-only
positives and B2 stored for the first 56 samples in 2010-11, the "D" sample numbers in
2012-2018, positives by year), and checks each against the sealed records where they have it.
Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def read(name):
    with open(os.path.join(DATA, name), newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["b1"] = float(r["B1_ng_g"])
        r["b2"] = float(r["B2_ng_g"])
        r["t"] = float(r["total_ng_g"])
    return rows


def record(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def stats(rows):
    """(samples, positives, min positive, max positive, sum of positives)."""
    pos = sorted(r["t"] for r in rows if r["t"] > 0)
    return (len(rows), len(pos), pos[0] if pos else None, pos[-1] if pos else None, sum(pos))


def rounds_to(x, printed):
    half = 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5
    return float(printed) - half <= x < float(printed) + half


def count_by(rows, key):
    d = {}
    for r in rows:
        d[r[key]] = d.get(r[key], 0) + 1
    return d


def positives(rows):
    return [r for r in rows if r["t"] > 0]


class Shapes(unittest.TestCase):
    def test_rows_unique_and_totals(self):
        for name, n in (("fumonisin_fum10_samples.csv", 277), ("fumonisin_fum11_samples.csv", 498),
                        ("fumonisin_fum1218_samples.csv", 4320)):
            rows = read(name)
            self.assertEqual(len(rows), n, name)
            self.assertEqual(len({r["sample"] for r in rows}), n, name)
            for r in rows:
                self.assertGreaterEqual(r["b1"], 0.0, r["sample"])
                self.assertGreaterEqual(r["b2"], 0.0, r["sample"])
                self.assertAlmostEqual(r["t"], r["b1"] + r["b2"], places=6, msg=r["sample"])

    def test_tally(self):
        held, failed = [], []
        for f in ("fum10", "fum11", "fum1218"):
            rec = record(f"fumonisin_{f}_record.json")
            self.assertTrue(rec["gate"]["G"], f)
            self.assertTrue(rec["gate"]["md5"] and rec["gate"]["size_in_band"], f)
            self.assertFalse(rec["gate"]["samples_as_printed"], f)
            self.assertTrue(all(v == [] for v in rec["gate"]["problems"].values()), f)
            held += rec["held"]
            failed += rec["failed"]
        self.assertEqual(sorted(held), ["A-V2", "B-V11", "B-V2", "B-V3", "B-V4", "V2"])
        self.assertEqual(sorted(failed), ["2010-V5", "A-V1", "A-V3", "A-V4", "B-V1", "B-V10",
                                          "B-V7", "B-V8", "V1", "V3", "V4"])
        self.assertEqual(len(held) + len(failed), 17)
        not_graded = [k for f in ("fum10", "fum11", "fum1218")
                      for k, v in record(f"fumonisin_{f}_record.json")["grades"].items()
                      if v["held"] is None]
        self.assertEqual(sorted(not_graded), ["B-V5", "B-V6", "B-V9"])


class File2010(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read("fumonisin_fum10_samples.csv")
        cls.rec = record("fumonisin_fum10_record.json")

    def test_graded_items(self):
        n, k, lo, hi, s = stats(self.rows)
        self.assertEqual((n, k, lo, hi), (277, 185, 20.0, 4750.0))
        self.assertAlmostEqual(s, 38268.0, delta=0.01)
        self.assertEqual(round(s / k, 2), 206.85)
        self.assertFalse(267.5 <= s / k < 268.5)
        self.assertAlmostEqual(self.rec["grades"]["V1"]["stats"]["mean"], s / k, places=5)
        at_min = [r for r in self.rows if r["t"] == 20.0]
        self.assertEqual(count_by(at_min, "group"),
                         {"block": 3, "cornmeal_grits": 2, "popcorn": 1})
        top = [r for r in self.rows if r["t"] == hi]
        self.assertEqual([(r["sample"], r["product"], r["b1"], r["b2"]) for r in top],
                         [("2010FMN0213", "Cornmeal", 4750.0, 0.0)])
        big = [r for r in self.rows if r["t"] > 800]
        self.assertEqual(count_by(big, "product"),
                         {"Cereal - Corn": 3, "Cornmeal": 3,
                          "Bakery Product - Tortilla/Wrap/Pita": 1})
        self.assertEqual(self.rec["held"], ["V2"])

    def test_b1_alone_gives_157(self):
        self.assertEqual(sum(1 for r in self.rows if r["b1"] == 0), 120)
        b1pos = [r for r in self.rows if r["b1"] > 0]
        self.assertEqual(len(b1pos), 157)
        self.assertEqual(sum(1 for r in self.rows if r["b1"] == 0 and r["b2"] > 0), 28)
        self.assertAlmostEqual(sum(r["b1"] for r in self.rows), 32475.0, delta=0.01)
        self.assertAlmostEqual(sum(r["b2"] for r in self.rows), 5793.0, delta=0.01)
        tot = sum(r["t"] for r in b1pos)
        self.assertAlmostEqual(tot, 34568.0, delta=0.01)
        self.assertEqual(round(tot / 157, 1), 220.2)
        self.assertEqual(round(32475.0 / 157, 1), 206.8)

    def test_b2_only_in_the_first_56_samples(self):
        first = [r for r in self.rows if r["sample"][:11] <= "2010FMN0055"]
        later = [r for r in self.rows if r["sample"][:11] > "2010FMN0055"]
        self.assertEqual((len(first), len(later)), (56, 221))
        self.assertIn("2010FMN0031-2", {r["sample"] for r in first})
        self.assertTrue(all(r["b2"] > 0 for r in first))
        self.assertTrue(all(r["b2"] == 0 for r in later))
        self.assertEqual(self.rec["descriptive"]["zero_rows"], {"B1": 120, "B2": 221})
        self.assertEqual(self.rec["descriptive"]["positives_with_b1_zero"], 28)

    def test_lead_arithmetic(self):
        first = [r for r in self.rows if r["sample"][:11] <= "2010FMN0055"]
        later_b1 = [r for r in self.rows if r["sample"][:11] > "2010FMN0055" and r["b1"] > 0]
        self.assertEqual(len(later_b1), 129)
        self.assertAlmostEqual(sum(r["b1"] for r in first), 4652.0, delta=0.01)
        later_sum = sum(r["b1"] for r in later_b1)
        self.assertAlmostEqual(later_sum, 27823.0, delta=0.01)
        missing = 268 * 157 - 34568
        self.assertEqual(missing, 7508)
        self.assertEqual(round(100.0 * missing / later_sum), 27)
        self.assertEqual(6650 - 4750, 1900)

    def test_descriptive(self):
        self.assertEqual(count_by(positives(self.rows), "function"),
                         {"Domestic": 90, "Import": 95})
        nz1 = sorted(r["b1"] for r in self.rows if r["b1"] > 0)
        nz2 = sorted(r["b2"] for r in self.rows if r["b2"] > 0)
        self.assertEqual((nz1[0], nz2[0]), (20.0, 20.0))


class File2011(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read("fumonisin_fum11_samples.csv")
        cls.rec = record("fumonisin_fum11_record.json")

    def grp(self, g):
        return [r for r in self.rows if r["group"] == g]

    def test_a_v1(self):
        self.assertEqual(stats(self.rows)[1], 175)
        self.assertEqual([stats(self.grp(g))[:2] for g in ("corn", "other", "soy")],
                         [(262, 157), (45, 16), (191, 2)])
        soy = sorted((r["sample"], r["product"], r["t"]) for r in positives(self.grp("soy")))
        self.assertEqual(soy, [("2011FUM0148", "Infant Formula - Soy", 284.6),
                               ("2011FUM0192", "Flour - Soy", 22.4)])

    def test_a_v2_to_a_v4(self):
        corn = stats(self.grp("corn"))
        self.assertEqual(corn[2], 20.8)
        self.assertEqual([r["sample"] for r in self.grp("corn") if r["t"] == 20.8], ["2011FUM0326"])
        top = [r for r in self.rows if r["t"] == stats(self.rows)[3]]
        self.assertEqual([(r["sample"], r["product"], r["t"]) for r in top],
                         [("2011FUM0456", "Corn Products", 4442.5)])
        self.assertEqual(round(corn[4] / corn[1], 2), 259.80)
        self.assertFalse(253.15 <= corn[4] / corn[1] < 253.25)
        both = stats(self.grp("corn") + self.grp("other"))
        self.assertEqual(round(both[4] / both[1], 2), 247.97)
        self.assertAlmostEqual(self.rec["grades"]["A-V4"]["corn"]["mean"], corn[4] / corn[1],
                               places=5)
        self.assertEqual(self.rec["held"], ["A-V2"])

    def test_descriptive(self):
        self.assertEqual(count_by(positives(self.rows), "survey_year"),
                         {"2010-11": 1, "2011-12": 174})
        early = [r for r in positives(self.rows) if r["survey_year"] == "2010-11"]
        self.assertEqual([(r["sample"], r["product"], r["date"]) for r in early],
                         [("2011FUM0037", "Cornmeal", "2011-02-09")])
        self.assertEqual(sum(1 for r in self.rows if r["b2"] > 0), 107)
        self.assertEqual(sum(1 for r in self.rows if r["b1"] == 0 and r["b2"] > 0), 0)
        self.assertEqual(min(r["b2"] for r in self.rows if r["b2"] > 0), 15.0)
        self.assertEqual(min(r["b1"] for r in self.rows if r["b1"] > 0), 20.8)
        self.assertEqual(count_by(positives(self.rows), "function"),
                         {"Domestic": 56, "Import": 109, "Unknown": 10})


class File2012to2018(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read("fumonisin_fum1218_samples.csv")
        cls.rec = record("fumonisin_fum1218_record.json")

    def grp(self, g):
        return [r for r in self.rows if r["group"] == g]

    def test_b_v1_b_v2_b_v11(self):
        n, k, lo, hi, s = stats(self.rows)
        self.assertEqual((n, k, lo, hi), (4320, 1080, 20.0, 7790.0))
        self.assertEqual([stats(self.grp(g))[:2] for g in ("grain", "soy", "tea")],
                         [(3713, 1077), (182, 2), (425, 1)])
        top = [r for r in self.rows if r["t"] == hi]
        self.assertEqual([(r["sample"], r["product"], r["survey_year"]) for r in top],
                         [("C2017FUMN00349", "Cornmeal", "2017-18")])
        g = stats(self.grp("grain"))
        self.assertTrue(rounds_to(g[4] / g[1], "365") and rounds_to(s / k, "364"))
        self.assertAlmostEqual(g[4] / g[1], self.rec["grades"]["B-V11"]["means"]["grain"], places=5)
        self.assertAlmostEqual(s / k, self.rec["grades"]["B-V11"]["means"]["total"], places=5)
        soy = stats(self.grp("soy"))
        self.assertEqual(soy[4] / soy[1], 36.0)
        self.assertEqual(sorted(self.rec["held"]), ["B-V11", "B-V2", "B-V3", "B-V4"])

    def test_b_v3_b_v4(self):
        soy = sorted((r["sample"], r["product"], r["survey_year"], r["t"])
                     for r in positives(self.grp("soy")))
        self.assertEqual(soy, [("C2012FUMN00438", "Tofu", "2012-13", 27.0),
                               ("C2013FUMN00420", "Flour - Soy", "2013-14", 45.0)])
        tea = [(r["sample"], r["product"], r["survey_year"], r["t"])
               for r in positives(self.grp("tea"))]
        self.assertEqual(tea, [("C2016FUMN00273", "Tea - Black", "2016-17", 43.0)])

    def test_text_slip_7710(self):
        y12 = [r for r in self.rows if r["survey_year"] == "2012-13"]
        self.assertEqual(max(r["t"] for r in y12), 7711.0)
        self.assertEqual([r["sample"] for r in y12 if r["t"] == 7711.0], ["C2012FUMN00452"])
        self.assertFalse(any(7709.5 <= r["t"] < 7710.5 for r in self.rows))

    def test_d_numbers(self):
        d = [r for r in self.rows if r["sample"].endswith("D")]
        self.assertEqual(len(d), 16)
        ids = {r["sample"] for r in self.rows}
        partners = [r["sample"] for r in d if r["sample"][:-1] in ids]
        self.assertEqual(partners, ["C2015FUMN00349D"])
        self.assertEqual([(r["sample"], r["product"], r["t"]) for r in positives(d)],
                         [("C2013FUMN00590D", "Bran - Corn", 288.0)])
        rest = [r for r in self.rows if not r["sample"].endswith("D")]
        self.assertEqual(stats(rest)[:2], (4304, 1079))

    def test_years_and_labels(self):
        self.assertEqual(count_by(positives(self.rows), "survey_year"),
                         {"2012-13": 229, "2013-14": 226, "2014-15": 178, "2015-16": 2,
                          "2016-17": 1, "2017-18": 444})
        mid = [r for r in self.rows if r["survey_year"] in ("2015-16", "2016-17")]
        self.assertEqual(len(mid), 1500)
        self.assertFalse(any(r["label_grain"] == "corn" for r in mid))
        corn = [r for r in self.rows if r["label_grain"] == "corn"]
        by_year = {}
        for y in ("2012-13", "2013-14", "2014-15", "2017-18"):
            by_year[y] = stats([r for r in corn if r["survey_year"] == y])[:2]
        self.assertEqual(by_year, {"2012-13": (272, 169), "2013-14": (264, 178),
                                   "2014-15": (201, 117), "2017-18": (493, 254)})
        teff = [r for r in self.rows if r["label_grain"] == "teff"]
        self.assertEqual(stats(teff)[:4], (59, 1, 43.0, 43.0))
        self.assertEqual(sum(1 for r in self.rows if r["b1"] == 0 and r["b2"] > 0), 0)
        self.assertEqual(count_by(positives(self.rows), "function"),
                         {"Domestic": 128, "Import": 752, "Unknown": 200})

    def test_printed_extremes_under_broad_labels(self):
        w = [(r["product"], r["survey_year"], r["b1"], r["b2"]) for r in self.rows
             if abs(r["t"] - 393.0) < 1e-6]
        self.assertEqual(w, [("Bread - Other", "2012-13", 308.9, 84.1)])
        rice = [(r["product"], r["survey_year"]) for r in self.rows if r["t"] == 249.0]
        self.assertEqual(rice, [("Cereal - Adult", "2014-15")])
        self.assertGreater(sum(1 for r in self.rows if r["t"] == 33.0), 1)
        self.assertGreater(sum(1 for r in self.rows if 52.95 <= r["t"] < 53.05), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
