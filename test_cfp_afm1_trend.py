# SPDX-License-Identifier: Apache-2.0
"""Offline tests for cfp_afm1_trend.py (no network, no CFIA file). Made with AI agents working in
MV2's (Munim, Inc.) name."""
import csv
import io
import unittest

import cfp_afm1_trend as m

HEADER_2020 = ["Sample No. – No. d’échantillon", "Region - Région", "Commodity", "Denrée",
               "Function", "Fonction", "Origin", "Origine", "Product", "Produit",
               "Date Sampled – Date d’échantillonage", "Component", "Composant", "Amount",
               "Report Unit - Unité de rapport"]
HEADER_2022 = ["Sample No. – No. d’échantillon", "Function", "Fonction", "Origin", "Origine",
               "Product", "Produit", "Organic – Biologique",
               "Date Sampled – Date d’échantillonage", "Type of test", "Type d’analyse",
               "Component", "Composant", "Result – Résultat", "Unit – Unité",
               "Plan Code – Code du régime"]


def row(sample, product, comp, amount, unit="ng/g"):
    return [sample, "ON", "Dairy", "Laitier", "Import", "Importation", "UNITED STATES",
            "ÉTATS-UNIS", product, product, "2020-01-01", comp, comp, amount, unit]


ROWS = [
    row("S1", "Pudding", "Aflatoxin M1", "0"),
    row("S1", "Pudding", "Aflatoxin M1", "0"),
    row("S2", "Yogurt", "Aflatoxin M1", "0.03"),
    row("S3", "Infant Formula - Dairy", "Aflatoxin M1", "0.05"),
    row("S3", "Infant Formula - Dairy", "Aflatoxin B1", "0.9"),
    row("S4", "Infant Formula - Dairy", "Aflatoxin M1", "<0.01"),
    row("S5", "Infant Formula - Dairy", "Aflatoxin M1", "ND"),
]
FIXTURE_EXPECTED = {"rows": 6, "samples": 5, "units": {"ng/g": 6},
                    "classes": {"formula": 3, "dairy-dessert": 2}}


