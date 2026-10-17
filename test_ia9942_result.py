"""Recompute the ia9942-lead-spice 0.1.1 headline grade from the committed firm table.

This is the frozen-files test for docs/ia9942-lead-spice-0.1.1-result.md. It reads
data/ia9942_lead_spice_firms.csv (the lead-spice firms on the current FDA Import Alert
99-42 page and on the 2021 Wayback copy of Import Alert 28-13, written by the sealed job
ia9942-lead-spice-v2) and recomputes E, L, the spice-tag counts and all five
pre-registered predictions, pinning the published numbers. No network. Apache-2.0.
MV2 of Munim, Inc.
"""
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "ia9942_lead_spice_firms.csv")

EARLY_SOURCE = "ia2813_wayback_20211208151355"   # the 2021 copy of Import Alert 28-13
LATE_SOURCE = "current"                           # the live 99-42 page (Oct 2026)


def _load():
    with open(CSV, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _year(row):
    return int(row["listing_date"][:4])


def _firms(rows, source, lo, hi):
    """Firms from `source` whose listing year is in [lo, hi]."""
    return [r for r in rows if r["source"] == source and lo <= _year(r) <= hi]


def _tag_counts(firms):
    counts = {}
    for r in firms:
        for tag in r["tags"].split(";"):
            tag = tag.strip()
            if tag:
                counts[tag] = counts.get(tag, 0) + 1
    return counts


def _top(counts):
    """The strictly-leading tag, or None if there is a tie for first."""
    if not counts:
        return None
    ordered = sorted(counts.items(), key=lambda kv: -kv[1])
    if len(ordered) > 1 and ordered[0][1] == ordered[1][1]:
        return None
    return ordered[0][0]


@unittest.skipUnless(os.path.exists(CSV), "committed firm table not present")
class TestIa9942Result(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = _load()
        cls.E = _firms(cls.rows, EARLY_SOURCE, 2016, 2020)
        cls.L = _firms(cls.rows, LATE_SOURCE, 2021, 2025)

    def test_E_count(self):
        self.assertEqual(len(self.E), 19)

    def test_L_count(self):
        self.assertEqual(len(self.L), 14)

    def test_E_by_country(self):
        by = {}
        for r in self.E:
            by[r["country"]] = by.get(r["country"], 0) + 1
        self.assertEqual(by.get("INDIA"), 9)
        self.assertEqual(by.get("LEBANON"), 2)
        self.assertEqual(by.get("VIETNAM"), 2)
        self.assertEqual(sum(by.values()), 19)
        self.assertNotIn("GEORGIA", by)  # P5

    def test_L_by_country(self):
        by = {}
        for r in self.L:
            by[r["country"]] = by.get(r["country"], 0) + 1
        self.assertEqual(by.get("VIETNAM"), 6)
        self.assertEqual(by.get("INDIA"), 4)
        self.assertEqual(sum(by.values()), 14)

    def test_E_tags(self):
        counts = _tag_counts(self.E)
        self.assertEqual(counts.get("cinnamon"), 14)
        self.assertEqual(counts.get("turmeric"), 2)
        self.assertEqual(counts.get("cumin"), 1)
        self.assertEqual(counts.get("other"), 2)

    def test_L_tags(self):
        counts = _tag_counts(self.L)
        self.assertEqual(counts.get("cinnamon"), 10)
        self.assertEqual(counts.get("other"), 4)
        self.assertEqual(counts.get("ginger"), 1)

    def test_P1_did_not_fall_FAILS(self):
        # P1: L > E. Predicted the border record did not fall; it did.
        self.assertFalse(len(self.L) > len(self.E))

    def test_P2_doubled_FAILS(self):
        self.assertFalse(len(self.L) >= 2 * len(self.E))

    def test_P3_cinnamon_tops_L_HOLDS(self):
        self.assertEqual(_top(_tag_counts(self.L)), "cinnamon")

    def test_P4_turmeric_tops_E_FAILS(self):
        self.assertNotEqual(_top(_tag_counts(self.E)), "turmeric")
        self.assertEqual(_top(_tag_counts(self.E)), "cinnamon")

    def test_P5_no_georgia_in_E_HOLDS(self):
        self.assertEqual(sum(1 for r in self.E if r["country"] == "GEORGIA"), 0)

    def test_two_of_five_held(self):
        held = [
            len(self.L) > len(self.E),                              # P1
            len(self.L) >= 2 * len(self.E),                         # P2
            _top(_tag_counts(self.L)) == "cinnamon",               # P3
            _top(_tag_counts(self.E)) == "turmeric",               # P4
            sum(1 for r in self.E if r["country"] == "GEORGIA") == 0,  # P5
        ]
        self.assertEqual(sum(held), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
