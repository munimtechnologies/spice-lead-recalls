#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/myco-don-0.1.0-result.md.

Re-derives every 2010-11 figure and the OTA x DON co-occurrence from the committed per-sample
table data/myco_don_2010_samples.csv, independently recomputes the odds ratio and the Fisher
exact p-value, and checks them against the result note and data/myco_don_cooccurrence.json. The
infant (2018-19) and 2011-12 headline values that need the other two SHA-pinned files are read
from the sealed grader record data/myco_don_summary.json. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import math
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "myco_don_2010_samples.csv")
COOC = os.path.join(DATA, "myco_don_cooccurrence.json")
SUMMARY = os.path.join(DATA, "myco_don_summary.json")

DON = "Deoxynivalenol"
OTA = "Ochratoxin A"
WINE = ("Wine",)
DRIED_FRUIT_2010 = ("Raisin", "Fig", "Date", "Apricot", "Prune")
INFANT_CEREAL = "Infant Food - Cereal"
GRAINLIKE_2010 = ("Cereal - Adult", "Cereal - Children", "Infant Food - Cereal", "Flour - Wheat",
                  "Flour - Corn", "Bran - Wheat", "Bran - Oat", "Wheat Products", "Grain - Oat",
                  "Cornmeal", "Chips - Corn", "Oatmeal")
HC_INFANT, HC_BRAN, HC_GRAIN = 0.5, 7.0, 3.0
ND_TOKENS = ("nd", "n.d.", "n/d", "not detected", "non détecté", "non detecte")


def parse_result(raw):
    """(ppb, detected) under the registered non-detect rule (blank / '<' / token / 0 = non-detect)."""
    s = (raw or "").strip()
    if not s or s.startswith("<") or s.lower() in ND_TOKENS:
        return 0.0, False
    v = float(s)
    if v == 0:
        return 0.0, False
    return v, True


def hc_limit(product):
    if product == INFANT_CEREAL:
        return HC_INFANT
    if product == "Bran - Wheat":
        return HC_BRAN
    return HC_GRAIN


def _logfact(n):
    return math.lgamma(n + 1)


def _hyper_logp(a, b, c, d):
    r1, r2, c1, c2, n = a + b, c + d, a + c, b + d, a + b + c + d
    return (_logfact(r1) + _logfact(r2) + _logfact(c1) + _logfact(c2)
            - _logfact(n) - _logfact(a) - _logfact(b) - _logfact(c) - _logfact(d))


def fisher_two_sided(a, b, c, d):
    r1, c1, n = a + b, a + c, a + b + c + d
    if n == 0:
        return 1.0
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)
    p_obs = _hyper_logp(a, b, c, d)
    total = 0.0
    for x in range(lo, hi + 1):
        bb, cc, dd = r1 - x, c1 - x, (n - r1) - (c1 - x)
        logp = _hyper_logp(x, bb, cc, dd)
        if logp <= p_obs + 1e-9:
            total += math.exp(logp)
    return min(1.0, total)


