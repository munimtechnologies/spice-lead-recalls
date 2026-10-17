"""Checks the georgia_trend 0.1.0 result against the committed NYC snapshot (no network).

Recomputes data/georgia_trend.csv and data/georgia_trend_by_year.csv with the committed
code, checks that the periods add up to data/purchase_place.csv, and pins every figure
quoted in docs/georgia-trend-0.1.0-result.md. Apache-2.0. MV2 of Munim, Inc.
"""
import csv
import os
import unittest
from fractions import Fraction

import georgia_trend as gt
import purchase_place as pp
import sampling_frame as sf

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
NYC = os.path.join(DATA, "nyc_spice_lead_snapshot_2026-10-17.csv")


def read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


class TestGeorgiaTrend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = gt.dated_rows(read(NYC))
        cls.tab = gt.table(cls.rows)

    def get(self, series, period):
        r = gt.find(self.tab, series, period)
        return r["n_result"], r["n_ge2"], r["n_ge50"]

    def test_rows_are_purchase_place_rows(self):
        self.assertEqual(len(self.rows), 3575)
        self.assertEqual(len(self.rows), len(pp.tagged_rows(read(NYC))))

    def test_table_matches_committed(self):
        committed = read(os.path.join(DATA, "georgia_trend.csv"))
        self.assertEqual(len(committed), len(self.tab))
        for want, got in zip(committed, self.tab):
            self.assertEqual((want["series"], want["period"]), (got["series"], got["period"]))
            for key in gt.COLUMNS:
                self.assertEqual(int(want[key]), got[key], (want["series"], want["period"], key))

    def test_by_year_matches_committed(self):
        committed = read(os.path.join(DATA, "georgia_trend_by_year.csv"))
        got = gt.by_year(self.rows)
        self.assertEqual(len(committed), len(got))
        for want, row in zip(committed, got):
            self.assertEqual((want["country"], int(want["year"])), (row["country"], row["year"]))
            self.assertEqual((int(want["n_result"]), int(want["n_ge50"])),
                             (row["n_result"], row["n_ge50"]))

    def test_periods_add_up_to_purchase_place(self):
        committed = read(os.path.join(DATA, "purchase_place.csv"))
        for series, group in (("abroad", "abroad"), ("US", "US")):
            want = next(r for r in committed if (r["period"], r["frame"], r["group"]) == ("2016-2025", "C", group))
            for key in gt.COLUMNS:
                total = sum(gt.find(self.tab, series, p)[key] for p in ("early", "late"))
                self.assertEqual(total, int(want[key]), (series, key))

    def test_series_partition_abroad(self):
        for period in ("early", "late"):
            parts = [self.get(s, period) for s in ("GEORGIA", "BANGLADESH", "other_abroad")]
            self.assertEqual(tuple(map(sum, zip(*parts))), self.get("abroad", period))

    def test_counts(self):
        self.assertEqual(self.get("GEORGIA", "early"), (141, 85, 49))
        self.assertEqual(self.get("GEORGIA", "late"), (16, 1, 0))
        self.assertEqual(self.get("BANGLADESH", "early"), (239, 48, 18))
        self.assertEqual(self.get("BANGLADESH", "late"), (159, 15, 3))
        self.assertEqual(self.get("abroad", "early"), (697, 179, 89))
        self.assertEqual(self.get("abroad", "late"), (421, 41, 9))
        self.assertEqual(self.get("US", "early"), (406, 25, 9))
        self.assertEqual(self.get("US", "late"), (365, 20, 0))

    def test_grades(self):
        g = gt.grade(self.tab)
        self.assertTrue(g["gradable"])
        met = [g[k]["met"] for k in sorted(k for k in g if k.startswith("P"))]
        self.assertEqual(met, [True, True, True, False, True])
        self.assertEqual(g["n_met"], 4)
        p1 = g["P1_georgia_late_share_ge50_below_early"]
        self.assertAlmostEqual(p1["early"], 49 / 141)
        self.assertEqual(p1["late"], 0)
        self.assertTrue(0.001 < g["P3_georgia_fisher_ge50_below_0.05"]["p"] < 0.01)
        p4 = g["P4_control_bangladesh_fisher_ge50_at_least_0.05"]
        self.assertAlmostEqual(p4["early"], 18 / 239)
        self.assertAlmostEqual(p4["late"], 3 / 159)
        self.assertTrue(0.008 < p4["p"] < 0.05)
        p5 = g["P5_georgia_fraction_of_abroad_smaller_late"]
        self.assertAlmostEqual(p5["early"], 141 / 697)
        self.assertAlmostEqual(p5["late"], 16 / 421)

    def test_collection_dates(self):
        d = gt.dates(self.rows, "GEORGIA")
        self.assertEqual(d["early"], {"n_dates": 44, "n_dates_ge50": 30})
        self.assertEqual(d["late"], {"n_dates": 4, "n_dates_ge50": 0})
        self.assertEqual(sf.fisher_two_sided(30, 14, 0, 4), Fraction(3060, 194580))
        self.assertAlmostEqual(gt.dates_fisher(d), 3060 / 194580)

    def test_not_only_georgia(self):
        f = lambda s, t: pp.fisher(gt.find(self.tab, s, "early"), gt.find(self.tab, s, "late"), t)
        self.assertLess(f("GEORGIA", 2), 0.001)
        self.assertLess(f("abroad", 50), 1e-6)
        self.assertTrue(0.002 < f("other_abroad", 50) < 0.1)
        self.assertTrue(0.002 < f("US", 50) < 0.008)
        self.assertGreater(f("US", 2), 0.3)


if __name__ == "__main__":
    unittest.main()
