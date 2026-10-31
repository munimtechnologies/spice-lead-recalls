#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exploratory: list every set of samples in the published pah-2018 per-sample table whose 16 PAH
values are all identical (ignoring samples with no PAH detected), and the same for the four TEQ
PAHs alone. Prints JSON; asserts nothing. Made with AI agents working in MV2's (Munim, Inc.)
name."""
import csv
import json
import sys

TEQ4 = ("Benzo[a]pyrene", "Benzo[a]anthracene", "Benzo[b]fluoranthene", "Chrysene")


def main(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    cols = [c for c in rows[0] if c.startswith("ppb:")]
    full, four = {}, {}
    for r in rows:
        v = tuple(float(r[c]) for c in cols)
        if any(x > 0 for x in v):
            full.setdefault(v, []).append(r)
        v4 = tuple(float(r["ppb:" + c]) for c in TEQ4)
        if any(x > 0 for x in v4):
            four.setdefault(v4, []).append(r)

    def sets(d):
        return [[{"sample": r["sample"], "product": r["product"], "origin": r["origin"],
                  "region": r["region"], "n_pah": int(r["n_pah"])} for r in rs]
                for rs in d.values() if len(rs) > 1]

    out = {"samples": len(rows), "with_any_pah": sum(len(v) for v in full.values()),
           "identical_16": sets(full), "with_any_teq4": sum(len(v) for v in four.values()),
           "identical_teq4": sets(four)}
    print("TWIN-SCAN " + json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
