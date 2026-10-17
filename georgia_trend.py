#!/usr/bin/env python3
"""georgia_trend 0.1.0: did lead in spices bought in Georgia fall after 2020?

Grades docs/georgia-trend-0.1.0-prereg.md, which was committed (release v0.4.1) before
any NYC result was split by year within a purchase country. The rows are exactly
purchase_place.tagged_rows (0.1.0, unchanged) read from the committed snapshot
data/nyc_spice_lead_snapshot_2026-10-17.csv, case investigations (frame C) only,
collection years 2016-2025: early = 2016-2020, late = 2021-2025.

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
"""
import argparse
import csv
import json
import os
import sys

import frame_period as fp
import purchase_place as pp
import sampling_frame as sf

VERSION = "0.1.0"
SNAPSHOT = fp.SNAPSHOT
PERIODS = (("early", 2016, 2020), ("late", 2021, 2025))
SERIES = ("GEORGIA", "BANGLADESH", "other_abroad", "abroad", "US")
COLUMNS = ("n_result", "n_ge2", "n_ge50")
YEAR_COUNTRIES = ("GEORGIA", "BANGLADESH")
MIN_RESULTS = 15


def dated_rows(records):
    """purchase_place.tagged_rows, one record at a time, plus the collection date."""
    rows = []
    for rec in records:
        for row in pp.tagged_rows([rec]):
            row["date"] = (rec.get("collection_date") or "")[:10]
            rows.append(row)
    return rows


def period_of(year):
    if not year:
        return None
    for name, lo, hi in PERIODS:
        if lo <= int(year) <= hi:
            return name
    return None


def in_series(row, series):
    if series == "abroad":
        return row["group"] == "abroad"
    if series == "US":
        return row["group"] == "US"
    if series == "other_abroad":
        return row["group"] == "abroad" and row["country"] not in YEAR_COUNTRIES
    return row["country"] == series


def case_rows(rows):
    return [r for r in rows if r["frame"] == "C" and period_of(r["year"]) and r["status"] != "missing"]


def table(rows):
    """One row per (series, period)."""
    cases = case_rows(rows)
    out = []
    for series in SERIES:
        for name, _, _ in PERIODS:
            c = pp.count([r for r in cases if in_series(r, series) and period_of(r["year"]) == name])
            row = {"series": series, "period": name}
            row.update({k: c[k] for k in COLUMNS})
            out.append(row)
    return out


def by_year(rows):
    """Results and results >= 50 ppm by collection year (reported without prediction)."""
    cases = case_rows(rows)
    out = []
    for country in YEAR_COUNTRIES:
        for year in range(PERIODS[0][1], PERIODS[-1][2] + 1):
            c = pp.count([r for r in cases if r["country"] == country and int(r["year"]) == year])
            out.append({"country": country, "year": year,
                        "n_result": c["n_result"], "n_ge50": c["n_ge50"]})
    return out


def dates(rows, country):
    """Distinct collection dates per period, and how many have any result >= 50 ppm.

    A date stands in for one investigation; it is a proxy, not a household ID.
    """
    cases = [r for r in case_rows(rows) if r["country"] == country]
    out = {}
    for name, _, _ in PERIODS:
        sel = [r for r in cases if period_of(r["year"]) == name]
        hot = {r["date"] for r in sel if r["status"] == "value" and r["value"] >= 50}
        out[name] = {"n_dates": len({r["date"] for r in sel}), "n_dates_ge50": len(hot)}
    return out


def dates_fisher(d):
    e, l = d["early"], d["late"]
    return float(sf.fisher_two_sided(e["n_dates_ge50"], e["n_dates"] - e["n_dates_ge50"],
                                     l["n_dates_ge50"], l["n_dates"] - l["n_dates_ge50"]))


def find(tab, series, period):
    return next(r for r in tab if (r["series"], r["period"]) == (series, period))


def grade(tab):
    """The five pre-registered predictions."""
    ge, gl = find(tab, "GEORGIA", "early"), find(tab, "GEORGIA", "late")
    be, bl = find(tab, "BANGLADESH", "early"), find(tab, "BANGLADESH", "late")
    ae, al = find(tab, "abroad", "early"), find(tab, "abroad", "late")
    gradable = min(ge["n_result"], gl["n_result"]) >= MIN_RESULTS
    p3 = pp.fisher(ge, gl, 50)
    p4 = pp.fisher(be, bl, 50)
    early_frac = ge["n_result"] / ae["n_result"]
    late_frac = gl["n_result"] / al["n_result"]
    grades = {
        "gradable": gradable,
        "P1_georgia_late_share_ge50_below_early": {
            "early": pp.share(ge, 50), "late": pp.share(gl, 50),
            "met": pp.share(gl, 50) < pp.share(ge, 50) if gradable else None},
        "P2_georgia_late_at_most_half_early": {
            "met": pp.share(gl, 50) <= 0.5 * pp.share(ge, 50) if gradable else None},
        "P3_georgia_fisher_ge50_below_0.05": {
            "p": p3, "met": p3 < 0.05 if gradable else None},
        "P4_control_bangladesh_fisher_ge50_at_least_0.05": {
            "early": pp.share(be, 50), "late": pp.share(bl, 50), "p": p4, "met": p4 >= 0.05},
        "P5_georgia_fraction_of_abroad_smaller_late": {
            "early": early_frac, "late": late_frac, "met": late_frac < early_frac},
    }
    grades["n_met"] = sum(1 for g in grades.values() if isinstance(g, dict) and g["met"] is True)
    return grades


def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--snapshot", default=SNAPSHOT)
    ap.add_argument("--out-dir", default="data")
    args = ap.parse_args(argv)
    rows = dated_rows(fp.read_snapshot(args.snapshot))
    tab = table(rows)
    write(os.path.join(args.out_dir, "georgia_trend.csv"), tab)
    write(os.path.join(args.out_dir, "georgia_trend_by_year.csv"), by_year(rows))
    print(json.dumps(grade(tab), indent=2))
    d = dates(rows, "GEORGIA")
    print("Georgia collection dates: %s; Fisher p (dates with any >= 50 ppm) = %.3g"
          % (json.dumps(d), dates_fisher(d)))
    for series in ("other_abroad", "abroad", "US"):
        e, l = find(tab, series, "early"), find(tab, series, "late")
        for t in (2, 50):
            print("%s >= %d ppm: early %d/%d, late %d/%d, Fisher p = %.3g" % (
                series, t, e["n_ge%d" % t], e["n_result"], l["n_ge%d" % t], l["n_result"],
                pp.fisher(e, l, t)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
