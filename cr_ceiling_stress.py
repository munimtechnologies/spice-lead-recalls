#!/usr/bin/env python3
"""cr_ceiling_stress: a natural-chromium ceiling-inflation stress test.

Reads data/cr_baseline.csv (or the same file from raw main), and for every pair the
cr_baseline tool scored "robust", computes the multiplicative headroom
    k = edge_ppm / highest_ceiling_ppm
which is the factor by which the published natural-chromium ceilings for that
pair's matrix would have to be inflated before the pair stops being robust.
Reports how many robust pairs survive a uniform inflation s in
{1.25, 1.5, 2, 3, 5, 10}, and the single most fragile robust pair (smallest k).

Pure transform of already-published bytes. Pre-registered in
docs/cr-ceiling-stress-0.1.0-prereg.md before it was run.

By MV2, Munim, Inc. Made with AI agents. Apache-2.0.
"""
import argparse
import csv
import io
import os
import urllib.request

__version__ = "0.1.0"

RAW = ("https://raw.githubusercontent.com/munimtechnologies/"
       "spice-lead-recalls/main/data/cr_baseline.csv")
HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL = os.path.join(HERE, "data", "cr_baseline.csv")
SCALES = [1.25, 1.5, 2.0, 3.0, 5.0, 10.0]
FIELDS = ["lead_row_id", "chromium_row_id", "product_name", "purchase_country",
          "edge_ppm", "highest_ceiling_ppm", "k", "survives_2x", "survives_5x"]


def load_rows(source=LOCAL):
    if source.startswith("http"):
        with urllib.request.urlopen(source, timeout=60) as r:
            text = r.read().decode("utf-8")
    else:
        with open(source, encoding="utf-8") as f:
            text = f.read()
    return list(csv.DictReader(io.StringIO(text)))


def analyse(rows):
    robust = []
    for row in rows:
        if row.get("baseline_verdict", "").strip() != "robust":
            continue
        edge = float(row["edge_ppm"])
        hi = float(row["highest_ceiling_ppm"])
        k = edge / hi
        robust.append({
            "lead_row_id": row.get("lead_row_id", ""),
            "chromium_row_id": row.get("chromium_row_id", ""),
            "product_name": row.get("product_name", ""),
            "purchase_country": row.get("purchase_country", ""),
            "matrix": row.get("matrix", ""),
            "edge_ppm": round(edge, 4),
            "highest_ceiling_ppm": round(hi, 4),
            "k": round(k, 4),
            "survives_2x": k > 2.0,
            "survives_5x": k > 5.0,
        })
    robust.sort(key=lambda d: d["k"])  # most fragile first; stable for ties
    survival = {s: sum(1 for d in robust if d["k"] > s) for s in SCALES}
    return {
        "n_total": len(rows),
        "n_robust": len(robust),
        "robust": robust,
        "survival": survival,
        "most_fragile": robust[0] if robust else None,
    }


def write_csv(res, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        for d in res["robust"]:
            w.writerow([d[c] for c in FIELDS])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", default=LOCAL, help="cr_baseline.csv path or URL")
    ap.add_argument("--out", default="", help="write the per-pair CSV here")
    a = ap.parse_args()
    res = analyse(load_rows(a.source))
    if a.out:
        write_csv(res, a.out)
    print(f"n_total={res['n_total']} n_robust={res['n_robust']}")
    print("survival:", {f"{s:g}x": res["survival"][s] for s in SCALES})
    mf = res["most_fragile"]
    if mf:
        print(f"most_fragile: {mf['product_name']}/{mf['purchase_country']} k={mf['k']}")


if __name__ == "__main__":
    main()
