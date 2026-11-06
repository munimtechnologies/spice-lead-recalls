#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""phthalates-series-census 0.1.0: a names-only structure census of two open CFIA phthalates
files, run after docs/phthalates-series-0.1.0-prereg.md is public and before any value is read:

- F: "Phthalates in Flatbread and Vegan Products - 2018-2019" (dataset c4202b90-...)
- P: "Food Safety Action Plan Targeted Survey - Phthalates 2012 to 2018" (dataset ea25d8e4-...)

For each file it runs phthalates_census.run_text (cfia_census.census: labels, units and cell
shapes per component; bpa_series_census.columns_census: shapes and text-label counts per column;
perchlorate_census.product_years: samples per product label per April-March survey year; and the
header cells that name a phthalate), then derives the census-gradable gate facts (F-G, P-G) with
phthalates_census.gate_facts. New here: the portal sizes are kibibytes, so each size band is the
whole-KiB rounding band, and survey_years() lists which April-March years are present. No result
value is printed, summed or compared. Both files are on open.canada.ca under the Open Government
Licence - Canada. Standard library only. Made with AI agents working in MV2's (Munim, Inc.) name.
Code Apache-2.0; derived data CC BY 4.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import cfia_census as cc
import phthalates_census as pc

VERSION = "0.1.0"


def kib_band(kib):
    """Byte counts that round to `kib` whole kibibytes: [(kib - 0.5) * 1024, (kib + 0.5) * 1024]."""
    return (int((kib - 0.5) * 1024), int((kib + 0.5) * 1024))


TARGETS = (
    {"name": "fv18",
     "dataset": "c4202b90-03d1-4eef-9fcc-0740066fc0c4",
     "resource": "8ce9082f-b339-4e5d-b74a-fa1747d295ac",
     "path": "fsap-chem-ts-2018-2019-phthalates-in-flatbread-and-vegan-products.csv",
     "size": None, "portal_kib": 147, "size_band": kib_band(147),
     "md5": "22dc3074e8e2c55b60fb96a666c5ff16", "samples": 599,
     "years": ("2018-19",)},
    {"name": "ps12",
     "dataset": "ea25d8e4-180c-4f7c-a912-f37381168664",
     "resource": "072329d5-0f9c-4e3f-aae1-c4996ae2b5d5",
     "path": ("fsap-chem-ts-2012-2018-phthalates-in-selected-foods-"
              "paaspa-chem-ec-2012-2018-phtalates-dans-cert.csv"),
     "size": None, "portal_kib": 1259, "size_band": kib_band(1259),
     "md5": "2c80659a91013f3657519375ee33b400", "samples": 4517,
     "years": ("2012-13", "2013-14", "2014-15", "2015-16", "2016-17", "2017-18")},
)


def survey_years(product_years, expected):
    """Which April-March survey years are present, and whether exactly the expected ones are."""
    by_year = (product_years or {}).get("by_year") or {}
    present = sorted(k for k in by_year if k != "(unparsed)")
    return {"present": present, "unparsed": by_year.get("(unparsed)", 0),
            "missing": [y for y in expected if y not in by_year],
            "extra": [y for y in present if y not in expected],
            "exact": present == sorted(expected) and not by_year.get("(unparsed)", 0)}


def run_target(target, data_dir):
    res = {"study": f"phthalates-series-{target['name']}-census", "version": VERSION,
           "dataset": target["dataset"], "resource": target["resource"],
           "portal_size": f"{target['portal_kib']} (KiB)", "portal_md5": target["md5"]}
    try:
        raw, src = cc.load(target, data_dir)
    except Exception as exc:  # noqa: BLE001 - recorded, the other file still runs
        res["error"] = f"{type(exc).__name__}: {exc}"
        return res
    text, enc = cc.decode(raw)
    md5 = hashlib.md5(raw).hexdigest()
    res.update({"source": src, "bytes": len(raw), "encoding": enc,
                "sha256": hashlib.sha256(raw).hexdigest(), "md5": md5,
                "md5_matches_portal": md5 == target["md5"]})
    res.update(pc.run_text(text))
    res["gate_facts"] = pc.gate_facts(res, target)
    res["survey_years"] = survey_years(res.get("product_years"), target["years"])
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description="Names-only census of two CFIA phthalates files.")
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
                          "survey_years": res.get("survey_years"),
                          "first": py.get("first"), "last": py.get("last")},
                         ensure_ascii=False))
    print(f"CENSUS-DONE {ok}/{len(TARGETS)}")
    return 0 if ok == len(TARGETS) else 1


if __name__ == "__main__":
    sys.exit(main())
