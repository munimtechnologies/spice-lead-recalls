"""Checks the sampling_frame 0.1.0 result against the committed snapshots (no network).

Recomputes data/frame_yield.csv and data/frame_period_ladder.csv from the two
2026-10-17 snapshots with the committed code, and pins every figure quoted in
docs/sampling-frame-0.1.0-result.md. Apache-2.0. MV2 of Munim, Inc.
"""
import csv
import os
import unittest
from fractions import Fraction

import frame_period as fp
import sampling_frame as sf

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
NYC = os.path.join(DATA, "nyc_spice_lead_snapshot_2026-10-17.csv")
KC = os.path.join(DATA, "kc_seasoning_food_snapshot_2026-10-17.csv")


def read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def build():
    nyc = sf.nyc_rows(read(NYC))
    kc = sf.kc_rows(read(KC))
    stats = sf.table(nyc, "NYC", "Food-Spice")
    stats += sf.table([r for r in kc if r["set"] == "Seasoning"], "King County", "Seasoning")
    stats += sf.table(kc, "King County", "Seasoning+Food")
    return nyc, kc, stats


class TestFrameYield(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nyc, cls.kc, cls.stats = build()

    def test_snapshot_sizes(self):
        self.assertEqual(len(read(NYC)), 3580)
        self.assertEqual(len(self.nyc), 3575)
        self.assertEqual(len(read(KC)), 260)
        self.assertEqual(len(self.kc), 260)

    def test_frame_yield_matches_committed(self):
        committed = read(os.path.join(DATA, "frame_yield.csv"))
        self.assertEqual(len(committed), len(self.stats))
        for want, got in zip(committed, self.stats):
            for key, text in want.items():
                value = got[key]
                if text == "":
                    self.assertIsNone(value, key)
                    continue
                try:
                    self.assertAlmostEqual(float(text), float(value), places=6, msg=key)
                except ValueError:
                    self.assertEqual(text, value, key)

    def test_grades(self):
        cs = sf.compare(self.stats, "NYC", "Food-Spice", "C", "S")
        self.assertEqual(cs["table"], [[403, 2387], [41, 436]])
        g = sf.grade(self.stats, [cs])
        self.assertEqual(g["n_met"], 3)
        met = [g[k]["met"] for k in sorted(k for k in g if k.startswith("P"))]
        self.assertEqual(met, [False, True, False, True, True])
        self.assertAlmostEqual(cs["fisher_two_sided_p"], 0.0003803918741808045, places=12)
        self.assertEqual((g["P4_survey_at_most_10pct_of_ge50"]["S_ge50"],
                          g["P4_survey_at_most_10pct_of_ge50"]["all_ge50"]), (2, 219))

    def test_king_county_observations_reproduced(self):
        def get(pset, frame):
            return sf.find(self.stats, "King County", pset, frame)
        self.assertEqual((get("Seasoning", "case")["n_ge2"], get("Seasoning", "case")["n_result"]), (2, 11))
        self.assertEqual((get("Seasoning", "community")["n_ge2"], get("Seasoning", "community")["n_result"]), (0, 184))
        self.assertEqual((get("Seasoning+Food", "case")["n_ge2"], get("Seasoning+Food", "case")["n_result"]), (5, 57))
        comm = get("Seasoning+Food", "community")
        self.assertEqual((comm["n_ge2"], comm["n_result"], comm["max_value"]), (0, 197, 1.3))
        self.assertEqual(sf.fisher_two_sided(2, 9, 0, 184), Fraction(55, 18915))

    def test_strict_cut_changes_no_grade(self):
        # ">" instead of ">=": five results read exactly 2 ppm (3 C, 1 S, 1 A).
        def above(frame):
            return sum(1 for r in self.nyc if r["frame"] == frame and r["status"] == "value"
                       and r["value"] > sf.THRESHOLD)
        c, s, a = above("C"), above("S"), above("A")
        self.assertEqual((c, s, a), (400, 40, 92))
        sc, ss = c / 2790, s / 477
        self.assertFalse(sc >= 2 * ss)          # P1 still fails
        self.assertTrue(ss <= 0.15)             # P2 still met
        self.assertFalse(0.20 <= sc <= 0.50)    # P3 still fails
        self.assertLess(float(sf.fisher_two_sided(c, 2790 - c, s, 477 - s)), 0.001)  # P5 still met


class TestFramePeriod(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nyc, _, cls.stats = build()
        cls.lad = fp.ladder(cls.nyc)

    def test_ladder_matches_committed(self):
        committed = read(os.path.join(DATA, "frame_period_ladder.csv"))
        self.assertEqual(len(committed), len(self.lad))
        for want, got in zip(committed, self.lad):
            self.assertEqual((want["period"], want["frame"]), (got["period"], got["frame"]))
            for key in ("n_result", "n_ge2", "n_ge10", "n_ge50", "n_ge500"):
                self.assertEqual(int(want[key]), got[key], (want["period"], want["frame"], key))

    def test_periods_add_up_to_frame_totals(self):
        for frame in fp.FRAMES:
            total = sf.find(self.stats, "NYC", "Food-Spice", frame)
            for key in ("n_result", "n_ge2", "n_ge10", "n_ge50"):
                self.assertEqual(sum(r[key] for r in self.lad if r["frame"] == frame), total[key])

    def test_within_2016_2025(self):
        p2 = fp.fisher_c_vs_s(self.lad, "2016-2025", 2)
        p50 = fp.fisher_c_vs_s(self.lad, "2016-2025", 50)
        self.assertTrue(0.005 < p2 < 0.05, p2)
        self.assertLess(p50, 0.001)


if __name__ == "__main__":
    unittest.main()
