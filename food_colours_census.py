#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""food-colours-census 0.1.0: a names-only structure census of two open CFIA food-colour survey
files (2009-10 manufactured foods; 2018-19 essences/flavourings, oils, sweets and processed
vegetables), run after docs/food-colours-0.1.0-prereg.md is public and before any value is read.

For each file it runs cfia_census.census (labels, units and cell shapes per component) and the
column-by-column census of bpa_series_census.columns_census (cell shapes and TEXT label counts per
column; numeric cells are never printed, summed or compared, and in value-like columns a text cell
holding a digit is recorded only as "<text with digits>"). It then derives the gate facts the
pre-registration names (size, MD5, distinct sample IDs, number of colour labels, rows). Both files
are on open.canada.ca under the Open Government Licence - Canada. Standard library only.
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
TARGETS = (
    {"name": "c18",
     "dataset": "1b0c4141-7a22-4c93-8679-63eb49f7be24",
     "resource": "3006ff94-fa7a-4cc4-8b58-a2164ce6a937",
     "path": ("cfia_acia-1133_2018-19_food_colours_in_selected_foods_-2018-2019_colorants-"
              "alimentaires-dans-les.csv"),
     "size": 3771543, "md5": "7651427618a70aa3ad2a51ab90bcae8c",
     "samples": 399, "max_colours": 43},
    {"name": "c09",
     "dataset": "e750a5e1-40e5-4428-b23f-cc3f613e7f9a",
     "resource": "9c6e2a16-c552-41cb-b95c-240db3c75b8d",
     "path": ("1550-v1-chem_ts_2009-2010_food_colours_used_in_the_production_of_manufactured_"
              "foods_open_data_po.csv"),
     "size": 33724, "md5": "dc558d850720b90610da2c75424d1cd7",
     "samples": 100, "max_colours": None},
)


def gate_facts(res, target):
    """The census-gradable facts of the pre-registration (G18 / G09, S3), from a census record."""
    cols = res.get("columns") or {}
    census = res.get("census") or {}
    components = census.get("components") if isinstance(census, dict) else None
    n_colours = len(components) if isinstance(components, dict) else None
    facts = {
        "size": res.get("size_matches_portal"),
        "md5": res.get("md5_matches_portal"),
        "samples": cols.get("samples"),
        "samples_match": cols.get("samples") == target["samples"],
        "rows": cols.get("rows"),
        "colour_labels": n_colours,
        "census_error": census.get("error") if isinstance(census, dict) else None,
    }
    if target["max_colours"] is not None:
        facts["colours_within_max"] = (n_colours is not None
                                       and n_colours <= target["max_colours"])
    if target["name"] == "c09":
        facts["s3_fewer_than_2000_rows"] = (cols.get("rows") is not None
                                            and cols.get("rows") < 2000)
    return facts


def run_target(target, data_dir):
    res = {"study": f"food-colours-{target['name']}-census", "version": VERSION,
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
    res["columns"] = columns_census(text)
    res["gate_facts"] = gate_facts(res, target)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description="Names-only census of two CFIA food-colour files.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    ok = 0
    for target in TARGETS:
        res = run_target(target, args.data_dir)
        if "error" not in res:
            ok += 1
        with open(os.path.join(args.out_dir, f"food_colours_{target['name']}_census.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(res, fh, indent=2, sort_keys=True, ensure_ascii=False)
        cols = res.get("columns", {})
        print(json.dumps({"name": target["name"], "error": res.get("error"),
                          "gate_facts": res.get("gate_facts"),
                          "header": [c["name"] for c in cols.get("columns", [])]},
                         ensure_ascii=False))
    print(f"CENSUS-DONE {ok}/{len(TARGETS)}")
    return 0 if ok == len(TARGETS) else 1


if __name__ == "__main__":
    sys.exit(main())
