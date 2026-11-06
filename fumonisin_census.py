#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""fumonisin-2010-census 0.1.0: a names-only structure census of CFIA's open 2010-11 fumonisin
file ("CHEM TS 2010-2011 Fumonisins in Selected Foods", opened on open.canada.ca on 2026-11-03),
run after docs/fumonisin-2010-0.1.0-prereg.md is public and before any value is read.

FUMONISIN-CENSUS-MODULE 0.1.0

It runs cfia_census.census (labels, units and cell shapes per component), the column-by-column
census of bpa_series_census.columns_census (cell shapes and text-label counts per column; numeric
cells are never printed, summed or compared) and perchlorate_census.product_years (samples per
product label per April-March survey year, from the sampling-date column). New here: each
component label and each header cell is classed as fumonisin B1, B2, B3, total or other, and each
unit as ppb-scale, ppm-scale or other, so the pre-registration's gate (G) and census items C1, C3
and C4 can be graded from names alone. C2 (the product map) is decided in the census note from
the product label counts printed here. The file is on open.canada.ca under the Open Government
Licence - Canada. Standard library only. Made with AI agents working in MV2's (Munim, Inc.) name.
Code Apache-2.0; derived data CC BY 4.0.
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


def kib_band_up(kib):
    """Byte counts whose size in KiB, rounded up, is `kib`: more than (kib-1)*1024, at most kib*1024."""
    return ((kib - 1) * 1024, kib * 1024)


TARGET = {
    "name": "fum10",
    "dataset": "5ac4ed9e-9dc4-4c3c-9a2b-e99530fbda13",
    "resource": "48123e67-3a23-44f3-8cf1-ef8054ca1766",
    "path": ("chem_ts_2010-2011_fumonisins_in_selected_foods_chem_ec_2010-2011_fumonisines_"
             "dans_des_aliments_s.csv"),
    # No exact byte count is known, so cfia_census.load always downloads afresh.
    "size": None, "portal_kib": 86, "size_band": kib_band_up(86),
    "md5": "219641dd2317367eb87069eef88a88b6", "samples": 276,
}
ROLES = ("sample", "product", "component", "value", "unit")
PPB = {"ppb", "ng/g", "ug/kg"}
PPM = {"ppm", "ug/g", "mg/kg"}
_TOTAL = re.compile(r"\b(total|sum|somme)\b")
_FUM = re.compile(r"(?:fumonisin(?:e)?s?|\bfb)\s*-?\s*b?\s*([123])\b")


def analyte_kind(label):
    """'Fumonisin B1' or 'FB1' -> 'B1'; 'Total Fumonisins' -> 'total'; anything else -> 'other'."""
    low = cc.clean(label).lower()
    if _TOTAL.search(low) and ("fumonisin" in low or re.search(r"\bfb", low)):
        return "total"
    m = _FUM.search(low)
    if m:
        return "B" + m.group(1)
    return "other"


def unit_kind(unit):
    u = cc.clean(unit).lower().replace("µ", "u").replace("μ", "u").replace(" ", "")
    if u in PPB:
        return "ppb"
    if u in PPM:
        return "ppm"
    return "other"


def header_of(text):
    return next(csv.reader(io.StringIO(text)), [])


def analyte_headers(header):
    """Header cells that name a fumonisin: [(index, cleaned cell, kind)]. Labels, not results."""
    out = []
    for i, cell in enumerate(header):
        c = cc.clean(cell)
        if "fumonisin" in c.lower() or re.search(r"\bfb\s*[123]\b", c.lower()):
            out.append([i, c, analyte_kind(c)])
    return out


def run_text(text):
    """Every names-only part of the census for one decoded file."""
    res = {}
    for key, fn in (("census", cc.census), ("columns", columns_census),
                    ("product_years", product_years)):
        try:
            res[key] = fn(text)
        except Exception as exc:  # noqa: BLE001 - the other parts still run
            res[key] = {"error": f"{type(exc).__name__}: {exc}"}
    header = header_of(text)
    roles = cc.find_columns(header)
    res["roles"] = {k: roles.get(k) for k in ROLES}
    res["analyte_headers"] = analyte_headers(header)
    return res


def gate_facts(res, target=TARGET):
    """The census-gradable facts of the pre-registration: G, C1, C3 and C4."""
    cols = res.get("columns") or {}
    census = res.get("census") or {}
    ok = isinstance(census, dict) and "error" not in census
    comps = census.get("components") if ok else None
    units = census.get("units") if ok else None
    lo, hi = target["size_band"]
    b = res.get("bytes")
    roles = res.get("roles") or {}
    kinds = {c: analyte_kind(c) for c in comps} if isinstance(comps, dict) else None
    ukinds = {u: unit_kind(u) for u in units} if isinstance(units, dict) else None
    facts = {
        "bytes": b,
        "size_band": [lo, hi],
        "size_in_band": isinstance(b, int) and lo < b <= hi,
        "md5": res.get("md5_matches_portal"),
        "roles_found": all(roles.get(k) is not None for k in ROLES),
        "samples": cols.get("samples"),
        "C1_samples_276": cols.get("samples") == target["samples"],
        "component_kinds": kinds,
        "unit_kinds": ukinds,
        "census_error": census.get("error") if isinstance(census, dict) else None,
    }
    facts["G"] = bool(facts["md5"] and facts["size_in_band"] and facts["roles_found"])
    if kinds is not None:
        found = set(kinds.values())
        facts["C3_subset_of_B1_B2_total"] = found <= {"B1", "B2", "total"}
        facts["C3_no_B3"] = "B3" not in found
    if ukinds is not None:
        facts["C4_all_ppb_scale"] = bool(ukinds) and set(ukinds.values()) == {"ppb"}
    return facts


def run_target(target, data_dir):
    res = {"study": "fumonisin-2010-census", "version": VERSION,
           "dataset": target["dataset"], "resource": target["resource"],
           "portal_size": f"{target['portal_kib']} (KiB)", "portal_md5": target["md5"]}
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
    ap = argparse.ArgumentParser(description="Names-only census of CFIA's 2010-11 fumonisin file.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    res = run_target(TARGET, args.data_dir)
    with open(os.path.join(args.out_dir, "fumonisin_2010_census.json"), "w",
              encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, sort_keys=True, ensure_ascii=False)
    census = res.get("census") or {}
    py = res.get("product_years") or {}
    print(json.dumps({"error": res.get("error"), "gate_facts": res.get("gate_facts"),
                      "header": census.get("header"), "roles": res.get("roles"),
                      "analyte_headers": res.get("analyte_headers"),
                      "components": census.get("components"), "units": census.get("units"),
                      "rows_per_sample": census.get("rows_per_sample"),
                      "by_year": py.get("by_year"), "first": py.get("first"),
                      "last": py.get("last")}, ensure_ascii=False))
    print("CENSUS-DONE" if "error" not in res else "CENSUS-FAILED")
    return 0 if "error" not in res else 1


if __name__ == "__main__":
    sys.exit(main())
