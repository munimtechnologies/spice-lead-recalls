# SPDX-License-Identifier: Apache-2.0
"""Tests for the cfia-open-data-errata agent skill 0.2.0 (skills/cfia-open-data-errata/).

Checks that SKILL.md is a valid skill file, that every command it documents parses and finds
items, that every item ID it cites is in data/cfia-open-data-errata.csv, that the lookup
script's filters return the counts hand-counted from that table, and that the skill works
offline: its bundled table is byte-identical to the repository's, a copy of the skill folder
installed on its own reads it, and the default path never opens a network connection.
Standard library only; no network.
Made with AI agents working in MV2's (Munim, Inc.) name.
"""
import contextlib
import importlib.util
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.join(HERE, "skills", "cfia-open-data-errata")
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")
SCRIPT = os.path.join(SKILL_DIR, "scripts", "cfia_errata.py")
BUNDLED = os.path.join(SKILL_DIR, "data", "cfia-open-data-errata.csv")
CSV = os.path.join(HERE, "data", "cfia-open-data-errata.csv")
NOTE_BASE = "https://github.com/munimtechnologies/spice-lead-recalls/blob/main/docs/"
STREET = re.compile(r"\b\d{1,5}\s+[A-Z][a-z]+\s+(Road|Street|Avenue|Lane|Drive|Boulevard)\b")
EXAMPLE_IDS = ["ec-2018-1000x", "cfp-afm1-2014-unit", "fum-2010-b2-first-56",
               "perc-avg-conventions", "ph-2015-rates", "fum-2011-min", "bpa-2011-ids",
               "fum-2018-d-numbers", "bpa-2009-dates"]


