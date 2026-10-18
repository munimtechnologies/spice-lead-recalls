# SPDX-License-Identifier: Apache-2.0
# Offline tests for raman_reach.py on small synthetic tables (no PDF, no network).
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


if __name__ == "__main__":
    unittest.main()
