# SPDX-License-Identifier: Apache-2.0
# Offline tests for raman_reach.py on small synthetic tables (no PDF, no network).
import json
import os
import tempfile
import unittest

import raman_reach as rr

MU = "µ"


def _rows():
    return [
        ["Supplementary Table 8. Lead in turmeric", None, None, None, None, None],
        ["Sample", "State", "City", "Form", "Pb (%sg/g)" % MU, "Cr (%sg/g)" % MU],
        ["1", "Bihar", "Patna", "Loose powder", "6,416", "1,610"],
        ["2", "", "Patna", "Double polished root", "<LOD", "ND"],
        ["3", "WB", "Kolkata", "Packaged powder", "8", "12"],
        ["Sample", "State", "City", "Form", "Pb (%sg/g)" % MU, "Cr (%sg/g)" % MU],
        ["4", "Jharkhand", "Ranchi", "Chilli powder", "40", "10"],
        ["5", "Bihar"],
    ]


def _r(pb, state="Bihar", form="root_single", cr=None, turmeric=True, purposive=False):
    return {"row": 0, "state": state, "city": "", "market": "", "form_class": form, "pb": float(pb), "cr": cr,
            "cr_detected": cr is not None and cr > 0, "turmeric": turmeric, "purposive": purposive}


def _base():
    recs = [_r(0, "West Bengal", "packaged_powder") for _ in range(350)]
    recs.append(_r(6416, "Bihar", "loose_powder"))
    recs += [_r(1000, "Bihar", "root_double") for _ in range(4)]
    recs += [_r(50, "Bihar", "root_single", cr=12.5) for _ in range(148)]
    recs.append(_r(9000, purposive=True))
    recs.append(_r(573, turmeric=False))
    return recs


S8_TEXT = "\n".join([
    "153",
    "154 Table S8. Turmeric market sample data used in analyses (n=503). All_pb_avg: average sample",
    "sampid_ city_final all_pb_avg type_groupfull4 sellstate_bin turm_major",
    "36_MC_3_1_1 Buxar 6416 1 1 1",
    "26_GM_1_2_4 Muzzafarpur 1287 3 1",
    "42_MB_3_1_2 Deoghar 240 2 0 1",
    "50_KD-1-2-5 Ambikapur 10 4 0",
    "15",
    "6_BB_1_1_2 Kolkata 2 2 0 1",
    "18_RG_2_1_1 Lucknow 2 1 0 0",
    "18_RG_2_1_1 Lucknow 2 1 0 1",
    "160",
    "197 1 Loose Powder",
])


def _s8_lines():
    lines = ["154 Table S8. Turmeric market sample data", " ".join(rr.S8_HEADER)]
    lines.append("1_A_1 Buxar 6416 1 1 1")
    lines += ["2_A_%d Deoghar 4000 3 0 1" % i for i in range(15)]
    lines += ["3_A_%d Patna 1000 3 1 1" % i for i in range(89)]
    lines += ["4_A_%d Varanasi 50 4 0 1" % i for i in range(47)]
    lines.append("5_A_1 Ambikapur 10 4 0")
    lines += ["6_A_%d Kolkata 2 2 0 1" % i for i in range(350)]
    return lines


class ValueTests(unittest.TestCase):
    def test_numbers(self):
        self.assertEqual(rr.parse_value("6,416"), (6416.0, True))
        self.assertEqual(rr.parse_value("6,416 %sg/g" % MU), (6416.0, True))
        self.assertEqual(rr.parse_value("12.5 ± 1.3"), (12.5, True))
        self.assertEqual(rr.parse_value("48*"), (48.0, True))

    def test_below_and_missing(self):
        self.assertEqual(rr.parse_value("<LOD"), (0.0, False))
        self.assertEqual(rr.parse_value("ND"), (0.0, False))
        self.assertEqual(rr.parse_value("0"), (0.0, False))
        self.assertIsNone(rr.parse_value(""))
        self.assertIsNone(rr.parse_value(None))
        self.assertIsNone(rr.parse_value("-"))
        self.assertIsNone(rr.parse_value("Bihar"))


