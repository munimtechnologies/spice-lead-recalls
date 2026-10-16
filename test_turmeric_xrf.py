"""Tests for turmeric_xrf.py (MV2 of Munim, Inc.; Apache-2.0)."""
import os
import unittest

import turmeric_xrf as tx

HERE = os.path.dirname(os.path.abspath(__file__))
SUPP_TEXT = os.path.join(HERE, "data", "forsyth2026_supp_text.txt")


class TestTurmericXrf(unittest.TestCase):
    def test_pure_lead_chromate_is_one(self):
        cr = 1000 * tx.CR / tx.PB
        self.assertAlmostEqual(tx.molar_pb_cr(1000, cr), 1.0, places=6)

    def test_no_ratio_without_chromium(self):
        self.assertIsNone(tx.molar_pb_cr(100, None))
        self.assertIsNone(tx.molar_pb_cr(100, 0))

    def test_half_percent_is_about_3200_ppm_lead(self):
        self.assertAlmostEqual(tx.pct_to_pb_ppm(0.5), 3205.6, delta=1.0)
        self.assertAlmostEqual(tx.pct_to_pb_ppm(0.005), 32.06, delta=0.1)

    def test_parse_values(self):
        self.assertEqual(tx.parse_value("6,416"), (6416.0, False))
        self.assertEqual(tx.parse_value(" 12.5 "), (12.5, False))
        self.assertEqual(tx.parse_value("<LOD"), (None, True))
        self.assertEqual(tx.parse_value("ND"), (None, True))
        self.assertEqual(tx.parse_value("<4"), (None, True))
        self.assertEqual(tx.parse_value(""), (None, False))
        self.assertEqual(tx.parse_value(None), (None, False))
        self.assertEqual(tx.parse_value("Bihar"), (None, False))

    def test_find_columns(self):
        cols = tx.find_columns(["Sample ID", "Type", "Source state", "City",
                                "Pb (µg/g)", "Cr (µg/g)"])
        self.assertEqual(cols, {"type": 1, "state": 2, "city": 3, "pb": 4, "cr": 5})
        self.assertIsNone(tx.find_columns(["Bihar", "Root", "48", "12"]))

    def test_rows_and_analysis(self):
        tables = [
            (5, [["ID", "Type", "State", "Lead (ug/g)", "Chromium (ug/g)"],
                 ["1", "Powder", "Bihar", "1000", "251"],
                 ["2", "Root", "Bihar", "<LOD", "<LOD"]]),
            (6, [["3", "Powder", "Jharkhand", "4000", "1004"],
                 ["4", "Root", "West Bengal", "20", "ND"]]),
        ]
        rows, cols, _ = tx.rows_from_tables(tables)
        self.assertEqual(len(rows), 4)
        self.assertIn("cr", cols)
        res = tx.analyse(rows)
        self.assertEqual(res["n_pb_nondetect"], 1)
        self.assertEqual(res["pb_ge_10"]["n"], 3)
        self.assertEqual(res["pb_ge_10"]["cr_nondetect"], 1)
        self.assertEqual(res["pb_ge_100"]["in_nyc_band_0.81_1.78"]["k"], 2)
        half = res["raman_reach"][0]
        self.assertEqual(half["caught_of_pb_ge_10"], {"k": 1, "n": 3, "pct": 33.3})
        self.assertEqual(res["by_type"]["powder"]["pb_ge_3205"], 1)
        self.assertNotIn("reach_by_group", res)

    def test_parse_s8_text_lines(self):
        # Real lines of Table S8 as pdfplumber writes them (turm_major blank in two).
        text = "\n".join([
            "=== page 15 ===",
            "154 Table S8. Turmeric market sample data used in analyses (n=503). All_pb_avg: average sample",
            "sampid_ city_final all_pb_avg type_groupfull4 sellstate_bin turm_major",
            "15_BS_5_1_1 Dhanbad 2 1 0 1",
            "15_PB_1_1_1 Dhanbad 2 1 0",
            "=== page 19 ===",
            "36_MC_3_1_1 Buxar 6416 1 1 1",
            "26_GM_1_2_4 Muzzafarpur 1287 3 1",
            "50_KD-1-2-5 Ambikapur 10 4 0",
            "42_MB_3_1_2 Deoghar 240 2 0 1",
            "19",
            "152",
        ])
        rows = tx.parse_s8_text(text)
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[0]["page"], 15)
        self.assertEqual(rows[2], {"page": 19, "id": "36_MC_3_1_1", "city": "Buxar", "pb": 6416.0,
                                   "pb_nd": False, "cr": None, "cr_nd": False, "type_code": 1,
                                   "type": "loose powder", "state": "Bihar", "turm_major": "1"})
        self.assertEqual(rows[1]["turm_major"], "")
        self.assertEqual([r["type"] for r in rows[3:]],
                         ["polished root", "unpolished root", "packaged powder"])
        res = tx.analyse(rows)
        groups = {g["group"]: g for g in res["reach_by_group"]}
        self.assertEqual(groups["all"]["pb_ge_10"], 4)
        self.assertEqual(groups["all"]["caught_0.5"], {"k": 1, "pct": 25.0})
        self.assertEqual(groups["powder"]["pb_ge_10"], 2)
        self.assertEqual(groups["root"]["caught_0.005"], {"k": 1, "pct": 50.0})


