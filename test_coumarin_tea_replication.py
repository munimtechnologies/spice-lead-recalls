# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
"""Offline tests for coumarin_tea_replication 0.1.1 (no network, no CFIA values)."""
import csv
import hashlib
import json
import os
import tempfile
import unittest
from unittest import mock

import coumarin_eu_limits as cel
import coumarin_tea_replication as ctr

HEADER = ("Sample No. – No. d’échantillon,Region - Région,Function,Fonction,Origin,Origine,"
          "Product,Produit,Date Sampled – Date d’échantillonage,Type of Test,Type d’analyse,"
          "Component,Composant,Result - Résultat,Unit - Unité,Plan Code - Code du régime")


def _row(sid, product, result):
    return (f"{sid},Ontario,Retail,Détail,Canada,Canada,{product},Produit,2015-09-01,Chem,Chim,"
            f"Coumarin,Coumarine,{result},µg/g,2015_TS020")


# cp1252 fixture with the 2014-15/2015-16 header (en dash, curly apostrophe, micro sign).
FIXTURE = "\r\n".join([
    HEADER,
    _row("S1", "Tea - Herbal", "0"),
    _row("S2", "Tea - Black", "1600.0"),
    _row("S3", "Tea - Herbal", "800.0"),
    _row("S4", "Sauce - Steak", "12.5"),
    _row("S5", "Tea - Green", "400.0"),
]).encode("cp1252")


def _rows():
    return cel.parse_rows(FIXTURE)


def _fake(label, a2, c1, c2, medians=None, units=None, n_rows=None):
    g = ctr.GATE[label]
    n = g["n_tea"]
    scen = {"A1": 0, "A2": a2, "C1": c1, "C2": c2}
    mean_key, bounds = g["mean"]
    tea = {"n": n, "n_detected": g["detected"][0], "ppm_max": sum(g["tea_max"]) / 2,
           "ppm_mean": -1.0, "ppm_mean_detected": -1.0}
    tea[mean_key] = sum(bounds) / 2
    return {
        "n_rows": n_rows if n_rows is not None else g["n_rows"][1],
        "tea_rows": n,
        "tea_types": dict(sorted(g["types"].items())),
        "tea_units": units if units is not None else {"ug/g": n},
        "tea": tea,
        "scenarios": {s: {"n_over_tdi": k, "share_over_tdi": k / n} for s, k in scen.items()},
        "by_type": {t: {"ppm_median": m} for t, m in (medians or {}).items()},
    }


GOOD_MEDIANS = {"Tea - Herbal": 300.0, "Tea - Black": 250.0, "Tea - Green": 10.0,
                "Tea - Oolong": 5.0, "Tea - White": 4.0, "Tea - Other": 100.0}


def _good():
    return {"2014-15": _fake("2014-15", 3, 21, 50),
            "2015-16": _fake("2015-16", 10, 60, 90, GOOD_MEDIANS)}


class TestParseFixture(unittest.TestCase):
    def test_cp1252_header_and_micro_unit(self):
        rows = _rows()
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]["product"], "Tea - Herbal")
        self.assertEqual(rows[0]["ppm"], 0.0)            # "0" is CFIA's non-detect
        self.assertEqual(rows[1]["ppm"], 1600.0)
        self.assertEqual(cel.norm_unit(rows[1]["unit_raw"]), "ug/g")
        self.assertEqual(rows[1]["origin"], "Canada")
        self.assertEqual(rows[1]["region"], "Ontario")

    def test_exact_label_selection_excludes_steak(self):
        rows = _rows()
        self.assertEqual([r["product"] for r in ctr.tea_rows(rows)],
                         ["Tea - Herbal", "Tea - Black", "Tea - Herbal", "Tea - Green"])
        s = ctr.summarise_survey(rows)
        self.assertEqual(s["tea_rows"], 4)
        self.assertEqual(s["classify_tea_rows"], 5)      # substring rule would take the sauce