def text_of(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def mk(sid, product, kind, stored=0.0, unit="ng/g"):
    return {"sample": sid, "product": product, "class": m.product_class(product),
            "type": m.formula_type(product), "origin": "", "unit": unit, "raws": [],
            "kinds": [kind], "kind": kind, "stored": stored}


class TestConstants(unittest.TestCase):
    def test_years_files_census(self):
        self.assertEqual(set(m.YEARS), set(m.FILES))
        self.assertEqual(set(m.YEARS), set(m.CENSUS))
        for y in m.YEARS:
            self.assertEqual(len(m.FILES[y][3]), 64, y)
            self.assertEqual(sum(m.CENSUS[y]["classes"].values()), m.CENSUS[y]["samples"], y)
            self.assertEqual(sum(m.CENSUS[y]["units"].values()), m.CENSUS[y]["rows"], y)

    def test_c1_only_twelve_rounds_to_twelve_percent(self):
        hits = [k for k in range(102) if round(100 * k / 101) == 12]
        self.assertEqual(hits, [m.C1_DET])


class TestValues(unittest.TestCase):
    def test_parse_value(self):
        self.assertEqual(m.parse_value("0"), (0.0, "nd"))
        self.assertEqual(m.parse_value("0.0566"), (0.0566, "det"))
        self.assertEqual(m.parse_value("0,02"), (0.02, "det"))
        self.assertEqual(m.parse_value("<0.01"), (0.0, "nd"))
        self.assertEqual(m.parse_value("<0"), (0.0, "nd"))
        self.assertEqual(m.parse_value("ND"), (0.0, "nd"))
        self.assertEqual(m.parse_value("n.d."), (0.0, "nd"))
        self.assertEqual(m.parse_value("<LOD"), (0.0, "nd"))
        for bad in ("", "NA", "N/A", "<LOQ", "Trace", "-0.1", "NQ"):
            self.assertEqual(m.parse_value(bad), (None, "bad"), bad)

    def test_units(self):
        self.assertEqual(m.unit_key("µg/g"), m.MICRO_G)
        self.assertEqual(m.unit_key("μg/g"), m.MICRO_G)
        self.assertEqual(m.unit_key(" NG/G "), "ng/g")
        self.assertEqual(m.UNIT_TO_PPB[m.MICRO_G], 1000.0)
        self.assertEqual(m.UNIT_TO_PPB["ng/g"], 1.0)

    def test_classes(self):
        self.assertEqual(m.product_class("Infant Formula - Milk"), "formula")
        self.assertEqual(m.product_class("Beverage - Yogurt"), "dairy-dessert")
        self.assertEqual(m.product_class("Pudding"), "dairy-dessert")
        self.assertEqual(m.product_class("Infant Biscuit"), "other")
        self.assertEqual(m.product_class("Toddler snacks"), "other")
        self.assertEqual(m.formula_type("Infant formula - Specialized"), "specialized")
        self.assertEqual(m.formula_type("Infant Formula - Soy"), "soy")
        self.assertEqual(m.formula_type("Infant Formula - Milk"), "milk")
        self.assertEqual(m.formula_type("Infant Formula - Dairy"), "milk")
        self.assertEqual(m.formula_type("Infant Formula"), "other")
        self.assertEqual(m.formula_type("Yogurt"), "")

    def test_matches(self):
        self.assertTrue(m.matches(0.0566, "0.0566"))
        self.assertTrue(m.matches(0.0805, "0.080"))
        self.assertFalse(m.matches(0.0806, "0.080"))
        self.assertTrue(m.matches(0.012, "0.01"))
        self.assertFalse(m.matches(0.016, "0.01"))
        self.assertFalse(m.matches(None, "0.01"))


class TestStats(unittest.TestCase):
    def test_wilson(self):
        lo, hi = m.wilson(0, 10)
        self.assertAlmostEqual(lo, 0.0, places=9)
        self.assertAlmostEqual(hi, 0.2775, places=3)
        self.assertIsNone(m.wilson(0, 0))

    def test_fisher(self):
        self.assertAlmostEqual(m.fisher_less(0, 5, 5, 5), 1 / 252)
        self.assertAlmostEqual(m.fisher_less(5, 5, 0, 5), 1.0)
        self.assertAlmostEqual(m.fisher_less(1, 3, 2, 5), 40 / 56)


class TestParseYear(unittest.TestCase):
    def test_columns(self):
        self.assertEqual(m.find_columns(HEADER_2020),
                         {"sample": 0, "component": 11, "value": 13, "unit": 14, "product": 8,
                          "origin": 6})
        self.assertEqual(m.find_columns(HEADER_2022),
                         {"sample": 0, "component": 11, "value": 13, "unit": 14, "product": 5,
                          "origin": 3})

    def test_fixture(self):
        samples, census = m.parse_year(text_of(HEADER_2020, ROWS))
        self.assertEqual(census["rows"], 6)
        self.assertEqual(census["samples"], 5)
        self.assertEqual(census["units"], {"ng/g": 6})
        self.assertEqual(census["kinds"], {"nd": 4, "det": 2})
        self.assertEqual(census["classes"], {"formula": 3, "dairy-dessert": 2})
        self.assertEqual(census["bad_shapes"], [])
        by = {s["sample"]: s for s in samples}
        self.assertEqual(by["S1"]["raws"], ["0", "0"])
        self.assertEqual(by["S1"]["kind"], "nd")
        self.assertEqual(by["S3"]["kind"], "det")
        self.assertAlmostEqual(by["S3"]["stored"], 0.05)
        self.assertEqual(by["S4"]["kind"], "nd")
        self.assertEqual(by["S3"]["origin"], "UNITED STATES")
        gate = m.gate_checks(census, True, FIXTURE_EXPECTED)
        self.assertTrue(all(gate.values()), gate)
        st = m.year_stats(samples, 1.0)
        self.assertEqual((st["n"], st["det"]), (5, 2))
        self.assertEqual(st["by_class"]["formula"]["det"], 1)
        self.assertAlmostEqual(st["by_class"]["dairy-dessert"]["max"], 0.03)
        self.assertAlmostEqual(st["max"], 0.05)

    def test_bad_value_fails_gate(self):
        rows = ROWS + [row("S6", "Infant Formula - Dairy", "Aflatoxin M1", "Trace 0.4")]
        _, census = m.parse_year(text_of(HEADER_2020, rows))
        self.assertEqual(census["kinds"].get("bad"), 1)
        self.assertEqual(census["bad_shapes"], ["Trace #.#"])
        gate = m.gate_checks(census, True, {"rows": 7, "samples": 6, "units": {"ng/g": 7},
                                            "classes": {"formula": 4, "dairy-dessert": 2}})
        self.assertFalse(gate["values"])
        self.assertTrue(gate["rows"] and gate["samples"] and gate["classes"])

    def test_missing_value_column(self):
        header = HEADER_2020[:13] + ["Comment"] + HEADER_2020[14:]
        samples, census = m.parse_year(text_of(header, ROWS))
        self.assertEqual(samples, [])
        self.assertFalse(m.gate_checks(census, True, FIXTURE_EXPECTED)["columns"])


class TestAnalyseAndGrade(unittest.TestCase):
    PASSING = {
        "2014-15": [mk("A", "Infant Formula", "det", 0.011, m.MICRO_G),
                    mk("B", "Infant Formula", "det", 0.061, m.MICRO_G),
                    mk("C", "Infant Formula", "nd", 0.0, m.MICRO_G),
                    mk("D", "Yogurt", "nd", 0.0, m.MICRO_G)],
        "2018": [mk("E", "Infant Formula - Dairy", "det", 0.03),
                 mk("F", "Infant Formula - Dairy", "nd")],
        "2022": [mk("G", "Infant Formula - Dairy", "nd"), mk("H", "Yogurt", "nd"),
                 mk("I", "Infant Formula - Dairy", "det", 0.0566),
                 mk("J", "Infant Formula - Dairy", "nd")],
    }

    def test_analyse(self):
        a = m.analyse(self.PASSING)
        self.assertEqual(a["unit_2014_15"]["reading"], "stored")
        self.assertEqual(a["ppb_factor"]["2014-15"], 1.0)
        cut = a["formula_at_cut"]
        self.assertEqual((cut["2014-15"]["k"], cut["2014-15"]["n"]), (1, 3))
        self.assertEqual((cut["2018"]["k"], cut["2018"]["n"]), (1, 2))
        self.assertEqual((cut["2022"]["k"], cut["2022"]["n"]), (1, 3))
        p5 = a["p5"]
        self.assertEqual(p5["earlier_years"], ["2014-15", "2018"])
        self.assertEqual((p5["pooled_k"], p5["pooled_n"]), (2, 5))
        self.assertAlmostEqual(p5["pooled_rate"], 0.4)
        self.assertAlmostEqual(p5["fisher_one_sided_p"], 40 / 56)
        self.assertEqual(a["dairy_dessert"]["n"], 2)
        self.assertEqual(a["dairy_dessert"]["det"], 0)
        self.assertEqual(a["p1"]["years"], ["2018", "2022"])
        self.assertAlmostEqual(a["p1"]["max_ppb"], 0.0566)
        self.assertNotIn("p4", a)

    def test_labelled_reading(self):
        samples = [mk("A", "Infant Formula", "det", 0.000011, m.MICRO_G),
                   mk("B", "Infant Formula", "det", 0.000061, m.MICRO_G)]
        r = m.unit_reading(m.year_stats(samples, 1.0))
        self.assertFalse(r["as_stored"])
        self.assertTrue(r["as_labelled"])
        self.assertEqual(r["reading"], "labelled")
        a = m.analyse({"2014-15": samples})
        self.assertEqual(a["ppb_factor"]["2014-15"], 1000.0)
        self.assertEqual(a["formula_at_cut"]["2014-15"]["k"], 1)

    def test_grade(self):
        a = m.analyse(self.PASSING)
        gates = {y: {"sha256": y in self.PASSING} for y in m.YEARS}
        p = {x["id"]: x for x in m.grade(a, gates)}
        self.assertFalse(p["G"]["met"])
        self.assertEqual(p["G"]["observed"]["passing"], ["2014-15", "2018", "2022"])
        for pid in ("C1", "C3", "C5", "P4"):
            self.assertFalse(p[pid]["graded"], pid)
            self.assertFalse(p[pid]["met"], pid)
        self.assertTrue(p["C2"]["graded"])
        self.assertFalse(p["C2"]["met"])
        self.assertTrue(p["C4"]["graded"])
        self.assertFalse(p["C4"]["met"])
        for pid in ("C6", "P1", "P2", "P3", "P5"):
            self.assertTrue(p[pid]["graded"], pid)
            self.assertTrue(p[pid]["met"], pid)

    def test_grade_c5_only(self):
        passing = {"2020": [mk("P%d" % i, "Pudding", "nd") for i in range(3)]}
        a = m.analyse(passing)
        gates = {y: {"sha256": y == "2020"} for y in m.YEARS}
        p = {x["id"]: x for x in m.grade(a, gates)}
        self.assertTrue(p["C5"]["met"])
        self.assertTrue(p["P1"]["graded"] and p["P1"]["met"])
        self.assertTrue(p["P3"]["met"])
        self.assertFalse(p["P5"]["graded"])
        self.assertFalse(p["P2"]["graded"])


if __name__ == "__main__":
    unittest.main()
