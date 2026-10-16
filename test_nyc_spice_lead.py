"""Offline tests for nyc_spice_lead.py. Apache-2.0."""
import json
import os
import tempfile
import unittest

import nyc_spice_lead as nyc


def rec(row_id, name, metal, conc, date="2017-07-18T00:00:00.000", inv="C", bought="GEORGIA",
        ptype="Food-Spice", units="ppm", made="UNKNOWN OR NOT STATED"):
    return {"row_id": str(row_id), "product_name": name, "metal": metal, "concentration": str(conc),
            "collection_date": date, "investigation_type": inv, "purchase_country": bought,
            "product_type": ptype, "units": units, "made_in_country": made, "analysis_type": "Laboratory",
            "manufacturer": "UNKNOWN OR NOT STATED"}


FIXTURE = [
    rec(2375, "Georgian saffron (zaprana)", "Chromium", 12000),
    rec(2376, "Georgian saffron (zaprana)", "Lead", 48000),
    rec(1000, "Berbere", "Chromium", -1, date="2014-01-08T00:00:00.000", bought="ERITREA"),
    rec(1001, "Berbere", "Lead", 220, date="2014-01-08T00:00:00.000", bought="ERITREA"),
    rec(3226, "Balqees Spices Yemeni Spices Mix", "Chromium", 130, date="2019-01-15T00:00:00.000", inv="S",
        bought="UNITED STATES"),
    rec(3227, "Balqees Spices Yemeni Spices Mix", "Lead", 570, date="2019-01-15T00:00:00.000", inv="S",
        bought="UNITED STATES"),
    rec(7638, "FIVE SPICE POWDER", "Chromium", 1, date="2024-01-17T00:00:00.000", bought="GUYANA"),
    rec(7639, "FIVE SPICE POWDER", "Lead", 40, date="2024-01-17T00:00:00.000", bought="GUYANA"),
    rec(7581, "Swad Cinnamon Powder", "Chromium", 0.44, date="2024-01-04T00:00:00.000", inv="S",
        bought="UNITED STATES"),
    rec(7582, "Swad Cinnamon Powder", "Lead", 2, date="2024-01-04T00:00:00.000", inv="S", bought="UNITED STATES"),
    rec(9001, "Turmeric", "Lead", -1, inv="S", bought="UNITED STATES", date="2020-01-01T00:00:00.000"),
    rec(9002, "Turmeric", "Lead", "n/a", inv="S", bought="UNITED STATES"),
    rec(9003, "Sindoor", "Lead", 570000, ptype="Religious powder", bought="UNITED STATES"),
    rec(9004, "Tajine", "Lead", 3, units="mg/cm^2", ptype="Food-Spice"),
    rec(9005, "Turmeric", "Mercury", 5),
]


class Constants(unittest.TestCase):
    def test_raman_limit(self):
        self.assertEqual(nyc.RAMAN_LIMIT_PPM, 3206)

    def test_molar_ratio(self):
        self.assertAlmostEqual(nyc.molar_ratio(48000, 12000), 1.0038, places=3)
        self.assertIsNone(nyc.molar_ratio(220, 0))
        self.assertIsNone(nyc.molar_ratio(0, 5))


class Verdict(unittest.TestCase):
    def test_verdicts(self):
        self.assertEqual(nyc.verdict(48000, 12000), "chromate-like")
        self.assertEqual(nyc.verdict(2200, 310), "chromate-like")  # Raz el hanout, molar 1.78
        self.assertEqual(nyc.verdict(220, 0), "no chromium detected")
        self.assertEqual(nyc.verdict(10, 5), "too little lead to judge")
        self.assertEqual(nyc.verdict(40, 1), "more lead than chromate")
        self.assertEqual(nyc.verdict(20, 30), "more chromium than lead")


class Georgian(unittest.TestCase):
    def test_names_and_country(self):
        self.assertTrue(nyc.georgian_style("TMT Khmeli Suneli"))
        self.assertTrue(nyc.georgian_style("Svanuri Marili"))
        self.assertTrue(nyc.georgian_style("Georgian spice (Yellow flour)"))
        self.assertTrue(nyc.georgian_style("Turmeric", "UNKNOWN OR NOT STATED", "GEORGIA"))
        self.assertFalse(nyc.georgian_style("Turmeric", "INDIA", "INDIA"))


