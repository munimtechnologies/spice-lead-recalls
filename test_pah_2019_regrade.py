#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for pah_2019_regrade.py (no network, no CFIA data). Made with AI agents working
in MV2's (Munim, Inc.) name."""
import unittest

import pah_2019 as g
import pah_2019_regrade as r

PUBLISHED = g.ID_RE.pattern          # captured at import, before any test calls apply()
OBSERVED = ["C2019PAHS00037AD", "C2019PAHS00040AD"]
ACCEPTED_BEFORE = ["C2019PAHS00001A", "C2019PAHS00037A", "C2019PAHS00296A"]
STILL_REJECTED = ["", "C2019PAHS00037", "C2019PAHS00037ADD", "C2019PAHS0037AD",
                  "C2019PAHS00037D", "C2018PAHS00037AD", "C2019PAHS00037AD "]


def toy(sid, teq, bap=0.0, product="Oil - Olive"):
    vals = {c: 0.0 for c in g.COMPONENTS}
    vals["Benzo[a]pyrene"] = bap
    return {"sample": sid, "product": product, "function": "Import", "origin": "ITALY",
            "date": "d", "teq": teq, "vals": vals}


class TestPattern(unittest.TestCase):
    def test_old_pattern_is_the_published_one(self):
        self.assertEqual(r.OLD_ID_RE.pattern, PUBLISHED)

    def test_observed_ids_rejected_before_and_accepted_now(self):
        for sid in OBSERVED:
            self.assertIsNone(r.OLD_ID_RE.match(sid), sid)
            self.assertIsNotNone(r.ID_RE.match(sid), sid)

    def test_everything_accepted_before_is_still_accepted(self):
        for sid in ACCEPTED_BEFORE:
            self.assertIsNotNone(r.OLD_ID_RE.match(sid), sid)
            self.assertIsNotNone(r.ID_RE.match(sid), sid)

    def test_other_shapes_still_rejected(self):
        for sid in STILL_REJECTED:
            self.assertIsNone(r.ID_RE.match(sid), repr(sid))

    def test_apply_patches_the_grader(self):
        self.assertIs(r.apply(), r.ID_RE)
        self.assertIs(g.ID_RE, r.ID_RE)


class TestReports(unittest.TestCase):
    def test_base_id(self):
        self.assertEqual(r.base_id("C2019PAHS00037AD"), "C2019PAHS00037A")
        self.assertEqual(r.base_id("C2019PAHS00037A"), "C2019PAHS00037A")

    def test_suffix_report(self):
        samples = [toy("C2019PAHS00037A", 0.5, 0.5), toy("C2019PAHS00037AD", 0.5, 0.5),
                   toy("C2019PAHS00040AD", 0.2, 0.2), toy("C2019PAHS00041A", 0.0)]
        rep = r.suffix_report(samples)
        self.assertEqual([x["sample"] for x in rep], ["C2019PAHS00037AD", "C2019PAHS00040AD"])
        self.assertTrue(rep[0]["base_present"])
        self.assertTrue(rep[0]["identical_16"])
        self.assertEqual(rep[0]["base"], "C2019PAHS00037A")
        self.assertFalse(rep[1]["base_present"])
        self.assertIsNone(rep[1]["identical_16"])

    def test_profiles_differ(self):
        a, b = toy("C2019PAHS00037A", 0.5, 0.5), toy("C2019PAHS00037AD", 0.4, 0.4)
        self.assertEqual(r.suffix_report([a, b])[0]["identical_16"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
