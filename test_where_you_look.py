# SPDX-License-Identifier: Apache-2.0
# Self-contained test for docs/where-you-look.md.
# Reads ONLY committed CSVs (stdlib csv, utf-8-sig to survive a BOM) and recomputes
# every headline number in the synthesis table. No repo-module import.
import csv
import os
import unittest

DATA = "data"


def _rows(name):
    with open(os.path.join(DATA, name), encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _f(x):
    x = (x or "").strip()
    return float(x) if x not in ("", "NA", "nan") else None


class WhereYouLook(unittest.TestCase):
    # --- NYC case/store frames, split by where the spice was bought ---
    def test_nyc_purchase_place(self):
        rows = _rows("purchase_place.csv")
        agg = {}
        for r in rows:
            key = (r["frame"], r["group"])
            n = agg.setdefault(key, [0, 0])
            n[0] += int(r["n_result"])
            n[1] += int(r["n_ge50"])
        ca_n, ca_g = agg[("C", "abroad")]
        us_n, us_g = agg[("C", "US")]
        st_n, st_g = agg[("S", "US")]
        self.assertEqual((ca_n, ca_g), (1332, 147))   # case, bought abroad
        self.assertEqual((us_n, us_g), (866, 12))      # case, bought in US
        self.assertEqual((st_n, st_g), (477, 2))       # NYC store survey
        # The headline ordering: gross lead (>=50 ppm) concentrates in abroad-bought spice.
        r_abroad = ca_g / ca_n
        r_us = us_g / us_n
        r_store = st_g / st_n
        self.assertGreater(r_abroad, 0.10)             # ~11%
        self.assertLess(r_us, 0.02)                    # ~1.4%
        self.assertLess(r_store, 0.01)                 # ~0.4%
        self.assertTrue(r_abroad > r_us > r_store)
        # Store and case-abroad sets are disjoint in scale, not noise:
        self.assertGreater(r_abroad / r_store, 20)

    # --- cross-check the store frame against the independent frame_yield file ---
    def test_frame_yield_cross_check(self):
        rows = _rows("frame_yield.csv")
        by = {(r["city"], r["product_set"], r["frame"]): r for r in rows}
        nyc_s = by[("NYC", "Food-Spice", "S")]
        self.assertEqual((int(nyc_s["n_result"]), int(nyc_s["n_ge50"])), (477, 2))
        nyc_all = by[("NYC", "Food-Spice", "all")]
        self.assertEqual((int(nyc_all["n_result"]), int(nyc_all["n_ge50"])), (3575, 219))
        kc = by[("King County", "Seasoning+Food", "all")]
        self.assertEqual((int(kc["n_result"]), int(kc["n_ge50"])), (254, 2))
        self.assertLess(int(kc["n_ge50"]) / int(kc["n_result"]), 0.02)  # ~0.8%

    # --- FDA import-alert list: firms refused at the border (no per-sample Pb) ---
    def test_fda_border_list(self):
        rows = _rows("ia9942_lead_spice_firms.csv")
        header = rows[0].keys()
        # It is a list of flagged firms; it carries no lead concentration at all.
        self.assertNotIn("pb", header)
        self.assertNotIn("lead_ppm", header)
        current = [r for r in rows if r["source"] == "current"]
        self.assertEqual(len(current), 48)
        india = [r for r in current if r["country"] == "INDIA"]
        self.assertEqual(len(india), 14)               # top origin by firm count
        georgia = [r for r in current if r["country"] == "GEORGIA"]
        self.assertEqual(len(georgia), 1)              # one firm, added 2026
        self.assertIn("cinnamon", georgia[0]["tags"])  # and it is cinnamon, not a ground blend

    # --- CFIA spice authenticity: 823 samples, zero lead findings ---
    def test_cfia_spice_authenticity(self):
        rows = _rows("cfia_spice_auth_rows.csv")
        self.assertEqual(len(rows), 823)
        lead = sum(int(r["lead"]) for r in rows)
        dye = sum(int(r["dye"]) for r in rows)
        filler = sum(int(r["filler"]) for r in rows)
        self.assertEqual(lead, 0)                       # lead chromate is never named
        self.assertEqual(dye, 5)                        # 5 undeclared-colour failures
        self.assertGreater(filler, dye)                 # allergen fillers dominate failures

    # --- CFIA red palm oil: Sudan dyes, both positives declared Nigerian ---
    def test_cfia_red_palm(self):
        rows = _rows("red_palm_dyes_sealed_samples.csv")
        self.assertEqual(len(rows), 104)
        pos = [r for r in rows if r["sudan_positive"] == "1"]
        self.assertEqual(len(pos), 2)                   # ~1.9%
        self.assertEqual({r["origin"] for r in pos}, {"NIGERIA"})

    # --- CFIA 2018-19 retail spices CFIA itself cleared: no gross lead, no confirmed chromate ---
    def test_cfia_chromate_2018(self):
        rows = _rows("cfia_chromate_2018_samples.csv")
        self.assertEqual(len(rows), 131)
        pb_ge50 = sum(1 for r in rows if (_f(r["pb"]) or 0) >= 50)
        pb_ge2 = sum(1 for r in rows if (_f(r["pb"]) or 0) >= 2)
        spot_pos = sum(1 for r in rows if "Positive" in r["spot"])
        self.assertEqual(pb_ge50, 0)                    # no gross lead in a regulator-cleared set
        self.assertEqual(pb_ge2, 6)                     # low-level lead persists
        self.assertEqual(spot_pos, 8)                   # 8 chromate spot-positives, all cleared


if __name__ == "__main__":
    unittest.main()
