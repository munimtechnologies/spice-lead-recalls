# SPDX-License-Identifier: Apache-2.0
"""Offline tests for coumarin_early_surveys 0.1.0. Fixtures only: no CFIA value is read here.
Made with AI agents working in MV2's (Munim, Inc.) name."""
import unittest

import coumarin_cinnamon as cc
import coumarin_early_surveys as ces

HEADER = ("Sample No. - No. d'échantillon,Region - Région,Function,Fonction,Origin,"
          "Origine,Product,Produit,Date sampled - Date d'échantillonage,Type of Test,"
          "Type d'analyse,Component,Composante,Result - Résultat,Unit - Unité,"
          "Plan Code - Code du régime")


def fixture_csv():
    lines = [HEADER,
             "X0001,WEST,Unknown,Inconnu,Canada,Canada,Tea,Thé,2011-05-01,,,Coumarin,"
             "Coumarine,<0.29,mg/kg,TS020",
             "X0002,WEST,Unknown,Inconnu,Unknown,Inconnu,Tea,Thé,2011-05-01,,,Coumarin,"
             "Coumarine,12.5,mg/kg,TS020",
             "X0003,QUEBEC,Unknown,Inconnu,Canada,Canada,Spice mix,Mélange,2011-05-02,,,"
             "Coumarin,Coumarine,300,mg/kg,TS020"]
    return ("\r\n".join(lines) + "\r\n").encode("cp1252")


def synthetic_rows(spec, values):
    """Rows shaped like coumarin_cinnamon.parse() output; `values` maps label -> list of
    special values placed first, the rest filled with values[label + '*']."""
    rows = []
    for lab, n in spec.items():
        special = values.get(lab, [])
        fill = values.get(lab + "*", 1.0)
        for i in range(n):
            ppm = special[i] if i < len(special) else fill
            rows.append({"product": lab, "ppm": ppm, "sample": f"{lab}-{i}",
                         "origin": "UNKNOWN"})
    return rows


def synthetic_parsed():
    v11 = {"Ground Cinnamon": [16.2, 7816.3], "Ground Cinnamon*": 1000.0,
           "Cinnamon Sticks": [6823.2], "Cinnamon Sticks*": 500.0}
    v12 = {"Cinnamon": [7621.1], "Cinnamon*": 2000.0, "Spice Mixes*": 40.0}
    out = {}
    for label, vals in (("2011-12", v11), ("2012-13", v12)):
        rows = synthetic_rows(ces.LABELS[label], vals)
        out[label] = {"rows": rows, "sha_ok": True,
                      "check": {"units": {"mg/kg": len(rows)}, "bad_numbers": 0,
                                "other_component_rows": 0}}
    return out