class TestSummary(unittest.TestCase):
    def setUp(self):
        self.s = ctr.summarise_survey(_rows())

    def test_counts_and_units(self):
        self.assertEqual(self.s["n_rows"], 5)
        self.assertEqual(self.s["tea_units"], {"ug/g": 4})
        self.assertEqual(self.s["tea_types"],
                         {"Tea - Black": 1, "Tea - Green": 1, "Tea - Herbal": 2})
        t = self.s["tea"]
        self.assertEqual((t["n"], t["n_detected"]), (4, 3))
        self.assertAlmostEqual(t["ppm_median"], 600.0)
        self.assertAlmostEqual(t["ppm_mean"], 2800.0 / 4)
        self.assertAlmostEqual(t["ppm_mean_detected"], 2800.0 / 3)
        self.assertEqual(t["ppm_max"], 1600.0)

    def test_scenarios_use_published_thresholds(self):
        sc = self.s["scenarios"]
        self.assertAlmostEqual(sc["A1"]["threshold_ppm"], 3000.0)
        self.assertAlmostEqual(sc["A2"]["threshold_ppm"], 1500.0)
        self.assertAlmostEqual(sc["C1"]["threshold_ppm"], 750.0)
        self.assertAlmostEqual(sc["C2"]["threshold_ppm"], 375.0)
        self.assertEqual([sc[k]["n_over_tdi"] for k in ctr.SIDS], [0, 1, 2, 3])
        self.assertAlmostEqual(sc["C1"]["share_over_tdi"], 0.5)
        self.assertAlmostEqual(sc["A2"]["max_pct_budget"], 100.0 * 1600 * 0.004 / 6.0)

    def test_by_type(self):
        bt = self.s["by_type"]
        self.assertEqual(sorted(bt), ["Tea - Black", "Tea - Green", "Tea - Herbal"])
        self.assertAlmostEqual(bt["Tea - Herbal"]["ppm_median"], 400.0)
        self.assertEqual(bt["Tea - Herbal"]["scenarios"]["C1"]["n_over_tdi"], 1)

    def test_pooled(self):
        rows = _rows()
        p = ctr.pooled({"x": rows, "y": rows})
        self.assertEqual(p["tea"]["n"], 8)
        self.assertEqual(p["scenarios"]["C2"]["n_over_tdi"], 6)


