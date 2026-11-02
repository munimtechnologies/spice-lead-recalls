# SPDX-License-Identifier: Apache-2.0
"""Offline tests for ethyl_carbamate.py (ethyl-carbamate 0.1.0 grader). Synthetic rows only; no
network and no CFIA file. Made with AI agents working in MV2's (Munim, Inc.) name."""
import csv
import hashlib
import io
import unittest

import ethyl_carbamate as ec

H18 = ["﻿Sample No. – No. d’échantillon", "Region - Région", "Commodity",
       "denrée", "Function", "Fonction", "Origin", "Origine", "Product", "Produit",
       "Date Sampled – Date d’échantillonage", "Type of Test",
       "Type d’analyse", "Component", "Composant", "MaxOfAMOUNT",
       "Report Unit - Unité de rapport", "PLAN_CODE"]
H19 = ["﻿Sample No. – No. d’échantillon", "Function", "Fonction", "Origin",
       "Origine", "Product", "Produit", "Date Sampled – Date d’échantillonage",
       "Type of Test", "Type d’analyse", "Component", "Composant",
       "Result - Résultat", "Unit - Unité", "Plan Code - Code du régime"]


def _csv(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def ec18_rows():
    """390 samples that meet every ec18 printed figure. Alcohol IDs 1-140 (sake 7, 7, 33; spirits
    4, 42 and 21 x 11.3; wine 17, 17, 86), beer 141-264, the 'Beef' row 265, vinegar 266-390
    (6, 7, 8, 9, 12, 135)."""
    other = [7.0, 7.0, 33.0, 4.0, 42.0] + [11.3] * 21 + [17.0, 17.0, 86.0]
    beer = [4.0, 4.2]
    vinegar = [6.0, 7.0, 8.0, 9.0, 12.0, 135.0]
    out = []
    for n in range(1, 391):
        if n <= 140:
            prod, vals, k = "Beverage - Alcohol", other, n - 1
        elif n <= 264:
            prod, vals, k = "Beer", beer, n - 141
        elif n == 265:
            prod, vals, k = "Beef", [], 0
        else:
            prod, vals, k = "Vinegar", vinegar, n - 266
        v = vals[k] if k < len(vals) else 0
        out.append([f"C2018ETCA{n:05d}", "WEST", "IMFD", "DAIM", "Import", "importé",
                    "UNKNOWN", "INCONNU", prod, prod, "4-Jun-18", "ETHYL CARBAMATE",
                    "CARBAMATE D'ÉTHYLE", "Ethyl carbamate", "Ethyl carbamate", str(v),
                    "ng/g", "2018_SB428"])
    return out


def ec19_rows(cabbage=9.0):
    """300 samples that meet every ec19 printed figure. Soy IDs 1-100 (97 Soy Products, 98-100
    Tofu; detects 7, 217, 106 x 4); vegetables 101-300 (Sauerkraut 4 and 6, Cabbage 9)."""
    out = []
    soy = [7.0, 217.0, 106.0, 106.0, 106.0, 106.0]
    for n in range(1, 301):
        if n <= 100:
            prod = "Tofu" if n >= 98 else "Soy Products"
            v = soy[n - 1] if n <= 6 else 0
        elif n in (101, 102):
            prod, v = "Sauerkraut", (4.0 if n == 101 else 6.0)
        elif n in (103, 104, 105):
            prod, v = "Cabbage", (cabbage if n == 103 else 0)
        elif n == 106:
            prod, v = "Fish/Seafood - Frozen/Refrigerated", 0
        else:
            prod, v = "Pickled Vegetable - Misc", 0
        sid = f"C2019ETCA{n:05d}" + ("D" if n == 152 else "")
        out.append([sid, "Import", "importé", "KOREA, REPUBLIC OF", "CORÉE", prod, prod,
                    "2019-04-09", "ETHYL CARBAMATE", "CARBAMATE D'ÉTHYLE",
                    "Ethyl carbamate", "Ethyl carbamate", str(v), "ng/g", "2019_SB428"])
    return out


def _target(text, name):
    raw = text.encode("utf-8")
    t = dict(ec.TARGETS[name])
    t.update(size=len(raw), md5=hashlib.md5(raw).hexdigest())
    return raw, t


def _by_id(preds):
    return {p["id"]: p for p in preds}


class TestReading(unittest.TestCase):
    def test_both_real_headers(self):
        c18 = ec.find_columns(H18)
        self.assertEqual((c18["sample"], c18["region"], c18["function"], c18["origin"],
                          c18["product"], c18["date"], c18["test"], c18["component"],
                          c18["value"], c18["unit"]), (0, 1, 4, 6, 8, 10, 11, 13, 15, 16))
        c19 = ec.find_columns(H19)
        self.assertNotIn("region", c19)
        self.assertEqual((c19["sample"], c19["function"], c19["origin"], c19["product"],
                          c19["date"], c19["value"], c19["unit"]), (0, 1, 3, 5, 7, 12, 13))

    def test_values_units_and_half_units(self):
        self.assertEqual(ec.to_value(" 0 "), 0.0)
        self.assertIsNone(ec.to_value("ND"))
        self.assertIsNone(ec.to_value("-1"))
        self.assertTrue(ec.in_range(4.2, "4"))
        self.assertFalse(ec.in_range(4.6, "4"))
        self.assertTrue(ec.in_range(29.54, "29.5"))
        self.assertFalse(ec.in_range(29.56, "29.5"))
        rows, problems = ec.parse(_csv(H18, [ec18_rows()[0][:16] + ["ug/g", "x"]]))
        self.assertEqual((len(rows), problems["bad_units"], problems["bad_values"]), (1, 1, 0))
        self.assertEqual(problems["missing_roles"], [])


class TestMapsAndBands(unittest.TestCase):
    def test_census_counts_map_to_report_types(self):
        ec18 = {"Beef": 1, "Beer": 124, "Beverage - Alcohol": 140, "Vinegar": 125}
        got = {}
        for label, n in ec18.items():
            got[ec.EC18_TYPE[label]] = got.get(ec.EC18_TYPE[label], 0) + n
        self.assertEqual(got, {"beer": 125, "other": 140, "vinegar": 125})
        self.assertEqual(17 + 117 + 6, got["other"])
        ec19 = {"Cabbage": 4, "Cucumber - Pickled": 21, "Fish/Seafood - Frozen/Refrigerated": 1,
                "Gherkin - Pickled": 1, "Pickled Vegetable - Misc": 118, "Sauerkraut": 55,
                "Soy Products": 97, "Tofu": 3}
        got = {}
        for label, n in ec19.items():
            got[ec.EC19_TYPE[label]] = got.get(ec.EC19_TYPE[label], 0) + n
        self.assertEqual(got, {"veg": 200, "soy": 100})

    def test_pooled_band_covers_printed_rows(self):
        lo = (3 * 15.65 + 23 * 12.25 + 3 * 39.5) / 29
        hi = (3 * 15.75 + 23 * 12.35 + 3 * 40.5) / 29
        self.assertLessEqual(ec.EC18_OTHER[4][0], lo)
        self.assertGreaterEqual(ec.EC18_OTHER[4][1], hi)
        self.assertEqual(ec.EC18_OTHER[:2], (140, 29))
        self.assertEqual(2 + 29 + 6, ec.EC18_TOTAL[1])
        self.assertEqual(2 + 29, ec.EC18_SUBTOTAL[1])


class TestEc18(unittest.TestCase):
    def setUp(self):
        text = _csv(H18, ec18_rows())
        raw, self.target = _target(text, "ec18")
        self.rec, preds, self.samples = ec.grade_ec18(raw, text, self.target)
        self.p = _by_id(preds)

    def test_gate_and_types(self):
        self.assertTrue(all(self.rec["gate"].values()), self.rec["gate"])
        self.assertEqual(self.rec["census_checks"]["types"],
                         {"beer": 125, "other": 140, "vinegar": 125})
        self.assertEqual(self.rec["census_checks"]["unmapped"], {})

    def test_v1_v2_v3_met_and_v4_ungraded(self):
        for pid in ("V1", "V2", "V3"):
            self.assertTrue(self.p[pid]["met"], (pid, self.p[pid]["observed"]))
        self.assertFalse(self.p["V4"]["graded"])
        rows = self.p["V1"]["observed"]["rows"]
        self.assertAlmostEqual(rows["vinegar"]["mean"], 29.5, places=9)
        self.assertAlmostEqual(rows["total"]["mean"], 635.5 / 37, places=9)
        self.assertAlmostEqual(rows["other_pooled"]["mean"], 450.3 / 29, places=9)
        self.assertAlmostEqual(self.p["V2"]["observed"]["vinegar_rest_sum"], 42.0, places=9)
        self.assertAlmostEqual(self.p["V3"]["observed"]["subtotal"]["mean"], 458.5 / 31,
                               places=9)

    def test_a_wrong_vinegar_fails_v1_and_v2_only(self):
        rows = ec18_rows()
        rows[269][15] = "14"  # ID 270: the fifth vinegar detect, 12 -> 14 (rounds outside 6-13)
        self.assertEqual(rows[269][0], "C2018ETCA00270")
        self.assertEqual(rows[270][15], "135.0")
        text = _csv(H18, rows)
        raw, target = _target(text, "ec18")
        _, preds, _ = ec.grade_ec18(raw, text, target)
        p = _by_id(preds)
        self.assertFalse(p["V2"]["met"])
        self.assertFalse(p["V1"]["met"])  # vinegar average 179 / 6 = 29.83
        self.assertTrue(p["V3"]["met"])

    def test_descriptive(self):
        d = self.rec["descriptive"]
        self.assertEqual(d["coding"]["above_zero"], 37)
        self.assertEqual(d["coding"]["zero"], 353)
        self.assertEqual([r["sample"] for r in d["beef_row"]], ["C2018ETCA00265"])
        self.assertEqual(d["other_alcohol_top"][0]["ppb"], 86.0)
        self.assertEqual(d["ids_dates"]["id_range"], [1, 390])
        self.assertEqual(d["ids_dates"]["first"], "2018-06-04")

    def test_gate_fails_on_wrong_md5(self):
        text = _csv(H18, ec18_rows())
        raw = text.encode("utf-8")
        rec, preds, _ = ec.grade_ec18(raw, text, dict(self.target, md5="0" * 32))
        self.assertFalse(rec["gate"]["md5"])
        self.assertFalse(any(p["graded"] for p in preds))


class TestEc19(unittest.TestCase):
    def test_all_met(self):
        text = _csv(H19, ec19_rows())
        raw, target = _target(text, "ec19")
        rec, preds, samples = ec.grade_ec19(raw, text, target)
        self.assertTrue(all(rec["gate"].values()), rec["gate"])
        p = _by_id(preds)
        for pid in ("V5", "V6", "V7"):
            self.assertTrue(p[pid]["met"], (pid, p[pid]["observed"]))
        self.assertEqual(p["V5"]["observed"]["soy"]["mean"], 108.0)
        self.assertEqual(p["V6"]["observed"]["veg_detect_labels"],
                         ["Sauerkraut", "Sauerkraut", "Cabbage"])
        self.assertEqual(p["V6"]["observed"]["soy_without_ec"], 94)
        self.assertAlmostEqual(p["V7"]["observed"]["total_mean"], 667 / 9, places=9)
        ids = rec["descriptive"]["ids_dates"]
        self.assertEqual(ids["gaps"], [])
        self.assertEqual(ids["suffixed"], [{"sample": "C2019ETCA00152D",
                                            "base": "C2019ETCA00152", "base_present": False}])
        self.assertEqual([r["sample"] for r in rec["descriptive"]["fish_seafood_row"]],
                         ["C2019ETCA00106"])

    def test_cabbage_ten_fails_v5_and_v7(self):
        text = _csv(H19, ec19_rows(cabbage=10.0))
        raw, target = _target(text, "ec19")
        _, preds, _ = ec.grade_ec19(raw, text, target)
        p = _by_id(preds)
        self.assertFalse(p["V5"]["met"])  # 10 does not round to 9
        self.assertTrue(p["V6"]["met"])
        self.assertFalse(p["V7"]["met"])  # 668 / 9 = 74.22, above 74.15
        self.assertTrue(p["V7"]["observed"]["checks"]["soy_min_7"])


if __name__ == "__main__":
    unittest.main()
