#!/usr/bin/env python3
"""frame_period 0.1.0: NYC spice lead hit rates by sampling frame, split by period and threshold.

A descriptive follow-up to sampling_frame 0.1.0 (not pre-registered; it grades no
predictions). NYC's store surveys are almost all from 2016 on, while a third of the
early case-investigation results come from 2011-2015, so this compares case
investigations (C) with store surveys (S) inside each period, at 2, 10, 50 and 500 ppm.

Reads the committed snapshot data/nyc_spice_lead_snapshot_2026-10-17.csv through
sampling_frame's own parser, so the rows are exactly those graded in
docs/sampling-frame-0.1.0-result.md.

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
"""
import argparse
import csv
import os
import sys

import sampling_frame as sf

VERSION = "0.1.0"
SNAPSHOT = os.path.join("data", "nyc_spice_lead_snapshot_2026-10-17.csv")
THRESHOLDS = (2, 10, 50, 500)
PERIODS = (("2011-2015", 2011, 2015), ("2016-2025", 2016, 2025))
FRAMES = ("C", "S")


def read_snapshot(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def period_of(year):
    if not year:
        return None
    for name, lo, hi in PERIODS:
        if lo <= int(year) <= hi:
            return name
    return None


def ladder(rows):
    """One row per (period, frame): results, and how many are at or above each threshold."""
    out = []
    for name, _, _ in PERIODS:
        for frame in FRAMES:
            sel = [r for r in rows if r["frame"] == frame and period_of(r["year"]) == name
                   and r["status"] != "missing"]
            values = [r["value"] for r in sel if r["status"] == "value"]
            row = {"period": name, "frame": frame, "n_result": len(sel)}
            for t in THRESHOLDS:
                row["n_ge%d" % t] = sum(1 for v in values if v >= t)
            out.append(row)
    return out


def find(lad, period, frame):
    return next(r for r in lad if (r["period"], r["frame"]) == (period, frame))


def fisher_c_vs_s(lad, period, threshold):
    """Exact two-sided Fisher p, case investigation vs store survey, within one period."""
    c, s = find(lad, period, "C"), find(lad, period, "S")
    k = "n_ge%d" % threshold
    return float(sf.fisher_two_sided(c[k], c["n_result"] - c[k], s[k], s["n_result"] - s[k]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--snapshot", default=SNAPSHOT)
    ap.add_argument("--out", default=os.path.join("data", "frame_period_ladder.csv"))
    args = ap.parse_args(argv)
    lad = ladder(sf.nyc_rows(read_snapshot(args.snapshot)))
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(lad[0].keys()))
        w.writeheader()
        w.writerows(lad)
    for name, _, _ in PERIODS:
        for t in THRESHOLDS:
            print("%s >= %d ppm: Fisher p (C vs S) = %.3g" % (name, t, fisher_c_vs_s(lad, name, t)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
