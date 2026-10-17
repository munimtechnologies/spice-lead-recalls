"""Offline checks of ia9942_lead_spice 0.1.0 (no network).

The HTML fixture copies the layout of one Import Alert 99-42 Red List entry (labels,
spacing, product-code format) and adds made-up firms to exercise the parser and the
pre-registered grading rules. Apache-2.0. MV2 of Munim, Inc.
"""
import unittest

import ia9942_lead_spice as ia

FIXTURE = """<html><body>
<p>List of firms and their products subject to Detention without Physical Examination (DWPE) under this Import Alert</p>
<div><b>BANGLADESH</b></div>
<div>FIRM ONE LTD</div><div>Date Published : 10/13/2022</div>
<div>Road 1 , Dhaka, BANGLADESH</div>
<div><i>28 A - - 49</i> Turmeric, Whole (Spice)</div><div>Date Published: 10/13/2022</div>
<div>Desc: Turmeric</div><div>Notes: DWPE date: 12/02/2014</div><div>Problems: LEAD;</div>
<div><i>28 B - - 49</i> Turmeric, Ground, Cracked (Spice)</div><div>Date Published: 10/13/2022</div>
<div>Desc: Turmeric</div><div>Notes: DWPE date: 12/02/2014</div><div>Problems: LEAD;</div>
<div><i>50 L - - 29</i> Turmeric</div><div>Date Published: 10/13/2022</div>
<div>Desc: Turmeric</div><div>Notes: DWPE date: 12/02/2014</div><div>Problems: LEAD;</div>
<div>FIRM TWO LTD</div><div>Date Published : 05/05/2018</div>
<div>Road 2, Khulna, BANGLADESH</div>
<div><i>28 B - - 49</i> Turmeric, Ground, Cracked (Spice)</div><div>Date Published: 05/05/2018</div>
<div>Desc: turmeric powder</div><div>Problems: LEAD;</div>
<div><b>Burma (Myanmar)</b></div>
<div>FIRM THREE</div><div>Date Published : 03/03/2023</div>
<div>Yangon, MYANMAR</div>
<div><i>28 B - - 07</i> Cinnamon, Ground, Cracked (Spice)</div><div>Date Published: 03/03/2023</div>
<div>Desc: cassia powder</div><div>Problems: LEAD; CHROMIUM;</div>
<div><i>21 T - - 99</i> Dried fruit</div><div>Date Published: 03/03/2023</div>
<div>Desc: raisins</div><div>Problems: LEAD;</div>
<div>CHINA</div>
<div>FIRM FOUR</div><div>Date Published : 06/06/2024</div>
<div>Guangxi, CHINA</div>
<div><i>28 B - - 07</i> Cinnamon, Ground, Cracked (Spice)</div><div>Date Published: 06/06/2024</div>
<div>Desc: cinnamon &amp; cassia</div><div>Problems: CADMIUM;</div>
</body></html>"""


def firm(country, date, tags):
    return {"country": country, "firm": country + date, "listing_date": date,
            "tags": set(tags), "n_lines": 1}


