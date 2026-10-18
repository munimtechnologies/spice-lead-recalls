# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
# Recomputes every count in docs/asta-yardstick-0.1.0-result.md from the committed
# tables in data/, using only the Python standard library.
import unittest

import asta_yardstick as ay


class CategoryMap(unittest.TestCase):
    def test_single_spice_wins_over_brand_words(self):
        self.assertEqual(ay.category("Masala King Spices Turmeric Powder"), "root_rhizome")
        self.assertEqual(ay.category("Ceylon Spices Organic Cinnamon Powder"), "bark")
        self.assertEqual(ay.category("Bulk Red Chili Spice"), "fruit")

    def test_order_and_word_starts(self):
        self.assertEqual(ay.category("Star Anise"), "fruit")
        self.assertEqual(ay.category("Anise seed"), "seed")
        self.assertEqual(ay.category("Curry leaf"), "herb")
        self.assertEqual(ay.category("Curry Powder (Kori Tozu)"), "blend")
        self.assertEqual(ay.category("Sausage seasoning"), "blend")
        self.assertEqual(ay.category("Oriental Mascot Chinese Pepper Powder"), "fruit")
        self.assertEqual(ay.category("Faiez Al Suhagy Safflower"), "unmapped")
        self.assertEqual(ay.category("Ground Barberry"), "unmapped")

    def test_blends(self):
        for name in ("Hot Jamaican Curry Powder", "Noor's Garam Masala Powder",
                     "Balqees Spices Yemeni Spices Mix", "Chief Brand Products 5 Spice Powder",
                     "Five Spices Powder", "Khmeli Suneli", "Humeli-Suneli", "Dry Adjika",
                     "Lucky Foods Georgian Dry Ajika", "Royal Mexican Spices", "Brown Spice"):
            self.assertEqual(ay.category(name), "blend", name)

    def test_non_spices_stay_unmapped(self):
        for name in ("Tequesquite", "TEQUESQUITE (Natural Mineral Salt)", "Hoja Santa (Saint Leaf)",
                     "La Bodeguita Achiote Annato", "Piment doux", "COMINO MOLIDO", "Anelina",
                     "CA RI NI AN DO KIM TU THAP", "Georgian Svanetian Salt", "Utskho Suneli"):
            self.assertEqual(ay.category(name), "unmapped", name)


class NycStore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = ay.nyc_store_rows()
        cls.raman = ay.raman_rows()
        cls.s = ay.score(cls.rows, cls.raman)

    def test_frame_size(self):
        self.assertEqual(len(self.rows), 477)
        self.assertEqual(sum(1 for r in self.rows if r["detected"]), 179)

    def test_detected_by_category(self):
        self.assertEqual(self.s["nyc_store"]["detected_by_category"],
                         {"root_rhizome": 26, "fruit": 42, "seed": 4, "flower_pistil": 7, "herb": 6,
                          "bud": 1, "bark": 22, "blend": 40, "unmapped": 31})

    def test_exceedances(self):
        got = {}
        for r in self.rows:
            if r["exceeds"]:
                got.setdefault(r["category"], []).append(int(r["row_id"]))
        for ids in got.values():
            ids.sort()
        self.assertEqual(got, {
            "root_rhizome": [167, 257, 674, 6102],
            "fruit": [1273, 2098, 4387, 5033, 5181],
            "flower_pistil": [1704, 1820, 1821, 1822, 1823, 2789, 5462],
            "seed": [6167],
            "herb": [6168],
            "bark": [7584, 7588, 7590, 7592, 7611, 7613, 7615, 7622, 7628, 7630, 8705],
            "blend": [1968, 2100, 3227, 3254, 4408, 4409, 4410, 5893, 6164, 6319, 6554, 8706],
        })
        n = self.s["nyc_store"]
        self.assertEqual((n["exceed_with_blends"], n["exceed_single_spice"], n["gross_ge50"]), (41, 29, 2))
        self.assertEqual((n["rate_with_blends"], n["rate_single_spice"]), (0.086, 0.0608))

    def test_level_is_strict(self):
        at_level = sorted(int(r["row_id"]) for r in self.rows
                          if r["detected"] and r["value"] == r["level"])
        self.assertEqual(at_level, [6573, 7582])  # paprika 0.6, cinnamon 2.0: not counted

    def test_cinnamon_and_saffron(self):
        bark = [r for r in self.rows if r["category"] == "bark"]
        self.assertEqual((len(bark), sum(1 for r in bark if r["exceeds"])), (25, 11))
        jan24 = [r for r in bark if 7582 <= int(r["row_id"]) <= 7663]
        self.assertEqual((len(jan24), sum(1 for r in jan24 if r["exceeds"])), (21, 10))
        saffron = [r for r in self.rows if r["category"] == "flower_pistil"]
        self.assertEqual((len(saffron), sum(1 for r in saffron if r["exceeds"])), (7, 7))


class RamanReach(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = ay.raman_rows()
        cls.s = ay.score(ay.nyc_store_rows(), cls.rows)["raman_reach"]

    def test_counts(self):
        self.assertEqual((self.s["n"], self.s["non_detects"]), (503, 340))
        self.assertEqual((self.s["exceed"], self.s["exceed_upper_bound"]), (163, 503))
        self.assertEqual(self.s["exceed_over_10"], 152)
        self.assertEqual(self.s["rate"], 0.3241)
        self.assertEqual(min(r["value"] for r in self.rows if r["detected"]), 3.0)


class Predictions(unittest.TestCase):
    def test_grades(self):
        p = ay.score(ay.nyc_store_rows(), ay.raman_rows())["predictions"]
        self.assertEqual(p["frame3_point_25_in_8_55"], {"with_blends": True, "single_spice": True})
        self.assertTrue(p["frame15_point_175_in_152_210"])
        self.assertEqual(p["H1_nyc_at_least_6"], {"with_blends": True, "single_spice": True})
        self.assertEqual(p["H2_raman_over_30pct_and_3x_nyc"], {"with_blends": True, "single_spice": True})
        self.assertFalse(p["H3_nyc_mostly_fruit_seed"])
        self.assertTrue(p["H3_raman_turmeric_far_above"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
