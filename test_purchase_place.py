"""Checks the purchase_place 0.1.0 result against the committed NYC snapshot (no network).

Recomputes data/purchase_place.csv with the committed code, checks that the purchase
groups split the frame_period ladder exactly, and pins every figure quoted in
docs/purchase-place-0.1.0-result.md. Apache-2.0. MV2 of Munim, Inc.
"""
import csv
import os
import unittest

import frame_period as fp
import purchase_place as pp

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
NYC = os.path.join(DATA, "nyc_spice_lead_snapshot_2026-10-17.csv")
KEYS = ("n_result", "n_ge2", "n_ge10", "n_ge50", "n_ge500")


def read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


class TestPurchasePlace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = pp.tagged_rows(read(NYC))
        cls.tab = pp.table(cls.rows)

    def get(self, period, frame, group):
        return pp.find(self.tab, period, frame, group)

    def test_groups(self):
        self.assertEqual(pp.purchase_group(" united states "), "US")
        self.assertEqual(pp.purchase_group(""), "unknown")
        self.assertEqual(pp.purchase_group("UNITED STATES MINOR OUTLYING ISLANDS"), "unknown")
        self.assertEqual(pp.purchase_group("GEORGIA"), "abroad")
        self.assertEqual(len(self.rows), 3575)

    def test_table_matches_committed(self):
        committed = read(os.path.join(DATA, "purchase_place.csv"))
        self.assertEqual(len(committed), len(self.tab))
        for want, got in zip(committed, self.tab):
            self.assertEqual((want["period"], want["frame"], want["group"]),
                             (got["period"], got["frame"], got["group"]))
            for key in KEYS:
                self.assertEqual(int(want[key]), got[key], (want["period"], want["frame"], want["group"], key))

    def test_groups_add_up_to_ladder(self):
        lad = fp.ladder(self.rows)
        for row in lad:
            parts = [self.get(row["period"], row["frame"], g) for g in pp.GROUPS]
            for key in KEYS:
                self.assertEqual(sum(p[key] for p in parts), row[key], (row["period"], row["frame"], key))

    def test_store_surveys_all_bought_in_us(self):
        for period, _, _ in fp.PERIODS:
            self.assertEqual(self.get(period, "S", "unknown")["n_result"], 0)
            self.assertEqual(self.get(period, "S", "abroad")["n_result"], 0)
        self.assertEqual(self.get("2011-2015", "S", "US")["n_result"]
                         + self.get("2016-2025", "S", "US")["n_result"], 477)

    def test_grades(self):
        g = pp.grade(self.tab)
        met = [g[k]["met"] for k in sorted(k for k in g if k.startswith("P"))]
        self.assertEqual(met, [True, False, True, True, True])
        self.assertEqual(g["n_met"], 4)
        self.assertAlmostEqual(g["P1_C_US_share_ge50_at_most_0.015"]["share"], 9 / 771)
        self.assertAlmostEqual(g["P2_C_abroad_share_ge50_at_least_0.10"]["share"], 98 / 1118)
        self.assertAlmostEqual(g["P3_C_US_share_ge2_in_0.04_to_0.16"]["share"], 45 / 771)
        p4 = g["P4_C_abroad_at_least_70pct_of_C_ge50"]
        self.assertEqual((p4["abroad_ge50"], p4["C_ge50"]), (98, 117))
        self.assertLess(g["P5_fisher_abroad_vs_US_ge50_below_0.001"]["p"], 1e-6)

    def test_bought_in_us_case_vs_store(self):
        us, s = self.get("2016-2025", "C", "US"), self.get("2016-2025", "S", "US")
        self.assertTrue(0.03 < pp.fisher(us, s, 2) < 0.3)
        self.assertTrue(0.1 < pp.fisher(us, s, 50) < 0.4)
        self.assertLess(pp.share(us, 2), pp.share(s, 2))
        self.assertLess(pp.share(us, 10), pp.share(s, 10))
        ab = self.get("2016-2025", "C", "abroad")
        self.assertLess(pp.fisher(ab, s, 2), 1e-5)

    def test_countries(self):
        def c(country):
            r = pp.by_country(self.rows, "2016-2025", "C", country)
            return r["n_result"], r["n_ge2"], r["n_ge50"]
        self.assertEqual(c("GEORGIA"), (157, 86, 49))
        self.assertEqual(c("BANGLADESH")[::2], (398, 21))
        self.assertEqual(c("INDIA")[::2], (181, 7))
        self.assertEqual(c("PAKISTAN")[::2], (88, 9))


if __name__ == "__main__":
    unittest.main()
