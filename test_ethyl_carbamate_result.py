#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent test for docs/ethyl-carbamate-0.1.0-result.md (CFIA ethyl carbamate 2018-19 and
2019-20).

Does not import the grader. From the committed per-sample table data/ethyl_carbamate_samples.csv
it rebuilds, with its own code: the graded rows of V1, V2, V3, V5, V6 and V7 as registered; the
scale finding (36 of the 37 2018-19 detects are 1000 times below the printed ppb, one vinegar is
not); the exploratory rescale that reproduces every printed 2018-19 cell; the region pattern; and
the labelled rows. Each is checked against the sealed record data/ethyl_carbamate_summary.json.
Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import datetime
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "ethyl_carbamate_samples.csv")
SUMMARY = os.path.join(DATA, "ethyl_carbamate_summary.json")

# Printed rows (samples, detects, minimum, maximum, average); a tuple average is an inclusive band.
BEER = (125, 2, "4", "4", "4")
VINEGAR = (125, 6, "6", "135", "29.5")
POOLED = (140, 29, "4", "86", (15.42, 15.62))
TOTAL18 = (390, 37, "4", "135", "17.2")
SUBTOTAL = (265, 31, "4", "86", (14.75, 14.85))
VEG = (200, 3, "4", "9", (6.25, 6.35))
SOY = (100, 6, "7", "217", (107.5, 108.5))
TOTAL19 = (300, 9, "4", "217", (73.5, 74.5))


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["v"] = float(r["ec_ppb"])
    return rows


def half(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def in_range(x, printed):
    return x is not None and abs(x - float(printed)) <= half(printed) + 1e-9


def stats(values):
    det = sorted(v for v in values if v > 0)
    mean = sum(det) / len(det) if det else None
    return (len(values), len(det), det[0] if det else None, det[-1] if det else None, mean)


def fits(st, spec):
    n, d, lo, hi, avg = spec
    if isinstance(avg, tuple):
        avg_ok = st[4] is not None and avg[0] - 1e-9 <= st[4] <= avg[1] + 1e-9
    else:
        avg_ok = in_range(st[4], avg)
    return {"samples": st[0] == n, "detects": st[1] == d, "min": in_range(st[2], lo),
            "max": in_range(st[3], hi), "average": avg_ok}


def rescaled(v):
    """Exploratory only: a 2018-19 value below 1 read as micrograms per gram."""
    return round(v * 1000, 6) if 0 < v < 1 else v


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = read(SAMPLES)
        cls.r18 = [r for r in rows if r["file"] == "ec18"]
        cls.r19 = [r for r in rows if r["file"] == "ec19"]
        with open(SUMMARY, encoding="utf-8") as fh:
            cls.s = json.load(fh)
        cls.preds = {p["id"]: p for p in cls.s["predictions"]}

    def vals(self, rows, t, scale=False):
        return [rescaled(r["v"]) if scale else r["v"] for r in rows if r["type"] == t]


class TestRecord(Base):
    def test_gates_and_three_of_six(self):
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (6, 3))
        met = {pid: p["met"] for pid, p in self.preds.items()}
        self.assertEqual(met, {"V1": False, "V2": False, "V3": False, "V4": None, "V5": True,
                               "V6": True, "V7": True})
        for name, md5 in (("ec18", "d7d7bf62a3bb275ccec657fb27501fd8"),
                          ("ec19", "e5aab1da6e57c1afa0536e9d92455a6e")):
            rec = self.s["files"][name]
            self.assertTrue(all(rec["gate"].values()), name)
            self.assertEqual(rec["facts"]["md5"], md5)
        self.assertEqual((len(self.r18), len(self.r19)), (390, 300))
        self.assertEqual(len({r["sample"] for r in self.r18 + self.r19}), 690)


class TestAsRegistered(Base):
    def test_v1_cells_fail_on_scale_only(self):
        cells = self.preds["V1"]["observed"]["cells"]
        beer, vin, oth = (self.vals(self.r18, t) for t in ("beer", "vinegar", "other"))
        self.assertEqual((len(beer), len(oth), len(vin)), (125, 140, 125))
        mine = {"beer": fits(stats(beer), BEER), "vinegar": fits(stats(vin), VINEGAR),
                "other_pooled": fits(stats(oth), POOLED),
                "total": fits(stats(beer + oth + vin), TOTAL18)}
        self.assertEqual(mine, cells)
        for k in mine:
            self.assertTrue(mine[k]["samples"] and mine[k]["detects"], k)
        self.assertEqual(stats(beer)[1:4], (2, 0.004, 0.004))
        self.assertAlmostEqual(stats(vin)[4], 135.042 / 6, places=9)
        self.assertAlmostEqual(stats(beer + oth + vin)[4],
                               self.preds["V1"]["observed"]["rows"]["total"]["mean"], places=9)

    def test_v2_and_v3(self):
        vin = sorted(v for v in self.vals(self.r18, "vinegar") if v > 0)
        self.assertEqual(vin, [0.006, 0.006, 0.007, 0.01, 0.013, 135.0])
        self.assertEqual(vin, self.preds["V2"]["observed"]["vinegar_detects"])
        self.assertAlmostEqual(sum(vin[:-1]), 0.042, places=9)
        sub = stats(self.vals(self.r18, "beer") + self.vals(self.r18, "other"))
        self.assertEqual(sub[:2], (265, 31))
        self.assertEqual(fits(sub, SUBTOTAL), self.preds["V3"]["observed"]["cells"])
        self.assertFalse(fits(sub, SUBTOTAL)["average"])


