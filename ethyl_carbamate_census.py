#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""ethyl-carbamate-census 0.1.0: a names-only structure census of two open CFIA ethyl carbamate
survey files (2018-19 alcoholic beverages and vinegars; 2019-20 fermented vegetables and soy
products), run after docs/ethyl-carbamate-0.1.0-prereg.md is public and before any value is read.

For each file it runs cfia_census.census (labels, units and cell shapes per component) and the
column-by-column census of bpa_series_census.columns_census (cell shapes and TEXT label counts per
column; numeric cells are never printed, summed or compared, and in value-like columns a text cell
holding a digit is recorded only as "<text with digits>"). It then derives the gate facts the
pre-registration names (size, MD5, distinct sample IDs, analyte labels, units, rows, and for the
2019-20 file whether the download is the 58-byte record the portal lists). Both files are on
open.canada.ca under the Open Government Licence - Canada. Standard library only.
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0; derived data CC BY 4.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import cfia_census as cc
from bpa_series_census import columns_census

VERSION = "0.1.0"
STUB_BYTES = 58
TARGETS = (
    {"name": "ec18",
     "dataset": "303903b7-91ba-4a79-ad37-7bcd9f0dc8a1",
     "resource": "0a30e00b-9c4b-4402-b329-51565119d767",
     "path": ("cfia-acia-1149_2018-19_ethylcarbamate_in_selected_foods_-_2018-2019_le-carbamate-"
              "dethyle-dans-le.csv"),
     "size": 71629, "md5": "d7d7bf62a3bb275ccec657fb27501fd8",
     "samples": 390, "stub_check": False},
    {"name": "ec19",
     "dataset": "920d97a1-b98d-4def-b386-dd234a45f457",
     "resource": "985e3d90-ecbb-4a34-b299-8032627c3c3d",
     "path": ("fsap-chem-ts-ethyl-carbamate-in-fermented-vegetables-and-soy-products-2019-2020_"
              "paaspa-chem-ec-c.csv"),
     "size": 58, "md5": "e5aab1da6e57c1afa0536e9d92455a6e",
     "samples": 300, "stub_check": True},
)


def gate_facts(res, target):
    """The census-gradable gate facts of the pre-registration (G18 / G19), from a census record."""
    cols = res.get("columns") or {}
    census = res.get("census") or {}
    ok_census = isinstance(census, dict) and "error" not in census
    components = census.get("components") if ok_census else None
    units = census.get("units") if ok_census else None
    facts = {
        "bytes": res.get("bytes"),
        "size": res.get("size_matches_portal"),
        "md5": res.get("md5_matches_portal"),
        "samples": cols.get("samples"),
        "samples_match": cols.get("samples") == target["samples"],
        "rows": cols.get("rows"),
        "analyte_labels": len(components) if isinstance(components, dict) else None,
        "unit_labels": sorted(units) if isinstance(units, dict) else None,
        "census_error": census.get("error") if isinstance(census, dict) else None,
    }
    facts["one_analyte"] = facts["analyte_labels"] == 1
    facts["one_unit"] = facts["unit_labels"] is not None and len(facts["unit_labels"]) == 1
    if target["stub_check"]:
        facts["not_stub"] = (res.get("bytes") is not None and res.get("bytes") > STUB_BYTES
                             and bool(cols.get("samples")))
    return facts


def run_target(target, data_dir):
    res = {"study": f"ethyl-carbamate-{target['name']}-census", "version": VERSION,
           "dataset": target["dataset"], "resource": target["resource"],
           "portal_size": target["size"], "portal_md5": target["md5"]}
    try:
        raw, src = cc.load(target, data_dir)
    except Exception as exc:  # noqa: BLE001 - recorded, the other file still runs
        res["error"] = f"{type(exc).__name__}: {exc}"
        return res
    text, enc = cc.decode(raw)
    md5 = hashlib.md5(raw).hexdigest()
    res.update({"source": src, "bytes": len(raw), "size_matches_portal": len(raw) == target["size"],
                "encoding": enc, "sha256": hashlib.sha256(raw).hexdigest(), "md5": md5,
                "md5_matches_portal": md5 == target["md5"]})
    try:
        res["census"] = cc.census(text)
    except Exception as exc:  # noqa: BLE001 - the column census below still runs
        res["census"] = {"error": f"{type(exc).__name__}: {exc}"}
    try:
        res["columns"] = columns_census(text)
    except Exception as exc:  # noqa: BLE001 - a stub or empty file is recorded, not fatal
        res["columns"] = {"error": f"{type(exc).__name__}: {exc}"}
    res["gate_facts"] = gate_facts(res, target)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description="Names-only census of two CFIA ethyl carbamate files.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    ok = 0
    for target in TARGETS:
        res = run_target(target, args.data_dir)
        if "error" not in res:
            ok += 1
        with open(os.path.join(args.out_dir, f"ethyl_carbamate_{target['name']}_census.json"),
                  "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=2, sort_keys=True, ensure_ascii=False)
        cols = res.get("columns", {})
        print(json.dumps({"name": target["name"], "error": res.get("error"),
                          "gate_facts": res.get("gate_facts"),
                          "header": [c.get("name") for c in cols.get("columns", [])]},
                         ensure_ascii=False))
    print(f"CENSUS-DONE {ok}/{len(TARGETS)}")
    return 0 if ok == len(TARGETS) else 1


if __name__ == "__main__":
    sys.exit(main())
