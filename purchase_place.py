#!/usr/bin/env python3
"""purchase_place 0.1.0: NYC spice lead hit rates by sampling frame and country of purchase.

Grades docs/purchase-place-0.1.0-prereg.md, which was committed before any NYC result
was split by purchase country. The rows are exactly sampling_frame.nyc_rows
(Food-Spice, lead, laboratory, ppm) read from the committed snapshot
data/nyc_spice_lead_snapshot_2026-10-17.csv. Each row gets a purchase group:
  US       purchase_country is exactly UNITED STATES
  unknown  blank, UNKNOWN OR NOT STATED, or UNITED STATES MINOR OUTLYING ISLANDS
  abroad   any other value

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
"""
import argparse
import csv
import json
import os
import sys

import frame_period as fp
import sampling_frame as sf

VERSION = "0.1.0"
SNAPSHOT = fp.SNAPSHOT
GROUPS = ("US", "unknown", "abroad")
UNKNOWN = {"", "UNKNOWN OR NOT STATED", "UNITED STATES MINOR OUTLYING ISLANDS"}


def purchase_group(text):
    value = (text or "").strip().upper()
    if value == "UNITED STATES":
        return "US"
    if value in UNKNOWN:
        return "unknown"
    return "abroad"


def tagged_rows(records):
    """sampling_frame.nyc_rows, one record at a time, plus purchase country and group."""
    rows = []
    for rec in records:
        for row in sf.nyc_rows([rec]):
            row["country"] = (rec.get("purchase_country") or "").strip().upper()
            row["group"] = purchase_group(row["country"])
            rows.append(row)
    return rows


def count(sel):
    values = [r["value"] for r in sel if r["status"] == "value"]
    out = {"n_result": len(sel)}
    for t in fp.THRESHOLDS:
        out["n_ge%d" % t] = sum(1 for v in values if v >= t)
    return out


def table(rows):
    """One row per (period, frame, purchase group)."""
    out = []
    for name, _, _ in fp.PERIODS:
        for frame in fp.FRAMES:
            for group in GROUPS:
                sel = [r for r in rows if r["frame"] == frame and r["group"] == group
                       and fp.period_of(r["year"]) == name and r["status"] != "missing"]
                row = {"period": name, "frame": frame, "group": group}
                row.update(count(sel))
                out.append(row)
    return out


def by_country(rows, period, frame, country):
    sel = [r for r in rows if r["frame"] == frame and r["country"] == country
           and fp.period_of(r["year"]) == period and r["status"] != "missing"]
    return count(sel)


def find(tab, period, frame, group):
    return next(r for r in tab if (r["period"], r["frame"], r["group"]) == (period, frame, group))


def share(row, threshold):
    return row["n_ge%d" % threshold] / row["n_result"]


def fisher(r1, r2, threshold):
    """Exact two-sided Fisher p for r1 vs r2 at one threshold."""
    k = "n_ge%d" % threshold
    return float(sf.fisher_two_sided(r1[k], r1["n_result"] - r1[k], r2[k], r2["n_result"] - r2[k]))


def grade(tab):
    """The five pre-registered predictions, on C rows from 2016-2025."""
    us = find(tab, "2016-2025", "C", "US")
    ab = find(tab, "2016-2025", "C", "abroad")
    c_ge50 = sum(r["n_ge50"] for r in tab if (r["period"], r["frame"]) == ("2016-2025", "C"))
    p5 = fisher(ab, us, 50)
    grades = {
        "P1_C_US_share_ge50_at_most_0.015": {
            "share": share(us, 50), "met": share(us, 50) <= 0.015},
        "P2_C_abroad_share_ge50_at_least_0.10": {
            "share": share(ab, 50), "met": share(ab, 50) >= 0.10},
        "P3_C_US_share_ge2_in_0.04_to_0.16": {
            "share": share(us, 2), "met": 0.04 <= share(us, 2) <= 0.16},
        "P4_C_abroad_at_least_70pct_of_C_ge50": {
            "abroad_ge50": ab["n_ge50"], "C_ge50": c_ge50, "met": ab["n_ge50"] >= 0.70 * c_ge50},
        "P5_fisher_abroad_vs_US_ge50_below_0.001": {
            "p": p5, "met": p5 < 0.001 and share(ab, 50) > share(us, 50)},
    }
    grades["n_met"] = sum(1 for g in grades.values() if isinstance(g, dict) and g["met"])
    return grades


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--snapshot", default=SNAPSHOT)
    ap.add_argument("--out", default=os.path.join("data", "purchase_place.csv"))
    args = ap.parse_args(argv)
    tab = table(tagged_rows(fp.read_snapshot(args.snapshot)))
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tab[0].keys()))
        w.writeheader()
        w.writerows(tab)
    print(json.dumps(grade(tab), indent=2))
    us, s = find(tab, "2016-2025", "C", "US"), find(tab, "2016-2025", "S", "US")
    for t in fp.THRESHOLDS:
        print("2016-2025 >= %d ppm: Fisher p (C-US vs S) = %.3g" % (t, fisher(us, s, t)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
