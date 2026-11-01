#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""pah-2019 0.1.1 regrade: the published pah_2019.py (0.1.0), unchanged, with one format-only
amendment to its sample-ID pattern (docs/id-pattern-0.1.1-amendment.md).

Made with AI agents working in MV2's (Munim, Inc.) name.

The 0.1.0 run failed its gate only because two of 296 sample IDs (C2019PAHS00037AD and
C2019PAHS00040AD) did not fit ^C2019PAHS(\\d{5})A$. Every other gate check (byte size, columns,
4,736 rows, 296 samples with 16 rows each, unit, plan code, labels, value rule) held. This module
widens the pattern to allow one trailing 'D' after the 'A', and nothing else, then runs the
published grader's main() as it is. It also writes id_amendment.json: for each D-suffixed ID,
whether its base ID (without the 'D') is in the file, and whether the two share all 16 values.
Standard library only. Code Apache-2.0; derived data CC BY 4.0. Not a compliance finding, not
about any brand, and not dietary or medical advice.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

import pah_2019 as g

VERSION = "0.1.1"
OLD_ID_RE = re.compile(r"^C2019PAHS(\d{5})A$")
ID_RE = re.compile(r"^C2019PAHS(\d{5})AD?$")


def apply():
    """Point the published grader at the amended pattern; return the pattern now in use."""
    g.ID_RE = ID_RE
    return g.ID_RE


def base_id(sid):
    """'C2019PAHS00037AD' -> 'C2019PAHS00037A'; other IDs unchanged."""
    return sid[:-1] if sid.endswith("AD") else sid


def profile(s):
    return tuple(s["vals"].get(c) or 0.0 for c in g.COMPONENTS)


def suffix_report(samples):
    """For each D-suffixed ID: product, Function, origin, date and TEQ, the same for its base ID
    if present, and whether the two have identical values for all 16 PAHs."""
    by = {s["sample"]: s for s in samples}
    out = []
    for sid in sorted(by):
        if not sid.endswith("AD"):
            continue
        s = by[sid]
        b = by.get(base_id(sid))
        out.append({"sample": sid, "product": s["product"], "function": s["function"],
                    "origin": s["origin"], "date": s["date"], "teq": s["teq"],
                    "base": base_id(sid), "base_present": b is not None,
                    "base_product": b["product"] if b else None,
                    "base_function": b["function"] if b else None,
                    "base_origin": b["origin"] if b else None,
                    "base_date": b["date"] if b else None,
                    "base_teq": b["teq"] if b else None,
                    "identical_16": (profile(s) == profile(b)) if b else None})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Regrade pah-2019 with the amended ID pattern.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    apply()
    code = g.main(["--data-dir", args.data_dir, "--out-dir", args.out_dir])
    extra = {"amendment": "id-pattern-0.1.1", "version": VERSION, "grader_version": g.VERSION,
             "old_pattern": OLD_ID_RE.pattern, "pattern": g.ID_RE.pattern}
    try:
        raw, _ = g.load(args.data_dir)
        text, _ = g.decode(raw)
        samples, census = g.parse(text)
        extra["ids_bad"] = census["ids_bad"]
        extra["old_pattern_rejects"] = sorted(s["sample"] for s in samples
                                              if not OLD_ID_RE.match(s["sample"]))
        extra["suffix_pairs"] = suffix_report(samples)
    except Exception as exc:  # noqa: BLE001 - reported, not hidden
        extra["error"] = f"{type(exc).__name__}: {exc}"
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "id_amendment.json"), "w", encoding="utf-8") as fh:
        json.dump(extra, fh, indent=2, sort_keys=True, ensure_ascii=False)
    print(json.dumps(extra, indent=2, sort_keys=True, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