class TestGrade(unittest.TestCase):
    def test_all_met(self):
        preds = ctr.grade(_good())
        self.assertEqual([p["id"] for p in preds],
                         ["G0"] + ["P%d" % i for i in range(1, 11)])
        self.assertTrue(all(p["met"] for p in preds), [p["id"] for p in preds if not p["met"]])
        self.assertTrue(all(p["blind"] is False for p in preds[1:]))

    def test_gate_failure_blocks_every_prediction(self):
        s = _good()
        s["2015-16"]["tea_units"] = {"ug/kg": 297}
        preds = ctr.grade(s)
        self.assertFalse(preds[0]["met"])
        self.assertFalse(preds[0]["observed"]["2015-16"]["checks"]["tea_units"])
        self.assertTrue(all(not p["met"] and not p["graded"] for p in preds[1:]))

    def test_gate_row_and_type_checks(self):
        s = _good()
        s["2014-15"]["n_rows"] = 729
        self.assertFalse(ctr.gate_survey("2014-15", s["2014-15"])[0])
        s = _good()
        s["2015-16"]["tea_types"] = dict(s["2015-16"]["tea_types"], **{"Tea - Black": 80})
        self.assertFalse(ctr.gate_survey("2015-16", s["2015-16"])[0])

    def test_amended_mean_check(self):
        # 0.1.1: 2014-15 compares CFIA's 302 with the all-sample mean, 2015-16 with positives.
        self.assertEqual(ctr.GATE["2014-15"]["mean"], ("ppm_mean", (285.0, 320.0)))
        self.assertEqual(ctr.GATE["2015-16"]["mean"], ("ppm_mean_detected", (420.0, 465.0)))
        s = _good()
        s["2014-15"]["tea"].update(ppm_mean=301.9, ppm_mean_detected=356.2)
        ok, chk = ctr.gate_survey("2014-15", s["2014-15"])
        self.assertTrue(ok and chk["mean"])
        s["2014-15"]["tea"].update(ppm_mean=356.2, ppm_mean_detected=301.9)
        self.assertFalse(ctr.gate_survey("2014-15", s["2014-15"])[1]["mean"])
        s["2015-16"]["tea"].update(ppm_mean=364.3, ppm_mean_detected=441.6)
        self.assertTrue(ctr.gate_survey("2015-16", s["2015-16"])[1]["mean"])
        s["2015-16"]["tea"].update(ppm_mean=441.6, ppm_mean_detected=500.0)
        self.assertFalse(ctr.gate_survey("2015-16", s["2015-16"])[1]["mean"])

    def test_primary_needs_both_surveys_below_2013(self):
        s = _good()
        s["2015-16"] = _fake("2015-16", 10, 86, 90, GOOD_MEDIANS)   # 86/297 = 0.2896
        p = {x["id"]: x for x in ctr.grade(s)}
        self.assertFalse(p["P2"]["met"])
        self.assertTrue(p["P4"]["met"])

    def test_herbal_tie_is_not_met(self):
        s = _good()
        s["2015-16"]["by_type"]["Tea - Black"]["ppm_median"] = 300.0
        p = {x["id"]: x for x in ctr.grade(s)}
        self.assertFalse(p["P10"]["met"])

    def test_direction_p9(self):
        s = _good()
        s["2014-15"] = _fake("2014-15", 3, 43, 50)                   # 43/210 = 0.2048
        p = {x["id"]: x for x in ctr.grade(s)}
        self.assertFalse(p["P9"]["met"])                             # 60/297 = 0.2020

    def test_range_edges(self):
        s = _good()
        s["2014-15"] = _fake("2014-15", 0, 21, 50)
        p = {x["id"]: x for x in ctr.grade(s)}
        self.assertFalse(p["P7"]["met"])
        s["2015-16"] = _fake("2015-16", 1, 60, 90, GOOD_MEDIANS)
        p = {x["id"]: x for x in ctr.grade(s)}
        self.assertFalse(p["P8"]["met"])

    def test_reproduction_check(self):
        s = {"tea": {"n": 115}, "scenarios": {"A1": {"n_over_tdi": 0}, "A2": {"n_over_tdi": 7},
                                              "C1": {"n_over_tdi": 33}, "C2": {"n_over_tdi": 45}}}
        self.assertTrue(ctr.reproduction_check(s)["match"])
        s["scenarios"]["C1"]["n_over_tdi"] = 32
        self.assertFalse(ctr.reproduction_check(s)["match"])


