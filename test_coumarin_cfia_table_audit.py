# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
"""Offline tests for coumarin_cfia_table_audit 0.1.0 (no network, no CFIA values)."""
import csv
import json
import os
import tempfile
import unittest
from unittest import mock

import coumarin_cfia_table_audit as cta


def _r(product, ppm, unit="µg/g"):
    return {"product": product, "ppm": ppm, "unit_raw": unit}


FAKE_TABLES = {
    "X": {"report": "https://example.org/x",
          "rows": [("Row A", ("A",), 3, 2, "3", "6", "3"),
                   ("Row B", ("B", "B2"), 2, 2, "2", "4", "3")],
          "total": ("Grand total", 5, 4, "2", "6", "3.75")},
}
FAKE_ROWS = [_r("A", 0.0), _r("A", 3.0), _r("A", 6.0), _r("B", 2.0), _r("B2", 4.0)]


class TestMatching(unittest.TestCase):
    def test_decimals(self):
        self.assertEqual([cta.decimals(x) for x in ("4.7", "329", "17.80")], [1, 0, 2])

    def test_matches_at_printed_precision(self):
        self.assertTrue(cta.matches(301.938, "302"))
        self.assertFalse(cta.matches(356.219, "302"))
        self.assertTrue(cta.matches(4.74, "4.7"))
        self.assertFalse(cta.matches(4.76, "4.7"))
        self.assertTrue(cta.matches(17.5, "18"))
        self.assertFalse(cta.matches(None, "1"))

    def test_verdicts(self):
        self.assertEqual(cta.verdict(500.01, 495.67, "500"), "positives")
        self.assertEqual(cta.verdict(356.2, 301.94, "302"), "all-samples")
        self.assertEqual(cta.verdict(10.0, 10.0, "10"), "both")
        self.assertEqual(cta.verdict(1.0, 2.0, "5"), "neither")


class TestRows(unittest.TestCase):
    def test_row_stats(self):
        s = cta.row_stats([4.0, 0.0, 2.0, 0.0])
        self.assertEqual((s["n"], s["n_detected"], s["min_detected"], s["max"]), (4, 2, 2.0, 4.0))
        self.assertAlmostEqual(s["mean_positives"], 3.0)
        self.assertAlmostEqual(s["mean_all"], 1.5)

    def test_audit_survey(self):
        with mock.patch.object(cta, "TABLES", FAKE_TABLES):
            a = cta.audit_survey("X", FAKE_ROWS)
        rows = {r["row"]: r for r in a["rows"]}
        self.assertEqual(rows["Row A"]["verdict"], "all-samples")      # 9/3 = 3; 9/2 = 4.5
        self.assertEqual(rows["Row B"]["verdict"], "both")             # 2 of 2 detected
        self.assertEqual(rows["Grand total"]["verdict"], "positives")  # 15/4 = 3.75
        self.assertTrue(all(all(r["checks"].values()) for r in a["rows"]))
        self.assertEqual(a["unmapped_labels"], {})
        self.assertEqual(a["units"], {"ug/g": 5})

    def test_gate_catches_unmapped_unmeasured_and_units(self):
        with mock.patch.object(cta, "TABLES", FAKE_TABLES):
            ok, _ = cta.gate({"X": cta.audit_survey("X", FAKE_ROWS)})
            self.assertTrue(ok)
            ok, chk = cta.gate({"X": cta.audit_survey("X", FAKE_ROWS + [_r("C", 1.0)])})
            self.assertFalse(ok)
            self.assertFalse(chk["X"]["all_labels_mapped"])
            ok, chk = cta.gate({"X": cta.audit_survey("X", FAKE_ROWS + [_r("A", None)])})
            self.assertFalse(chk["X"]["no_unmeasured"])
            bad = FAKE_ROWS[:-1] + [_r("B2", 4.0, "µg/kg")]
            ok, chk = cta.gate({"X": cta.audit_survey("X", bad)})
            self.assertFalse(chk["X"]["units"])


def _fake_audits(flip=None):
    """Audits for the real TABLES whose verdicts equal every prediction (or flip one)."""
    want = {(lab, name): v for _, lab, name, v in cta.PREDICTIONS}
    audits = {}
    for label, spec in cta.TABLES.items():
        names = [r[0] for r in spec["rows"]] + [spec["total"][0]]
        rows = []
        for name in names:
            v = want.get((label, name), "both")
            if flip == (label, name):
                v = "neither"
            rows.append({"row": name, "verdict": v, "checks": {"n": True}, "n_unmeasured": 0,
                         "cfia": {"average": "1"}, "mean_positives": 1.0, "mean_all": 1.0})
        n = spec["total"][1]
        audits[label] = {"rows": rows, "unmapped_labels": {}, "n_file_rows": n,
                         "units": {"ug/g": n}}
    return audits


