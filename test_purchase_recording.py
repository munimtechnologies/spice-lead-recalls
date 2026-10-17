"""Checks the purchase_recording 0.1.0 note against the committed NYC snapshot (no network).

Recomputes data/purchase_recording_by_year.csv with the committed code, checks that it
adds up to the v0.4.1 and v0.4.2 tables, and pins every figure quoted in
docs/purchase-recording-0.1.0.md. Apache-2.0. MV2 of Munim, Inc.
"""
import csv
import os
import unittest

import georgia_trend as gt
import purchase_recording as pr

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
NYC = os.path.join(DATA, "nyc_spice_lead_snapshot_2026-10-17.csv")


def read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


class TestPurchaseRecording(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = gt.dated_rows(read(NYC))
        cls.table = pr.by_year(cls.rows)
        cls.b = pr.bounds(cls.rows, gt.table(cls.rows))

    def test_by_year_matches_committed(self):
        committed = read(os.path.join(DATA, "purchase_recording_by_year.csv"))
        self.assertEqual(len(committed), len(self.table))
        for want, got in zip(committed, self.table):
            for key in want:
                self.assertEqual(int(want[key]), got[key], (want["year"], key))

    def test_adds_up_to_purchase_place(self):
        committed = read(os.path.join(DATA, "purchase_place.csv"))
        unk = next(r for r in committed if (r["period"], r["frame"], r["group"]) == ("2016-2025", "C", "unknown"))
        self.assertEqual(sum(r["n_unknown"] for r in self.table), int(unk["n_result"]))
        self.assertEqual(sum(r["n_ge50_unknown"] for r in self.table), int(unk["n_ge50"]))
        c_ge50 = sum(int(r["n_ge50"]) for r in committed if (r["period"], r["frame"]) == ("2016-2025", "C"))
        self.assertEqual(sum(r["n_ge50"] for r in self.table), c_ge50)

    def test_period_totals(self):
        p = self.b["periods"]
        self.assertEqual(p["early"], {"n_result": 1159, "n_unknown": 56, "n_ge50": 99, "n_ge50_unknown": 1})
        self.assertEqual(p["late"], {"n_result": 1286, "n_unknown": 500, "n_ge50": 18, "n_ge50_unknown": 9})
        # recorded + unknown = all, using the v0.4.2 abroad and US series
        tab = gt.table(self.rows)
        for period in ("early", "late"):
            known = sum(gt.find(tab, s, period)["n_result"] for s in ("abroad", "US"))
            self.assertEqual(known + p[period]["n_unknown"], p[period]["n_result"])

    def test_unknown_share_by_year(self):
        share = {r["year"]: r["n_unknown"] / r["n_result"] for r in self.table}
        self.assertTrue(all(share[y] < 0.07 for y in range(2016, 2021)))
        self.assertGreater(share[2023], 0.59)
        self.assertGreater(share[2024], 0.45)

    def test_bounds(self):
        b = self.b
        self.assertEqual(b["all_cases_ge50"]["early"], [99, 1159])
        self.assertEqual(b["all_cases_ge50"]["late"], [18, 1286])
        self.assertLess(b["all_cases_ge50"]["p"], 1e-10)
        self.assertEqual(b["unknown_share_of_ge50"]["early"], [1, 99])
        self.assertEqual(b["unknown_share_of_ge50"]["late"], [9, 18])
        self.assertTrue(1e-8 < b["unknown_share_of_ge50"]["p"] < 2e-7)
        self.assertEqual(b["abroad_worst_case_ge50"]["early"], [89, 697])
        self.assertEqual(b["abroad_worst_case_ge50"]["late"], [18, 921])
        self.assertLess(b["abroad_worst_case_ge50"]["p"], 1e-10)
        g = b["georgia_worst_case_share_ge50"]
        self.assertEqual(g["early"], [49, 141])
        self.assertEqual(g["late"], [9, 25])
        self.assertTrue(g["late_share_exceeds_early"])
        self.assertEqual(b["georgia_ge50_count"], {"early": 49, "late_min": 0, "late_max": 9})

    def test_unknown_gross_dates(self):
        self.assertEqual(pr.unknown_gross_dates(self.rows), [
            "2021-04-06", "2023-05-03", "2023-09-05", "2023-10-20", "2024-05-08", "2024-06-24"])


if __name__ == "__main__":
    unittest.main()