class TestPinned(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(ctr.VERSION, "0.1.1")
        self.assertIn("verification", ctr.GRADING_STATUS)
        for label, spec in ctr.SURVEYS.items():
            self.assertEqual(len(spec["sha256"]), 64)
            int(spec["sha256"], 16)
            self.assertIn(spec["resource"], spec["fallback"])
            self.assertIn(spec["dataset"], spec["fallback"])
            g = ctr.GATE[label]
            self.assertEqual(sum(g["types"].values()), g["n_tea"])
            self.assertEqual(set(g["types"]), set(ctr.TEA_TYPES))
        self.assertEqual(ctr.REF_1314, {"n": 115, "A1": 0, "A2": 7, "C1": 33, "C2": 45})
        self.assertEqual(ctr.ct.SCENARIOS["C1"], (15.0, 2.0, 1.0))
        # The predictions are the 0.1.0 ones, unchanged by the amendment.
        self.assertEqual((ctr.P3_C1_1415, ctr.P4_C1_1516, ctr.P5_C2_1415, ctr.P6_C2_1516,
                          ctr.P7_A2_1415_N, ctr.P8_A2_1516_N),
                         ((0.04, 0.22), (0.10, 0.32), (0.12, 0.40), (0.18, 0.45), (1, 12),
                          (2, 30)))


class TestUrls(unittest.TestCase):
    def test_candidate_order(self):
        got = ctr.candidate_urls("https://open.canada.ca/data/x.csv",
                                 "https://open.canada.ca/data/y.csv")
        self.assertEqual(got, ["https://open.canada.ca/data/x.csv",
                               "https://ouvert.canada.ca/data/x.csv",
                               "https://open.canada.ca/data/y.csv",
                               "https://ouvert.canada.ca/data/y.csv"])

    def test_relative_none_and_http(self):
        self.assertEqual(ctr.candidate_urls("/data/x.csv", None),
                         ["https://ouvert.canada.ca/data/x.csv",
                          "https://open.canada.ca/data/x.csv"])
        self.assertEqual(ctr.candidate_urls(None, "https://ouvert.canada.ca/a"),
                         ["https://ouvert.canada.ca/a", "https://open.canada.ca/a"])
        self.assertEqual(ctr.candidate_urls("http://example.org/a", None), [])
        self.assertIsNone(ctr.swap_host(None))


class TestLoad(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.sha = hashlib.sha256(FIXTURE).hexdigest()

    def tearDown(self):
        self.tmp.cleanup()

    def test_data_volume_copy(self):
        with open(os.path.join(self.dir, "cfia-2015-16-coumarin.csv"), "wb") as fh:
            fh.write(FIXTURE)
        with mock.patch.dict(ctr.SURVEYS["2015-16"], {"sha256": self.sha}), \
                mock.patch.object(ctr.cel, "_fetch", side_effect=AssertionError("no network")):
            raw, path, source = ctr.load_survey("2015-16", self.dir)
        self.assertEqual((raw, source), (FIXTURE, "data-volume"))

    def test_download_verified_and_saved(self):
        with mock.patch.dict(ctr.SURVEYS["2015-16"], {"sha256": self.sha}), \
                mock.patch.object(ctr.cel, "_fetch", return_value=FIXTURE):
            raw, path, source = ctr.load_survey("2015-16", self.dir)
        self.assertEqual(raw, FIXTURE)
        self.assertTrue(source.startswith("https://"))
        with open(os.path.join(self.dir, "cfia-2015-16-coumarin.csv"), "rb") as fh:
            self.assertEqual(fh.read(), FIXTURE)

    def test_sha_mismatch_refuses(self):
        with open(os.path.join(self.dir, "cfia-2014-15-coumarin.csv"), "wb") as fh:
            fh.write(FIXTURE)                                   # wrong digest for 2014-15
        with mock.patch.object(ctr.cel, "_fetch", return_value=b"tampered"):
            with self.assertRaises(RuntimeError):
                ctr.load_survey("2014-15", self.dir)

    def test_offline_refuses(self):
        with mock.patch.object(ctr.cel, "_fetch", side_effect=OSError("offline")):
            with self.assertRaises(RuntimeError):
                ctr.load_survey("2014-15", self.dir)


class TestOutputs(unittest.TestCase):
    def test_write_outputs(self):
        rows = _rows()
        by = {k: rows for k in ctr.ALL}
        summ = {k: ctr.summarise_survey(rows) for k in ctr.ALL}
        preds = ctr.grade(summ)
        with tempfile.TemporaryDirectory() as d:
            res = ctr.write_outputs(d, by, summ, preds, {"provenance": {}})
            with open(os.path.join(d, "coumarin_tea_replication_samples.csv"),
                      encoding="utf-8") as fh:
                table = list(csv.reader(fh))
            self.assertEqual(table[0], ctr.SAMPLE_FIELDS)
            self.assertEqual(len(table) - 1, 12)
            self.assertEqual(table[1][:2], ["2013-14", "Tea - Black"])
            self.assertEqual(table[1][-1], "ug/g")
            with open(os.path.join(d, "coumarin_tea_replication_by_type.csv"),
                      encoding="utf-8") as fh:
                self.assertEqual(len(list(csv.reader(fh))) - 1, 9)
            with open(os.path.join(d, "summary.json"), encoding="utf-8") as fh:
                got = json.load(fh)
            self.assertEqual(got["n_predictions"], 11)
            self.assertEqual(got["version"], "0.1.1")
            with open(os.path.join(d, "grades.json"), encoding="utf-8") as fh:
                self.assertIn("verification", json.load(fh)["grading_status"])
        self.assertEqual(res["n_met"], 0)                       # fixture fails the gate


if __name__ == "__main__":
    unittest.main()