def load_module():
    spec = importlib.util.spec_from_file_location("cfia_errata", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read().replace("\r\n", "\n")


def frontmatter(text):
    lines = text.split("\n")
    assert lines[0] == "---", "SKILL.md must start with ---"
    end = lines.index("---", 1)
    fields = {}
    for line in lines[1:end]:
        key, _, value = line.partition(": ")
        fields[key] = value
    return fields, "\n".join(lines[end + 1:])


def run_main(mod, argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = mod.main(argv)
    return code, buf.getvalue()


def install_copy(tmp):
    """Copy the skill folder on its own, the way a skills installer places it in a project."""
    dest = os.path.join(tmp, ".claude", "skills", "cfia-open-data-errata")
    shutil.copytree(SKILL_DIR, dest, ignore=shutil.ignore_patterns("__pycache__"))
    return dest


class SkillFile(unittest.TestCase):
    def setUp(self):
        self.text = read(SKILL_MD)
        self.fields, self.body = frontmatter(self.text)

    def test_frontmatter(self):
        self.assertEqual(self.fields["name"], "cfia-open-data-errata")
        self.assertEqual(self.fields["name"], os.path.basename(SKILL_DIR))
        self.assertRegex(self.fields["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
        desc = self.fields["description"]
        self.assertTrue(desc.startswith("Use when"))
        self.assertLessEqual(len(desc), 1024)
        self.assertNotIn(": ", desc)
        self.assertNotIn("<", desc)
        self.assertEqual(self.fields["license"], "Apache-2.0")
        self.assertEqual(set(self.fields), {"name", "description", "license"})

    def test_cited_ids_exist(self):
        ids = {r["item_id"] for r in load_module().load(CSV)}
        for item in EXAMPLE_IDS:
            self.assertIn("`" + item + "`", self.body, item)
            self.assertIn(item, ids, item)

    def test_documented_commands_parse_and_match(self):
        mod = load_module()
        cmds = [ln.strip() for ln in self.body.split("\n")
                if ln.strip().startswith("python scripts/cfia_errata.py")]
        self.assertEqual(len(cmds), 5)
        for cmd in cmds:
            argv = shlex.split(cmd)[2:]
            code, out = run_main(mod, ["--csv", CSV] + argv)
            self.assertEqual(code, 0, cmd)
            self.assertTrue(out.strip(), cmd)

    def test_disclosure_licence_and_no_address(self):
        script = read(SCRIPT)
        for text in (self.text, script):
            self.assertIn("Made with AI agents working in MV2's (Munim, Inc.) name", text)
            self.assertNotRegex(text, r"\bMIT\b")
            self.assertIsNone(STREET.search(text))
            # No download address is built into the skill: the default is the bundled table.
            self.assertNotIn("raw.githubusercontent.com", text)
        self.assertIn("SPDX-License-Identifier: Apache-2.0", script)
        self.assertIn("pointers, not confirmed errors", self.text)
        self.assertIn("works offline", self.text)
        self.assertTrue(self.text.rstrip().endswith("MV2, Munim, Inc., mv2@munimtech.com"))
        self.assertIsNotNone(STREET.search(" ".join(["12", "Example", "Road"])))


class Lookup(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()
        self.rows = self.mod.load(CSV)

    def ids(self, **kw):
        return [r["item_id"] for r in self.mod.select(self.rows, **kw)]

    def test_bundled_default_and_header(self):
        self.assertEqual(os.path.normcase(self.mod.BUNDLED_CSV), os.path.normcase(BUNDLED))
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("network used")):
            self.assertEqual(len(self.mod.load()), 75)
        self.assertEqual(len(self.rows), 75)
        self.assertEqual(len({r["item_id"] for r in self.rows}), 75)

    def test_filter_counts(self):
        self.assertEqual(len(self.ids(series="fumonisin-2010")), 5)
        self.assertEqual(len(self.ids(series="fumonisin-2011-2018")), 17)
        self.assertEqual(len(self.ids(analyte="fumonisin")), 22)
        self.assertEqual(len(self.ids(analyte="FUMONISIN")), 22)
        self.assertEqual(len(self.ids(analyte="ethyl carbamate")), 7)
        self.assertEqual(len(self.ids(analyte="BPA")), 8)
        self.assertEqual(len(self.ids(year="2018-19")), 21)
        self.assertEqual(len(self.ids(evidence="report_internal")), 17)
        self.assertEqual(len(self.ids(analyte="fumonisin", evidence="report_internal")), 10)
        self.assertEqual(self.ids(year="2018-19", analyte="ethyl carbamate"),
                         ["ec-2018-1000x", "ec-2018-beef", "ec-2018-dates", "ec-2018-onelabel"])
        self.assertEqual(self.ids(kind="unit"),
                         ["cfp-afm1-2014-unit", "ec-2018-1000x", "ph-2020-ppb", "ph-2018-ppb"])
        self.assertEqual(self.ids(text="1,000 times"), ["ec-2018-1000x"])
        self.assertEqual(self.ids(text="soy infant formula"), ["fum-2011-soy-formula"])

    def test_json_output(self):
        code, out = run_main(self.mod, ["--csv", CSV, "--id", "ec-2018-1000x", "--json"])
        self.assertEqual(code, 0)
        rows = json.loads(out)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["printed"], "4 (beers)")
        self.assertEqual(rows[0]["open_file"], "0.004 (beers)")
        self.assertEqual(rows[0]["note_url"], NOTE_BASE + "ethyl-carbamate-0.1.0-result.md")

    def test_text_and_summary_output(self):
        code, out = run_main(self.mod, ["--csv", CSV, "--id", "fum-2010-157"])
        self.assertEqual(code, 0)
        self.assertIn("printed:   157 | open file: 185 (157 with B1)", out)
        self.assertIn("1 of 75 items matched. Pointers, not confirmed errors.", out)
        self.assertIn("Table: local file " + CSV + ".", out)
        code, out = run_main(self.mod, ["--csv", CSV, "--summary"])
        self.assertEqual(code, 0)
        self.assertEqual(out.split("\n")[0], "75 items")
        self.assertIn("by kind: count 17, value 10, ", out)
        self.assertIn("by evidence: report_vs_file 45, report_internal 17, file_internal 9, "
                      "report_vs_report 4", out)

    def test_exit_codes(self):
        code, _ = run_main(self.mod, ["--csv", CSV, "--id", "no-such-item"])
        self.assertEqual(code, 1)
        with tempfile.TemporaryDirectory() as tmp:
            bad = os.path.join(tmp, "bad.csv")
            with open(bad, "w", encoding="utf-8") as fh:
                fh.write("a,b\n1,2\n")
            with contextlib.redirect_stderr(io.StringIO()):
                code, _ = run_main(self.mod, ["--csv", bad])
            self.assertEqual(code, 2)
        with contextlib.redirect_stderr(io.StringIO()):
            code, _ = run_main(self.mod, ["--url", "http://example.org/x.csv", "--summary"])
        self.assertEqual(code, 2)

    def test_version_subprocess(self):
        r = subprocess.run([sys.executable, SCRIPT, "--version"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("0.2.0 (bundled errata 0.3.0)", r.stdout)


class Bundle(unittest.TestCase):
    def test_bundled_copy_matches_repo_table(self):
        with open(BUNDLED, "rb") as a, open(CSV, "rb") as b:
            self.assertEqual(a.read(), b.read())

    def test_installed_copy_works_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = os.path.join(install_copy(tmp), "scripts", "cfia_errata.py")
            r = subprocess.run([sys.executable, "-I", script, "--summary"], cwd=tmp,
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stdout.split("\n")[0], "75 items")
            r = subprocess.run([sys.executable, "-I", script, "--id", "ec-2018-1000x"], cwd=tmp,
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("1 of 75 items matched.", r.stdout)
            self.assertIn("Table: errata 0.3.0 bundled with this skill.", r.stdout)

    def test_missing_bundle_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = install_copy(tmp)
            os.remove(os.path.join(dest, "data", "cfia-open-data-errata.csv"))
            r = subprocess.run([sys.executable, "-I", os.path.join(dest, "scripts",
                                                                     "cfia_errata.py"),
                                "--summary"], cwd=tmp, capture_output=True, text=True,
                               encoding="utf-8")
            self.assertEqual(r.returncode, 2)
            self.assertIn("bundled table is missing", r.stderr)


if __name__ == "__main__":
    unittest.main()
