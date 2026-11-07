#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline checks of data/cfia-open-data-errata.csv (CFIA open-data errata 0.2.0).

Checks the schema, the controlled vocabularies, the counts stated in
docs/cfia-open-data-errata-0.2.0.md, and that every row cites a note that the CFIA chemistry
surveys index links. Standard library only. Run from the repository root or anywhere:
    python -m unittest -v test_cfia_errata
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0; data CC BY 4.0."""
import collections
import csv
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "data", "cfia-open-data-errata.csv")
INDEX_PATH = os.path.join(HERE, "docs", "cfia-chemistry-surveys-index.md")
DOC_PATH = os.path.join(HERE, "docs", "cfia-open-data-errata-0.2.0.md")

HEADER = ["item_id", "series", "survey_years", "analyte", "where", "finding", "printed",
          "open_file", "kind", "evidence", "note"]
KINDS = {"unit": 4, "value": 8, "count": 12, "share": 6, "average": 7, "origin": 3,
         "subset": 5, "text": 8, "label": 4, "date": 2, "duplicate": 2, "coverage": 3}
EVIDENCE = {"report_vs_file": 36, "report_internal": 17, "file_internal": 7,
            "report_vs_report": 4}
SERIES = {"cfp": 2, "furan-2018": 5, "tmet-2018": 1, "pah-2018": 2, "pah-2019": 3,
          "bisphenols-2018-2020": 3, "bpa-2009-2018": 6, "food-colours": 6,
          "ethyl-carbamate": 7, "perchlorate": 6, "phthalates-2020": 3,
          "phthalates-2012-2019": 9, "fumonisin-2011-2018": 11}
TOTAL = 64
# A street address (a number, a name, then Road, Street and so on) has no place in this dataset.
STREET = re.compile(r"\b\d{1,5}\s+[A-Z][a-z]+\s+(Road|Street|Avenue|Lane|Drive|Boulevard)\b")


def load_rows():
    with open(CSV_PATH, encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        rows = [dict(zip(header, r)) for r in reader if r]
    return header, rows


class ErrataSchema(unittest.TestCase):
    def setUp(self):
        self.header, self.rows = load_rows()

    def test_header(self):
        self.assertEqual(self.header, HEADER)

    def test_every_row_has_every_field(self):
        with open(CSV_PATH, encoding="utf-8", newline="") as fh:
            for line_no, row in enumerate(csv.reader(fh), start=1):
                if row:
                    self.assertEqual(len(row), len(HEADER), f"line {line_no}")

    def test_total(self):
        self.assertEqual(len(self.rows), TOTAL)

    def test_ids_unique_and_slugs(self):
        ids = [r["item_id"] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        for i in ids:
            self.assertRegex(i, r"^[a-z0-9]+(-[a-z0-9]+)*$")

    def test_kind_counts(self):
        self.assertEqual(dict(collections.Counter(r["kind"] for r in self.rows)), KINDS)
        self.assertEqual(sum(KINDS.values()), TOTAL)

    def test_evidence_counts(self):
        self.assertEqual(dict(collections.Counter(r["evidence"] for r in self.rows)), EVIDENCE)
        self.assertEqual(sum(EVIDENCE.values()), TOTAL)

    def test_series_counts(self):
        self.assertEqual(dict(collections.Counter(r["series"] for r in self.rows)), SERIES)
        self.assertEqual(sum(SERIES.values()), TOTAL)

    def test_ids_start_with_a_series_prefix(self):
        prefixes = {"cfp": "cfp-", "furan-2018": "furan-2018-", "tmet-2018": "tmet-2018-",
                    "pah-2018": "pah-2018-", "pah-2019": "pah-2019-",
                    "bisphenols-2018-2020": "bpa-20", "bpa-2009-2018": "bpa-20",
                    "food-colours": "fc-", "ethyl-carbamate": "ec-", "perchlorate": "perc-",
                    "phthalates-2020": "ph-2020-", "phthalates-2012-2019": "ph-201",
                    "fumonisin-2011-2018": "fum-20"}
        for r in self.rows:
            self.assertTrue(r["item_id"].startswith(prefixes[r["series"]]), r["item_id"])

    def test_findings_are_sentences(self):
        for r in self.rows:
            self.assertTrue(r["finding"][:1].isupper() or r["finding"][:1].isdigit()
                            or r["finding"][:1] == "'", r["item_id"])
            self.assertTrue(r["finding"].endswith("."), r["item_id"])
            self.assertNotIn('"', r["finding"], r["item_id"])

    def test_no_street_address(self):
        with open(CSV_PATH, encoding="utf-8") as fh:
            text = fh.read()
        self.assertIsNone(STREET.search(text))
        self.assertIsNotNone(STREET.search(" ".join(["12", "Example", "Road"])))


class ErrataContent(unittest.TestCase):
    """Spot checks of values copied verbatim from the cited notes."""

    def setUp(self):
        _, rows = load_rows()
        self.rows = rows
        self.by_id = {r["item_id"]: r for r in rows}

    def test_ethyl_carbamate_scale(self):
        r = self.by_id["ec-2018-1000x"]
        self.assertEqual((r["printed"], r["open_file"], r["kind"]),
                         ("4 (beers)", "0.004 (beers)", "unit"))
        self.assertIn("36 of the 37", r["finding"])
        self.assertIn("West", r["finding"])

    def test_bisphenol_four_missing(self):
        r = self.by_id["bpa-2018-381"]
        self.assertEqual((r["printed"], r["open_file"]), ("381", "377"))
        self.assertEqual(int(r["printed"]) - int(r["open_file"]), 4)

    def test_furan_dried_beverage_average(self):
        r = self.by_id["furan-2018-bev-avg"]
        self.assertEqual((r["printed"], r["open_file"], r["evidence"]),
                         ("9.7", "10.35", "report_internal"))
        # 15 values whose mean is 10.35 sum to 155.25; that sum over 16 is 9.703...
        self.assertEqual(round(10.35 * 15 / 16, 1), 9.7)

    def test_phthalates_ppb_arithmetic(self):
        # 0.006 mg/L = 6 micrograms per litre = 6 parts per billion.
        for item in ("ph-2020-ppb", "ph-2018-ppb"):
            self.assertEqual(self.by_id[item]["open_file"], "6 ppb")
        self.assertEqual(round(0.006 * 1000, 6), 6.0)

    def test_phthalates_origin_totals_agree(self):
        r = self.by_id["ph-2020-origin"]
        groups = [g.split(" / ") for g in r["printed"].split(" and ")]
        files = [g.split(" / ") for g in r["open_file"].split(" and ")]
        for printed, held in zip(groups, files):
            self.assertEqual(sum(map(int, printed)), 250)
            self.assertEqual(sum(map(int, held)), 250)
            self.assertNotEqual(printed, held)

    def test_colour_origin_totals_agree(self):
        r = self.by_id["fc-2018-origin"]
        printed = list(map(int, r["printed"].split(" / ")))
        held = list(map(int, r["open_file"].split(" / ")))
        self.assertEqual(sum(printed), sum(held))
        self.assertEqual(sum(held), 399)

    def test_perchlorate_nonsoy_subsets(self):
        r = self.by_id["perc-t3-nonsoy"]
        printed = list(map(int, r["printed"].split(" / ")))
        held = list(map(int, r["open_file"].replace(" formulas", "").split(" / ")))
        self.assertEqual(printed, [74, 68, 30])
        self.assertEqual(held, [89, 87, 39])
        for p, h in zip(printed, held):
            self.assertLess(p, h)

    def test_phthalates_2012_15_rates(self):
        r = self.by_id["ph-2015-rates"]
        self.assertEqual((r["printed"], r["open_file"]), ("57.1% / 36%", "54.0% / 19.0%"))
        self.assertEqual(round(100 * 128 / 224, 1), 57.1)
        self.assertEqual(round(100 * 8 / 22), 36)
        self.assertEqual(round(100 * 128 / 237, 1), 54.0)
        self.assertEqual(round(100 * 8 / 42, 1), 19.0)

    def test_nut_butter_average(self):
        r = self.by_id["ph-2015-nut-avg"]
        self.assertEqual((r["printed"], r["open_file"]), ("17.2", "17.26"))
        self.assertEqual(round(1018.30 / 59, 2), 17.26)
        self.assertEqual(round(1018.30 / 59, 1), 17.3)

    def test_fumonisin_teff_arithmetic(self):
        r = self.by_id["fum-2018-teff-11"]
        self.assertEqual((r["printed"], r["evidence"]), ("11", "report_internal"))
        self.assertEqual(3584 - 11 + 77, 3650)
        self.assertEqual(13 + 8 + 14 + 42, 77)

    def test_fumonisin_wheat_2012_impossible(self):
        r = self.by_id["fum-2018-wheat-2012"]
        self.assertEqual(r["printed"], "99.7")
        self.assertGreater((28.8 + 28.8 + 393) / 3, 99.7)

    def test_unread_fumonisin_files_give_no_file_figure(self):
        # Neither fumonisin file had been opened when these items were fixed.
        for r in self.rows:
            if r["series"] == "fumonisin-2011-2018":
                self.assertEqual(r["open_file"], "", r["item_id"])
                self.assertIn(r["evidence"], ("report_internal", "report_vs_report"))


class ErrataLinks(unittest.TestCase):
    def test_every_note_is_linked_from_the_index(self):
        _, rows = load_rows()
        with open(INDEX_PATH, encoding="utf-8") as fh:
            index = fh.read()
        for r in rows:
            self.assertRegex(r["note"], r"^[a-z0-9.-]+\.md$")
            self.assertIn("(" + r["note"] + ")", index, r["item_id"])

    def test_doc_states_the_same_counts(self):
        with open(DOC_PATH, encoding="utf-8") as fh:
            doc = fh.read()
        self.assertIn("ERRATA-MARKER: cfia-open-data-errata-0.2.0", doc)
        for kind, n in KINDS.items():
            self.assertRegex(doc, r"\| `" + re.escape(kind) + r"` \| " + str(n) + r" \|")
        for ev, n in EVIDENCE.items():
            self.assertRegex(doc, r"\| `" + re.escape(ev) + r"` \| " + str(n) + r" \|")
        self.assertIn(f"{TOTAL} items", doc)


if __name__ == "__main__":
    unittest.main()
