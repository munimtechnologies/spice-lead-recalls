#!/usr/bin/env python3
"""purchase_recording 0.1.0: how often NYC's spice lead records lack a purchase country, by year.

A descriptive robustness check of georgia_trend 0.1.0. It is not pre-registered and
grades no predictions. NYC case-investigation spice results (frame C, 2016-2025) are
split by collection year into those with a recorded purchase country and those in
purchase_place's "unknown" group (blank, UNKNOWN OR NOT STATED, or UNITED STATES MINOR
OUTLYING ISLANDS). Then each georgia_trend claim is re-checked with the unknowns
assigned in the way least favourable to it.

Reads the committed snapshot data/nyc_spice_lead_snapshot_2026-10-17.csv through
georgia_trend.dated_rows, so the rows are exactly those graded in v0.4.2.

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
"""
import argparse
import csv
import json
import os
import sys

import frame_period as fp
import georgia_trend as gt
import sampling_frame as sf

VERSION = "0.1.0"
SNAPSHOT = fp.SNAPSHOT
YEARS = range(2016, 2026)
GROSS = 50


def gross(row):
    return row["status"] == "value" and row["value"] >= GROSS


def by_year(rows):
    """Case-investigation results per collection year: all, purchase country unknown, >= 50 ppm."""
    cases = gt.case_rows(rows)
    out = []
    for year in YEARS:
        sel = [r for r in cases if int(r["year"]) == year]
        unk = [r for r in sel if r["group"] == "unknown"]
        out.append({"year": year, "n_result": len(sel), "n_unknown": len(unk),
                    "n_ge50": sum(1 for r in sel if gross(r)),
                    "n_ge50_unknown": sum(1 for r in unk if gross(r))})
    return out


def period_totals(table):
    out = {}
    for name, lo, hi in gt.PERIODS:
        sel = [r for r in table if lo <= r["year"] <= hi]
        out[name] = {k: sum(r[k] for r in sel) for k in ("n_result", "n_unknown", "n_ge50", "n_ge50_unknown")}
    return out


def fisher(a, n1, c, n2):
    return float(sf.fisher_two_sided(a, n1 - a, c, n2 - c))


def bounds(rows, gtab):
    """Each georgia_trend claim with the unknown-country results placed against it."""
    tot = period_totals(by_year(rows))
    e, l = tot["early"], tot["late"]
    ae, al = gt.find(gtab, "abroad", "early"), gt.find(gtab, "abroad", "late")
    ge, gl = gt.find(gtab, "GEORGIA", "early"), gt.find(gtab, "GEORGIA", "late")
    # Abroad, worst case for "it fell": every late unknown was bought abroad, no early one was.
    al_n = al["n_result"] + l["n_unknown"]
    al_k = al["n_ge50"] + l["n_ge50_unknown"]
    # Georgia, worst case for "its share fell": only the late unknown results >= 50 ppm were Georgian.
    gl_n = gl["n_result"] + l["n_ge50_unknown"]
    gl_k = gl["n_ge50"] + l["n_ge50_unknown"]
    return {
        "periods": tot,
        "all_cases_ge50": {"early": [e["n_ge50"], e["n_result"]], "late": [l["n_ge50"], l["n_result"]],
                           "p": fisher(e["n_ge50"], e["n_result"], l["n_ge50"], l["n_result"])},
        "unknown_share_of_ge50": {"early": [e["n_ge50_unknown"], e["n_ge50"]],
                                  "late": [l["n_ge50_unknown"], l["n_ge50"]],
                                  "p": fisher(e["n_ge50_unknown"], e["n_ge50"], l["n_ge50_unknown"], l["n_ge50"])},
        "abroad_worst_case_ge50": {"early": [ae["n_ge50"], ae["n_result"]], "late": [al_k, al_n],
                                   "p": fisher(ae["n_ge50"], ae["n_result"], al_k, al_n)},
        "georgia_worst_case_share_ge50": {"early": [ge["n_ge50"], ge["n_result"]], "late": [gl_k, gl_n],
                                          "late_share_exceeds_early": gl_k / gl_n > ge["n_ge50"] / ge["n_result"]},
        "georgia_ge50_count": {"early": ge["n_ge50"], "late_min": gl["n_ge50"],
                               "late_max": gl["n_ge50"] + l["n_ge50_unknown"]},
    }


def unknown_gross_dates(rows):
    """Distinct collection dates of late results >= 50 ppm with no purchase country."""
    return sorted({r["date"] for r in gt.case_rows(rows)
                   if gt.period_of(r["year"]) == "late" and r["group"] == "unknown" and gross(r)})


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--snapshot", default=SNAPSHOT)
    ap.add_argument("--out", default=os.path.join("data", "purchase_recording_by_year.csv"))
    args = ap.parse_args(argv)
    rows = gt.dated_rows(fp.read_snapshot(args.snapshot))
    table = by_year(rows)
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(table[0].keys()))
        w.writeheader()
        w.writerows(table)
    print(json.dumps(bounds(rows, gt.table(rows)), indent=2))
    print("late unknown-country dates with a result >= 50 ppm:", unknown_gross_dates(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
