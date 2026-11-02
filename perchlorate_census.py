#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""perchlorate-census 0.1.0: a names-only structure census of CFIA's three open perchlorate survey
files (2010-11, 2011-13, 2013-14), run after docs/perchlorate-series-0.1.0-prereg.md is public and
before any value is read.

For each file it runs cfia_census.census (labels, units and cell shapes per component), the
column-by-column census of bpa_series_census.columns_census (cell shapes and TEXT label counts per
column; numeric cells are never printed, summed or compared) and, new here, a count of samples per
product label per survey year (April to March) taken from the sampling-date column, with the
shapes of the date strings. Dates are labels, not results. It then derives the gate facts the
pre-registration names (size, MD5, distinct sample IDs, analyte labels, units, rows per sample).
All three files are on open.canada.ca under the Open Government Licence - Canada. Standard library
only. Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0; derived data
CC BY 4.0.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import io
import json
import os
import re
import sys

import cfia_census as cc
from bpa_series_census import columns_census

VERSION = "0.1.0"
TARGETS = (
    {"name": "p10",
     "dataset": "436bec6d-f410-45cc-89ff-f5331cfa663c",
     "resource": "46630289-3b83-4392-b648-da594e5357ce",
     "path": ("cfia_acia-1339-v1-cfia_acia_-_19007386_-_fsap_chem_ts_-_2010-11_perchlorate_in_"
              "fresh_fruits_and_.csv"),
     "size": 95033, "md5": "f497970ea94e7d4eaf74fdabb9535bca", "samples": 611},
    {"name": "p11",
     "dataset": "0bdaecc5-805e-4f42-a182-338870635221",
     "resource": "beccac79-f18e-4270-9c2c-c6ce645fc2b4",
     "path": ("cfia_acia-1340-v1-cfia_acia_-_19007867_-_fsap_chem_ts_-_2011-13_perchlorate_in_"
              "fresh_fruits_and_.csv"),
     "size": 228127, "md5": "66a04ce98555c6898c18ebaefc042a96", "samples": 1426},
    {"name": "p13",
     "dataset": "79e83e09-be72-4cec-b410-1e69aaa450f7",
     "resource": "7511b1a3-48c7-4386-ae6e-f2c4e87c6e84",
     "path": "2013-14_perchlorate_in_selected_foods_perchlorate-dans-certains-aliments.csv",
     "size": 78310, "md5": "05b587cb13f15932894200ba5879445a", "samples": 477},
)
DATE_FORMATS = ("%d-%b-%y", "%d-%b-%Y", "%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%d/%m/%Y",
                "%b %d, %Y", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M", "%m/%d/%Y %I:%M:%S %p")


def date_shape(text):
    """'4-Jun-18' -> '9-Aaa-99'; '2019-04-09' -> '9999-99-99'. Digits -> 9, letters -> a/A."""
    out = []
    for ch in text:
        if ch.isdigit():
            out.append("9")
        elif ch.isalpha():
            out.append("A" if ch.isupper() else "a")
        else:
            out.append(ch)
    return re.sub(r"9+", lambda m: "9" * min(len(m.group(0)), 4), "".join(out))


def parse_date(text):
    """A date string -> (date, ambiguous). Ambiguous: a slash date that also parses day-first to a
    different month."""
    t = (text or "").strip()
    for fmt in DATE_FORMATS:
        try:
            d = datetime.datetime.strptime(t, fmt).date()
        except ValueError:
            continue
        amb = False
        if fmt.startswith("%m/%d/%Y"):
            try:
                alt = datetime.datetime.strptime(t.split(" ")[0], "%d/%m/%Y").date()
                amb = alt.month != d.month
            except ValueError:
                amb = False
        return d, amb
    return None, False


def survey_year(d):
    """April-March survey year: 2011-05-01 -> '2011-12'; 2012-03-31 -> '2011-12'."""
    y = d.year if d.month >= 4 else d.year - 1
    return f"{y}-{(y + 1) % 100:02d}"


def product_years(text):
    """Samples per product label per survey year, from each sample's first row. Never reads a
    result cell."""
    reader = csv.reader(io.StringIO(text))
    header = next(reader, [])
    col = cc.find_columns(header)
    out = {"date_column": col.get("date"), "product_column": col.get("product"),
           "sample_column": col.get("sample"), "by_product": {}, "by_year": {},
           "date_shapes": {}, "unparsed": 0, "ambiguous": 0, "first": None, "last": None}
    if col.get("sample") is None or col.get("product") is None or col.get("date") is None:
        out["error"] = "missing sample, product or date column"
        return out
    seen = set()
    first = last = None
    for r in reader:
        if not any(c.strip() for c in r):
            continue
        sid = cc.clean(cc._cell(r, col["sample"]))
        if sid in seen:
            continue
        seen.add(sid)
        prod = cc.clean(cc._cell(r, col["product"]))
        raw = cc.clean(cc._cell(r, col["date"]))
        cc._bump(out["date_shapes"], date_shape(raw) if raw else "(blank)")
        d, amb = parse_date(raw)
        if amb:
            out["ambiguous"] += 1
        if d is None:
            out["unparsed"] += 1
            year = "(unparsed)"
        else:
            year = survey_year(d)
            first = d if first is None or d < first else first
            last = d if last is None or d > last else last
        cc._bump(out["by_product"].setdefault(prod, {}), year)
        cc._bump(out["by_year"], year)
    out["first"] = first.isoformat() if first else None
    out["last"] = last.isoformat() if last else None
    return out


def gate_facts(res, target):
    """The census-gradable gate facts of the pre-registration (G), from a census record."""
    cols = res.get("columns") or {}
    census = res.get("census") or {}
    ok_census = isinstance(census, dict) and "error" not in census
    components = census.get("components") if ok_census else None
    units = census.get("units") if ok_census else None
    per = census.get("rows_per_sample") if ok_census else None
    facts = {
        "bytes": res.get("bytes"),
        "size": res.get("size_matches_portal"),
        "md5": res.get("md5_matches_portal"),
        "samples": cols.get("samples"),
        "samples_match": cols.get("samples") == target["samples"],
        "rows": cols.get("rows"),
        "analyte_labels": len(components) if isinstance(components, dict) else None,
        "unit_labels": sorted(units) if isinstance(units, dict) else None,
        "rows_per_sample": per,
        "census_error": census.get("error") if isinstance(census, dict) else None,
    }
    facts["one_analyte"] = facts["analyte_labels"] == 1
    facts["one_unit"] = facts["unit_labels"] is not None and len(facts["unit_labels"]) == 1
    facts["one_row_per_sample"] = per == {"1": target["samples"]}
    return facts


def run_target(target, data_dir):
    res = {"study": f"perchlorate-{target['name']}-census", "version": VERSION,
           "dataset": target["dataset"], "resource": target["resource"],
           "portal_size": target["size"], "portal_md5": target["md5"]}
    try:
        raw, src = cc.load(target, data_dir)
    except Exception as exc:  # noqa: BLE001 - recorded, the other files still run
        res["error"] = f"{type(exc).__name__}: {exc}"
        return res
    text, enc = cc.decode(raw)
    md5 = hashlib.md5(raw).hexdigest()
    res.update({"source": src, "bytes": len(raw), "size_matches_portal": len(raw) == target["size"],
                "encoding": enc, "sha256": hashlib.sha256(raw).hexdigest(), "md5": md5,
                "md5_matches_portal": md5 == target["md5"]})
    for key, fn in (("census", cc.census), ("columns", columns_census),
                    ("product_years", product_years)):
        try:
            res[key] = fn(text)
        except Exception as exc:  # noqa: BLE001 - the other parts still run
            res[key] = {"error": f"{type(exc).__name__}: {exc}"}
    res["gate_facts"] = gate_facts(res, target)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description="Names-only census of three CFIA perchlorate files.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    ok = 0
    for target in TARGETS:
        res = run_target(target, args.data_dir)
        if "error" not in res:
            ok += 1
        with open(os.path.join(args.out_dir, f"perchlorate_{target['name']}_census.json"),
                  "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=2, sort_keys=True, ensure_ascii=False)
        cols = res.get("columns", {})
        py = res.get("product_years", {})
        print(json.dumps({"name": target["name"], "error": res.get("error"),
                          "gate_facts": res.get("gate_facts"),
                          "header": [c.get("name") for c in cols.get("columns", [])],
                          "by_year": py.get("by_year"), "first": py.get("first"),
                          "last": py.get("last")}, ensure_ascii=False))
    print(f"CENSUS-DONE {ok}/{len(TARGETS)}")
    return 0 if ok == len(TARGETS) else 1


if __name__ == "__main__":
    sys.exit(main())
