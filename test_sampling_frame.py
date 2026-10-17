"""Offline tests for sampling_frame 0.1.0 (no network). Apache-2.0. MV2 of Munim, Inc."""
import unittest
from fractions import Fraction

import sampling_frame as sf


def nyc(frame, conc, units="ppm", analysis="Laboratory", metal="Lead", ptype="Food-Spice",
        date="2019-05-01T00:00:00.000"):
    return {"product_type": ptype, "metal": metal, "units": units, "analysis_type": analysis,
            "concentration": conc, "investigation_type": frame, "collection_date": date}


def kc(source, value, qualifier=None, ptype="Seasoning", method="Laboratory", year="2022"):
    rec = {"product_type": ptype, "data_source": source, "test_method": method,
           "year_tested": year}
    if value is not None:
        rec["lead_concentration_ppm"] = value
    if qualifier is not None:
        rec["qualifier"] = qualifier
    return rec


class TestFisher(unittest.TestCase):
    def test_lady_tasting_tea(self):
        # Fisher's own example: [[3, 1], [1, 3]] -> two-sided p = 34/70.
        self.assertEqual(sf.fisher_two_sided(3, 1, 1, 3), Fraction(34, 70))

    def test_extreme_table_is_a_single_term(self):
        # [[2, 9], [0, 184]]: all hits in row 1 -> p = C(11,2)/C(195,2) = 55/18915.
        self.assertEqual(sf.fisher_two_sided(2, 9, 0, 184), Fraction(55, 18915))
        # [[5, 52], [0, 197]] -> C(57,5)/C(254,5).
        self.assertEqual(sf.fisher_two_sided(5, 52, 0, 197), Fraction(4187106, 8468125050))

    def test_symmetric(self):
        self.assertEqual(sf.fisher_two_sided(7, 20, 3, 40), sf.fisher_two_sided(3, 40, 7, 20))


class TestWilson(unittest.TestCase):
    def test_zero_of_n(self):
        lo, hi = sf.wilson(0, 197)
        self.assertAlmostEqual(lo, 0.0, places=12)
        self.assertAlmostEqual(hi, 0.0191, places=4)

    def test_half(self):
        lo, hi = sf.wilson(50, 100)
        self.assertAlmostEqual(lo, 0.4038, places=4)
        self.assertAlmostEqual(hi, 0.5962, places=4)


class TestParsers(unittest.TestCase):
    def test_nyc_filters_and_statuses(self):
        recs = [nyc("C", "-1"), nyc("C", "0"), nyc("C", "2.0"), nyc("S", "1.99"),
                nyc("S", None), nyc(" a ", "60"),
                nyc("C", "5", units="mg/l"), nyc("C", "5", analysis="XRF"),
                nyc("C", "5", metal="Chromium"), nyc("C", "5", ptype="Food Other")]
        rows = sf.nyc_rows(recs)
        self.assertEqual(len(rows), 6)
        self.assertEqual([r["status"] for r in rows], ["nd", "nd", "value", "value", "missing", "value"])
        self.assertEqual(rows[5]["frame"], "A")
        self.assertEqual(rows[0]["year"], "2019")

    def test_kc_qualifier_overrides_value(self):
        recs = [kc("Case Investigation", "2800"), kc("Case Investigation", None),
                kc("Case Investigation", None, qualifier="<LOD"),
                kc("Community product testing event", "5", qualifier="<"),
                kc("Community product testing event", "1.3", ptype="Food"),
                kc("Community product testing event", "9", method="XRF"),
                kc("Community product testing event", "9", ptype="Jewelry")]
        rows = sf.kc_rows(recs)
        self.assertEqual(len(rows), 5)
        self.assertEqual([r["status"] for r in rows], ["value", "missing", "nd", "nd", "value"])
        self.assertEqual([r["frame"] for r in rows], ["case", "case", "case", "community", "community"])
        self.assertEqual(rows[4]["set"], "Food")


class TestSummaryAndGrades(unittest.TestCase):
    def rows(self, frame, n_hi, n_lo, n_nd, n_missing=0, hi=60.0):
        out = [{"frame": frame, "status": "value", "value": hi, "year": "2020", "set": "Food-Spice"}] * n_hi
        out += [{"frame": frame, "status": "value", "value": 0.5, "year": "2021", "set": "Food-Spice"}] * n_lo
        out += [{"frame": frame, "status": "nd", "value": None, "year": "2022", "set": "Food-Spice"}] * n_nd
        out += [{"frame": frame, "status": "missing", "value": None, "year": "", "set": "Food-Spice"}] * n_missing
        return out

    def test_missing_excluded_from_denominator(self):
        s = sf.summarize(self.rows("C", 3, 4, 3, n_missing=5), "NYC", "Food-Spice", "C")
        self.assertEqual((s["n_rows"], s["n_result"], s["n_ge2"], s["n_ge50"]), (15, 10, 3, 3))
        self.assertEqual(s["share_ge2"], 0.3)
        self.assertEqual((s["year_min"], s["year_max"]), ("2020", "2022"))

    def test_threshold_is_inclusive(self):
        s = sf.summarize(self.rows("C", 1, 0, 0, hi=2.0), "NYC", "Food-Spice", "C")
        self.assertEqual(s["n_ge2"], 1)

    def test_grades_all_met(self):
        rows = self.rows("C", 30, 50, 20) + self.rows("S", 2, 48, 50) + self.rows("A", 5, 5, 0)
        stats = sf.table(rows, "NYC", "Food-Spice")
        tests = [sf.compare(stats, "NYC", "Food-Spice", "C", "S")]
        g = sf.grade(stats, tests)
        self.assertEqual(g["n_met"], 5)
        self.assertEqual(g["P4_survey_at_most_10pct_of_ge50"]["all_ge50"], 37)

    def test_grades_all_failed(self):
        rows = self.rows("C", 6, 94, 0) + self.rows("S", 20, 80, 0)
        stats = sf.table(rows, "NYC", "Food-Spice")
        tests = [sf.compare(stats, "NYC", "Food-Spice", "C", "S")]
        g = sf.grade(stats, tests)
        self.assertEqual(g["n_met"], 0)


if __name__ == "__main__":
    unittest.main()
