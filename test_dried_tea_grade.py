# SPDX-License-Identifier: Apache-2.0
"""Tests for dried_tea_grade.py (dried-tea-2009 value grader) on small synthetic files.
Test fixture fix 0.1.1 (2026-11-09): the V4 expectations now follow the pre-registration, which says
that if V6 holds (mercury not detected in every sample), V4 fails for mercury. The grader is unchanged.
Made with AI agents working in MV2's (Munim, Inc.) name."""
import csv
import io
import json
import os
import tempfile
import unittest

import dried_tea_census as dc
import dried_tea_grade as g

HEADER = ["Sample No. - No. d'echantillon", "Function", "Fonction", "Origin", "Origine",
          "Product", "Produit", "Date Sampled", "Type of test", "Type d'analyse", "Component",
          "Composant", "Result - Resultat", "Unit - Unite", "Plan Code"]
METALS = ["Aluminum", "Antimony", "Arsenic", "Beryllium", "Boron", "Cadmium", "Chromium",
          "Copper", "Iron", "Lead", "Manganese", "Mercury", "Molybdenum", "Nickel", "Selenium",
          "Tin", "Titanium", "Zinc"]
UG = chr(0xB5) + "g/g"
FPH, LC = "PESTICIDES-FPH053", "PESTICIDES-LC"
ORIGINS = {1: "CHINA", 2: "JAPAN", 3: "CANADA"}


def row(sid, tea, test, comp, value, unit):
    o = ORIGINS[tea]
    return [sid, "Import", "Importe", o, o, "Tea", "The", "2009-12-03", test, test, comp, comp,
            value, unit, "2009_SB457"]


def screen(n):
    return f"{n} Pesticide detected/détecté" if n == 1 else f"{n} Pesticides detected/détectés"


def build(metal_value=None, extra=()):
    """Three teas. Pesticides on '...A' numbers, metals on '...B' numbers."""
    rows = []
    p = {t: f"2009TEA000{t}A" for t in ORIGINS}
    rows += [row(p[1], 1, FPH, "Pesticide Screen", screen(1), "n/a"),
             row(p[1], 1, FPH, "Bifenthrin", "0.25", UG),
             row(p[1], 1, LC, "Pesticide Screen", screen(0), "n/a"),
             row(p[2], 2, FPH, "Pesticide Screen", screen(0), "n/a"),
             row(p[2], 2, LC, "Pesticide Screen", screen(2), "n/a"),
             row(p[2], 2, LC, "Imidacloprid", "0.05", UG),
             row(p[2], 2, LC, "Methomyl", "0.1", UG),
             row(p[3], 3, FPH, "Pesticide Screen", screen(0), "n/a"),
             row(p[3], 3, LC, "Pesticide Screen", screen(0), "n/a")]
    for t in ORIGINS:
        for m in METALS:
            v = (metal_value or default_metal)(t, m)
            rows.append(row(f"2009TEA000{t}B", t, "METALS-P", m, v, UG))
    rows += list(extra)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(HEADER)
    w.writerows(rows)
    return buf.getvalue()


def default_metal(tea, metal):
    if metal == "Beryllium":
        return "0.01" if tea == 3 else "0"
    if metal == "Mercury":
        return {1: "0.005", 2: "0", 3: "0.004"}[tea]
    return "1.5"


class Helpers(unittest.TestCase):
    def test_tea_number(self):
        self.assertEqual(g.tea_number("2009TEA0001A"), "2009TEA0001")
        self.assertEqual(g.tea_number("2009TEA0001B"), "2009TEA0001")
        self.assertEqual(g.tea_number("2009TEA0001"), "2009TEA0001")

    def test_screen_count(self):
        self.assertEqual(g.screen_count("0 Pesticides detected/détecté"), 0)
        self.assertEqual(g.screen_count("1 Pesticide detected/détecté"), 1)
        self.assertEqual(g.screen_count(" 4 Pesticides detected/détectés"), 4)
        self.assertIsNone(g.screen_count("ND"))

    def test_number(self):
        self.assertEqual(g.number("0,5"), 0.5)
        self.assertEqual(g.number(" 0.25 "), 0.25)
        self.assertIsNone(g.number("<0.01"))
        self.assertIsNone(g.number(""))

    def test_unit_key(self):
        self.assertEqual(g.UNITS[g.unit_key(chr(0x3BC) + "g/g")], 1.0)
        self.assertEqual(g.UNITS[g.unit_key(UG)], 1.0)
        self.assertEqual(g.UNITS[g.unit_key("MG/KG")], 1.0)
        self.assertEqual(g.UNITS[g.unit_key("ng/g")], 0.001)


