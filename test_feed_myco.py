# SPDX-License-Identifier: Apache-2.0
"""Offline tests for feed_myco 0.1.0 (no network, synthetic rows only)."""
import csv
import io
import os
import tempfile
import unittest
from unittest import mock

import feed_myco as fm

MU = "µg/kg"

# (year, sid, province, ingredient name, mycotoxin label, result, unit)
ROWS = [
    ("2000-2001", "S1", "Ontario", "Corn", "Deoxynivalenol", "2.5", "mg/kg"),
    ("2000-2001", "S1", "Ontario", "Corn", "Zearalenone", "0.3", "mg/kg"),
    ("2000-2001", "S1", "Ontario", "Corn", "15-Acetyldeoxynivalenol", "0.2", "mg/kg"),
    ("2000-2001", "S1", "Ontario", "Corn", "3-Acetyldeoxynivalenol", "<0.05", "mg/kg"),
    ("2000-2001", "S1", "Ontario", "Corn", "Ochratoxin A", "<2", MU),
    ("2000-2001", "S1", "Ontario", "Corn", "HT-2", "<0.1", "mg/kg"),
    ("2000-2001", "S1", "Ontario", "Corn", "Fumonisins (total B1 and B2)", "1.5", "mg/kg"),
    ("2000-2001", "S2", "Alberta", "Barley", "Deoxynivalenol", "<0.1", "mg/kg"),
    ("2000-2001", "S2", "Alberta", "Barley", "Zearalenone", "<0.05", "mg/kg"),
    ("2000-2001", "S2", "Alberta", "Barley", "15-Acetyldeoxynivalenol", "<0.05", "mg/kg"),
    ("2000-2001", "S2", "Alberta", "Barley", "3-Acetyldeoxynivalenol", "0.1", "mg/kg"),
    ("2000-2001", "S2", "Alberta", "Barley", "Ochratoxin A", "3", MU),
    ("2000-2001", "S2", "Alberta", "Barley", "HT-2", "<0.2", "mg/kg"),
    ("2000-2001", "S2", "Alberta", "Barley", "Fumonisins (total B1 and B2)", "<0.5", "mg/kg"),
    ("2017-2018", "S3", "Quebec", "Wheat", "Deoxynivalenol", "0.4", "mg/kg"),
    ("2017-2018", "S3", "Quebec", "Wheat", "Zearalenone", "<0.05", "mg/kg"),
    ("2017-2018", "S3", "Quebec", "Wheat", "15-Acetyldeoxynivalenol", "<0.05", "mg/kg"),
    ("2017-2018", "S3", "Quebec", "Wheat", "3-AcetyldeoxyNivalenol", "<0.05", "mg/kg"),
    ("2017-2018", "S3", "Quebec", "Wheat", "Aflatoxin B1", "<1", MU),
    ("2017-2018", "S3", "Quebec", "Wheat", "HT-2", "<0.05", "mg/kg"),
]


def make_text(rows=ROWS):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(fm.COLUMNS)
    for year, sid, prov, name, label, result, unit in rows:
        w.writerow([year, sid, "Multiple species", "Single ingredient feed", "Cereals", name,
                    prov, label, result, unit])
    return "﻿" + buf.getvalue()


def parsed():
    return fm.parse_text(make_text())


class TestParse(unittest.TestCase):
    def test_parse_result(self):
        self.assertEqual(fm.parse_result("<0.05"), (0.0, False, 0.05))
        self.assertEqual(fm.parse_result("< 2"), (0.0, False, 2.0))
        self.assertEqual(fm.parse_result("<LOQ"), (0.0, False, None))
        self.assertEqual(fm.parse_result("2.5"), (2.5, True, None))
        self.assertEqual(fm.parse_result("0"), (0.0, False, None))
        self.assertEqual(fm.parse_result("0,4"), (0.4, True, None))
        self.assertEqual(fm.parse_result(""), (None, False, None))
        self.assertEqual(fm.parse_result("abc"), (None, False, None))

    def test_classify_like_census(self):
        self.assertEqual(fm.classify_result("<0.05"), "censored")
        self.assertEqual(fm.classify_result("<LOQ"), "token")
        self.assertEqual(fm.classify_result("1.2"), "numeric")
        self.assertEqual(fm.classify_result("0"), "zero")
        self.assertEqual(fm.classify_result(""), "blank")
        self.assertEqual(fm.classify_result("x"), "bad")

    def test_units_and_labels(self):
        self.assertAlmostEqual(fm.to_ppm(3.0, MU), 0.003)
        self.assertEqual(fm.to_ppm(2.5, "mg/kg"), 2.5)
        self.assertIsNone(fm.to_ppm(1.0, "ppm?"))
        self.assertEqual(fm.canon("3-AcetyldeoxyNivalenol"), "3-ADON")
        self.assertEqual(fm.canon("3-Acetyldeoxynivalenol"), "3-ADON")
        self.assertEqual(fm.canon(" Fumonisins (total B1 and B2) "), "FUM")
        self.assertIsNone(fm.canon("Ergot"))

    def test_parse_text_shapes(self):
        rows, check = parsed()
        self.assertEqual(check["header"], fm.COLUMNS)  # BOM stripped
        self.assertEqual(check["n_rows"], 20)
        self.assertEqual(check["distinct_samples"], 3)
        self.assertEqual(check["units"], {"mg/kg": 17, MU: 3})
        self.assertEqual(check["labels"]["3-AcetyldeoxyNivalenol"], 1)
        self.assertEqual(check["result_kinds"], {"numeric": 7, "censored": 13})
        self.assertEqual(check["unparsed"], 0)
        self.assertEqual(check["unknown_analyte"], 0)
        ota = [r for r in rows if r["analyte"] == "OTA" and r["sid"] == "S1"][0]
        self.assertAlmostEqual(ota["limit_ppm"], 0.002)


