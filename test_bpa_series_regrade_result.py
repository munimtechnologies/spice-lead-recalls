#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent test for docs/bpa-series-0.1.1-regrade-result.md (CFIA BPA 2009-10 and 2011-12).

Does not import the grader. From the committed per-sample tables data/bpa_2009_samples.csv and
data/bpa_2011_samples.csv it recomputes, with its own code: V1 (2009-10: 82 positives, 9 infant
food, 1.4-9.6 ppb); V3 (2011-12: exactly six positives); the 2009-10 date sequence (the n-th ID
in text order is dated 2009-07-21 + (n - 1) days, for all 200); the ID arithmetic (the numbers
are exactly 1-200; 27 IDs with an extra zero, 8 with one too few; 1-100 formula, 101-200 food);
and the three 2011-12 '-2' pairs. Each is checked against the sealed records
data/bpa_series_summary_0.1.1.json and data/bpa_series_id_amendment.json. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import datetime
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SUMMARY = os.path.join(DATA, "bpa_series_summary_0.1.1.json")
AMEND = os.path.join(DATA, "bpa_series_id_amendment.json")
FILES = {"bpa-2009": "bpa_2009_samples.csv", "bpa-2011": "bpa_2011_samples.csv"}
SHA256 = {
    "bpa-2009": "8eaedfd8b8503368ed31e00631a91ba08378f6e5cad7f34724d65d2e91b33121",
    "bpa-2011": "64dff91acbd2eb953ef1c42effa34f709e868902d6ed03e5643320377f287918",
}
NEW_PATTERN = r"^C?\d{4}[A-Z]+\d{3,6}(?:D|-2)?$"
START = datetime.date(2009, 7, 21)


