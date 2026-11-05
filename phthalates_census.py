#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""phthalates-census 0.1.0: a names-only structure census of CFIA's open 2020-21 phthalates file
(ready-to-eat meals, vegetable fats and oils), run after docs/phthalates-2020-0.1.0-prereg.md is
public and before any value is read.

It runs cfia_census.census (labels, units and cell shapes per component; it records an error and
stops if the file has no component column), the column-by-column census of
bpa_series_census.columns_census (cell shapes and TEXT label counts per column; numeric cells are
never printed, summed or compared), perchlorate_census.product_years (samples per product label
per April-March survey year, from the sampling-date column), and, new here, the list of header
cells that name a phthalate, so a wide layout (one result column per phthalate) is visible. Header
cells are labels, not results. It then derives the census-gradable gate facts of the
pre-registration (G). The file is on open.canada.ca under the Open Government Licence - Canada.
Standard library only. Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0;
derived data CC BY 4.0.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys

import cfia_census as cc
from bpa_series_census import columns_census
from perchlorate_census import product_years

VERSION = "0.1.0"
TARGETS = (
    {"name": "ph20",
     "dataset": "4ae4c2b3-e1b7-451a-b313-02e51d73da73",
     "resource": "960252a3-4b35-44ef-9e8d-46ed1b0dd61c",
     "path": "fsap-chem-ts-2020-2021-phthalates-in-ready-to-eat-meals-vegetable-fats-and-oils.csv",
     # The portal gives "115" (kB), so no exact byte count is known: cfia_census.load then
     # downloads afresh, and the gate checks a band.
     "size": None, "size_band": (113000, 118000),
     "md5": "612780be14a4a571044d93aaa27f99f2", "samples": 500},
)
PHTHALATES = ("BBP", "DBP", "DNOP", "DEHP", "DINP", "DIDP")
_NAME = re.compile(r"(?<![A-Z])(BBP|DBP|DNOP|DEHP|DINP|DIDP|DIBP|DEP|DMP)(?![A-Z])")


def analyte_headers(header):
    """Header cells that name a phthalate: [(index, cleaned cell, abbreviations found)]."""
    out = []
    for i, cell in enumerate(header):
        c = cc.clean(cell)
        up = c.upper()
        names = sorted(set(_NAME.findall(up)))
        if names or "PHTHALATE" in up or "PHTALATE" in up:
            out.append([i, c, names])
    return out


def header_of(text):
    return next(csv.reader(io.StringIO(text)), [])


def layout(census, headers):
    """'long' (a component column with several labels), 'single' (one component label), 'wide'
    (no component column, two or more phthalate result columns) or 'unknown'."""
    comps = census.get("components") if isinstance(census, dict) and "error" not in census else None
    if isinstance(comps, dict) and len(comps) > 1:
        return "long"
    if isinstance(comps, dict) and len(comps) == 1:
        return "single"
    named = {n for _, _, names in headers for n in names}
    if len(named) >= 2:
        return "wide"
    return "unknown"


def gate_facts(res, target):
    """The census-gradable gate facts of the pre-registration (G), from a census record."""
    cols = res.get("columns") or {}
    census = res.get("census") or {}
    ok = isinstance(census, dict) and "error" not in census
    comps = census.get("components") if ok else None
    units = census.get("units") if ok else None
    lo, hi = target["size_band"]
    b = res.get("bytes")
    headers = res.get("analyte_headers") or []
    named = sorted({n for _, _, names in headers for n in names})
    facts = {
        "bytes": b,
        "size_in_band": isinstance(b, int) and lo <= b <= hi,
        "md5": res.get("md5_matches_portal"),
        "samples": cols.get("samples"),
        "samples_match": cols.get("samples") == target["samples"],
        "rows": cols.get("rows"),
        "component_labels": sorted(comps) if isinstance(comps, dict) else None,
        "unit_labels": sorted(units) if isinstance(units, dict) else None,
        "rows_per_sample": census.get("rows_per_sample") if ok else None,
        "header_phthalates": named,
        "layout": layout(census, headers),
        "census_error": census.get("error") if isinstance(census, dict) else None,
    }
    facts["six_named_in_header"] = set(PHTHALATES) <= set(named)
    return facts


def run_text(text):
    """Every names-only part of the census for one decoded file."""
    res = {}
    for key, fn in (("census", cc.census), ("columns", columns_census),
                    ("product_years", product_years)):
        try:
            res[key] = fn(text)
        except Exception as exc:  # noqa: BLE001 - the other parts still run
            res[key] = {"error": f"{type(exc).__name__}: {exc}"}
    try:
        res["analyte_headers"] = analyte_headers(header_of(text))
    except Exception as exc:  # noqa: BLE001
        res["analyte_headers"] = []
        res["analyte_headers_error"] = f"{type(exc).__name__}: {exc}"
    return res


def run_target(target, data_dir):
    res = {"study": f"phthalates-{target['name']}-census", "version": VERSION,
           "dataset": target["dataset"], "resource": target["resource"],
           "portal_size": "115 (kB)", "portal_md5": target["md5"]}
    try:
        raw, src = cc.load(target, data_dir)
    except Exception as exc:  # noqa: BLE001 - recorded
        res["error"] = f"{type(exc).__name__}: {exc}"
        return res
    text, enc = cc.decode(raw)
    md5 = hashlib.md5(raw).hexdigest()
    res.update({"source": src, "bytes": len(raw), "encoding": enc,
                "sha256": hashlib.sha256(raw).hexdigest(), "md5": md5,
                "md5_matches_portal": md5 == target["md5"]})
    res.update(run_text(text))
    res["gate_facts"] = gate_facts(res, target)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description="Names-only census of CFIA's 2020-21 phthalates file.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    ok = 0
    for target in TARGETS:
        res = run_target(target, args.data_dir)
        if "error" not in res:
            ok += 1
        with open(os.path.join(args.out_dir, f"phthalates_{target['name']}_census.json"),
                  "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=2, sort_keys=True, ensure_ascii=False)
        cols = res.get("columns", {})
        py = res.get("product_years", {})
        print(json.dumps({"name": target["name"], "error": res.get("error"),
                          "gate_facts": res.get("gate_facts"),
                          "header": (res.get("census") or {}).get("header"),
                          "samples": cols.get("samples"), "by_year": py.get("by_year"),
                          "first": py.get("first"), "last": py.get("last")},
                         ensure_ascii=False))
    print(f"CENSUS-DONE {ok}/{len(TARGETS)}")
    return 0 if ok == len(TARGETS) else 1


if __name__ == "__main__":
    sys.exit(main())
