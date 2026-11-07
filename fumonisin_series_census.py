#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""fumonisin-series-census 0.1.0: a names-only structure census of CFIA's open 2011-12 and
2012-2018 fumonisin files (both opened on open.canada.ca on 2026-11-03), run after
docs/fumonisin-series-0.1.0-prereg.md is public and before any value is read.

FUMONISIN-SERIES-CENSUS-MODULE 0.1.0

For each file it runs cfia_census.census (labels, units and cell shapes per component),
bpa_series_census.columns_census (cell shapes and text-label counts per column; numeric cells are
never printed, summed or compared) and perchlorate_census.product_years (samples per product label
per April-March survey year, from the sampling-date column), and classes analyte labels and units
with fumonisin_census (B1, B2, B3, total or other; ppb-scale, ppm-scale or other). New here:
keyword_samples counts, for every text column except the sample and value columns, the distinct
samples whose cell names a grain, soy, tea or organic keyword, so that the pre-registration's teff
(B-C6), rice (B-C7) and organic (B-C9) items can be read from names alone. The files are on
open.canada.ca under the Open Government Licence - Canada. Standard library only. Made with AI
agents working in MV2's (Munim, Inc.) name. Code Apache-2.0; derived data CC BY 4.0.
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
import fumonisin_census as fc
from bpa_series_census import columns_census
from perchlorate_census import product_years

VERSION = "0.1.0"
ROLES = ("sample", "product", "component", "value", "unit")
TARGETS = (
    {"name": "fum11",
     "dataset": "e5906422-e8bf-498b-972e-faf2b688aa97",
     "resource": "fe5490e6-35c6-4175-be9d-8b679548784d",
     "path": ("chem_ts_2011-2012_fumonisins_in_selected_foods_chem_ec_2011-2012_fumonisines_"
              "dans_des_aliments_s.csv"),
     # No exact byte count is known, so cfia_census.load always downloads afresh.
     "size": None, "portal_kib": 155, "size_band": fc.kib_band_up(155),
     "md5": "9f6fddeb2448a199d1beae925a5f3a96", "samples": 454},
    {"name": "fum1218",
     "dataset": "449c63d9-c545-4cce-b907-e32840967873",
     "resource": "df04bd3f-d591-49dc-91c7-0e498b74f22f",
     "path": ("chem_ts_2012-2018_fumonisins_in_selected_foods_chem_ec_2012-2018_fumonisines_"
              "dans_des_aliments_s.csv"),
     "size": None, "portal_kib": 1371, "size_band": fc.kib_band_up(1371),
     "md5": "6c87fb0bc35b3fc0cea0d3bd2e93e97b", "samples": 4261},
)
KEYWORDS = ("amaranth", "arrowroot", "barley", "buckwheat", "corn", "kamut", "millet", "oat",
            "quinoa", "rice", "rye", "sorghum", "spelt", "teff", "triticale", "wheat", "soy",
            "tofu", "tea", "black tea", "organic", "conventional", "cereal", "child", "infant")
_KW = {k: re.compile(r"(?<![a-z])" + re.escape(k)) for k in KEYWORDS}


def keyword_samples(text):
    """{column header: {keyword: distinct samples whose cell names it}} for every column except
    the sample and value columns. Only text labels are looked at; no result is read."""
    rows = [r for r in csv.reader(io.StringIO(text)) if any(c.strip() for c in r)]
    if not rows:
        return {"error": "empty file"}
    header = rows[0]
    roles = cc.find_columns(header)
    s, v = roles.get("sample"), roles.get("value")
    if s is None:
        return {"error": "no sample column"}
    out = {}
    for i, name in enumerate(header):
        if i in (s, v):
            continue
        hits = {}
        for r in rows[1:]:
            if i >= len(r) or s >= len(r):
                continue
            cell = cc.clean(r[i]).lower()
            if not cell:
                continue
            for k, rx in _KW.items():
                if rx.search(cell):
                    hits.setdefault(k, set()).add(cc.clean(r[s]))
        if hits:
            out[cc.clean(name)] = {k: len(ids) for k, ids in sorted(hits.items())}
    return out


def run_text(text):
    """Every names-only part of the census for one decoded file."""
    res = {}
    for key, fn in (("census", cc.census), ("columns", columns_census),
                    ("product_years", product_years), ("keywords", keyword_samples)):
        try:
            res[key] = fn(text)
        except Exception as exc:  # noqa: BLE001 - the other parts still run
            res[key] = {"error": f"{type(exc).__name__}: {exc}"}
    header = fc.header_of(text)
    roles = cc.find_columns(header)
    res["roles"] = {k: roles.get(k) for k in ROLES}
    res["all_roles"] = roles
    res["analyte_headers"] = fc.analyte_headers(header)
    return res


def gate_facts(res, target):
    """The census-gradable facts of the pre-registration for one file: G, C1, C3 and C4."""
    cols = res.get("columns") or {}
    census = res.get("census") or {}
    ok = isinstance(census, dict) and "error" not in census
    comps = census.get("components") if ok else None
    units = census.get("units") if ok else None
    lo, hi = target["size_band"]
    b = res.get("bytes")
    roles = res.get("roles") or {}
    kinds = {c: fc.analyte_kind(c) for c in comps} if isinstance(comps, dict) else None
    ukinds = {u: fc.unit_kind(u) for u in units} if isinstance(units, dict) else None
    facts = {
        "bytes": b,
        "size_band": [lo, hi],
        "size_in_band": isinstance(b, int) and lo < b <= hi,
        "md5": res.get("md5_matches_portal"),
        "roles_found": all(roles.get(k) is not None for k in ROLES),
        "samples": cols.get("samples"),
        "C1_samples": cols.get("samples") == target["samples"],
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
    res = {"study": f"fumonisin-series-census-{target['name']}", "version": VERSION,
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
    ap = argparse.ArgumentParser(
        description="Names-only census of CFIA's 2011-12 and 2012-2018 fumonisin files.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    ok = 0
    for target in TARGETS:
        res = run_target(target, args.data_dir)
        if "error" not in res:
            ok += 1
        with open(os.path.join(args.out_dir, f"fumonisin_{target['name']}_census.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(res, fh, indent=2, sort_keys=True, ensure_ascii=False)
        census = res.get("census") or {}
        py = res.get("product_years") or {}
        print(json.dumps({"name": target["name"], "error": res.get("error"),
                          "gate_facts": res.get("gate_facts"),
                          "header": census.get("header"), "roles": res.get("all_roles"),
                          "analyte_headers": res.get("analyte_headers"),
                          "components": census.get("components"), "units": census.get("units"),
                          "rows_per_sample": census.get("rows_per_sample"),
                          "keywords": res.get("keywords"),
                          "by_year": py.get("by_year"), "first": py.get("first"),
                          "last": py.get("last")}, ensure_ascii=False))
    print(f"CENSUS-DONE {ok}/{len(TARGETS)}")
    return 0 if ok == len(TARGETS) else 1


if __name__ == "__main__":
    sys.exit(main())
