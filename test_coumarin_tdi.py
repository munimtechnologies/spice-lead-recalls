#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for coumarin_tdi (no network, no CFIA download). Validates the exposure
arithmetic, sample selection, descriptive stats and the pre-registered grading on a small
hand-computed fixture."""
import unittest

import coumarin_tdi as ct


def build_samples(ppms):
    return [{"cinnamon": True, "ppm": float(p), "product": "ground cinnamon",
             "origin": "", "form": "ground", "claim": "none", "class": ""} for p in ppms]


FIXTURE = [500, 700, 1000, 2000, 3000, 4000, 5000, 7816]


class TestArithmetic(unittest.TestCase):
    def test_serving_to_tdi_adult(self):
        self.assertAlmostEqual(ct.serving_to_tdi_g(1000, 60), 6.0, places=6)
        self.assertAlmostEqual(ct.serving_to_tdi_g(3339, 60), 6000 / 3339, places=6)
        self.assertAlmostEqual(ct.serving_to_tdi_g(7816, 60), 6000 / 7816, places=6)

    def test_serving_to_tdi_child(self):
        self.assertAlmostEqual(ct.serving_to_tdi_g(1000, 15), 1.5, places=6)
        self.assertAlmostEqual(ct.serving_to_tdi_g(3339, 15), 1500 / 3339, places=6)

    def test_serving_handles_missing(self):
        self.assertIsNone(ct.serving_to_tdi_g(None, 60))
        self.assertIsNone(ct.serving_to_tdi_g(0, 60))
        self.assertIsNone(ct.serving_to_tdi_g(-5, 60))

    def test_dose_mg(self):
        self.assertAlmostEqual(ct.dose_mg(2.6, 1000), 2.6, places=6)
        self.assertAlmostEqual(ct.dose_mg(10, 500), 5.0, places=6)

    def test_child_teaspoon_threshold(self):
        self.assertAlmostEqual(ct.child_teaspoon_ppm_threshold(), 1.5 / 0.0026, places=4)


class TestSelection(unittest.TestCase):
    def test_select_cinnamon(self):
        rows = [
            {"cinnamon": True, "ppm": 1000.0},
            {"cinnamon": True, "ppm": 0.0},        # non-positive -> excluded
            {"cinnamon": True, "ppm": None},       # missing -> excluded
            {"cinnamon": False, "ppm": 2000.0},    # not cinnamon -> excluded
            {"cinnamon": True, "ppm": True},        # bool -> excluded
        ]
        sel = ct.select_cinnamon(rows)
        self.assertEqual(len(sel), 1)
        self.assertEqual(sel[0]["ppm"], 1000.0)


class TestSummariseGrade(unittest.TestCase):
    def setUp(self):
        self.samples = build_samples(FIXTURE)
        self.s = ct.summarise(self.samples)

    def test_summary_values(self):
        self.assertEqual(self.s["n_samples"], 8)
        self.assertAlmostEqual(self.s["ppm_median"], 2500.0, places=6)
        self.assertAlmostEqual(self.s["ppm_max"], 7816.0, places=6)
        self.assertAlmostEqual(self.s["adult_serving_g_median"], 2.5, places=6)
        self.assertAlmostEqual(self.s["adult_serving_g_min"], 6000 / 7816, places=6)
        self.assertAlmostEqual(self.s["frac_adult_under_2g"], 0.375, places=6)
        self.assertAlmostEqual(self.s["frac_child_teaspoon_over_tdi"], 0.875, places=6)

    def test_grade(self):
        preds = {p["id"]: p for p in ct.grade(self.samples)}
        # n=8 < 120 so the parse gate is not met on this tiny fixture:
        self.assertFalse(preds["G0"]["met"])
        self.assertTrue(preds["P1"]["met"])   # median adult serving 2.5 g < 3.0
        self.assertTrue(preds["P2"]["met"])   # 37.5% reach adult TDI under 2 g
        self.assertTrue(preds["P3"]["met"])   # 87.5% of child teaspoons over TDI

    def test_grade_g0_passes_on_large_set(self):
        many = build_samples([2000] * 130 + [7816])
        preds = {p["id"]: p for p in ct.grade(many)}
        self.assertTrue(preds["G0"]["met"])   # n=131 >=120 and max 7816 in [7000,8200]


if __name__ == "__main__":
    unittest.main()
