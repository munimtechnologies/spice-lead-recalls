#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent test for docs/perchlorate-series-0.1.0-result.md (CFIA perchlorate 2010-11,
2011-13 and 2013-14).

Does not import the grader. From the committed per-sample table data/perchlorate_samples.csv it
rebuilds, with its own code: the record's grades; the two averaging conventions (the 2010-11
summary's all-sample averages and Table 3's detect-only averages); Table 3's formula rows (non-soy
count and range, all-formula average); and the 2013-14 block counts and shares. Each is checked
against the sealed record data/perchlorate_summary.json where the record has it.
Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "perchlorate_samples.csv")
SUMMARY = os.path.join(DATA, "perchlorate_summary.json")


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["v"] = float(r["perchlorate_ppb"])
    return rows


def half(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def matches(x, printed):
    return x is not None and abs(x - float(printed)) <= half(printed) + 1e-9


def stats(values):
    """(samples, detects, min detect, max detect, sum of detects)."""
    det = sorted(v for v in values if v > 0)
    return (len(values), len(det), det[0] if det else None, det[-1] if det else None, sum(det))


def detect_mean(values):
    st = stats(values)
    return st[4] / st[1] if st[1] else None


def all_mean(values):
    return sum(values) / len(values) if values else None


def is_soy(r):
    return "soy" in r["product"].lower()


def is_juice(r):
    p = r["product"].strip().lower()
    return p.startswith("juice") or p.startswith("nectar") or p == "beverage - fruit"


BLOCK_LABELS = {"mixed_vegetables": "Mixed Vegetables", "dried_vegetables": "Dried Vegetables",
                "soup": "Soup", "salsa": "Salsa", "beverage_other": "Beverage - Other",
                "pizza": "Pizza Products"}


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = read(SAMPLES)
        cls.f = {k: [r for r in rows if r["file"] == k] for k in ("p10", "p11", "p13")}
        with open(SUMMARY, encoding="utf-8") as fh:
            cls.s = json.load(fh)
        cls.preds = {p["id"]: p for p in cls.s["predictions"]}

    def vals(self, key, pred):
        return [r["v"] for r in self.f[key] if pred(r)]


class TestRecord(Base):
    def test_gates_and_one_of_nine(self):
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (9, 1))
        met = {pid: p["met"] for pid, p in self.preds.items()}
        expect = {"V%d" % i: False for i in range(1, 10)}
        expect["V1"] = True
        self.assertEqual(met, expect)
        for key, n, md5 in (("p10", 611, "f497970ea94e7d4eaf74fdabb9535bca"),
                            ("p11", 1426, "66a04ce98555c6898c18ebaefc042a96"),
                            ("p13", 477, "05b587cb13f15932894200ba5879445a")):
            rec = self.s["files"][key]
            self.assertTrue(all(rec["gate"].values()), key)
            self.assertEqual(rec["facts"]["md5"], md5)
            self.assertEqual(len(self.f[key]), n)
            self.assertEqual(len({r["sample"] for r in self.f[key]}), n)

    def test_coding_zero_and_smallest_two(self):
        for key, zeros in (("p10", 195), ("p11", 637), ("p13", 205)):
            v = [r["v"] for r in self.f[key]]
            self.assertEqual(sum(1 for x in v if x == 0), zeros, key)
            self.assertTrue(all(x >= 0 for x in v), key)
            self.assertEqual(min(x for x in v if x > 0), 2.0, key)

    def test_v1_held(self):
        groups = {g: self.vals("p10", lambda r, g=g: r["group"] == g)
                  for g in ("fv", "dairy", "formula")}
        self.assertEqual({g: stats(v)[:2] for g, v in groups.items()},
                         {"fv": (433, 283), "dairy": (89, 77), "formula": (89, 56)})
        allv = [r["v"] for r in self.f["p10"]]
        self.assertEqual(stats(allv)[2:4], (2.0, 540.0))
        top = max(self.f["p10"], key=lambda r: r["v"])
        self.assertEqual((top["sample"], top["commodity"]), ("2010PER0391", "Kale"))