def load(name):
    with open(os.path.join(DATA, FILES[name]), newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["bpa"] = float(r["bpa_ppb"])
    return rows


def half(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def in_range(x, printed):
    return x is not None and abs(x - float(printed)) <= half(printed) + 1e-9


def digits(sample):
    m = re.fullmatch(r"\d{4}BPA(\d+)(?:-2)?", sample)
    return m.group(1)


def d2009(text):
    return datetime.datetime.strptime(text, "%m/%d/%Y").date()


def d2011(text):
    return datetime.datetime.strptime(text, "%d-%b-%y").date()


def positives(rows, kind=None):
    return sorted((r for r in rows if r["bpa"] > 0 and (kind is None or r["type"] == kind)),
                  key=lambda r: -r["bpa"])


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {name: load(name) for name in FILES}
        with open(SUMMARY, encoding="utf-8") as fh:
            cls.s = json.load(fh)
        with open(AMEND, encoding="utf-8") as fh:
            cls.a = json.load(fh)
        cls.preds = {p["id"]: p for p in cls.s["predictions"]}


class TestRecord(Base):
    def test_all_gates_pass_and_six_of_eight(self):
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (8, 6))
        gates = {p["id"]: p["met"] for p in self.s["predictions"] if p["kind"] == "gate"}
        self.assertEqual(gates, {g: True for g in
                                 ("G09", "G10", "G11", "G12", "G13", "G16", "G17")})
        graded = {p["id"]: p["met"] for p in self.s["predictions"]
                  if p["kind"] == "prediction" and p["graded"]}
        self.assertEqual(graded, {"V1": True, "V2": True, "V3": True, "V4": False, "V5": True,
                                  "V6": False, "V7": True, "D1": True})
        self.assertIsNone(self.preds["T1"]["met"])
        self.assertEqual(self.preds["T1"]["kind"], "descriptive")

    def test_provenance_and_census(self):
        for name, sha in SHA256.items():
            prov = self.s["provenance"][name]
            self.assertEqual(prov["sha256"], sha, name)
            self.assertTrue(prov["md5_matches_portal"], name)
            self.assertEqual(self.a["files"][name]["sha256"], sha, name)
            products = {}
            for r in self.rows[name]:
                products[r["product"]] = products.get(r["product"], 0) + 1
            self.assertEqual(products, self.s["census"][name]["products"], name)

    def test_amended_pattern(self):
        self.assertEqual(self.a["pattern"], NEW_PATTERN)
        for name, rows in self.rows.items():
            for r in rows:
                self.assertIsNotNone(re.match(NEW_PATTERN, r["sample"]), r["sample"])
        self.assertEqual(self.a["files"]["bpa-2009"]["old_pattern_rejects"],
                         ["2009BPA%d" % n for n in range(176, 184)])
        self.assertEqual(self.a["files"]["bpa-2011"]["old_pattern_rejects"],
                         ["2011BPA0086-2", "2011BPA0270-2", "2011BPA0272-2"])


class Test2009Values(Base):
    def test_v1(self):
        rows = self.rows["bpa-2009"]
        self.assertEqual(len(rows), 200)
        self.assertEqual(len({r["sample"] for r in rows}), 200)
        for r in rows:
            self.assertEqual(r["type"], {"Infant Formula": "formula",
                                         "Infant Food": "food"}[r["product"]], r["sample"])
        allp, food, formula = positives(rows), positives(rows, "food"), positives(rows, "formula")
        self.assertEqual((len(allp), len(food), len(formula)), (82, 9, 73))
        self.assertTrue(in_range(allp[-1]["bpa"], "1.4") and in_range(allp[0]["bpa"], "9.6"))
        self.assertTrue(in_range(food[-1]["bpa"], "1.4") and in_range(food[0]["bpa"], "9.6"))
        self.assertTrue(in_range(formula[-1]["bpa"], "1.6") and in_range(formula[0]["bpa"], "9.2"))
        obs = self.preds["V1"]["observed"]
        self.assertTrue(all(obs["checks"].values()), obs["checks"])
        for key, sub in (("all", allp), ("food", food), ("formula", formula)):
            self.assertEqual(obs["stats"][key]["k"], len(sub), key)
            self.assertAlmostEqual(obs["stats"][key]["mean"],
                                   sum(r["bpa"] for r in sub) / len(sub), places=9)


class Test2009Dates(Base):
    def test_text_order_is_a_day_by_day_series(self):
        rows = self.rows["bpa-2009"]
        order = sorted(rows, key=lambda r: r["sample"])
        for i, r in enumerate(order):
            self.assertEqual(d2009(r["date"]), START + datetime.timedelta(days=i), r["sample"])
        dates = {d2009(r["date"]) for r in rows}
        self.assertEqual(len(dates), 200)
        self.assertEqual(max(dates), datetime.date(2010, 2, 5))
        self.assertIn(datetime.date(2009, 12, 25), dates)
        self.assertIn(datetime.date(2010, 1, 1), dates)
        self.assertEqual(START.weekday(), 1)
        week = {}
        for d in dates:
            week[d.weekday()] = week.get(d.weekday(), 0) + 1
        self.assertEqual(week, {0: 28, 1: 29, 2: 29, 3: 29, 4: 29, 5: 28, 6: 28})

    def test_not_a_series_of_the_numbers(self):
        rows = self.rows["bpa-2009"]
        by_num = sorted(rows, key=lambda r: int(digits(r["sample"])))
        fits = sum(1 for i, r in enumerate(by_num)
                   if d2009(r["date"]) == START + datetime.timedelta(days=i))
        self.assertLess(fits, 200)
        registered = sum(1 for r in rows if d2009(r["date"]) == datetime.date(2009, 10, 1)
                         + datetime.timedelta(days=int(digits(r["sample"])) - 1))
        self.assertEqual(registered, 0)
        by_id = {r["sample"]: d2009(r["date"]) for r in rows}
        self.assertEqual(by_id["2009BPA0064"], datetime.date(2009, 10, 19))
        self.assertEqual(by_id["2009BPA00065"], datetime.date(2009, 7, 27))
        self.assertEqual(by_id["2009BPA0067"], datetime.date(2009, 10, 20))

    def test_id_arithmetic(self):
        rows = self.rows["bpa-2009"]
        nums = sorted(int(digits(r["sample"])) for r in rows)
        self.assertEqual(nums, list(range(1, 201)))
        width = {}
        for r in rows:
            n = len(digits(r["sample"]))
            width[n] = width.get(n, 0) + 1
        self.assertEqual(width, {3: 8, 4: 165, 5: 27})
        five = sorted(int(digits(r["sample"])) for r in rows if len(digits(r["sample"])) == 5)
        self.assertEqual(five, [65, 66] + list(range(81, 89)) + list(range(134, 151)))
        three = sorted(int(digits(r["sample"])) for r in rows if len(digits(r["sample"])) == 3)
        self.assertEqual(three, list(range(176, 184)))
        for r in rows:
            self.assertEqual(r["type"] == "formula", int(digits(r["sample"])) <= 100,
                             r["sample"])

    def test_record_t1(self):
        rows = self.rows["bpa-2009"]
        obs = self.preds["T1"]["observed"]
        self.assertEqual((obs["first"], obs["last"]), ("2009-07-21", "2010-02-05"))
        self.assertEqual((obs["n"], obs["distinct"]), (200, 200))
        self.assertTrue(obs["consecutive"])
        self.assertEqual(obs["rank_fits"]["text"], 200)
        self.assertEqual(obs["start_plus_number_fits"], 0)
        self.assertEqual(obs["weekdays"], {"Mon": 28, "Tue": 29, "Wed": 29, "Thu": 29,
                                           "Fri": 29, "Sat": 28, "Sun": 28})
        long_ids = sorted((r["sample"], d2009(r["date"]).isoformat()) for r in rows
                          if len(digits(r["sample"])) == 5)
        self.assertEqual([tuple(x) for x in obs["long_ids"]], long_ids)


class Test2011(Base):
    def test_v3(self):
        rows = self.rows["bpa-2011"]
        self.assertEqual(len(rows), 403)
        self.assertEqual(len({r["sample"] for r in rows}), 403)
        types, label_type = {}, {}
        for r in rows:
            types[r["type"]] = types.get(r["type"], 0) + 1
            self.assertEqual(label_type.setdefault(r["product"], r["type"]), r["type"])
        self.assertEqual(types, {"fruit": 101, "juice": 50, "pasta": 96, "soup": 5, "veg": 151})
        pos = positives(rows)
        want = [("Carrot", "307"), ("Pea", "183.3"), ("Corn", "74.0"), ("Pasta - Canned", "73.0"),
                ("Carrot", "21.9"), ("Carrot", "18.0")]
        self.assertEqual([r["product"] for r in pos], [w[0] for w in want])
        for r, (_, printed) in zip(pos, want):
            self.assertTrue(in_range(r["bpa"], printed), (r["sample"], r["bpa"]))
        for kind in ("fruit", "juice", "soup"):
            self.assertEqual(positives(rows, kind), [], kind)
        obs = self.preds["V3"]["observed"]
        self.assertTrue(all(obs["checks"].values()), obs["checks"])
        self.assertEqual(obs["counts"], {"carrot": 3, "corn": 1, "pasta": 1, "pea": 1})
        self.assertEqual({p["sample"] for p in obs["positives"]}, {r["sample"] for r in pos})

    def test_suffix_pairs_are_separate_samples(self):
        rows = self.rows["bpa-2011"]
        by = {r["sample"]: r for r in rows}
        suffixed = sorted(s for s in by if s.endswith("-2"))
        self.assertEqual(suffixed, ["2011BPA0086-2", "2011BPA0270-2", "2011BPA0272-2"])
        days = {}
        for s in suffixed:
            base = by[s[:-2]]
            self.assertEqual(base["product"], by[s]["product"], s)
            self.assertEqual((base["bpa"], by[s]["bpa"]), (0.0, 0.0), s)
            days[s] = (d2011(by[s]["date"]) - d2011(base["date"])).days
        self.assertEqual(days, {"2011BPA0086-2": 82, "2011BPA0270-2": 113,
                                "2011BPA0272-2": 113})
        self.assertEqual((by["2011BPA0270"]["origin"], by["2011BPA0270"]["function"]),
                         ("CANADA", "Domestic"))
        self.assertEqual((by["2011BPA0270-2"]["origin"], by["2011BPA0270-2"]["function"]),
                         ("UNITED STATES", "Import"))
        self.assertEqual(by["2011BPA0272"]["origin"], "CANADA")
        self.assertEqual(by["2011BPA0272-2"]["origin"], "THAILAND")
        rec = self.a["files"]["bpa-2011"]["suffix_pairs"]
        self.assertEqual([p["sample"] for p in rec], suffixed)
        for p in rec:
            self.assertTrue(p["base_present"], p["sample"])
            self.assertEqual(p["base_product"], p["product"])
            self.assertEqual(p["date"], by[p["sample"]]["date"])
            self.assertEqual(p["base_date"], by[p["base"]]["date"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