class TestForsythTableS8(unittest.TestCase):
    """The committed text of the Forsyth et al. 2026 supplement (CC BY 4.0), as the
    sealed 0.1.0 run extracted it. These are the counts in docs/forsyth2026-raman-reach.md."""

    @classmethod
    def setUpClass(cls):
        with open(SUPP_TEXT, encoding="utf-8") as fh:
            cls.rows = tx.parse_s8_text(fh.read())
        cls.groups = {g["group"]: g for g in tx.reach_by_group(cls.rows)}

    def test_row_count_matches_the_paper(self):
        self.assertEqual(len(self.rows), 503)

    def test_p0_samples_with_lead_at_least_10(self):
        # The paper: 30% of 503, n = 153.
        self.assertEqual(self.groups["all"]["pb_ge_10"], 153)

    def test_no_chromium_column(self):
        self.assertTrue(all(r["cr"] is None for r in self.rows))

    def test_reach_all(self):
        g = self.groups["all"]
        self.assertEqual((g["n"], g["pb_ge_100"], g["pb_ge_1000"]), (503, 131, 91))
        self.assertEqual(g["median_pb_of_pb_ge_10"], 1287)
        self.assertEqual([g["caught_%g" % p]["k"] for p in tx.RAMAN_PCT], [16, 103, 111, 124, 141])

    def test_reach_powder_and_root(self):
        p, r = self.groups["powder"], self.groups["root"]
        self.assertEqual((p["n"], p["pb_ge_10"], p["pb_ge_100"], p["pb_ge_1000"]), (192, 60, 44, 24))
        self.assertEqual(p["median_pb_of_pb_ge_10"], 515)
        self.assertEqual([p["caught_%g" % x]["k"] for x in tx.RAMAN_PCT], [2, 29, 34, 40, 50])
        self.assertEqual((r["n"], r["pb_ge_10"], r["pb_ge_100"], r["pb_ge_1000"]), (311, 93, 87, 67))
        self.assertEqual([r["caught_%g" % x]["k"] for x in tx.RAMAN_PCT], [14, 74, 77, 84, 91])

    def test_by_product_type(self):
        got = {k: (self.groups[k]["n"], self.groups[k]["pb_ge_10"])
               for k in ("loose powder", "packaged powder", "polished root", "unpolished root")}
        self.assertEqual(got, {"loose powder": (162, 57), "packaged powder": (30, 3),
                               "polished root": (235, 83), "unpolished root": (76, 10)})


if __name__ == "__main__":
    unittest.main()
