#!/usr/bin/env python3
"""cr_band_sensitivity: does the chromate verdict depend on the band edge or on rounding?

cr_baseline scores NYC's chromate-like spice pairs with a molar Pb:Cr upper band
edge R = 2.0 and treats the lab's lead and chromium values as exact. This script
varies both, as a descriptive sensitivity table (not a pre-registered test):

1. Band edge. For R in {1.5, 2.0, 3.0} it recomputes
       edge_R = Cr - (Pb / 207.2) / R * 51.996      (ppm)
   and the verdict against the same published natural-chromium ceilings. A pair
   whose own molar ratio is above R is "outside-band" (no longer chromate-like).
   It also reports r_crit = Pb * 51.996 / 207.2 / (Cr - highest_ceiling), the
   smallest upper edge at which the pair is still robust (empty when the measured
   chromium is itself at or below the highest ceiling, so no edge can make it
   robust), and any pair from the full NYC pairs table that would newly enter
   the band at that R.
2. Rounding. NYC reports values to two significant figures. At R = 2.0 it
   takes the worst case for each pair: lead up and chromium down by half a unit
   in the second significant figure, which gives the smallest possible edge.

Inputs (both committed): data/cr_baseline.csv and data/nyc_spice_pb_cr_pairs.csv.
Pure transform of already-published bytes; no new chemistry or ceilings.

By MV2, Munim, Inc. Made with AI agents. Apache-2.0.
"""
import argparse
import csv
import io
import os
import urllib.request
from decimal import Decimal

__version__ = "0.1.0"

RAW = "https://raw.githubusercontent.com/munimtechnologies/spice-lead-recalls/main/"
HERE = os.path.dirname(os.path.abspath(__file__))
BASELINE = os.path.join(HERE, "data", "cr_baseline.csv")
PAIRS = os.path.join(HERE, "data", "nyc_spice_pb_cr_pairs.csv")

PB = 207.2
CR = 51.996
EDGES = [1.5, 2.0, 3.0]
OPERATING_EDGE = 2.0
# Pairs the NYC screen judged (enough lead) but left out of the band for having
# too much lead; these are the only ones a wider upper edge could bring in.
JUDGED_ABOVE_BAND = "more lead than chromate"

FIELDS = ["lead_row_id", "chromium_row_id", "product_name", "purchase_country", "matrix",
          "lead_ppm", "chromium_ppm", "molar_ratio_pb_cr", "highest_ceiling_ppm",
          "edge_r1_5", "verdict_r1_5", "edge_r2", "verdict_r2", "edge_r3", "verdict_r3",
          "r_crit", "edge_r2_worst_rounding", "verdict_r2_worst_rounding"]


def _suffix(r):
    return ("%g" % r).replace(".", "_")


def load_rows(source):
    if source.startswith("http"):
        with urllib.request.urlopen(source, timeout=60) as resp:
            text = resp.read().decode("utf-8-sig")
    else:
        with open(source, encoding="utf-8-sig") as fh:
            text = fh.read()
    return list(csv.DictReader(io.StringIO(text, newline="")))


def molar_ratio(pb, cr):
    return (pb / PB) / (cr / CR)


def edge_ppm(pb, cr, r):
    """Largest natural chromium that can come off cr before Pb:Cr rises above r."""
    return cr - (pb / PB) / r * CR


def half_unit(v):
    """Half a unit in the second significant figure of a reported value."""
    if v <= 0:
        return 0.0
    return 0.5 * 10.0 ** (Decimal(repr(v)).adjusted() - 1)


def verdict(pb, cr, r, hi, lo):
    if molar_ratio(pb, cr) > r:
        return "outside-band"
    e = edge_ppm(pb, cr, r)
    if e > hi:
        return "robust"
    if e <= lo:
        return "background-limited"
    return "unresolved"


def r_crit(pb, cr, hi):
    if cr <= hi:
        return None
    return (pb / PB) * CR / (cr - hi)


def analyse(baseline_rows, pair_rows):
    out = []
    for b in baseline_rows:
        pb, cr = float(b["lead_ppm"]), float(b["chromium_ppm"])
        hi, lo = float(b["highest_ceiling_ppm"]), float(b["lowest_ceiling_ppm"])
        d = {
            "lead_row_id": b["lead_row_id"],
            "chromium_row_id": b["chromium_row_id"],
            "product_name": b["product_name"],
            "purchase_country": b["purchase_country"],
            "matrix": b["matrix"],
            "lead_ppm": pb,
            "chromium_ppm": cr,
            "molar_ratio_pb_cr": round(molar_ratio(pb, cr), 3),
            "highest_ceiling_ppm": hi,
        }
        for r in EDGES:
            d["edge_r" + _suffix(r)] = round(edge_ppm(pb, cr, r), 2)
            d["verdict_r" + _suffix(r)] = verdict(pb, cr, r, hi, lo)
        rc = r_crit(pb, cr, hi)
        d["r_crit"] = "" if rc is None else round(rc, 4)
        pb_w, cr_w = pb + half_unit(pb), cr - half_unit(cr)
        d["edge_r2_worst_rounding"] = round(edge_ppm(pb_w, cr_w, OPERATING_EDGE), 2)
        d["verdict_r2_worst_rounding"] = verdict(pb_w, cr_w, OPERATING_EDGE, hi, lo)
        out.append(d)

    counts = {}
    for r in EDGES:
        key = "verdict_r" + _suffix(r)
        c = {}
        for d in out:
            c[d[key]] = c.get(d[key], 0) + 1
        counts[r] = c
    worst = {}
    for d in out:
        worst[d["verdict_r2_worst_rounding"]] = worst.get(d["verdict_r2_worst_rounding"], 0) + 1

    entrants = {}
    for r in EDGES:
        entrants[r] = []
        for p in pair_rows:
            if p.get("verdict") != JUDGED_ABOVE_BAND:
                continue
            pb, cr = float(p["lead_ppm"]), float(p["chromium_ppm"])
            if cr > 0 and molar_ratio(pb, cr) <= r:
                entrants[r].append(p["lead_row_id"])
    above = sorted(molar_ratio(float(p["lead_ppm"]), float(p["chromium_ppm"]))
                   for p in pair_rows
                   if p.get("verdict") == JUDGED_ABOVE_BAND and float(p["chromium_ppm"]) > 0)
    return {
        "rows": out,
        "counts": counts,
        "worst_rounding_counts": worst,
        "entrants": entrants,
        "nearest_above_band_ratio": above[0] if above else None,
    }


def write_csv(res, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(FIELDS)
        for d in res["rows"]:
            w.writerow([d[c] for c in FIELDS])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--baseline", default=BASELINE, help="cr_baseline.csv path or URL")
    ap.add_argument("--pairs", default=PAIRS, help="nyc_spice_pb_cr_pairs.csv path or URL")
    ap.add_argument("--out", default="", help="write the per-pair CSV here")
    a = ap.parse_args()
    res = analyse(load_rows(a.baseline), load_rows(a.pairs))
    if a.out:
        write_csv(res, a.out)
    for r in EDGES:
        print("R=%g:" % r, res["counts"][r], "entrants:", res["entrants"][r])
    print("R=2 worst-case rounding:", res["worst_rounding_counts"])
    if res["nearest_above_band_ratio"] is not None:
        print("nearest judged pair above the band: molar Pb:Cr %.3f"
              % res["nearest_above_band_ratio"])


if __name__ == "__main__":
    main()
