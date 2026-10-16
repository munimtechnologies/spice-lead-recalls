"""Offline tests for lead_recalls.py. Apache-2.0."""
import os
import tempfile
import unittest

import lead_recalls as lr


def rec(desc, reason, date="20240528", rn="F-0001-2024", event="1", **kw):
    r = {"product_description": desc, "reason_for_recall": reason, "recall_initiation_date": date,
         "recall_number": rn, "event_id": event, "classification": "Class II", "state": "NY",
         "country": "United States", "recalling_firm": "Firm  A"}
    r.update(kw)
    return r


class LeadReason(unittest.TestCase):
    def test_metal(self):
        self.assertTrue(lr.is_lead_recall("Product contains elevated levels of lead (2,040ppb)."))
        self.assertTrue(lr.is_lead_recall("LEAD CHROMATE detected"))
        self.assertTrue(lr.is_lead_recall("Elevated Pb found by state testing"))
        self.assertTrue(lr.is_lead_recall("FDA testing found that lead levels were high"))

    def test_not_metal(self):
        self.assertFalse(lr.is_lead_recall("Undeclared milk could lead to an allergic reaction"))
        self.assertFalse(lr.is_lead_recall("Mislabeled; may lead consumers to believe it is gluten free"))
        self.assertFalse(lr.is_lead_recall("PB&J sandwiches may contain Listeria"))
        self.assertFalse(lr.is_lead_recall(""))
        self.assertFalse(lr.is_lead_recall(None))


class Levels(unittest.TestCase):
    def ppm(self, text):
        return [lv["ppm"] for lv in lr.parse_levels(text)]

    def test_units(self):
        self.assertEqual(self.ppm("elevated levels of lead (2,040ppb)."), [2.04])
        self.assertEqual(self.ppm("lead at 5.11 mg/g"), [5110.0])
        self.assertEqual(self.ppm("lead 3 mg / kg"), [3.0])
        self.assertEqual(self.ppm("lead: 120 ug/kg"), [0.12])
        self.assertEqual(self.ppm("lead at 7 µg/g"), [7.0])
        self.assertEqual(self.ppm("lead at 1.5 parts per million"), [1.5])

    def test_no_leading_zero(self):
        # F-0077-2014, ginger candy: missed by 0.1.0.
        self.assertEqual(self.ppm("found that it may contain as much as .012 ppm of lead."), [0.012])

    def test_range(self):
        self.assertEqual(sorted(self.ppm("lead levels from 2.03 – 3.40 ppm")), [2.03, 3.40])
        self.assertEqual(sorted(self.ppm("lead ranging 2.03 to 7.68 ppm")), [2.03, 7.68])

    def test_other_metal(self):
        self.assertEqual(self.ppm("lead 12 ppm and arsenic 3 ppm"), [12.0])
        self.assertEqual(self.ppm("arsenic 3 ppm"), [])
        self.assertEqual(self.ppm("contains 4 ppm"), [])

    def test_no_decimal_comma_misread(self):
        self.assertEqual(self.ppm("lead 2,04 ppm"), [])

    def test_snippet(self):
        lv = lr.parse_levels("Product contains elevated levels of lead (2,040ppb).")
        self.assertIn("2,040ppb", lv[0]["text"])