class TestTable1(unittest.TestCase):
    def test_transcription_is_self_consistent(self):
        # Every printed percentage must be k/n for some whole k (catches transcription slips).
        for year, cells in fm.TABLE1.items():
            for an, (pct, n) in cells.items():
                ok = any(fm.matches(100.0 * k / n, pct) for k in range(n + 1))
                self.assertTrue(ok, (year, an, pct, n))

    def test_sums_match_the_census(self):
        tot = {an: sum(fm.TABLE1[y][an][1] for y in fm.YEARS) for an in fm.REPORT_ORDER}
        self.assertEqual(tot["DON"], fm.LABELS["Deoxynivalenol"])
        self.assertEqual(tot["T-2"], fm.LABELS["T-2"])
        self.assertEqual(tot["DAS"], fm.LABELS["Diacetoxyscirpenol"])
        self.assertEqual(tot["FUM"], fm.LABELS["Fumonisins (total B1 and B2)"])
        self.assertEqual(tot["OTA"], fm.LABELS["Ochratoxin A"])
        self.assertEqual(tot["ZEA"], fm.LABELS["Zearalenone"])
        self.assertEqual(tot["HT-2"], 3202)
        self.assertEqual(fm.LABELS["HT-2"] - tot["HT-2"], 41)
        gap = {y: fm.TABLE1[y]["T-2"][1] - fm.TABLE1[y]["HT-2"][1] for y in fm.YEARS}
        self.assertEqual({y: g for y, g in gap.items() if g},
                         {"2010-2011": 2, "2011-2012": 15, "2012-2013": 11, "2013-2014": 13})

    def test_gate_constants(self):
        self.assertEqual(sum(fm.LABELS.values()), fm.N_ROWS)
        self.assertEqual(sum(fm.UNITS.values()), fm.N_ROWS)
        self.assertEqual(sum(fm.RESULT_KINDS.values()), fm.N_ROWS)
        self.assertEqual(len(fm.SHA256), 64)
        self.assertTrue(all(ch in "0123456789abcdef" for ch in fm.SHA256))
        self.assertEqual(set(fm.canon(k) for k in fm.LABELS), set(fm.ANALYTES))
        self.assertEqual(len(fm.YEARS), 18)
        self.assertEqual(set(fm.TABLE1), set(fm.YEARS))

    def test_cells_on_synthetic(self):
        rows, _ = parsed()
        cells = {(c["year"], c["analyte"]): c for c in fm.table1_cells(rows)}
        self.assertEqual(len(cells), 18 * 7)
        don = cells[("2000-2001", "DON")]
        self.assertEqual((don["file_n"], don["below"]), (2, 1))
        self.assertAlmostEqual(don["pct"], 50.0)
        self.assertFalse(don["n_match"])
        ht2 = cells[("2000-2001", "HT-2")]
        self.assertEqual((ht2["file_n"], ht2["below"], ht2["indeterminate"]), (2, 2, 1))
        self.assertAlmostEqual(ht2["pct_excl_indeterminate"], 100.0)
        self.assertEqual(cells[("2005-2006", "DON")]["file_n"], 0)
        self.assertIsNone(cells[("2005-2006", "DON")]["pct"])

    def test_below_rules(self):
        r = {"value": 1.0, "detected": True, "ppm": 1.0, "limit_ppm": None}
        self.assertFalse(fm.is_below(r, 1.0))
        self.assertTrue(fm.is_below(r, 1.0, inclusive=True))
        c = {"value": 0.0, "detected": False, "ppm": 0.0, "limit_ppm": 0.2}
        self.assertTrue(fm.is_below(c, 0.1))
        self.assertTrue(fm.is_indeterminate(c, 0.1))
        self.assertFalse(fm.is_indeterminate(c, 0.2))


