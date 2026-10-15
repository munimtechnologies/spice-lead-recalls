"""Offline tests for spot_sampling.py. Apache-2.0."""
import json
import math
import os
import random
import tempfile
import unittest

import lod_curve as lc
import spot_sampling as ss


class Poisson(unittest.TestCase):
    def test_known_values(self):
        self.assertAlmostEqual(ss.poisson_sf(1, 0.5), 1 - math.exp(-0.5), places=12)
        lam = 0.0624
        self.assertAlmostEqual(ss.poisson_sf(2, lam), 1 - math.exp(-lam) * (1 + lam), places=12)
        self.assertAlmostEqual(ss.poisson_sf(3, 2.0), 1 - 5 * math.exp(-2.0), places=12)

    def test_edges(self):
        self.assertEqual(ss.poisson_sf(0, 3.0), 1.0)
        self.assertEqual(ss.poisson_sf(2, 0.0), 0.0)
        self.assertGreater(ss.poisson_sf(1, 1e-12), 0.0)

    def test_both_branches_agree(self):
        # lam just below and just above k use different sums.
        self.assertAlmostEqual(ss.poisson_sf(5, 4.9999999), ss.poisson_sf(5, 5.0000001), places=6)
        self.assertAlmostEqual(ss.poisson_sf(5, 5.0), 0.5595067149, places=8)

    def test_large_lambda_no_underflow(self):
        self.assertGreater(ss.poisson_sf(1000, 1100.0), 0.99)
        self.assertLess(ss.poisson_sf(1000, 900.0), 0.01)


class Model(unittest.TestCase):
    def test_k_star(self):
        self.assertEqual(ss.k_star(0.3), 1)
        self.assertEqual(ss.k_star(1.0), 1)
        self.assertEqual(ss.k_star(1.0001), 2)
        self.assertEqual(ss.k_star(3.0), 3)

    def test_matched_probe_closed_form(self):
        # At r = 1 a spot is positive with 1 - exp(-x): ln(10)/x spots for 90%.
        self.assertEqual(ss.spots_needed(0.05, 1.0), 47)
        for x in (0.01, 0.0312, 0.1, 0.5):
            self.assertEqual(ss.spots_needed(x, 1.0), math.ceil(math.log(10) / x - 1e-9))

    def test_matched_is_best(self):
        x = ss.x_of_ppm(100)
        best = ss.spots_needed(x, 1.0)
        self.assertEqual(best, 74)
        for r in (0.1, 0.3, 2.0, 3.0, 10.0):
            self.assertGreater(ss.spots_needed(x, r), best)
        self.assertGreater(ss.spots_needed(x, 2.0), 10 * best)
        self.assertIsNone(ss.spots_needed(x, 1000.0))

    def test_bulk_is_a_step_at_the_limit(self):
        self.assertGreater(ss.spot_p(1.1, 1000.0), 0.99)
        self.assertLess(ss.spot_p(0.9, 1000.0), 0.01)

    def test_x_of_ppm(self):
        self.assertAlmostEqual(ss.x_of_ppm(lc.limit_ppm(0.5)), 1.0, places=3)
        self.assertAlmostEqual(ss.x_of_ppm(lc.limit_ppm(0.025)), 0.05, places=3)

    def test_catch_prob(self):
        p = ss.spot_p(0.2, 1.0)
        self.assertAlmostEqual(ss.catch_prob(0.2, 1.0, 10), 1 - (1 - p) ** 10, places=12)
        self.assertEqual(ss.catch_from_p(1.0, 3), 1.0)

    def test_grains(self):
        self.assertAlmostEqual(ss.grain_mass_g(10) * 1e9, 3.2044, places=3)
        m10, e10 = ss.matched_probe(10)
        m20, e20 = ss.matched_probe(20)
        self.assertAlmostEqual(m20 / m10, 8.0, places=9)
        self.assertAlmostEqual(e20 / e10, 2.0, places=9)
        self.assertAlmostEqual(e10, 108.6, places=0)


class MonteCarlo(unittest.TestCase):
    def test_simulation_matches_formula(self):
        rng = random.Random(7)
        cells = 20000
        for x, r in ss.MC_CASES:
            p = ss.spot_p(x, r)
            sim = ss.simulate(x, r, cells, rng)
            se = math.sqrt(p * (1 - p) / cells)
            self.assertLess(abs(sim - p), 5 * se + 0.002, (x, r, p, sim))


class EndToEnd(unittest.TestCase):
    def test_outputs(self):
        samples = [("NYC C", 5000.0), ("NYC C", 160.0), ("NYC S", 0.0), ("NYC A", 400.0),
                   ("King County Case Investigation", 2800.0)]
        s = ss.summarize(samples, {"nyc": {}, "king_county": {}}, mc_cells=2000)
        rows = [r for r in s["data"] if r["channel"] == "NYC all" and r["base_ppm"] == 100 and r["r"] == 1.0]
        self.assertEqual([r["spots"] for r in rows], ss.N_GRID)
        self.assertEqual(rows[0]["samples"], 3)
        shares = [r["share"] for r in rows]
        self.assertEqual(shares, sorted(shares))  # more spots never catch less
        self.assertEqual(rows[-1]["caught_at_90pct"], 3)  # 200 spots: 160 ppm needs 47
        with tempfile.TemporaryDirectory() as d:
            ss.write_markdown(s, os.path.join(d, "m.md"))
            ss.write_csv(s, os.path.join(d, "c.csv"))
            json.dumps(s)
            with open(os.path.join(d, "m.md"), encoding="utf-8") as fh:
                md = fh.read()
            self.assertIn("never", md)
            self.assertIn("| 160 | 0.025 |", md)


if __name__ == "__main__":
    unittest.main()