class LeadRows(unittest.TestCase):
    def test_filters_and_not_detected(self):
        rows = nyc.lead_rows(FIXTURE)
        ids = [r["row_id"] for r in rows]
        self.assertEqual(ids, [1001, 2376, 3227, 7582, 7639, 9001])
        nd = rows[-1]
        self.assertFalse(nd["detected"])
        self.assertEqual(nd["lead_ppm"], 0.0)
        top = [r for r in rows if r["row_id"] == 2376][0]
        self.assertTrue(top["at_or_above_raman_limit"])
        self.assertTrue(top["georgian_style"])
        self.assertEqual(top["collection_date"], "2017-07-18")
        self.assertEqual(top["year"], "2017")


class Pairs(unittest.TestCase):
    def test_pairs(self):
        pairs = nyc.pair_pb_cr(FIXTURE)
        by = {p["lead_row_id"]: p for p in pairs}
        self.assertEqual(sorted(by), [1001, 2376, 3227, 7582, 7639])
        self.assertEqual(by[2376]["chromium_row_id"], 2375)
        self.assertEqual(by[2376]["verdict"], "chromate-like")
        self.assertEqual(by[2376]["molar_ratio_pb_cr"], 1.004)
        self.assertEqual(by[1001]["verdict"], "no chromium detected")
        self.assertEqual(by[1001]["molar_ratio_pb_cr"], "")
        self.assertEqual(by[3227]["verdict"], "chromate-like")
        self.assertEqual(by[7639]["verdict"], "more lead than chromate")
        self.assertEqual(by[7582]["verdict"], "too little lead to judge")
        self.assertEqual(pairs[0]["lead_row_id"], 2376)

    def test_needs_same_product_and_date(self):
        recs = [rec(1, "Cumin", "Chromium", 100), rec(2, "Cumin", "Lead", 500, date="2018-01-01T00:00:00.000"),
                rec(3, "Paprika", "Lead", 500)]
        self.assertEqual(nyc.pair_pb_cr(recs), [])

    def test_case_and_spaces_and_nearest_row(self):
        recs = [rec(10, "khmeli  suneli", "Lead", 900), rec(20, "Khmeli Suneli", "Chromium", 200),
                rec(21, "Khmeli Suneli", "Lead", 1000)]
        pairs = nyc.pair_pb_cr(recs)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["lead_row_id"], 21)


class Summary(unittest.TestCase):
    def test_channels(self):
        rows = nyc.lead_rows(FIXTURE)
        s = nyc.summarize(rows, nyc.pair_pb_cr(FIXTURE), {"sha256": "ab" * 32, "rows": len(FIXTURE)})
        self.assertEqual(s["spice_lead_results"], 6)
        self.assertEqual(s["at_or_above_raman_limit"], 1)
        self.assertEqual(s["at_or_above_raman_limit_georgian_style"], 1)
        self.assertEqual(s["by_investigation_type"]["S"]["samples"], 3)
        self.assertEqual(s["by_investigation_type"]["S"][">=3206"], 0)
        self.assertEqual(s["by_investigation_type"]["S"]["max_ppm"], 570)
        self.assertEqual(s["by_investigation_type"]["C"][">=3206"], 1)
        self.assertEqual(s["bought_in_us"], {"samples": 3, ">=3206": 0})
        self.assertEqual(s["pb_cr_pairs"], 5)
        self.assertEqual(s["pb_cr_pairs_judged"], 4)
        self.assertEqual(s["chromate_like"], 2)
        self.assertEqual(s["chromate_like_store_survey"], 1)
        self.assertEqual(s["first_collected"], "2014-01-08")