class TestPure(unittest.TestCase):
    def test_cat_stats(self):
        s = ces.cat_stats([4.0, 0.0, 2.0])
        self.assertEqual((s["n"], s["n_detected"]), (3, 2))
        self.assertEqual(s["min"], 0.0)
        self.assertEqual(s["min_detected"], 2.0)
        self.assertAlmostEqual(s["median"], 2.0)
        self.assertAlmostEqual(s["mean_all"], 2.0)
        self.assertAlmostEqual(s["mean_positives"], 3.0)
        self.assertEqual(s["max"], 4.0)
        e = ces.cat_stats([])
        self.assertEqual(e["n"], 0)
        self.assertIsNone(e["mean_all"])

    def test_pct_detected(self):
        self.assertEqual(ces.pct_detected(189, 193), 98)
        self.assertEqual(ces.pct_detected(190, 193), 98)
        self.assertEqual(ces.pct_detected(188, 193), 97)
        self.assertEqual(ces.pct_detected(93, 93), 100)

    def test_reprint_checks(self):
        s = ces.cat_stats([0.0, 5.0, 1040.2])
        self.assertEqual(ces.reprint_checks(s, 3, "<0.29", "1040"),
                         {"n": True, "min": True, "max": True})
        s2 = ces.cat_stats([30.4, 100.0, 3078.0])
        self.assertEqual(ces.reprint_checks(s2, 3, "30", "3078"),
                         {"n": True, "min": True, "max": True})
        # a non-detect cannot match a printed numeric minimum, and "<x" needs a non-detect
        self.assertFalse(ces.reprint_checks(ces.cat_stats([0.0, 31.0]), 2, "30", "31")["min"])
        self.assertFalse(ces.reprint_checks(ces.cat_stats([1.0, 31.0]), 2, "<0.29", "31")["min"])

    def test_verdicts_via_table_audit(self):
        s = ces.cat_stats([568.0, 568.0, 568.0])
        self.assertEqual(ces.cta.verdict(s["mean_positives"], s["mean_all"], "568"), "both")
        s = ces.cat_stats([0.0, 380.0, 380.0])
        self.assertEqual(ces.cta.verdict(s["mean_positives"], s["mean_all"], "380"), "positives")

    def test_infant_and_counts(self):
        self.assertAlmostEqual(ces.infant_pct_tdi(10.0), 37.5)
        self.assertAlmostEqual(ces.infant_pct_tdi(80.0 / 3.0), 100.0)
        self.assertEqual(ces.n_over([15.0, 15.1, 50.0, 50.5], 15.0), 3)
        self.assertEqual(ces.n_over([15.0, 15.1, 50.0, 50.5], 50.0), 1)
        self.assertTrue(ces.within(0, (0, 8)))
        self.assertFalse(ces.within(3, (1, 2)))

    def test_pins(self):
        for label in ces.LABELS_ORDER:
            self.assertEqual(len(ces.SURVEYS[label]["sha256"]), 64)
            self.assertTrue(ces.SURVEYS[label]["fallback"].startswith("https://"))
        self.assertEqual(sum(ces.LABELS["2011-12"].values()), 193)
        self.assertEqual(sum(ces.LABELS["2012-13"].values()), 93)


class TestParseFixture(unittest.TestCase):
    def test_cp1252_fixture_through_published_parser(self):
        rows, check = cc.parse(fixture_csv(), "fixture")
        self.assertEqual(check["encoding"], "cp1252")
        self.assertEqual(check["units"], {"mg/kg": 3})
        self.assertEqual(check["bad_numbers"], 0)
        self.assertEqual(ces.census(rows), {"Tea": 2, "Spice mix": 1})
        tea = ces.by_label(rows)["Tea"]
        self.assertEqual(tea, [0.0, 12.5])


class TestGateAndGrade(unittest.TestCase):
    def test_gate_passes_on_synthetic_files(self):
        ok, checks = ces.gate(synthetic_parsed())
        self.assertTrue(ok, checks)

    def test_gate_fails_on_wrong_census_and_nothing_is_graded(self):
        p = synthetic_parsed()
        p["2011-12"]["rows"] = p["2011-12"]["rows"][:-1]
        ok, checks = ces.gate(p)
        self.assertFalse(ok)
        self.assertFalse(checks["2011-12"]["labels"])
        preds, _, _, _ = ces.grade(p)
        self.assertFalse(preds[0]["met"])
        self.assertTrue(all(not q["graded"] and not q["met"] for q in preds[1:]))

    def test_gate_fails_when_known_value_moves(self):
        p = synthetic_parsed()
        p["2012-13"]["rows"][0]["ppm"] = 7600.0
        ok, checks = ces.gate(p)
        self.assertFalse(ok)
        self.assertFalse(checks["2012-13"]["known_values"])

    def test_grade_on_synthetic_files(self):
        preds, st, reprints, _ = ces.grade(synthetic_parsed())
        got = {q["id"]: q for q in preds}
        self.assertEqual(list(got), ["E0", "C1", "C2", "C3", "V1", "V2", "V3",
                                     "R1", "R2", "R3", "R4", "R5"])
        self.assertTrue(all(q["graded"] for q in preds))
        self.assertTrue(got["R1"]["met"])          # 0 of 20 over 15
        self.assertTrue(got["R2"]["met"])          # 0 of 20 over 50
        self.assertFalse(got["R3"]["met"])         # 0 of 15 over 20
        self.assertFalse(got["R4"]["met"])         # 0 of 11 teas over 750
        self.assertFalse(got["R5"]["met"])         # equal medians are not "below"
        self.assertFalse(got["C2"]["met"])         # 100% detected, CFIA prints 98%
        self.assertEqual(reprints["T3"]["verdict"], "neither")
        self.assertEqual(st["2012-13"]["Spice Mixes"]["n"], 53)


if __name__ == "__main__":
    unittest.main()