class TestScale(Base):
    def test_one_value_on_the_printed_scale(self):
        det = [r for r in self.r18 if r["v"] > 0]
        self.assertEqual(len(det), 37)
        big = [r for r in det if r["v"] >= 1]
        self.assertEqual([(r["sample"], r["product"], r["region"], r["v"]) for r in big],
                         [("C2018ETCA00370", "Vinegar", "ONTARIO", 135.0)])
        small = [r for r in det if r["v"] < 1]
        self.assertEqual(len(small), 36)
        self.assertEqual((min(r["v"] for r in small), max(r["v"] for r in small)),
                         (0.004, 0.086))
        self.assertEqual({r["region"] for r in small}, {"WEST"})
        self.assertTrue(all(r["v"] == 0 for r in self.r18 if r["v"] <= 0))
        self.assertTrue(all(r["v"] >= 4 for r in self.r19 if r["v"] > 0))
        self.assertTrue(self.s["files"]["ec18"]["gate"]["units"])

    def test_regions(self):
        n, d = {}, {}
        for r in self.r18:
            n[r["region"]] = n.get(r["region"], 0) + 1
            if r["v"] > 0:
                d[r["region"]] = d.get(r["region"], 0) + 1
        self.assertEqual(n, {"ATLANTIC": 27, "ONTARIO": 154, "QUEBEC": 87, "WEST": 122})
        self.assertEqual(d, {"WEST": 36, "ONTARIO": 1})


class TestRescaleExploratory(Base):
    def test_every_printed_2018_cell(self):
        beer, vin, oth = (self.vals(self.r18, t, scale=True) for t in ("beer", "vinegar", "other"))
        for got, spec in ((stats(beer), BEER), (stats(vin), VINEGAR), (stats(oth), POOLED),
                          (stats(beer + oth + vin), TOTAL18), (stats(beer + oth), SUBTOTAL)):
            self.assertTrue(all(fits(got, spec).values()), (got, spec))
        self.assertAlmostEqual(sum(v for v in oth if v > 0), 451, places=6)
        self.assertAlmostEqual(stats(vin)[4], 29.5, places=9)
        self.assertAlmostEqual(stats(beer + oth + vin)[4], 636 / 37, places=9)
        self.assertAlmostEqual(stats(beer + oth)[4], 459 / 31, places=9)
        vd = sorted(v for v in vin if v > 0)
        self.assertEqual([round(v) for v in vd], [6, 6, 7, 10, 13, 135])
        self.assertAlmostEqual(sum(vd[:-1]), 42, places=6)
        self.assertEqual([round(v) for v in sorted(v for v in beer if v > 0)], [4, 4])

    def test_the_86_and_the_three_japanese(self):
        top = max((r for r in self.r18 if r["type"] == "other"), key=lambda r: r["v"])
        self.assertEqual((top["sample"], top["function"], top["origin"], top["v"]),
                         ("C2018ETCA00126", "Import", "KOREA, REPUBLIC OF", 0.086))
        jp = sorted(round(rescaled(r["v"])) for r in self.r18
                    if r["type"] == "other" and r["origin"] == "JAPAN" and r["v"] > 0)
        self.assertEqual(jp, [7, 17, 33])


class TestEc19(Base):
    def test_v5_v6_v7(self):
        veg, soy = self.vals(self.r19, "veg"), self.vals(self.r19, "soy")
        self.assertTrue(all(fits(stats(veg), VEG).values()))
        self.assertTrue(all(fits(stats(soy), SOY).values()))
        self.assertTrue(all(fits(stats(veg + soy), TOTAL19).values()))
        self.assertEqual(sorted(v for v in veg if v > 0), [4.0, 6.0, 9.0])
        self.assertEqual(sorted(v for v in soy if v > 0), [7.0, 9.0, 94.0, 157.0, 164.0, 217.0])
        self.assertEqual(stats(soy)[4], 108.0)
        self.assertAlmostEqual(stats(veg + soy)[4], 667 / 9, places=9)
        self.assertTrue(74.05 <= stats(veg + soy)[4] <= 74.15)
        self.assertEqual(sum(1 for v in soy if v == 0), 94)
        vd = sorted((r for r in self.r19 if r["type"] == "veg" and r["v"] > 0),
                    key=lambda r: r["v"])
        self.assertEqual([r["product"] for r in vd],
                         ["Sauerkraut", "Sauerkraut", "Pickled Vegetable - Misc"])
        self.assertEqual([r["product"] for r in vd],
                         self.preds["V6"]["observed"]["veg_detect_labels"])
        sd = [r for r in self.r19 if r["type"] == "soy" and r["v"] > 0]
        self.assertEqual(sorted(r["origin"] for r in sd),
                         ["CANADA"] + ["TAIWAN, PROVINCE OF CHINA"] * 5)
        self.assertEqual({r["product"] for r in sd}, {"Soy Products"})


class TestLabelsAndDates(Base):
    def test_odd_labels(self):
        beef = [r for r in self.r18 if r["product"] == "Beef"]
        self.assertEqual([(r["sample"], r["type"], r["origin"], r["v"]) for r in beef],
                         [("C2018ETCA00251", "beer", "ICELAND", 0.0)])
        fish = [r for r in self.r19 if r["product"].startswith("Fish/Seafood")]
        self.assertEqual([(r["sample"], r["type"], r["origin"], r["v"]) for r in fish],
                         [("C2019ETCA00272", "veg", "KOREA, REPUBLIC OF", 0.0)])

    def test_date_ranges(self):
        d18 = sorted(datetime.datetime.strptime(r["date"], "%d-%b-%y").date() for r in self.r18)
        d19 = sorted(datetime.date.fromisoformat(r["date"][:10]) for r in self.r19)
        self.assertEqual((d18[0], d18[-1]), (datetime.date(2018, 4, 3), datetime.date(2019, 3, 6)))
        self.assertEqual((d19[0], d19[-1]), (datetime.date(2019, 4, 9), datetime.date(2020, 3, 23)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