def load_samples():
    with open(SAMPLES, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def don(rows):
    return [r for r in rows if r["component"] == DON]


def ota(rows):
    return [r for r in rows if r["component"] == OTA]


def n_det(rows):
    return sum(1 for r in rows if r["_det"])


def min_det(rows):
    vals = [r["_ppb"] for r in rows if r["_det"]]
    return min(vals) if vals else None


def max_val(rows):
    vals = [r["_ppb"] for r in rows if r["_ppb"] is not None]
    return max(vals) if vals else None


class TestSamplesTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_samples()
        for r in cls.rows:
            ppb, det = parse_result(r["result_raw"])
            r["_ppb"], r["_det"] = ppb, det

    def test_shape(self):
        self.assertEqual(len(self.rows), 1886)
        self.assertEqual(len({r["sample"] for r in self.rows}), 943)
        comps = {}
        for r in self.rows:
            comps[r["component"]] = comps.get(r["component"], 0) + 1
        self.assertEqual(comps, {DON: 943, OTA: 943})

    def test_detection_flag_matches_raw(self):
        # The published 'detected' column must equal detection re-derived from the raw result cell.
        for r in self.rows:
            self.assertEqual(int(r["detected"]), int(r["_det"]), msg=r["sample"] + " " + r["component"])

    def test_format_literal_zero(self):
        # Non-detects are a literal 0 (no '<', no token): every DON/OTA raw cell is a plain number.
        for r in self.rows:
            s = r["result_raw"].strip()
            self.assertFalse(s.startswith("<"))
            self.assertNotIn(s.lower(), ND_TOKENS)
            float(s)  # raises if not a bare number


class TestDon2010(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = TestSamplesTable.rows if hasattr(TestSamplesTable, "rows") else None
        if cls.rows is None:
            cls.rows = load_samples()
            for r in cls.rows:
                ppb, det = parse_result(r["result_raw"])
                r["_ppb"], r["_det"] = ppb, det
        cls.don = don(cls.rows)

    def test_p5_detected_555(self):
        self.assertEqual(n_det(self.don), 555)

    def test_p6_range(self):
        self.assertAlmostEqual(min_det(self.don), 1.0, places=4)
        self.assertEqual(max_val(self.don), 2060.0)

    def test_p7_wine_and_dried_fruit_clean(self):
        wine = [r for r in self.don if r["product"] in WINE]
        dried = [r for r in self.don if r["product"] in DRIED_FRUIT_2010]
        self.assertEqual(len(wine), 139)
        self.assertEqual(len(dried), 97)
        self.assertEqual(n_det(wine), 0)
        self.assertEqual(n_det(dried), 0)

    def test_p8_infant_cereals(self):
        ic = [r for r in self.don if r["product"] == INFANT_CEREAL]
        self.assertEqual(len(ic), 93)
        self.assertEqual(n_det(ic), 76)
        self.assertEqual(max_val(ic), 128.0)
        self.assertAlmostEqual(min_det(ic), 1.1, places=4)


class TestOta2010(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_samples()
        for r in cls.rows:
            ppb, det = parse_result(r["result_raw"])
            r["_ppb"], r["_det"] = ppb, det
        cls.ota = ota(cls.rows)

    def test_p9_detected_range(self):
        self.assertEqual(n_det(self.ota), 315)
        self.assertAlmostEqual(min_det(self.ota), 0.040, places=4)
        self.assertAlmostEqual(max_val(self.ota), 6.773, places=4)

    def test_p10_over_health_canada(self):
        grain = [r for r in self.ota if r["product"] in GRAINLIKE_2010]
        over = [r for r in grain if r["_det"] and r["_ppb"] > hc_limit(r["product"])]
        self.assertEqual(len(over), 8)
        self.assertEqual(sum(1 for r in over if r["product"] == INFANT_CEREAL), 5)


class TestCooccurrence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = load_samples()
        for r in rows:
            ppb, det = parse_result(r["result_raw"])
            r["_ppb"], r["_det"] = ppb, det
        by = {}
        for r in rows:
            s = by.setdefault(r["sample"], {})
            if r["component"] == OTA:
                s["ota"] = r["_det"]
            elif r["component"] == DON:
                s["don"] = r["_det"]
        a = b = c = d = paired = 0
        for s in by.values():
            if "ota" not in s or "don" not in s:
                continue
            paired += 1
            if s["ota"] and s["don"]:
                a += 1
            elif s["ota"]:
                b += 1
            elif s["don"]:
                c += 1
            else:
                d += 1
        cls.a, cls.b, cls.c, cls.d, cls.paired = a, b, c, d, paired
        with open(COOC, encoding="utf-8") as fh:
            cls.committed = json.load(fh)

    def test_table(self):
        self.assertEqual((self.a, self.b, self.c, self.d), (275, 40, 280, 348))
        self.assertEqual(self.paired, 943)
        self.assertEqual(self.committed["both"], self.a)
        self.assertEqual(self.committed["ota_only"], self.b)
        self.assertEqual(self.committed["don_only"], self.c)
        self.assertEqual(self.committed["neither"], self.d)
        self.assertEqual(self.committed["n_pairs"], self.paired)

    def test_odds_ratio(self):
        orr = (self.a * self.d) / (self.b * self.c)
        self.assertAlmostEqual(orr, 8.544642857142858, places=9)
        self.assertAlmostEqual(self.committed["odds_ratio"], orr, places=9)
        self.assertFalse(self.committed["haldane_corrected"])
        # Registered independence band [0.5, 2.0] is refuted (P11, the miss).
        self.assertGreater(orr, 2.0)

    def test_fisher_p(self):
        p = fisher_two_sided(self.a, self.b, self.c, self.d)
        self.assertTrue(math.isclose(p, self.committed["fisher_p"], rel_tol=1e-9))
        self.assertLess(p, 1e-30)


class TestSealedRecord(unittest.TestCase):
    """Infant (2018-19) and 2011-12 headlines, read from the sealed grader output."""

    @classmethod
    def setUpClass(cls):
        with open(SUMMARY, encoding="utf-8") as fh:
            cls.s = json.load(fh)
        cls.p = {pr["id"]: pr for pr in cls.s["predictions"]}

    def test_gate_and_tally(self):
        self.assertEqual(self.s["n_met"], 12)
        self.assertTrue(self.p["G"]["met"])
        for f in ("infant", "don2011", "otadon2010"):
            self.assertTrue(self.p["G"]["observed"][f]["met"])

    def test_p1_settles_contradiction(self):
        obs = self.p["P1"]["observed"]
        self.assertEqual(obs["n_detected"], 119)
        self.assertEqual(obs["n_at_or_above_20"], 13)
        self.assertTrue(self.p["P1"]["met"])

    def test_p3_report_error(self):
        obs = self.p["P3"]["observed"]
        self.assertAlmostEqual(obs["smallest_at_or_above_20"], 22.3, places=4)
        self.assertEqual(obs["text_min"], 44.1)
        self.assertTrue(self.p["P3"]["met"])

    def test_p11_is_the_miss(self):
        self.assertFalse(self.p["P11"]["met"])

    def test_p12_2011(self):
        obs = self.p["P12"]["observed"]
        self.assertEqual(obs["nd_share"], 37)
        self.assertEqual(obs["max"], 2460.0)
        self.assertEqual(obs["dried_fruit_detected"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