class TestParse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lines = ia.parse(ia.html_to_lines(FIXTURE))

    def test_product_lines(self):
        self.assertEqual(len(self.lines), 7)
        first = self.lines[0]
        self.assertEqual(first["code"], "28A--49")
        self.assertEqual(first["industry"], "28")
        self.assertEqual(first["country"], "BANGLADESH")
        self.assertEqual(first["firm"], "FIRM ONE LTD")
        self.assertEqual(first["date_published"], "2022-10-13")
        self.assertEqual(first["problems"], "LEAD;")
        self.assertEqual(ia.listing_date(first), "2014-12-02")

    def test_heading_country_and_address_country(self):
        three = [l for l in self.lines if l["firm"] == "FIRM THREE"]
        self.assertEqual({l["country"] for l in three}, {"BURMA (MYANMAR)"})
        self.assertEqual({l["address_country"] for l in three}, {"MYANMAR"})
        two = [l for l in self.lines if l["firm"] == "FIRM TWO LTD"]
        self.assertEqual({l["country"] for l in two}, {"BANGLADESH"})

    def test_listing_date_falls_back_to_date_published(self):
        two = next(l for l in self.lines if l["firm"] == "FIRM TWO LTD")
        self.assertEqual(ia.listing_date(two), "2018-05-05")

    def test_lead_spice_firms(self):
        fs = ia.firms(self.lines)
        self.assertEqual(sorted(k[1] for k in fs), ["FIRM ONE LTD", "FIRM THREE", "FIRM TWO LTD"])
        one = fs[("BANGLADESH", "FIRM ONE LTD")]
        self.assertEqual(one["n_lines"], 2)          # the industry-50 line is not a spice line
        self.assertEqual(one["listing_date"], "2014-12-02")
        self.assertEqual(one["tags"], {"turmeric"})
        three = fs[("BURMA (MYANMAR)", "FIRM THREE")]
        self.assertEqual(three["n_lines"], 1)        # dried fruit (industry 21) is excluded
        self.assertEqual(three["tags"], {"cinnamon"})

    def test_code_and_product_on_two_lines(self):
        lines = ["INDIA", "FIRM FIVE", "Date Published : 01/02/2020", "Kochi, INDIA",
                 "28 B - - 49", "Turmeric, Ground, Cracked (Spice)", "Date Published: 01/02/2020",
                 "Desc: haldi", "Problems: LEAD;"]
        parsed = ia.parse(lines)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["product"], "Turmeric, Ground, Cracked (Spice)")
        self.assertEqual((parsed[0]["firm"], parsed[0]["country"]), ("FIRM FIVE", "INDIA"))
        self.assertEqual(ia.listing_date(parsed[0]), "2020-01-02")

    def test_spice_tags(self):
        self.assertEqual(ia.spice_tags("Chilli powder"), ["chili"])
        self.assertEqual(ia.spice_tags("Paprika, Ground"), ["chili"])
        self.assertEqual(ia.spice_tags("Curry Powder with turmeric"), ["turmeric", "curry_masala"])
        self.assertEqual(ia.spice_tags("Clove"), ["other"])


class TestGrade(unittest.TestCase):
    def test_rules(self):
        early = {i: firm("INDIA", "2017-01-01", ["turmeric"]) for i in range(3)}
        early["g"] = firm("BANGLADESH", "2019-01-01", ["chili"])
        early["old"] = firm("INDIA", "2012-01-01", ["cinnamon"])   # outside both periods
        late = {i: firm("INDIA", "2024-01-01", ["cinnamon"]) for i in range(7)}
        late["t"] = firm("INDIA", "2022-01-01", ["turmeric"])
        g = ia.grade(early, late, "test")
        self.assertTrue(g["gradable"])
        self.assertEqual((g["E"], g["L"]), (4, 8))
        self.assertTrue(g["P1_L_greater_than_E"]["met"])
        self.assertTrue(g["P2_L_at_least_2E"]["met"])
        self.assertTrue(g["P3_cinnamon_top_spice_in_L"]["met"])
        self.assertTrue(g["P4_turmeric_top_spice_in_E"]["met"])
        self.assertTrue(g["P5_no_georgia_firm_in_E"]["met"])
        self.assertEqual(g["n_met"], 5)

    def test_ties_and_georgia(self):
        early = {"a": firm("GEORGIA", "2018-01-01", ["turmeric"]),
                 "b": firm("INDIA", "2018-01-01", ["chili"])}
        late = {"c": firm("CHINA", "2023-01-01", ["cinnamon"])}
        g = ia.grade(early, late, "test")
        self.assertFalse(g["gradable"])
        self.assertIsNone(g["P1_L_greater_than_E"]["met"])
        self.assertFalse(g["P4_turmeric_top_spice_in_E"]["met"])   # tie is not "top"
        self.assertFalse(g["P5_no_georgia_firm_in_E"]["met"])


if __name__ == "__main__":
    unittest.main()