class HeaderTests(unittest.TestCase):
    def test_find_header_skips_caption(self):
        self.assertEqual(rr.find_header(_rows()), 1)

    def test_roles(self):
        roles = rr.roles_from_header(_rows()[1])
        self.assertEqual((roles["pb"], roles["cr"], roles["state"], roles["city"], roles["form"]), (4, 5, 1, 2, 3))
        self.assertEqual(roles["pb_factor"], 1.0)

    def test_role_preferences(self):
        roles = rr.roles_from_header(["ID", "Pb SD", "Pb mean (ppm)", "Pb:Cr ratio", "Cr (ppb)"])
        self.assertEqual(roles["pb"], 2)
        self.assertEqual(roles["cr"], 4)
        self.assertEqual(roles["pb_factor"], 1.0)
        self.assertEqual(roles["cr_factor"], 0.001)
        self.assertIsNone(rr.roles_from_header(["Sample", "City", "Form"]))

    def test_states_and_markers(self):
        self.assertEqual(rr.norm_state("Chattisgarh"), "Chhattisgarh")
        self.assertEqual(rr.norm_state("UP"), "Uttar Pradesh")
        self.assertEqual(rr.find_state("Patna, Bihar"), "Bihar")
        self.assertTrue(rr.PURPOSIVE.search("Dec 2023 truck"))
        self.assertFalse(rr.PURPOSIVE.search("June 2023"))


class RecordTests(unittest.TestCase):
    def test_build(self):
        rows = _rows()
        recs, skipped = rr.build_records(rows, 1, rr.roles_from_header(rows[1]))
        self.assertEqual(len(recs), 4)
        self.assertEqual([r["pb"] for r in recs], [6416.0, 0.0, 8.0, 40.0])
        self.assertEqual([r["state"] for r in recs], ["Bihar", "Bihar", "West Bengal", "Jharkhand"])
        self.assertEqual([r["form_class"] for r in recs],
                         ["loose_powder", "root_double", "packaged_powder", "loose_powder"])
        self.assertEqual([r["turmeric"] for r in recs], [True, True, True, False])
        self.assertFalse(recs[1]["pb_detected"])
        self.assertEqual(recs[0]["cr"], 1610.0)
        self.assertEqual(skipped, {"length-2": 1})


class GradeTests(unittest.TestCase):
    def test_all_met(self):
        g = rr.grade(_base(), {"pb": 0, "cr": 1})
        self.assertEqual([g["P%d" % i]["result"] for i in range(1, 10)], ["met"] * 9)
        self.assertEqual(g["P4"]["detail"], "1 of 153 above-limit samples at or above 3,200 ug/g")

    def test_raman_share_too_high(self):
        recs = _base()
        for r in [r for r in recs if r["pb"] == 50][:20]:
            r["pb"] = 4000.0
        g = rr.grade(recs, {"pb": 0, "cr": 1})
        self.assertEqual(g["P4"]["result"], "not met")
        self.assertEqual(g["P5"]["result"], "met")

    def test_gate(self):
        g = rr.grade(_base()[100:], {"pb": 0, "cr": 1})
        self.assertEqual(g["P1"]["result"], "not met")
        self.assertEqual(g["P2"]["result"], "not graded (gate failed)")

    def test_no_chromium_column(self):
        self.assertEqual(rr.grade(_base(), {"pb": 0})["P9"]["result"], "not gradable")

    def test_outputs(self):
        recs = _base()
        roles = {"pb": 0, "cr": 1}
        g = rr.grade(recs, roles)
        with tempfile.TemporaryDirectory() as d:
            met, gradable = rr.write_outputs(d, recs, roles, g, {"sha256": "x", "method": "lines", "pages": [3],
                                                                 "header": ["a", "b"]})
            self.assertEqual((met, gradable), (9, 9))
            for name in ("summary.md", "grades.json", "raman_reach_samples.csv"):
                self.assertTrue(os.path.exists(os.path.join(d, name)))
            with open(os.path.join(d, "summary.md"), encoding="utf-8") as f:
                self.assertIn("reaches 1 of the 153 samples", f.read())