class TestSummary2010AllSamples(Base):
    """Exploratory: the 2010-11 summary's averages are over all samples (non-detects as 0)."""

    def com(self, name):
        return self.vals("p10", lambda r: r["commodity"] == name)

    def test_six_printed_averages(self):
        cases = (("Cucumber", (22, 18, 1069.0), "48.6"), ("Tomato", (55, 35, 2472.0), "44.9"),
                 ("Cheese", (23, 16, 116.0), "5"), ("Yogurt", (24, 23, 118.0), "4.9"),
                 ("Infant Formula - Soy", (15, 13, 250.0), "16.7"))
        for name, (n, d, total), printed in cases:
            v = self.com(name)
            st = stats(v)
            self.assertEqual((st[0], st[1]), (n, d), name)
            self.assertAlmostEqual(st[4], total, places=6, msg=name)
            self.assertTrue(matches(all_mean(v), printed), (name, all_mean(v)))
            self.assertFalse(matches(detect_mean(v), printed), (name, detect_mean(v)))
        milk = self.com("Milk")
        self.assertEqual(stats(milk)[:2], (42, 38))
        self.assertAlmostEqual(stats(milk)[4], 193.0, places=6)
        self.assertLess(all_mean(milk), all_mean(self.com("Yogurt")))
        self.assertLess(all_mean(milk), all_mean(self.com("Cheese")))

    def test_record_detect_means_agree(self):
        obs = self.preds["V2"]["observed"]
        for name in ("Cheese", "Milk", "Yogurt"):
            self.assertAlmostEqual(obs["dairy_means"][name], detect_mean(self.com(name)),
                                   places=9)
        ranked = dict(obs["commodity_means"])
        self.assertAlmostEqual(ranked["Cucumber"], 1069 / 18, places=9)
        self.assertAlmostEqual(ranked["Tomato"], 2472 / 35, places=9)

    def test_kale_tops_on_any_reading(self):
        kale = self.com("Kale")
        self.assertEqual(sorted(kale), [15.0, 30.0, 130.0, 540.0])
        self.assertEqual(all_mean(kale), 178.75)
        self.assertEqual(detect_mean(kale), 178.75)


class TestTable3DetectOnly(Base):
    def test_2010_dairy_rows(self):
        com = lambda name: self.vals("p10", lambda r: r["commodity"] == name)
        self.assertTrue(matches(detect_mean(com("Milk")), "5.1"))
        self.assertTrue(matches(detect_mean(com("Yogurt")), "5.1"))
        self.assertEqual(detect_mean(com("Cheese")), 7.25)
        self.assertFalse(matches(detect_mean(com("Cheese")), "5.1"))
        self.assertFalse(matches(all_mean(com("Cheese")), "5.1"))
        dairy = self.vals("p10", lambda r: r["group"] == "dairy")
        self.assertAlmostEqual(stats(dairy)[4], 427.0, places=6)
        self.assertAlmostEqual(detect_mean(dairy), 427 / 77, places=9)
        self.assertFalse(5.05 <= detect_mean(dairy) <= 5.15)
        self.assertFalse(5.05 <= all_mean(dairy) <= 5.15)
        for name, n, hi in (("Cheese", 23, 24.0), ("Milk", 42, 9.0), ("Yogurt", 24, 12.0)):
            st = stats(com(name))
            self.assertEqual((st[0], st[2], st[3]), (n, 2.0, hi), name)

    def test_2013_dairy_and_2012_cream(self):
        # 2013-14 dairy = 20 cheeses (Cheese, Cheddar, Camembert, Feta, Gouda) and 30 yogurts
        # (Yogurt, Yogurt - Frozen, Beverage - Yogurt).
        yog = self.vals("p13", lambda r: r["group"] == "dairy" and
                        "yogurt" in r["product"].lower())
        cheese = self.vals("p13", lambda r: r["group"] == "dairy" and
                           "yogurt" not in r["product"].lower())
        self.assertEqual(stats(cheese)[:4], (20, 11, 3.0, 42.0))
        self.assertTrue(matches(detect_mean(cheese), "9.0"))
        self.assertEqual(stats(yog)[:4], (30, 29, 2.0, 11.0))
        self.assertTrue(matches(detect_mean(yog), "4.9"))
        cream = {y: self.vals("p11", lambda r, y=y: r["product"] == "Cream" and
                              r["survey_year"] == y) for y in ("2011-12", "2012-13")}
        self.assertEqual(stats(cream["2012-13"])[:4], (9, 9, 3.0, 7.0))
        self.assertEqual(detect_mean(cream["2012-13"]), 4.0)
        self.assertEqual(stats(cream["2011-12"])[:4], (6, 5, 3.0, 6.0))
        self.assertAlmostEqual(detect_mean(cream["2011-12"]), 4.6, places=9)


