#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/multimyco-2018-detail-0.1.0.md (exploratory, not graded).

Rebuilds Table 3's toxin-group rows of CFIA's 2018-19 multi-mycotoxin report from the committed
listing of every positive cell, data/multimyco_2018_positives.csv, summing each group's analytes
per sample: the fumonisin (3,503), ergot (664) and HT-2/T-2 (98) maxima and the ergot (79) and
HT-2/T-2 (37) averages reproduce that way, while the aflatoxin row (11 / 30 / 4.4) needs one
result of 29.5-30.5 ppb that the file does not hold. Also checks the listing against the
committed per-sample group flags (data/multimyco_2018_samples.csv). Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
POSITIVES = os.path.join(DATA, "multimyco_2018_positives.csv")
SAMPLES = os.path.join(DATA, "multimyco_2018_samples.csv")

FUMONISINS = ("Fumonisin B1", "Fumonisin B2", "Fumonisin B3")
ERGOT = ("Ergocristine", "Ergocryptine", "Ergosine")
HT2T2 = ("HT-2 Toxin", "T-2 Toxin")
AFLATOXINS = ("Aflatoxin B1", "Aflatoxin B2", "Aflatoxin G1", "Aflatoxin G2")
ZEN = "Zearalenone(ppb)"


def read_csv(path):
    for enc in ("utf-8-sig", "cp1252"):
        try:
            with open(path, newline="", encoding=enc) as fh:
                return list(csv.DictReader(fh))
        except UnicodeDecodeError:
            continue
    raise ValueError(path)


def group_sums(rows, labels):
    """{sample: sum of the group's positive cells}."""
    out = {}
    for r in rows:
        if r["component"] in labels:
            out[r["sample"]] = out.get(r["sample"], 0.0) + float(r["ppb"])
    return out


def cells(rows, labels):
    return [float(r["ppb"]) for r in rows if r["component"] in labels]


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv(POSITIVES)
        cls.samples = read_csv(SAMPLES)

    def flagged(self, group):
        return {r["sample"] for r in self.samples if r[group] == "1"}


class TestListing(Base):
    def test_shape(self):
        self.assertEqual(len(self.rows), 722)
        self.assertEqual(list(self.rows[0]), ["sample", "product", "component", "composant",
                                              "ppb"])
        self.assertTrue(all(float(r["ppb"]) > 0 for r in self.rows))
        don = cells(self.rows, ("Deoxynivalenol",))
        self.assertEqual((len(don), max(don), round(sum(don))), (306, 2570.0, 55480))

    def test_listing_matches_group_flags(self):
        for group, labels in (("Fumonisins", FUMONISINS), ("Ergot", ERGOT), ("HT2T2", HT2T2),
                              ("Aflatoxins", AFLATOXINS), ("Zearalenone", (ZEN,))):
            self.assertEqual(set(group_sums(self.rows, labels)), self.flagged(group), msg=group)


class TestSummedGroups(Base):
    def test_fumonisins(self):
        s = group_sums(self.rows, FUMONISINS)
        top = max(s, key=s.get)
        self.assertEqual((len(s), top, round(s[top], 6)), (106, "C2018MUMY00067", 3503.0))
        total = sum(s.values())
        self.assertAlmostEqual(total, 29381.0, places=6)
        self.assertEqual((round(total / 106, 2), round(total / 105, 2)), (277.18, 279.82))
        self.assertTrue(275 <= total / 106 < 285)          # "280" read at 2 significant figures
        self.assertTrue(279.5 <= total / 105 < 280.5)      # "280" read at 3, over 105 samples
        self.assertEqual(max(cells(self.rows, FUMONISINS)), 2370.0)  # no single cell is 3,503

    def test_ergot(self):
        s = group_sums(self.rows, ERGOT)
        top = max(s, key=s.get)
        self.assertEqual((len(s), top, round(s[top], 6)), (46, "C2018MUMY00471", 664.0))
        self.assertAlmostEqual(sum(s.values()), 3639.0, places=6)
        self.assertEqual(round(sum(s.values()) / 46), 79)

    def test_ht2_t2(self):
        s = group_sums(self.rows, HT2T2)
        top = max(s, key=s.get)
        self.assertEqual((len(s), top, round(s[top], 6)), (8, "C2018MUMY00479", 98.0))
        self.assertAlmostEqual(sum(s.values()) / 8, 37.0, places=9)


class TestAflatoxins(Base):
    def test_file_row(self):
        s = group_sums(self.rows, AFLATOXINS)
        self.assertEqual(len(s), 10)
        self.assertEqual(len(cells(self.rows, AFLATOXINS)), 11)
        self.assertAlmostEqual(sum(s.values()), 18.4, places=6)
        top = max(s, key=s.get)
        self.assertEqual((top, round(s[top], 6)), ("C2018MUMY00663", 10.0))

    def test_printed_row_needs_a_missing_result(self):
        total = sum(group_sums(self.rows, AFLATOXINS).values())
        # Printed: 11 positives, max 30 (29.5-30.5), average 4.4 (4.35-4.45).
        lo = max(4.35 * 11 - total, 29.5)
        hi = min(4.45 * 11 - total, 30.5)
        self.assertAlmostEqual(lo, 29.5, places=6)
        self.assertAlmostEqual(hi, 30.5, places=6)
        self.assertLess(max(cells(self.rows, AFLATOXINS)), lo)    # no file cell can be it
        # Counting cells instead of samples gives 11, but not the max or the average.
        self.assertFalse(4.35 <= total / 11 < 4.45)
        self.assertFalse(4.35 <= total / 10 < 4.45)


class TestZearalenone(Base):
    def test_no_threshold_gives_34(self):
        zen = cells(self.rows, (ZEN,))
        self.assertEqual((len(zen), max(zen), round(sum(zen), 6)), (38, 450.0, 1632.0))
        counts = {t: sum(1 for v in zen if v >= t) for t in (8, 9, 10)}
        self.assertEqual(counts, {8: 37, 9: 36, 10: 32})
        self.assertNotIn(34, [sum(1 for v in zen if v >= t) for t in sorted(set(zen))])
        zol = [r for r in self.rows if r["component"].endswith("Zearalenol(ppb)")]
        self.assertEqual([(r["sample"], float(r["ppb"])) for r in zol],
                         [("C2018MUMY00330", 11.0)])
        self.assertNotIn("C2018MUMY00330", set(group_sums(self.rows, (ZEN,))))
        self.assertEqual(round(sum(zen) / 38, 1), 42.9)    # printed 44 needs 1,479-1,513 over 34


if __name__ == "__main__":
    unittest.main(verbosity=2)
