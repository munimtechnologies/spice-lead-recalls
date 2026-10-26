#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/feed-myco-0.1.0-result.md.

Rebuilds the Table 1 checks (C1-C6) and the fumonisin 2016-17 reconciliation from the committed
data/feed_myco_table1.csv, the limit findings (P10, P11, C5's mechanism, the method-change table)
from data/feed_myco_limits.csv, and the co-occurrence and chemotype tables (P3-P8) with their
odds ratios and Fisher exact p-values from the per-sample table data/feed_myco_samples.csv,
checking each against the note and data/feed_myco_cooccurrence.json. Row-level figures (P1, P2,
P9, P12) and the per-year detection counts are read from the sealed grader record
data/feed_myco_summary.json. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import math
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
TABLE1 = os.path.join(DATA, "feed_myco_table1.csv")
SAMPLES = os.path.join(DATA, "feed_myco_samples.csv")
LIMITS = os.path.join(DATA, "feed_myco_limits.csv")
COOC = os.path.join(DATA, "feed_myco_cooccurrence.json")
SUMMARY = os.path.join(DATA, "feed_myco_summary.json")

YEARS = tuple(f"{y}-{y + 1}" for y in range(2000, 2018))
EARLY, LATE = YEARS[:9], YEARS[9:]
SIX = ("DON", "T-2", "DAS", "FUM", "OTA", "ZEA")
FIVE = ("T-2", "DAS", "FUM", "OTA", "ZEA")
HT2_GAP = {"2010-2011": 2, "2011-2012": 15, "2012-2013": 11, "2013-2014": 13}


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def matches(x, printed):
    """Does x round to the printed figure at the printed precision?"""
    d = len(printed.split(".")[1]) if "." in printed else 0
    return abs(x - float(printed)) <= 0.5 * 10 ** (-d) + 1e-9


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


def modal(counts):
    """Most common limit (ties -> the smaller)."""
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


class TestTable1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_csv(TABLE1)
        cls.by = {(r["year"], r["analyte"]): r for r in cls.rows}

    @staticmethod
    def pct(r):
        return 100.0 * int(r["below"]) / int(r["file_n"])

    def test_shape(self):
        self.assertEqual(len(self.rows), 126)
        self.assertEqual({r["year"] for r in self.rows}, set(YEARS))
        self.assertEqual({r["analyte"] for r in self.rows},
                         {"DON", "HT-2", "T-2", "DAS", "FUM", "OTA", "ZEA"})

    def test_pct_column_is_below_over_n(self):
        for r in self.rows:
            self.assertGreater(int(r["file_n"]), 0)
            self.assertLess(abs(float(r["pct"]) - self.pct(r)), 1e-5, msg=r["year"] + r["analyte"])

    def test_c1_counts(self):
        six = [r for r in self.rows if r["analyte"] in SIX]
        self.assertEqual(len(six), 108)
        ok = [r for r in six if int(r["file_n"]) == int(r["printed_n"])]
        self.assertEqual(len(ok), 107)
        misses = [(r["year"], r["analyte"], int(r["file_n"]), int(r["printed_n"]))
                  for r in six if int(r["file_n"]) != int(r["printed_n"])]
        self.assertEqual(misses, [("2016-2017", "FUM", 163, 164)])

    def test_c3_don(self):
        don = [r for r in self.rows if r["analyte"] == "DON"]
        ok = [r for r in don if int(r["file_n"]) == int(r["printed_n"])
              and matches(self.pct(r), r["printed_pct"])]
        self.assertEqual(len(ok), 18)

    def test_c4_five(self):
        five = [r for r in self.rows if r["analyte"] in FIVE]
        self.assertEqual(len(five), 90)
        bad = [(r["year"], r["analyte"]) for r in five
               if not (int(r["file_n"]) == int(r["printed_n"])
                       and matches(self.pct(r), r["printed_pct"]))]
        self.assertEqual(bad, [("2016-2017", "FUM")])

    def test_c5_ht2_gap_is_indeterminate(self):
        gaps = {}
        for y in YEARS:
            r = self.by[(y, "HT-2")]
            gap = int(r["file_n"]) - int(r["printed_n"])
            self.assertEqual(int(r["indeterminate"]), gap, msg=y)
            if gap:
                gaps[y] = gap
        self.assertEqual(gaps, HT2_GAP)
        self.assertEqual(sum(gaps.values()), 41)

    def test_c6_ht2_after_exclusion(self):
        ok = 0
        for y in YEARS:
            r = self.by[(y, "HT-2")]
            indet = int(r["indeterminate"])
            n_ex = int(r["file_n"]) - indet
            pct_ex = 100.0 * (int(r["below"]) - indet) / n_ex
            if n_ex == int(r["printed_n"]) and matches(pct_ex, r["printed_pct"]):
                ok += 1
        self.assertEqual(ok, 18)

    def test_fumonisin_blank_year_row_reconciles(self):
        r = self.by[("2016-2017", "FUM")]
        self.assertEqual((int(r["file_n"]), int(r["below"])), (163, 160))
        self.assertFalse(matches(self.pct(r), r["printed_pct"]))
        # The one blank-fiscal-year row is a fumonisin non-detect below 1 ppm; placed in 2016-17
        # it gives the printed n and percentage exactly.
        blank = load_json(SUMMARY)["descriptive"]["blank_year_rows"]
        self.assertEqual(blank, [["2016FED-0000067789-4", "Fumonisins (total B1 and B2)",
                                  "<0.30", "mg/kg"]])
        self.assertLess(float(blank[0][2].lstrip("<")), 1.0)
        self.assertEqual(int(r["file_n"]) + 1, int(r["printed_n"]))
        self.assertTrue(matches(100.0 * (int(r["below"]) + 1) / (int(r["file_n"]) + 1),
                                r["printed_pct"]))
        self.assertEqual(r["printed_pct"], "98.17")


class TestLimits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.counts = {}
        for r in load_csv(LIMITS):
            cell = cls.counts.setdefault((r["analyte"], r["year"]), {})
            cell[float(r["limit_ppm"])] = cell.get(float(r["limit_ppm"]), 0) + int(r["n"])

    def over(self, analyte, years):
        out = {}
        for y in years:
            for lim, n in self.counts.get((analyte, y), {}).items():
                out[lim] = out.get(lim, 0) + n
        return out

    def test_p10_don_mode_unchanged(self):
        early = self.over("DON", YEARS[:4])
        late = self.over("DON", YEARS[14:])
        self.assertEqual(early, {0.1: 147})
        self.assertEqual(late, {0.05: 1, 0.1: 136, 0.12: 27, 0.2: 1, 0.23: 1, 0.32: 1, 0.5: 11})
        self.assertEqual(modal(early), 0.1)
        self.assertEqual(modal(late), 0.1)  # not lower: P10 missed

    def test_p11_ht2_modes(self):
        for y in YEARS[:14]:
            self.assertEqual(modal(self.counts[("HT-2", y)]), 0.1, msg=y)
        for y in YEARS[14:]:
            self.assertEqual(modal(self.counts[("HT-2", y)]), 0.015, msg=y)

    def test_c5_mechanism_from_limits(self):
        for y in YEARS:
            above = sum(n for lim, n in self.counts[("HT-2", y)].items() if lim > 0.1 + 1e-9)
            self.assertEqual(above, HT2_GAP.get(y, 0), msg=y)

    def test_method_changes(self):
        def m(a, y):
            return modal(self.counts[(a, y)])
        self.assertEqual((m("T-2", "2013-2014"), m("T-2", "2014-2015")), (0.1, 0.01))
        self.assertEqual((m("HT-2", "2013-2014"), m("HT-2", "2014-2015")), (0.1, 0.015))
        self.assertEqual((m("OTA", "2013-2014"), m("OTA", "2014-2015")), (0.005, 0.01))
        self.assertEqual((m("FUM", "2015-2016"), m("FUM", "2016-2017")), (0.1, 0.3))
        for y in YEARS[:17]:
            self.assertEqual(m("DON", y), 0.1, msg=y)
        self.assertEqual(m("DON", "2017-2018"), 0.12)
        for y in YEARS:
            self.assertEqual(m("ZEA", y), 0.1, msg=y)

    def test_method_change_detection_rates(self):
        det = load_json(SUMMARY)["descriptive"]["detection_by_analyte_year"]

        def tally(a, years):
            n = k = 0
            for y in years:
                n += det[a][y][0]
                k += det[a][y][1]
            return n, k

        expected = {  # analyte: (split index, before (n, k), after (n, k)) as in the note
            "T-2": (14, (2544, 49), (699, 178)),
            "HT-2": (14, (2544, 113), (699, 241)),
            "OTA": (14, (2542, 179), (698, 17)),
            "FUM": (16, (1322, 589), (350, 30)),
            "DON": (14, (2535, 1932), (703, 525)),
            "ZEA": (14, (2541, 249), (699, 83)),
        }
        for a, (i, before, after) in expected.items():
            self.assertEqual(tally(a, YEARS[:i]), before, msg=a)
            self.assertEqual(tally(a, YEARS[i:]), after, msg=a)
        # Printed percentages (one decimal).
        self.assertEqual(round(100 * 49 / 2544, 1), 1.9)
        self.assertEqual(round(100 * 178 / 699, 1), 25.5)
        self.assertEqual(round(100 * 113 / 2544, 1), 4.4)
        self.assertEqual(round(100 * 241 / 699, 1), 34.5)
        self.assertEqual(round(100 * 179 / 2542, 1), 7.0)
        self.assertEqual(round(100 * 17 / 698, 1), 2.4)
        self.assertEqual(round(100 * 589 / 1322, 1), 44.6)
        self.assertEqual(round(100 * 30 / 350, 1), 8.6)


class TestSamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_csv(SAMPLES)
        cls.cooc = load_json(COOC)

    @staticmethod
    def flag(r, a):
        v = r["det_" + a]
        return None if v == "" else v == "1"

    def table(self, x, y):
        a = b = c = d = 0
        for r in self.rows:
            fx, fy = self.flag(r, x), self.flag(r, y)
            if fx is None or fy is None:
                continue
            if fx and fy:
                a += 1
            elif fx:
                b += 1
            elif fy:
                c += 1
            else:
                d += 1
        return a, b, c, d

    def check_pair(self, key, x, y, cells, orr):
        t = self.table(x, y)
        self.assertEqual(t, cells)
        com = self.cooc[key]
        self.assertEqual((com["both"], com["x_only"], com["y_only"], com["neither"]), cells)
        self.assertEqual(com["n_pairs"], sum(cells))
        a, b, c, d = t
        self.assertAlmostEqual((a * d) / (b * c), orr, places=9)
        self.assertAlmostEqual(com["odds_ratio"], orr, places=9)
        self.assertFalse(com["haldane_corrected"])
        p = fisher_two_sided(a, b, c, d)
        self.assertTrue(math.isclose(p, com["fisher_p"], rel_tol=1e-6))
        return p

    def test_shape(self):
        self.assertEqual(len(self.rows), 3258)
        self.assertEqual(len({r["sid"] for r in self.rows}), 3258)

    def test_p3_don_zea(self):
        p = self.check_pair("DON x ZEA", "DON", "ZEA", (328, 2127, 2, 770), 59.370004701457454)
        self.assertLess(p, 0.001)

    def test_p4_don_15adon(self):
        p = self.check_pair("DON x 15-ADON", "DON", "15-ADON", (917, 1540, 1, 780),
                            464.45454545454544)
        self.assertLess(p, 0.001)

    def test_p5_ota_don_reversed(self):
        p = self.check_pair("OTA x DON", "OTA", "DON", (136, 60, 2312, 711), 0.6970588235294117)
        self.assertLess(p, 0.05)
        self.assertGreater(p, 0.01)
        self.assertEqual(round(100 * 136 / 196, 1), 69.4)
        self.assertEqual(round(100 * 2312 / 3023, 1), 76.5)

    def test_p6_acetyl_counts(self):
        n15 = sum(1 for r in self.rows if self.flag(r, "15-ADON"))
        n3 = sum(1 for r in self.rows if self.flag(r, "3-ADON"))
        self.assertEqual((n15, n3), (918, 174))

    def split(self, key):
        out = {}
        for r in self.rows:
            if not (self.flag(r, "3-ADON") or self.flag(r, "15-ADON")):
                continue
            g = key(r)
            if not g:
                continue
            cell = out.setdefault(g, [0, 0])
            cell[0] += 1
            if self.flag(r, "3-ADON"):
                cell[1] += 1
        return out

    def test_p7_region(self):
        s = self.split(lambda r: r["region"])
        self.assertEqual(s, {"West": [36, 14], "East": [966, 160]})
        p = fisher_two_sided(14, 22, 160, 806)
        self.assertTrue(math.isclose(p, self.cooc["3-ADON share by region"]["fisher_p"],
                                     rel_tol=1e-6))
        self.assertLess(p, 0.05)
        self.assertEqual(round(100 * 14 / 36, 1), 38.9)
        self.assertEqual(round(100 * 160 / 966, 1), 16.6)

    def test_p8_period_flat(self):
        s = self.split(lambda r: "late" if r["year"] in LATE
                       else ("early" if r["year"] in EARLY else None))
        self.assertEqual(s, {"late": [546, 95], "early": [456, 79]})
        late, early = 95 / 546, 79 / 456
        self.assertGreater(late, early)          # met on the point estimate only
        self.assertLess(late - early, 0.001)
        p = fisher_two_sided(95, 451, 79, 377)
        self.assertAlmostEqual(p, self.cooc["3-ADON share by period"]["fisher_p"], places=9)
        self.assertGreater(p, 0.9)


class TestSealedRecord(unittest.TestCase):
    """Row-level headlines, read from the sealed grader output."""

    @classmethod
    def setUpClass(cls):
        cls.s = load_json(SUMMARY)
        cls.p = {pr["id"]: pr for pr in cls.s["predictions"]}

    def test_tally(self):
        self.assertEqual(self.s["n_graded"], 21)
        self.assertEqual(self.s["n_met"], 17)
        self.assertEqual({k for k, v in self.p.items() if not v["met"]}, {"P2", "P5", "P9", "P10"})
        self.assertEqual(self.s["provenance"]["sha256"],
                         "6de28d69d6d2fe0552aae55720b2b481b6673efafbcccf90dc87f7002a2c1491")
        for cid in ("G", "C1", "C2", "C3", "C4", "C5", "C6", "C7"):
            self.assertTrue(self.p[cid]["met"], msg=cid)

    def test_p1_p2_don(self):
        counts = self.p["P1"]["observed"]["counts"]
        self.assertEqual(counts["DON"], [3238, 2457])
        shares = {a: k / n for a, (n, k) in counts.items() if n}
        self.assertEqual(max(shares, key=shares.get), "DON")
        self.assertEqual(round(100 * shares["FUM"], 1), 37.0)
        self.assertEqual(round(100 * shares["15-ADON"], 1), 28.3)
        self.assertGreater(shares["DON"], 0.75)  # P2 missed, narrowly
        self.assertEqual(round(100 * shares["DON"], 1), 75.9)

    def test_p9_fumonisins_corn(self):
        obs = self.p["P9"]["observed"]
        self.assertEqual(obs["corn"], [1436, 579])
        self.assertEqual(obs["other_named"], [215, 37])
        ratio = (579 / 1436) / (37 / 215)
        self.assertEqual(round(ratio, 1), 2.3)
        self.assertLess(ratio, 3.0)

    def test_p12_s1_c7(self):
        self.assertEqual(self.p["P12"]["observed"]["counts"], [699, 7])
        self.assertEqual(self.p["S1"]["observed"], {"censored": 35368, "without_numeric_limit": 0})
        self.assertEqual(self.p["C7"]["observed"]["n_over"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
