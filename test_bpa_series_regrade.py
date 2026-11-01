#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for bpa_series_regrade.py (no network, no CFIA data). Made with AI agents working
in MV2's (Munim, Inc.) name."""
import unittest

import bpa_series_grade as g
import bpa_series_regrade as r

PUBLISHED = g.ID_RE.pattern          # captured at import, before any test calls apply()
OBSERVED = ["2009BPA%d" % n for n in range(176, 184)] + [
    "2011BPA0086-2", "2011BPA0270-2", "2011BPA0272-2"]
ACCEPTED_BEFORE = ["2009BPA0001", "2009BPA00065", "2011BPA0086", "C2012BPHA00270",
                   "C2013BHPA00319D", "C2016BPHA00420", "C2017BPHA00234"]
STILL_REJECTED = ["", "2009BPA17", "2011BPA0086-3", "2011BPA0086-2D", "X2009BPA0001",
                  "2009BPA0001 ", "C2012BPHA0027000", "2011BPA0086-"]


def toy(sid, product="Carrot", date="d", bpa=0.0):
    return {"sample": sid, "product": product, "date": date, "ppb": {"bpa": bpa}}


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
        self.assertEqual(r.base_id("2011BPA0086-2"), "2011BPA0086")
        self.assertEqual(r.base_id("2009BPA176"), "2009BPA176")

    def test_old_rejects(self):
        samples = [toy("2011BPA0086-2"), toy("2009BPA0001"), toy("2009BPA176")]
        self.assertEqual(r.old_rejects(samples), ["2009BPA176", "2011BPA0086-2"])

    def test_suffix_report(self):
        samples = [toy("2011BPA0086", "Carrot", "d1", 0.0),
                   toy("2011BPA0086-2", "Carrot", "d2", 5.0),
                   toy("2011BPA0270-2", "Corn", "d3", 0.0)]
        rep = r.suffix_report(samples)
        self.assertEqual([x["sample"] for x in rep], ["2011BPA0086-2", "2011BPA0270-2"])
        self.assertTrue(rep[0]["base_present"])
        self.assertEqual((rep[0]["base_product"], rep[0]["base_date"], rep[0]["base_bpa_ppb"]),
                         ("Carrot", "d1", 0.0))
        self.assertEqual(rep[0]["bpa_ppb"], 5.0)
        self.assertFalse(rep[1]["base_present"])
        self.assertIsNone(rep[1]["base_product"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