class GeorgiaTrend(unittest.TestCase):
    RECS = [
        rec(1, "Khmeli Suneli", "Lead", 22000, date="2017-04-07T00:00:00.000"),
        rec(2, "Svanuri Marili", "Lead", 4100, date="2017-04-07T00:00:00.000"),
        rec(3, "Yellow flower", "Lead", 50, date="2019-09-07T00:00:00.000"),
        rec(4, "Yellow Flower or Kviteli Kvavili", "Lead", 1.4, date="2021-03-28T00:00:00.000"),
        rec(5, "Red Ajika", "Lead", -1, date="2021-03-28T00:00:00.000"),
        rec(6, "Ground mixed spices", "Lead", 3.5, date="2022-12-02T00:00:00.000"),
        rec(7, "Khmeli Suneli", "Lead", 900, date="2018-01-01T00:00:00.000", inv="S"),
        rec(8, "Chili powder", "Lead", 12700, date="2024-03-01T00:00:00.000", bought="PAKISTAN", inv="A"),
        rec(9, "Turmeric", "Lead", 300, date="2016-01-01T00:00:00.000", bought="INDIA"),
    ]

    def test_hypergeom(self):
        self.assertAlmostEqual(nyc.hypergeom_p0(81, 52, 4), 29 * 28 * 27 * 26 / (81 * 80 * 79 * 78))
        self.assertEqual(nyc.hypergeom_p0(10, 0, 3), 1.0)
        self.assertEqual(nyc.hypergeom_p0(5, 5, 1), 0.0)
        self.assertIsNone(nyc.hypergeom_p0(3, 1, 4))

    def test_groups_and_periods(self):
        g = nyc.georgia_trend(nyc.lead_rows(self.RECS))
        ga = g["groups"]["bought in Georgia"]
        # Store-survey row 7 is left out; row 5 (not detected) counts as a sample at 0 ppm.
        self.assertEqual(ga["before"], {"samples": 3, ">=100": 2, ">=3206": 2, "max_ppm": 22000.0,
                                        "collection_dates": 2, "dates_with_hot_sample": 1})
        self.assertEqual(ga["after"], {"samples": 3, ">=100": 0, ">=3206": 0, "max_ppm": 3.5,
                                       "collection_dates": 2, "dates_with_hot_sample": 0})
        el = g["groups"]["bought elsewhere"]
        self.assertEqual(el["before"]["samples"], 1)
        self.assertEqual(el["after"][">=3206"], 1)
        self.assertAlmostEqual(g["p_none_hot_after_samples"], nyc.hypergeom_p0(6, 2, 3))
        self.assertAlmostEqual(g["p_none_hot_after_dates"], nyc.hypergeom_p0(4, 1, 2))
        self.assertEqual(sorted(g["georgia_by_year"]), ["2017", "2019", "2021", "2022"])
        self.assertEqual(g["georgia_by_year"]["2021"]["collection_dates"], 1)

    def test_no_p_when_after_has_hot(self):
        recs = self.RECS + [rec(10, "Ajika", "Lead", 5200, date="2023-01-01T00:00:00.000")]
        g = nyc.georgia_trend(nyc.lead_rows(recs))
        self.assertNotIn("p_none_hot_after_samples", g)


class EndToEnd(unittest.TestCase):
    def test_main_with_cached_file(self):
        with tempfile.TemporaryDirectory() as d:
            data, out = os.path.join(d, "data"), os.path.join(d, "out")
            os.makedirs(data)
            with open(os.path.join(data, nyc.CACHE_NAME), "w", encoding="utf-8") as fh:
                json.dump(FIXTURE, fh)
            self.assertEqual(nyc.main(["--data-dir", data, "--out-dir", out]), 0)
            for name in ("nyc_spice_lead.csv", "nyc_spice_pb_cr_pairs.csv", "nyc_summary.json", "nyc_summary.md"):
                self.assertTrue(os.path.exists(os.path.join(out, name)), name)
            with open(os.path.join(out, "nyc_summary.md"), encoding="utf-8") as fh:
                md = fh.read()
            self.assertIn("Georgian saffron (zaprana)", md)
            self.assertIn("| S | 3 |", md)
            self.assertIn("| bought in Georgia | 2021 on | 0 | 0 | 0 | - | 0 | 0 |", md)


if __name__ == "__main__":
    unittest.main()
