#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""pah2019-census 0.1.0: re-run the names-only census of CFIA's open 2019-20 PAH file alone, with
patient retries.

The first census job (cfia-census-2019-v1, 2026-10-31) read the two BPA files but could not
download this one: both open.canada.ca and ouvert.canada.ca reset the connection twice. This
module runs exactly the published cfia_census.run_target on the same target (dataset
4884f9d1-...), retrying a few minutes apart, so the bpa-pah-report 0.1.0 item D1 can be graded
on the same names-only census code. It never prints, sums or compares a result value. Standard
library only. Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0; derived
data CC BY 4.0.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import cfia_census as cc

VERSION = "0.1.0"
NAME = "pah-2019"


def target():
    """The pah-2019 entry of cfia_census.TARGETS."""
    return next(t for t in cc.TARGETS if t["name"] == NAME)


def ok(res):
    return "error" not in res and "error" not in res.get("census", {})


def census_with_retries(data_dir, tries=6, pause=120):
    """(result, attempts): run cfia_census.run_target until it reads the file or tries run out."""
    res, errors = {}, []
    for i in range(1, tries + 1):
        res = cc.run_target(target(), data_dir)
        if ok(res):
            res["attempts"] = i
            res["earlier_errors"] = errors
            return res, i
        errors.append(res.get("error") or res.get("census", {}).get("error"))
        print(f"attempt {i} of {tries} failed: {errors[-1]}")
        if i < tries:
            time.sleep(pause)
    res["attempts"] = tries
    res["earlier_errors"] = errors[:-1]
    return res, tries


def main(argv=None):
    ap = argparse.ArgumentParser(description="Names-only census of CFIA's 2019-20 PAH file.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--tries", type=int, default=6)
    ap.add_argument("--pause", type=float, default=120)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    res, _ = census_with_retries(args.data_dir, args.tries, args.pause)
    with open(os.path.join(args.out_dir, f"{NAME}_census.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, sort_keys=True, ensure_ascii=False)
    print(json.dumps(res, indent=2, sort_keys=True, ensure_ascii=False))
    print(f"CENSUS-DONE {1 if ok(res) else 0}/1")
    return 0 if ok(res) else 1


if __name__ == "__main__":
    sys.exit(main())
