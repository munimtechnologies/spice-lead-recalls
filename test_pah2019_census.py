#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for pah2019_census.py (no network, no data). Made with AI agents working in MV2's
(Munim, Inc.) name. Code Apache-2.0."""
import unittest
from unittest import mock

import cfia_census as cc
import pah2019_census as p


class TestTarget(unittest.TestCase):
    def test_same_target_as_the_published_census(self):
        t = p.target()
        self.assertEqual(t["dataset"], "4884f9d1-0a59-4c8e-85ca-157d13411d19")
        self.assertEqual(t["resource"], "d5b3cca2-4ccf-4aed-a4d1-0af540422575")
        self.assertEqual((t["size"], t["md5"]), (831190, "0bb033bbcdab8305839d0a8716def1b3"))


class TestRetries(unittest.TestCase):
    def test_retries_until_the_file_is_read(self):
        calls = []

        def fake(target, data_dir):
            calls.append(target["name"])
            return {"error": "reset"} if len(calls) < 3 else {"census": {"rows": 1}}

        with mock.patch.object(cc, "run_target", fake):
            res, n = p.census_with_retries("/nowhere", tries=5, pause=0)
        self.assertEqual(n, 3)
        self.assertEqual(calls, ["pah-2019"] * 3)
        self.assertTrue(p.ok(res))
        self.assertEqual((res["attempts"], res["earlier_errors"]), (3, ["reset", "reset"]))

    def test_gives_up_after_the_last_try(self):
        with mock.patch.object(cc, "run_target", lambda t, d: {"error": "reset"}):
            res, n = p.census_with_retries("/nowhere", tries=2, pause=0)
        self.assertEqual(n, 2)
        self.assertFalse(p.ok(res))
        self.assertEqual(res["attempts"], 2)

    def test_a_census_error_is_not_ok(self):
        self.assertFalse(p.ok({"census": {"error": "missing key column"}}))
        self.assertTrue(p.ok({"census": {"rows": 4736}}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