class TestStats(unittest.TestCase):
    def test_fisher(self):
        self.assertAlmostEqual(fm.fisher_two_sided(5, 5, 5, 5), 1.0, places=9)
        self.assertLess(fm.fisher_two_sided(10, 0, 0, 10), 0.001)
        self.assertEqual(fm.fisher_two_sided(0, 0, 0, 0), 1.0)

    def test_odds_ratio(self):
        self.assertEqual(fm.odds_ratio(2, 1, 1, 2), (4.0, False))
        orr, corrected = fm.odds_ratio(1, 1, 0, 1)
        self.assertTrue(corrected)
        self.assertAlmostEqual(orr, (1.5 * 1.5) / (1.5 * 0.5))

    def test_cooccurrence(self):
        rows, _ = parsed()
        samples = fm.samples_of(rows)
        co = fm.cooccurrence(samples, "DON", "ZEA")
        self.assertEqual((co["both"], co["x_only"], co["y_only"], co["neither"]), (1, 1, 0, 1))
        self.assertAlmostEqual(co["odds_ratio"], 3.0)
        self.assertEqual(fm.cooccurrence(samples, "OTA", "DON")["n_pairs"], 2)

    def test_adon_split(self):
        rows, _ = parsed()
        samples = fm.samples_of(rows)
        reg = fm.adon_split(samples, lambda s: fm.region(s["province"]) or None)
        self.assertEqual(reg, {"East": [1, 0], "West": [1, 1]})
        cmp_ = fm.compare_shares(reg, "West", "East")
        self.assertEqual(cmp_["share"], [1.0, 0.0])

    def test_limits_and_corn(self):
        rows, _ = parsed()
        self.assertEqual(fm.modal_limit(rows, "DON", ("2000-2001",)), (0.1, 1))
        self.assertEqual(fm.modal_limit(rows, "DON", ("2017-2018",)), (None, 0))
        self.assertEqual(fm.limit_counts(rows, "HT-2", fm.YEARS), {0.1: 1, 0.2: 1, 0.05: 1})
        self.assertTrue(fm.is_corn("Dried corn distillers grains"))
        self.assertFalse(fm.is_corn("Barley"))
        self.assertEqual(fm.region("Manitoba"), "West")
        self.assertEqual(fm.region("Nova Scotia"), "East")


class TestGrade(unittest.TestCase):
    IDS = ["G", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "S1"] + [f"P{i}" for i in range(1, 13)]

    def test_gate_fails_on_synthetic(self):
        rows, check = parsed()
        preds, _, _, _ = fm.grade(rows, check, True)
        self.assertEqual([p["id"] for p in preds], self.IDS)
        self.assertFalse(preds[0]["met"])
        self.assertTrue(all(not p["graded"] and not p["met"] for p in preds[1:]))

    def test_grades_when_gate_open(self):
        rows, check = parsed()
        with mock.patch.object(fm, "gate", return_value=(True, {"ok": True})):
            preds, cells, samples, co = fm.grade(rows, check, True)
        met = {p["id"]: p["met"] for p in preds}
        graded = {p["id"]: p["graded"] for p in preds}
        self.assertTrue(met["G"])
        self.assertTrue(met["C7"])       # no aflatoxin detected
        self.assertTrue(met["S1"])       # every '<' has a number
        self.assertFalse(met["P6"])      # 1 sample each
        self.assertFalse(graded["P7"])   # too few acetyl-DON positives
        self.assertFalse(graded["P8"])
        self.assertFalse(graded["P9"])
        self.assertFalse(graded["P10"])
        self.assertFalse(met["C1"])

    def test_outputs(self):
        rows, check = parsed()
        with mock.patch.object(fm, "gate", return_value=(True, {"ok": True})):
            preds, cells, samples, co = fm.grade(rows, check, True)
        desc = fm.descriptive(rows, check, samples)
        self.assertEqual(desc["label_variant_3-AcetyldeoxyNivalenol_by_year"], {"2017-2018": 1})
        self.assertEqual(desc["don_at_or_above"][">=1 ppm"], 1)
        with tempfile.TemporaryDirectory() as tmp:
            fm.write_outputs(tmp, rows, preds, cells, samples, co, desc, {"x": "y"})
            for name in ("feed_myco_table1.csv", "feed_myco_samples.csv", "feed_myco_limits.csv",
                         "feed_myco_cooccurrence.json", "feed_myco_summary.json",
                         "feed_myco_grades.json"):
                self.assertTrue(os.path.exists(os.path.join(tmp, name)), name)
            with open(os.path.join(tmp, "feed_myco_samples.csv"), encoding="utf-8") as fh:
                lines = list(csv.reader(fh))
            self.assertEqual(len(lines), 4)  # header + 3 samples
            self.assertEqual(lines[0], fm.SAMPLE_FIELDS)
            with open(os.path.join(tmp, "feed_myco_table1.csv"), encoding="utf-8") as fh:
                self.assertEqual(len(list(csv.reader(fh))), 1 + 18 * 7)


if __name__ == "__main__":
    unittest.main()
