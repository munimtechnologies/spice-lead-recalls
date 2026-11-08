#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Look up known report-vs-file items in CFIA's open food-chemistry survey data.

Reads the CFIA open-data errata table (CC BY 4.0) and filters it by item, series, analyte,
survey year, kind, evidence or free text. Standard library only; read-only.

Where the table comes from, in this order:
  1. --csv PATH, if given;
  2. --url URL, only if you pass one yourself (one HTTPS GET; nothing is fetched otherwise);
  3. the copy bundled with this skill, ../data/cfia-open-data-errata.csv (the default).

By default the script works offline and makes no network request. The bundled copy is
byte-identical to data/cfia-open-data-errata.csv in the source repository
github.com/munimtechnologies/spice-lead-recalls, which a test there checks.

Exit codes: 0 = at least one item matched, 1 = no item matched, 2 = the table could not be read.
The items are pointers, not confirmed errors: no person at Munim, Inc. or at CFIA has confirmed
them. None is a compliance finding, and none is dietary or medical advice.

Made with AI agents working in MV2's (Munim, Inc.) name.
"""
import argparse
import csv
import io
import json
import os
import sys
from collections import Counter

__version__ = "0.2.0"
TABLE_VERSION = "0.3.0"

NOTE_BASE = "https://github.com/munimtechnologies/spice-lead-recalls/blob/main/docs/"
HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLED_CSV = os.path.normpath(os.path.join(HERE, "..", "data", "cfia-open-data-errata.csv"))
COLUMNS = ["item_id", "series", "survey_years", "analyte", "where", "finding", "printed",
           "open_file", "kind", "evidence", "note"]


def _read_text(csv_path=None, url=None):
    if csv_path:
        with open(csv_path, encoding="utf-8-sig", newline="") as fh:
            return fh.read()
    if url:
        if not url.startswith("https://"):
            raise ValueError("--url must be an https:// address")
        import urllib.request  # only when the caller asked for a download
        req = urllib.request.Request(url, headers={"User-Agent": "cfia-open-data-errata/"
                                                   + __version__})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read().decode("utf-8-sig")
    if not os.path.exists(BUNDLED_CSV):
        raise FileNotFoundError("the bundled table is missing (%s); reinstall the skill or "
                                "pass --csv PATH" % BUNDLED_CSV)
    with open(BUNDLED_CSV, encoding="utf-8-sig", newline="") as fh:
        return fh.read()


def describe_source(csv_path=None, url=None):
    if csv_path:
        return "local file " + csv_path
    if url:
        return "downloaded from " + url
    return "errata %s bundled with this skill" % TABLE_VERSION


def load(csv_path=None, url=None):
    """Return the table as a list of dicts, after checking its header."""
    reader = csv.DictReader(io.StringIO(_read_text(csv_path, url), newline=""))
    if reader.fieldnames != COLUMNS:
        raise ValueError("unexpected header: %r" % (reader.fieldnames,))
    rows = [r for r in reader if r.get("item_id")]
    for r in rows:
        r["note_url"] = NOTE_BASE + r["note"]
    return rows


def select(rows, item_id=None, series=None, analyte=None, year=None, kind=None,
           evidence=None, text=None):
    """Filter rows. item_id, series, kind and evidence match exactly; analyte and year match
    as case-insensitive substrings of their columns; text matches any column."""
    out = []
    for r in rows:
        if item_id and r["item_id"] != item_id:
            continue
        if series and r["series"] != series:
            continue
        if kind and r["kind"] != kind:
            continue
        if evidence and r["evidence"] != evidence:
            continue
        if analyte and analyte.lower() not in r["analyte"].lower():
            continue
        if year and year.lower() not in r["survey_years"].lower():
            continue
        if text and not any(text.lower() in (r[c] or "").lower() for c in COLUMNS):
            continue
        out.append(r)
    return out


def summary_lines(rows):
    lines = ["%d items" % len(rows)]
    for col in ("series", "kind", "evidence"):
        counts = Counter(r[col] for r in rows)
        lines.append("by %s: %s" % (col, ", ".join(
            "%s %d" % (k, n) for k, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))))
    return lines


def text_block(r):
    lines = ["%s  [%s, %s]  %s, %s" % (r["item_id"], r["kind"], r["evidence"], r["analyte"],
                                       r["survey_years"]),
             "  where:     " + r["where"],
             "  finding:   " + r["finding"]]
    if r["printed"] or r["open_file"]:
        lines.append("  printed:   %s | open file: %s" % (r["printed"] or "-", r["open_file"] or "-"))
    lines.append("  note:      " + r["note_url"])
    return "\n".join(lines)


def build_parser():
    ap = argparse.ArgumentParser(
        description="Look up known report-vs-file items in CFIA's open food-chemistry survey data "
                    "(pointers, not confirmed errors). Offline by default.")
    ap.add_argument("--csv", help="read the table from this local file instead of the bundled copy")
    ap.add_argument("--url", help="download the table from this https:// URL instead (only if "
                                  "you ask; the default makes no network request)")
    ap.add_argument("--id", dest="item_id", help="one item, e.g. ec-2018-1000x")
    ap.add_argument("--series", help="exact series name, e.g. fumonisin-2010 (see --summary)")
    ap.add_argument("--analyte", help="substring of the analyte, e.g. fumonisin, BPA, lead")
    ap.add_argument("--year", help="substring of the survey years, e.g. 2018-19")
    ap.add_argument("--kind", help="count, value, text, average, share, subset, label, unit, "
                                   "origin, coverage, date or duplicate")
    ap.add_argument("--evidence", help="report_vs_file, report_internal, file_internal or "
                                       "report_vs_report")
    ap.add_argument("--grep", dest="text", help="substring of any column")
    ap.add_argument("--json", action="store_true", help="print matching rows as JSON")
    ap.add_argument("--summary", action="store_true", help="print counts of the matching rows")
    ap.add_argument("--version", action="version",
                    version="%(prog)s " + __version__ + " (bundled errata " + TABLE_VERSION + ")")
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass
    try:
        rows = load(args.csv, args.url)
    except Exception as exc:  # noqa: BLE001 - any read problem is reported the same way
        print("error: could not read the errata table: %s" % exc, file=sys.stderr)
        return 2
    hits = select(rows, args.item_id, args.series, args.analyte, args.year, args.kind,
                  args.evidence, args.text)
    if args.json:
        print(json.dumps(hits, indent=1))
    elif args.summary:
        print("\n".join(summary_lines(hits)))
    else:
        if hits:
            print("\n\n".join(text_block(r) for r in hits))
        print("\n%d of %d items matched. Pointers, not confirmed errors." % (len(hits), len(rows)))
        print("Table: %s." % describe_source(args.csv, args.url))
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())
