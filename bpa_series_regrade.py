#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""bpa-series 0.1.1 regrade: the published bpa_series_grade.py (0.1.0), unchanged, with one
format-only amendment to its sample-ID pattern (docs/id-pattern-0.1.1-amendment.md).

Made with AI agents working in MV2's (Munim, Inc.) name.

The 0.1.0 run failed two of seven gates (2009-10 and 2011-12) only because some sample IDs did not
fit the pattern ^C?\\d{4}[A-Z]+\\d{4,6}D?$: eight 2009-10 IDs have a three-digit number
(2009BPA176 to 2009BPA183) and three 2011-12 IDs end in '-2'. Every other gate check (byte size,
columns, rows, sample count, units, plan code, labels, value rule) held. This module widens the
pattern to accept a three-digit number and a '-2' suffix, and nothing else, then runs the
published grader's main() as it is. It also writes id_amendment.json: the IDs the old pattern
rejects and, for each '-2' ID, whether its base ID is also in the file. Standard library only.
Code Apache-2.0; derived data CC BY 4.0. Not a compliance finding, not about any brand, and not
dietary or medical advice.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

import bpa_series_grade as g

VERSION = "0.1.1"
OLD_ID_RE = re.compile(r"^C?\d{4}[A-Z]+\d{4,6}D?$")
ID_RE = re.compile(r"^C?\d{4}[A-Z]+\d{3,6}(?:D|-2)?$")
SUFFIX_FILES = ("bpa-2009", "bpa-2011")


def apply():
    """Point the published grader at the amended pattern; return the pattern now in use."""
    g.ID_RE = ID_RE
    return g.ID_RE


def base_id(sid):
    """'2011BPA0086-2' -> '2011BPA0086'; other IDs unchanged."""
    return sid[:-2] if sid.endswith("-2") else sid


def old_rejects(samples):
    """Sorted IDs the 0.1.0 pattern rejects."""
    return sorted(s["sample"] for s in samples if not OLD_ID_RE.match(s["sample"]))


def suffix_report(samples):
    """For each '-2' ID: its product, date and BPA, and the same for its base ID if present."""
    by = {s["sample"]: s for s in samples}
    out = []
    for sid in sorted(by):
        if not sid.endswith("-2"):
            continue
        s = by[sid]
        b = by.get(base_id(sid))
        out.append({"sample": sid, "product": s["product"], "date": s["date"],
                    "bpa_ppb": s["ppb"]["bpa"], "base": base_id(sid),
                    "base_present": b is not None,
                    "base_product": b["product"] if b else None,
                    "base_date": b["date"] if b else None,
                    "base_bpa_ppb": b["ppb"]["bpa"] if b else None})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Regrade bpa-series with the amended ID pattern.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    apply()
    code = g.main(["--data-dir", args.data_dir, "--out-dir", args.out_dir])
    extra = {"amendment": "id-pattern-0.1.1", "version": VERSION, "grader_version": g.VERSION,
             "old_pattern": OLD_ID_RE.pattern, "pattern": g.ID_RE.pattern, "files": {}}
    for name in SUFFIX_FILES:
        try:
            samples, census, size, prov = g.run_one(name, args.data_dir)
            gate = g.gate_checks(census, size, name)
            extra["files"][name] = {"gate": gate, "ids_bad": census["ids_bad"],
                                    "old_pattern_rejects": old_rejects(samples),
                                    "suffix_pairs": suffix_report(samples),
                                    "sha256": prov.get("sha256")}
        except Exception as exc:  # noqa: BLE001 - reported, not hidden
            extra["files"][name] = {"error": f"{type(exc).__name__}: {exc}"}
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "id_amendment.json"), "w", encoding="utf-8") as fh:
        json.dump(extra, fh, indent=2, sort_keys=True, ensure_ascii=False)
    print(json.dumps(extra, indent=2, sort_keys=True, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