class Classify(unittest.TestCase):
    def test_spices(self):
        self.assertEqual(lr.classify("Spice Class brand Ground Cinnamon, 7oz PET jars"), ("cinnamon", "spice"))
        self.assertEqual(lr.classify("TURMERIC POWDER 200g"), ("turmeric", "spice"))
        self.assertEqual(lr.classify("Kashmiri Chilli Powder"), ("chili/paprika", "spice"))
        self.assertEqual(lr.classify("Garam Masala 100 g"), ("curry/masala", "spice"))
        self.assertEqual(lr.classify("Ground nutmeg"), ("other single spice", "spice"))
        self.assertEqual(lr.classify("All purpose seasoning"), ("mixed spice/seasoning", "spice"))

    def test_forms(self):
        self.assertEqual(lr.classify("WanaBana Apple Cinnamon Fruit Puree pouches"),
                         ("cinnamon", "food containing spice"))
        self.assertEqual(lr.classify("Weis CINNAMON APPLE SAUCE, Net Weight: 3.2 oz (90g) Pouches"),
                         ("cinnamon", "food containing spice"))
        self.assertEqual(lr.classify("Tamarind candy with chili"), ("chili/paprika", "food containing spice"))
        self.assertEqual(lr.classify("Turmeric Curcumin 500 mg capsules"), ("turmeric", "supplement"))

    def test_not_spice(self):
        self.assertEqual(lr.classify("Shrimp Paste 16 oz"), (None, None))
        self.assertEqual(lr.classify("Dried apricots, Product of Chile"), (None, None))
        self.assertEqual(lr.classify("Something thing"), (None, None))

    def test_spot_check_fixes(self):
        # Rows the hand spot check of 0.1.0 found misclassified.
        self.assertEqual(lr.classify("Dragonfly brand Galanga Powder; Net Weight: 5 oz. Product of Thailand"),
                         ("other single spice", "spice"))
        self.assertEqual(lr.classify("Pran Spice Powder Turmeric , 14.10 oz. (400g) clear plastic laminated pouch"),
                         ("turmeric", "spice"))
        self.assertEqual(lr.classify("SUPER BRAND DRIED CINNAMON POWDER Net Wt: 4oz PRODUCT OF CHINA "
                                     "DISTRIBUTOR: IHA BEVERAGE COMMERCE, CA"), ("cinnamon", "spice"))
        self.assertEqual(lr.classify("El Chavito Saladitos Enchilados Salted Plums with Chili, net wt. 1.7 oz."),
                         ("chili/paprika", "food containing spice"))
        self.assertEqual(lr.classify("Toxin Absorber with Organic Ginger Root - 14 packets and 30 packets"),
                         ("ginger", "supplement"))
        self.assertEqual(lr.classify("Colon Cleansing Kit Ginger"), ("ginger", "supplement"))
        self.assertEqual(lr.classify("Red Vines Black Licorice Twists, anise flavored"), (None, None))


class Origin(unittest.TestCase):
    def test_origin(self):
        self.assertEqual(lr.origin_of("Ground cinnamon. Product of India. Net wt 7 oz"), "India")
        self.assertEqual(lr.origin_of("Made in Sri Lanka"), "Sri Lanka")
        self.assertEqual(lr.origin_of("no origin here"), "")


class Bins(unittest.TestCase):
    def test_limit(self):
        self.assertTrue(3150 < lr.RAMAN_LIMIT_PPM < 3250)
        self.assertEqual(lr.level_bin(0.5), "<1")
        self.assertEqual(lr.level_bin(2.04), "2-5")
        self.assertEqual(lr.level_bin(5110.0), lr.BINS[-1][2])
        self.assertEqual(lr.level_bin(3000.0), lr.BINS[-2][2])


class EndToEnd(unittest.TestCase):
    def test_rows_and_summary(self):
        records = [
            rec("Spice Class brand Ground Cinnamon", "Product contains elevated levels of lead (2,040ppb).",
                rn="F-1", event="10"),
            rec("WanaBana Apple Cinnamon Fruit Puree", "Elevated lead (lead chromate); cinnamon at 5,110 ppm lead",
                date="20231028", rn="F-2", event="11"),
            rec("Shrimp Paste", "Product tested high for lead.", rn="H-3", event="12"),
            rec("Peanut butter", "Undeclared allergen could lead to reaction", rn="F-4", event="13"),
        ]
        rows = lr.build_rows(records)
        self.assertEqual([r["recall_number"] for r in rows], ["F-2", "F-1", "H-3"])
        self.assertEqual(rows[1]["lead_ppm_max"], 2.04)
        self.assertEqual(rows[1]["recalling_firm"], "Firm A")
        self.assertTrue(rows[0]["mentions_chromate"])
        s = lr.summarize(rows, len(records), {"last_updated": "2026-10-13", "sha256": "ab" * 32})
        self.assertEqual(s["version"], lr.__version__)
        self.assertEqual(s["lead_recalls"], 3)
        self.assertEqual(s["spice_lead_recalls"], 2)
        self.assertEqual(s["spice_products_only"], 1)
        self.assertEqual(s["spice_at_or_above_raman_limit"], 1)
        self.assertEqual(s["spice_by_year"], {"2023": 1, "2024": 1})
        with tempfile.TemporaryDirectory() as d:
            lr.write_markdown(s, os.path.join(d, "summary.md"))
            lr.write_csv(rows, os.path.join(d, "rows.csv"))
            with open(os.path.join(d, "summary.md"), encoding="utf-8") as fh:
                md = fh.read()
            self.assertIn("Recalls naming lead: 3", md)
            self.assertIn("F-2", md)


if __name__ == "__main__":
    unittest.main()