class S8ParserTests(unittest.TestCase):
    """0.1.1: deviations D1-D4 (docs/raman-reach-0.1.1-deviation.md)."""

    def test_captions_with_line_numbers(self):
        self.assertTrue(rr.CAPTION_8.search("154 Table S8. Turmeric market sample data"))
        self.assertTrue(rr.CAPTION_ANY.match("62 Figure S1. Turmeric value chain map."))
        self.assertFalse(rr.CAPTION_8.search("153 Table S7. Grade-wise turmeric"))

    def test_header_roles(self):
        roles = rr.roles_from_header(rr.S8_HEADER)
        self.assertEqual((roles["pb"], roles["city"], roles["form"]), (2, 1, 3))
        self.assertEqual(roles["pb_factor"], 1.0)
        self.assertNotIn("state", roles)
        self.assertNotIn("cr", roles)
        self.assertEqual(rr.pb_score("all_pb_avg"), 3)

    def test_records(self):
        lines = S8_TEXT.splitlines()
        self.assertEqual(rr.find_s8_header(lines), 2)
        recs = rr.build_s8_records(lines, 2)
        self.assertEqual(len(recs), 7)
        self.assertEqual([r["pb"] for r in recs], [6416.0, 1287.0, 240.0, 10.0, 2.0, 2.0, 2.0])
        self.assertEqual([r["state_city_map"] for r in recs],
                         ["Bihar", "Bihar", "Jharkhand", "Chhattisgarh", "West Bengal", "Uttar Pradesh",
                          "Uttar Pradesh"])
        self.assertEqual([r["state"] for r in recs], [""] * 7)
        self.assertEqual([r["form_class"] for r in recs], ["unknown"] * 7)
        self.assertEqual([r["form_class_counts"] for r in recs],
                         ["loose_powder", "root_double", "packaged_powder", "root_single", "packaged_powder",
                          "loose_powder", "loose_powder"])
        self.assertEqual([r["form_class_caption"] for r in recs],
                         ["loose_powder", "unknown", "packaged_powder", "root_double", "packaged_powder",
                          "loose_powder", "loose_powder"])
        self.assertEqual([r["turm_major"] for r in recs], ["1", "", "1", "", "1", "0", "1"])
        self.assertEqual(recs[3]["sample"], "50_KD-1-2-5")

    def test_checks(self):
        lines = S8_TEXT.splitlines()
        c = rr.s8_checks(rr.build_s8_records(lines, 2))
        self.assertEqual(c["state_n"], {"Bihar": 2, "Jharkhand": 1, "Chhattisgarh": 1, "West Bengal": 1,
                                        "Uttar Pradesh": 2})
        self.assertFalse(c["state_n_matches_table_s2"])
        self.assertEqual(c["sellstate_agrees"], 7)
        self.assertEqual(c["form_code_n"], {"1": 3, "3": 1, "2": 2, "4": 1})
        self.assertEqual(c["repeated_sample_ids"], ["18_RG_2_1_1"])
        self.assertEqual(c["pb_exactly_10"], 1)
        self.assertEqual(c["unmapped_cities"], [])

    def test_readings(self):
        lines = _s8_lines()
        recs = rr.build_s8_records(lines, rr.find_s8_header(lines))
        self.assertEqual(len(recs), 503)
        frozen = rr.grade(rr.reading(recs, None, None), rr.S8_ROLES)
        self.assertEqual(frozen["P2"]["detail"], "152 samples above 10 ug/g")
        self.assertEqual(frozen["P3"], {"result": "not gradable", "detail": "highest 6,416.0 ug/g, state unknown"})
        self.assertEqual(frozen["P4"], {"result": "not met",
                                        "detail": "16 of 152 above-limit samples at or above 3,200 ug/g"})
        self.assertEqual(frozen["P5"], {"result": "not met", "detail": "median lead in E 1,000.0 ug/g"})
        self.assertEqual(frozen["P6"]["detail"], "105 samples at or above 500 ug/g, 105 without a state")
        self.assertEqual(frozen["P8"], {"result": "not gradable", "detail": "0 packaged powders"})
        a = rr.grade(rr.reading(recs, "state_city_map", "form_class_counts"), rr.S8_ROLES)
        self.assertEqual(a["P3"]["result"], "met")
        self.assertEqual(a["P6"], {"result": "met", "detail": "90 of 105 samples at or above 500 ug/g from Bihar"})
        self.assertEqual(a["P7"], {"result": "met", "detail": "104 roots, 1 powders at or above 500 ug/g"})
        self.assertEqual(a["P8"], {"result": "met", "detail": "0 of 350 packaged powders above 100 ug/g"})
        self.assertEqual(a["P9"]["result"], "not gradable")
        b = rr.grade(rr.reading(recs, "state_city_map", "form_class_caption"), rr.S8_ROLES)
        self.assertEqual(b["P7"], {"result": "not gradable",
                                   "detail": "1 samples at or above 500 ug/g with a known form"})

    def test_s8_outputs(self):
        lines = _s8_lines()
        recs = rr.build_s8_records(lines, rr.find_s8_header(lines))
        with tempfile.TemporaryDirectory() as d:
            res = rr.write_s8_outputs(d, recs, {"sha256": "x", "method": "s8-text-lines", "pages": [15],
                                                "header": list(rr.S8_HEADER)})
            self.assertEqual(res, {"frozen": (2, 4), "A": (6, 8), "B": (5, 7)})
            with open(os.path.join(d, "summary.md"), encoding="utf-8") as f:
                text = f.read()
            self.assertIn("reaches 16 of the 152 samples", text)
            self.assertIn("- A: 6 of 8 gradable predictions met.", text)
            with open(os.path.join(d, "grades.json"), encoding="utf-8") as f:
                g = json.load(f)
            self.assertEqual(g["checks"]["pb_exactly_10"], 1)
            with open(os.path.join(d, "raman_reach_samples.csv"), encoding="utf-8") as f:
                self.assertEqual(len(f.read().splitlines()), 504)


if __name__ == "__main__":
    unittest.main()