class Grade(unittest.TestCase):
    def test_columns_found(self):
        col = dc.find_columns(HEADER)
        self.assertEqual((col["sample"], col["test"], col["component"], col["value"],
                          col["unit"]), (0, 8, 10, 12, 13))

    def test_basic(self):
        res = g.grade(build())
        it = res["items"]
        self.assertEqual(res["pesticide_samples"], 3)
        self.assertEqual(res["metal_samples"], 3)
        self.assertEqual(res["named_pesticide_rows"], 3)
        self.assertEqual(it["V1"]["found"], 2)
        self.assertEqual(it["V1"]["screen_count_above_zero"], 2)
        self.assertFalse(it["V1"]["holds"])          # expects 69
        self.assertEqual(it["V2"]["found"], 1)       # 0.1 exactly is not above 0.1
        self.assertEqual(it["V2"]["at_or_above"], 2)
        self.assertFalse(it["V3"]["graded"])
        # Mercury is 0 in tea 2, so V6 holds and, as the pre-registration says, V4 fails for mercury.
        self.assertFalse(it["V4"]["holds"])
        self.assertEqual(it["V4"]["metals_not_above_zero_in_all"], {"Hg": 1})
        self.assertTrue(it["V5"]["holds"])
        self.assertEqual(it["V5"]["beryllium_above_zero"], 1)
        self.assertTrue(it["V6"]["holds"])           # 2 of 3 < 87%
        self.assertEqual(it["V6"]["mercury_above_zero"], 2)
        self.assertTrue(it["P1"]["holds"])
        self.assertEqual(it["P1"]["teas_in_both"], 3)
        self.assertEqual(it["P1"]["metal_numbers_ending_B"], 3)
        self.assertTrue(it["P2"]["holds"])
        self.assertEqual(it["P2"]["screen_rows"], 6)
        self.assertTrue(it["P3"]["holds"])
        self.assertIn("2010-11", res["R5"])
        rep = res["reported"]
        self.assertEqual(rep["teas_with_two_or_more_over_0_1"], 0)
        self.assertEqual(rep["per_pesticide"]["Bifenthrin"]["teas_over_0_1"], 1)
        self.assertEqual(rep["per_pesticide"]["Methomyl"]["max_ugg"], 0.1)
        self.assertEqual(rep["by_origin"]["CHINA"], {"teas": 1, "detected": 1, "over_0_1": 1})
        self.assertEqual(rep["by_origin"]["CANADA"], {"teas": 1, "detected": 0, "over_0_1": 0})
        self.assertEqual(rep["metals"]["Hg"]["zero"], 1)
        self.assertEqual(rep["metals"]["Hg"]["max"], 0.005)
        self.assertEqual(len(rep["metals"]), 18)
        json.dumps(res)  # serialisable

    def test_mercury_everywhere_supports_2009_page(self):
        def mv(t, m):
            return "0" if m == "Beryllium" else "0.003"
        res = g.grade(build(metal_value=mv))
        self.assertFalse(res["items"]["V6"]["holds"])
        self.assertTrue(res["items"]["V4"]["holds"])
        self.assertEqual(res["items"]["V4"]["metals_not_above_zero_in_all"], {})
        self.assertIn("2009-10", res["R5"])

    def test_v4_fails_on_a_zero_metal(self):
        def mv(t, m):
            return "0" if (m == "Lead" and t == 2) else default_metal(t, m)
        res = g.grade(build(metal_value=mv))
        self.assertFalse(res["items"]["V4"]["holds"])
        self.assertEqual(res["items"]["V4"]["metals_not_above_zero_in_all"], {"Hg": 1, "Pb": 1})

    def test_v4_fails_on_lead_alone_when_mercury_is_everywhere(self):
        def mv(t, m):
            if m == "Lead" and t == 2:
                return "0"
            return "0.004" if m == "Mercury" else default_metal(t, m)
        res = g.grade(build(metal_value=mv))
        self.assertFalse(res["items"]["V4"]["holds"])
        self.assertEqual(res["items"]["V4"]["metals_not_above_zero_in_all"], {"Pb": 1})
        self.assertFalse(res["items"]["V6"]["holds"])

    def test_p2_and_p3_catch_problems(self):
        extra = [row("2009TEA0003A", 3, LC, "Diuron", "ND", UG)]
        res = g.grade(build(extra=extra))
        self.assertFalse(res["items"]["P3"]["holds"])
        self.assertEqual(res["items"]["P3"]["bad_count"], 1)
        self.assertTrue(res["items"]["P2"]["holds"])   # the bad row is not counted as a detection
        extra = [row("2009TEA0003A", 3, LC, "Diuron", "0.02", UG)]
        res = g.grade(build(extra=extra))
        self.assertFalse(res["items"]["P2"]["holds"])  # screen says 0, one row exists
        self.assertEqual(res["items"]["P2"]["mismatch_count"], 1)
        self.assertEqual(res["items"]["V1"]["found"], 3)
        self.assertEqual(res["items"]["V1"]["screen_count_above_zero"], 2)

    def test_p1_fails_when_numbers_do_not_pair(self):
        extra = [row("2009TEA0009B", 3, "METALS-P", m, "1", UG) for m in METALS]
        res = g.grade(build(extra=extra))
        self.assertFalse(res["items"]["P1"]["holds"])
        self.assertEqual(res["items"]["P1"]["teas_metal"], 4)
        self.assertEqual(res["metal_samples"], 4)


class Main(unittest.TestCase):
    def test_refuses_a_different_file(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, dc.CSV_TARGET["resource"] + ".csv"), "wb") as fh:
                fh.write(build().encode("utf-8"))
            out = os.path.join(d, "out")
            self.assertEqual(g.main(["--data-dir", d, "--out-dir", out]), 1)
            with open(os.path.join(out, "dried_tea_grade_2009.json"), encoding="utf-8") as fh:
                res = json.load(fh)
            self.assertIn("error", res)
            self.assertFalse(res["md5_matches_portal"])
            self.assertNotIn("items", res)


if __name__ == "__main__":
    unittest.main()