class TestTable3Formulas(Base):
    ROWS = {"p10": ((74, 2.0, 22.0), "10.4", (43, 333.0), (89, 56, 50.0, 583.0)),
            "p11": ((68, 2.0, 33.0), "11.8", (37, 359.0), (87, 51, 35.0, 604.0)),
            "p13": ((30, 2.0, 64.0), "16.5", (14, 220.0), (39, 21, 64.0, 347.0))}

    def test_count_and_range_non_soy_average_all(self):
        for key, (row, avg, (nd, nsum), (an, ad, amax, asum)) in self.ROWS.items():
            form = [r for r in self.f[key] if r["group"] == "formula"]
            non = [r["v"] for r in form if not is_soy(r)]
            allf = [r["v"] for r in form]
            st, sa = stats(non), stats(allf)
            self.assertEqual((st[0], st[2], st[3]), row, key)
            self.assertEqual(st[1], nd, key)
            self.assertAlmostEqual(st[4], nsum, places=6, msg=key)
            self.assertEqual((sa[0], sa[1], sa[3]), (an, ad, amax), key)
            self.assertAlmostEqual(sa[4], asum, places=6, msg=key)
            self.assertTrue(matches(detect_mean(allf), avg), (key, detect_mean(allf)))
            self.assertFalse(matches(detect_mean(non), avg), (key, detect_mean(non)))
            self.assertFalse(matches(all_mean(non), avg), key)

    def test_soy_max_outside_printed_range(self):
        for key, hi in (("p10", 22.0), ("p11", 33.0)):
            soy = [r["v"] for r in self.f[key] if r["group"] == "formula" and is_soy(r)]
            self.assertGreater(max(soy), hi, key)

    def test_record_agrees(self):
        o4 = self.preds["V4"]["observed"]
        self.assertAlmostEqual(o4["all_formulas"]["mean"], 583 / 56, places=9)
        self.assertAlmostEqual(o4["dairy_formula"]["mean"], 333 / 43, places=9)
        o6 = self.preds["V6"]["observed"]
        self.assertAlmostEqual(o6["non_soy_formulas"]["mean"], 359 / 37, places=9)
        self.assertEqual(o6["non_soy_formula_years"], {"2011-12": 68})
        o9 = self.preds["V9"]["observed"]
        self.assertAlmostEqual(o9["all_formulas"]["mean"], 347 / 21, places=9)
        self.assertAlmostEqual(o9["non_soy_formula"]["mean"], 220 / 14, places=9)


class TestShares2013(Base):
    def block(self, name):
        if name == "juices":
            return [r for r in self.f["p13"] if is_juice(r)]
        if name == "base_processed":
            named = set(BLOCK_LABELS.values())
            return [r for r in self.f["p13"] if r["group"] == "processed" and
                    r["product"] not in named]
        return [r for r in self.f["p13"] if r["product"] == BLOCK_LABELS[name]]

    def tally(self, name):
        st = stats([r["v"] for r in self.block(name)])
        return st[0], st[1]

    def test_block_counts(self):
        expect = {"base_processed": (46, 19), "dried_vegetables": (17, 12),
                  "mixed_vegetables": (10, 9), "soup": (15, 4), "salsa": (9, 9),
                  "juices": (47, 12), "beverage_other": (3, 2), "pizza": (20, 17)}
        self.assertEqual({k: self.tally(k) for k in expect}, expect)

    def test_grading_map_shares(self):
        got = {}
        for g in ("fresh", "processed", "dairy", "formula", "grain", "assorted"):
            got[g] = stats(self.vals("p13", lambda r, g=g: r["group"] == g))[:2]
        self.assertEqual(got, {"fresh": (131, 92), "processed": (97, 53), "dairy": (50, 40),
                               "formula": (39, 21), "grain": (60, 18), "assorted": (100, 48)})
        self.assertEqual(sum(d for _, d in got.values()), 272)
        pct = lambda n, d: int(100.0 * d / n + 0.5)
        self.assertEqual([pct(*got[g]) for g in ("fresh", "processed", "dairy", "grain",
                                                 "assorted")], [70, 55, 80, 30, 48])

    def test_no_allowed_placement_gives_processed_40(self):
        placements = self.s["files"]["p13"]["map_search_all_blocks_feasible"]
        self.assertEqual(len(placements), 11)
        movable = ("mixed_vegetables", "dried_vegetables", "juices", "soup", "salsa",
                   "beverage_other")
        tallies = {k: self.tally(k) for k in movable + ("base_processed",)}
        shares = []
        for p in placements:
            n, d = tallies["base_processed"]
            for k in movable:
                if p["choice"][k] == "processed":
                    n += tallies[k][0]
                    d += tallies[k][1]
            shares.append(100.0 * d / n)
        self.assertTrue(all(int(s + 0.5) != 40 for s in shares), shares)
        self.assertAlmostEqual(min(shares), 4000 / 102, places=9)
        self.assertAlmostEqual(max(shares), 4900 / 82, places=9)

    def test_juices_as_processed(self):
        jp = self.s["files"]["p13"]["descriptive"]["juices_as_processed"]
        self.assertEqual((jp["processed"]["n"], jp["processed"]["detects"]), (144, 65))
        self.assertEqual((jp["assorted"]["n"], jp["assorted"]["detects"]), (53, 36))
        self.assertEqual((97 + self.tally("juices")[0], 53 + self.tally("juices")[1]), (144, 65))

    def test_max_arugula(self):
        top = max(self.f["p13"], key=lambda r: r["v"])
        self.assertEqual((top["sample"], top["product"], top["v"]),
                         ("C2013PERC00065", "Arugula", 3300.0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