class TestGrade(unittest.TestCase):
    def test_all_met(self):
        preds = cta.grade(_fake_audits())
        self.assertEqual([p["id"] for p in preds], ["A0"] + ["Q%d" % i for i in range(1, 9)])
        self.assertTrue(all(p["met"] for p in preds))

    def test_one_flip(self):
        preds = {p["id"]: p for p in cta.grade(_fake_audits(flip=("2015-16", "Baked goods")))}
        self.assertFalse(preds["Q7"]["met"])
        self.assertEqual(sum(1 for p in preds.values() if p["met"]), 8)

    def test_gate_blocks(self):
        a = _fake_audits()
        a["2014-15"]["unmapped_labels"] = {"Other": 1}
        preds = cta.grade(a)
        self.assertFalse(preds[0]["met"])
        self.assertTrue(all(not p["met"] and not p["graded"] for p in preds[1:]))

    def test_descriptive_rows(self):
        d = cta.descriptive(_fake_audits())
        self.assertEqual(sorted((x["survey"], x["row"]) for x in d),
                         [("2014-15", "Tea"), ("2015-16", "Ground cinnamon"), ("2015-16", "Tea")])


class TestPinned(unittest.TestCase):
    def test_rows_sum_to_cfia_totals(self):
        for label, spec in cta.TABLES.items():
            _, n, n_det, *_ = spec["total"]
            self.assertEqual(sum(r[2] for r in spec["rows"]), n, label)
            self.assertEqual(sum(r[3] for r in spec["rows"]), n_det, label)
        self.assertEqual(cta.TABLES["2014-15"]["total"][1:3], (739, 462))
        self.assertEqual(cta.TABLES["2015-16"]["total"][1:3], (747, 670))

    def test_headline_arithmetic_behind_the_predictions(self):
        # 2014-15: if every row average is an all-sample mean, the all-sample grand mean is
        # sum(n * avg) / 739 = 148.9 -> "149"; the positives reading gives 186.5 instead.
        rows = cta.TABLES["2014-15"]["rows"]
        all_mean = sum(r[2] * float(r[6]) for r in rows) / 739
        pos_mean = sum(r[3] * float(r[6]) for r in rows) / 462
        self.assertTrue(cta.matches(all_mean, "149"))
        self.assertFalse(cta.matches(pos_mean, "149"))
        # 2015-16: the positives reading gives sum(n_det * avg) / 670 = 391.8 -> "392"; the
        # all-sample reading gives 387.8.
        rows = cta.TABLES["2015-16"]["rows"]
        pos_mean = sum(r[3] * float(r[6]) for r in rows) / 670
        all_mean = sum(r[2] * float(r[6]) for r in rows) / 747
        self.assertTrue(cta.matches(pos_mean, "392"))
        self.assertFalse(cta.matches(all_mean, "392"))

    def test_tea_rows_use_the_replication_labels(self):
        for label in cta.SURVEYS:
            tea = [r for r in cta.TABLES[label]["rows"] if r[0] == "Tea"][0]
            self.assertEqual(tea[1], cta.ctr.TEA_TYPES)


class TestOutputs(unittest.TestCase):
    def test_write_outputs(self):
        with mock.patch.object(cta, "TABLES", FAKE_TABLES), \
                mock.patch.object(cta, "SURVEYS", ("X",)), \
                mock.patch.object(cta, "PREDICTIONS", (("Q1", "X", "Row A", "all-samples"),)), \
                mock.patch.object(cta, "NOT_GRADED", {("X", "Row B"): "both"}):
            audits = {"X": cta.audit_survey("X", FAKE_ROWS)}
            preds = cta.grade(audits)
            with tempfile.TemporaryDirectory() as d:
                res = cta.write_outputs(d, audits, preds, {"provenance": {}})
                with open(os.path.join(d, "coumarin_cfia_table_audit.csv"),
                          encoding="utf-8") as fh:
                    table = list(csv.reader(fh))
                with open(os.path.join(d, "audit_grades.json"), encoding="utf-8") as fh:
                    grades = json.load(fh)
        self.assertEqual(table[0], cta.TABLE_FIELDS)
        self.assertEqual(len(table) - 1, 3)
        self.assertEqual(table[1][:2], ["X", "Row A"])
        self.assertEqual(table[1][-1], "all-samples")
        self.assertEqual(res["n_met"], 2)
        self.assertEqual([p["id"] for p in grades["predictions"]], ["A0", "Q1"])


if __name__ == "__main__":
    unittest.main()
