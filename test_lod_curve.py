"""Offline tests for lod_curve.py. Apache-2.0."""
import json
import os
import tempfile
import unittest

import lod_curve as lc


def nyc(conc, inv="C", ptype="Food-Spice", metal="Lead", units="ppm"):
    return {"product_type": ptype, "metal": metal, "units": units, "concentration": str(conc),
            "investigation_type": inv}


def kc(name, ppm=None, ptype="Seasoning", qualifier=None, source="Case Investigation"):
    r = {"product_type": ptype, "product_name": name, "data_source": source}
    if ppm is not None:
        r["lead_concentration_ppm"] = str(ppm)
    if qualifier is not None:
        r["qualifier"] = qualifier
    return r


class Limits(unittest.TestCase):
    def test_half_percent_is_3206(self):
        self.assertEqual(lc.limit_ppm(0.5), 3206)

    def test_other_limits(self):
        self.assertEqual(lc.limit_ppm(0.1), 641)
        self.assertEqual(lc.limit_ppm(0.05), 321)
        self.assertEqual(lc.limit_ppm(0.025), 160)
        self.assertEqual(lc.limit_ppm(1.0), 6411)


class Samples(unittest.TestCase):
    def test_nyc_filters_and_not_detected(self):
        got = lc.nyc_samples([nyc(5000), nyc(-1, inv="S"), nyc("n/a"), nyc(9, ptype="Cosmetic"),
                              nyc(9, metal="Chromium"), nyc(9, units="mg/cm^2")])
        self.assertEqual(got, [("NYC C", 5000.0), ("NYC S", 0.0)])

    def test_kc_spice_selection(self):
        rows = [kc("Homemade turmeric powder", 2800), kc("Homemade Spice from India", 620, ptype="Food"),
                kc("Jaggery", 8.6, ptype="Food"), kc("Ground Cinnamon", qualifier="<LOD", ptype="Food"),
                kc("Mixed spice", 0.05, qualifier="<"), kc("Garam masala spice powder"),
                kc("Pot", 50, ptype="Cookware/pressure cooker"),
                kc("Original Ginger Honey Crystals", 0.05, ptype="Food", qualifier="<")]
        got = lc.kc_samples(rows)
        self.assertEqual(got, [("King County Case Investigation", 2800.0),
                               ("King County Case Investigation", 620.0),
                               ("King County Case Investigation", 0.0),
                               ("King County Case Investigation", 0.0)])


class Curve(unittest.TestCase):
    def test_counts_and_shares(self):
        vals = [10, 100, 200, 700, 4000, 7000]
        c = lc.curve(vals, 100)
        self.assertEqual(c["samples_at_or_above_base"], 5)
        by = {r["limit_pct_pbcro4"]: r for r in c["rows"]}
        self.assertEqual(by[0.5]["caught"], 2)
        self.assertEqual(by[0.1]["caught"], 3)
        self.assertEqual(by[0.025]["caught"], 4)
        self.assertEqual(by[0.01]["caught"], 5)  # 64 ppm limit is below the base: all caught
        self.assertEqual(by[0.5]["share"], 0.4)

    def test_empty(self):
        c = lc.curve([1, 2], 100)
        self.assertEqual(c["samples_at_or_above_base"], 0)
        self.assertIsNone(c["rows"][0]["share"])
        self.assertIsNone(lc.needed_for([1, 2], 100, 0.9))

    def test_needed_for_90pct(self):
        vals = list(range(100, 1100, 100))  # 10 samples, 100..1000
        n = lc.needed_for(vals, 100, 0.9)
        self.assertEqual(n["must_see_ppm_pb"], 200)  # catching 9 of 10 means seeing 200
        self.assertAlmostEqual(n["pct_pbcro4"], round(200 / (lc.PB_IN_PBCRO4 * 1e4), 4))


class EndToEnd(unittest.TestCase):
    def test_outputs(self):
        samples = lc.nyc_samples([nyc(5000), nyc(400), nyc(-1, inv="S"), nyc(610, inv="S")]) + \
            lc.kc_samples([kc("Turmeric", 2800)])
        s = lc.summarize(samples, {"nyc": {}, "king_county": {}})
        self.assertEqual(s["channels"]["NYC all"]["samples"], 4)
        self.assertEqual(s["channels"]["NYC S"]["max_ppm"], 610.0)
        self.assertEqual(s["channels"]["King County all"]["samples"], 1)
        with tempfile.TemporaryDirectory() as d:
            lc.write_markdown(s, os.path.join(d, "m.md"))
            lc.write_csv(s, os.path.join(d, "c.csv"))
            json.dumps(s)
            with open(os.path.join(d, "m.md"), encoding="utf-8") as fh:
                md = fh.read()
            self.assertIn("3,206 ppm", md)
            self.assertIn("NYC all", md)


if __name__ == "__main__":
    unittest.main()
