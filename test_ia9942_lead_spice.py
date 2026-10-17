"""Offline checks of ia9942_lead_spice 0.1.1 (no network).

The HTML fixture copies the layout of one Import Alert 99-42 Red List entry (labels,
spacing, product-code format) and adds made-up firms to exercise the parser and the
pre-registered grading rules. The 0.1.1 cases copy the live page's text lines, where
"Problems:" stands alone with its value on the next line. Apache-2.0. MV2 of Munim, Inc.
"""
import gzip
import os
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

# text lines of the live page as frozen on 2026-10-17 (first two firms verbatim), plus
# one made-up spice firm in the same layout
LIVE = ["AFGHANISTAN", "Arizo Zeba LLC", "Date Published : 03/30/2023",
        "Np.55170 Mandawi Kocha Baghbanan Markaz", ", Kabul,", "Kabul AFGHANISTAN",
        "33 G - - 05 Candy Bar or Pieces (not Caramel or Fondant), Soft, with Nuts or Nut Products (without Chocolate)",
        "Date Published: 03/30/2023", "Desc: Sour Candy Dried Fruit", "Problems:", "LEAD;",
        "Jan Aqa S/O Faqir Mohammad", "Date Published : 07/17/2025",
        "Line 1 Khosh Sediqyar Center Market , Unit Number: 129-68", ", Herat,", "Herat AFGHANISTAN",
        "33 E - - 06 Flavored Candy, Hard (Live Savers, Etc.), without Nuts and Fruit (without Chocolate)",
        "Date Published: 07/17/2025", "Desc: Sour Candy (Qurot)", "Problems:", "LEAD;",
        "33 E - - 12 Mixed/Assorted Hard Candy without Nuts and Fruit (without Chocolate)",
        "Date Published: 07/17/2025", "Desc: Sour Candy (Qurot)", "Problems:", "LEAD;",
        "BANGLADESH", "Spice Firm Ltd", "Date Published : 10/13/2022", "Road 3 , Dhaka,",
        "Dhaka BANGLADESH", "28 B - - 49 Turmeric, Ground, Cracked (Spice)",
        "Date Published: 10/13/2022", "Desc: Turmeric", "Notes: DWPE date: 12/02/2014",
        "Problems:", "CADMIUM; LEAD;"]


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

    def test_live_layout_problems_on_next_line(self):
        # 0.1.0 read the "LEAD;" under "Problems:" as the next firm's country heading
        parsed = ia.parse(LIVE)
        self.assertEqual(len(parsed), 4)
        self.assertEqual([p["problems"] for p in parsed], ["LEAD;", "LEAD;", "LEAD;", "CADMIUM; LEAD;"])
        self.assertEqual([p["country"] for p in parsed], ["AFGHANISTAN"] * 3 + ["BANGLADESH"])
        self.assertEqual(parsed[1]["firm"], "JAN AQA S/O FAQIR MOHAMMAD")
        fs = ia.firms(parsed)
        self.assertEqual(list(fs), [("BANGLADESH", "SPICE FIRM LTD")])
        self.assertEqual(fs[("BANGLADESH", "SPICE FIRM LTD")]["listing_date"], "2014-12-02")
        c = ia.check(LIVE, parsed, "99-42")
        self.assertEqual(c["problems_lines_in_text"], c["parsed_lines_with_problems"])
        self.assertEqual((c["firm_date_lines_in_text"], c["parsed_firm_blocks"]), (3, 3))
        self.assertEqual(len(ia.merge_fields(LIVE)), len(LIVE) - 4)

    def test_older_layout_one_problem_per_line(self):
        lines = ["CHINA", "Herb Trading Co.", "Date Published : 11/24/2021", "1 Road , Nanhai District",
                 ", Foshan,", "Yandong CHINA", "54 F - - 03 Angelica (Herbal & Botanicals, not Teas)",
                 "Date Published: 11/24/2021", "Desc: Angelicae Sinensis", "Problems:", "CADMIUM;",
                 "LEAD;", "54 - - - -- Vit/Min/Prot/Unconv Diet(Human/Animal)",
                 "Date Published: 11/24/2021", "Desc: pills", "Problems:", "LEAD;", "INDIA"]
        parsed = ia.parse(lines)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["problems"], "CADMIUM; LEAD;")
        self.assertEqual((parsed[1]["code"], parsed[1]["industry"]), ("54-----", "54"))

    def test_dwpe_date_separators(self):
        # every separator found after "DWPE date" in the live page's Notes
        for notes, iso in (("DWPE Date-9/25/2019", "2019-09-25"), ("DWPE date - 3/14/2002", "2002-03-14"),
                           ("DWPE date- 2/14/2020", "2020-02-14"), ("Original DWPE date; 3/27/2007", "2007-03-27"),
                           ("Firm is subject to DWPE when declared as Manufacturer or Shipper. DWPE date; 07/29/2019",
                            "2019-07-29"), ("DWPE date: 08/23/2019", "2019-08-23")):
            self.assertEqual(ia.listing_date({"notes": notes, "date_published": "2022-10-13"}), iso)
        self.assertEqual(ia.listing_date({"notes": "Listing moved from deactivated IA 15-01",
                                          "date_published": "2022-10-13"}), "2022-10-13")

    def test_alert_2813_counts_every_spice_line(self):
        line = {"industry": "28", "problems": "", "desc": "ground turmeric", "notes": "", "product": "Turmeric"}
        self.assertTrue(ia.is_lead_spice(line, True, "28-13"))
        self.assertFalse(ia.is_lead_spice(line, True, "99-42"))
        self.assertFalse(ia.is_lead_spice(dict(line, industry="50"), True, "28-13"))

    def test_union_and_without(self):
        a = {("INDIA", "X LTD"): dict(firm("INDIA", "2019-01-01", ["turmeric"]), firm="X LTD")}
        b = {("INDIA", "X LTD"): dict(firm("INDIA", "2017-05-05", ["chili"]), firm="X LTD"),
             ("CHINA", "Y"): dict(firm("CHINA", "2018-01-01", ["cinnamon"]), firm="Y")}
        u = ia.union(a, b)
        self.assertEqual(len(u), 2)
        self.assertEqual(u[("INDIA", "X LTD")]["listing_date"], "2017-05-05")
        self.assertEqual(u[("INDIA", "X LTD")]["tags"], {"turmeric", "chili"})
        late = {("INDIA", "X LTD."): dict(firm("INDIA", "2022-01-01", ["turmeric"]), firm="X LTD."),
                ("PERU", "Z"): dict(firm("PERU", "2022-01-01", ["other"]), firm="Z")}
        self.assertEqual(list(ia.without(late, b)), [("PERU", "Z")])

    def test_gzip_decode(self):
        self.assertEqual(ia.decode(gzip.compress("Import Alert # 28-13".encode())), "Import Alert # 28-13")
        self.assertEqual(ia.decode(b"plain"), "plain")

    def test_spice_tags(self):
        self.assertEqual(ia.spice_tags("Chilli powder"), ["chili"])
        self.assertEqual(ia.spice_tags("Paprika, Ground"), ["chili"])
        self.assertEqual(ia.spice_tags("Curry Powder with turmeric"), ["turmeric", "curry_masala"])
        self.assertEqual(ia.spice_tags("Clove"), ["other"])


SCOPE_2021 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data",
                          "ia9942_wayback_20211205053251.txt")


@unittest.skipUnless(os.path.exists(SCOPE_2021), "frozen 2021 copy not present (compute workdir)")
class TestScope2021(unittest.TestCase):
    """The December 2021 copy of 99-42 sends lead in spices to Import Alert 28-13."""

    def test_no_spice_lines_and_28_13_scope(self):
        with open(SCOPE_2021, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        scope = "Spice and spice products containing lead fall under the scope of Import Alert 28-13."
        self.assertTrue(any(scope in l for l in lines))
        parsed = ia.parse(lines)
        c = ia.check(lines, parsed, "99-42")
        self.assertEqual(c["alert_on_page"], "99-42")
        self.assertEqual(len(parsed), 156)
        self.assertEqual((c["firm_date_lines_in_text"], c["parsed_firm_blocks"]), (17, 17))
        self.assertEqual(c["problems_lines_in_text"], c["parsed_lines_with_problems"])
        self.assertEqual(c["industry28_lines"], 0)
        self.assertEqual(ia.firms(parsed), {})


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
        self.assertEqual(g["E_by_country"], {"INDIA": 3, "BANGLADESH": 1})

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
