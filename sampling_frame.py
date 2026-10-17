#!/usr/bin/env python3
"""sampling_frame 0.1.0: how often does a spice lead test find >= 2 ppm, split by how
the sample was obtained (lead-poisoning case investigation vs store survey or
community testing event)?

Reads two open municipal lab tables:
  NYC DOHMH "Metal Content of Consumer Products" (data.cityofnewyork.us, da9u-wz3r)
  Public Health - Seattle & King County "Lead Content of Consumer Products" (i6sy-ckp7)

Pre-registered in docs/sampling-frame-0.1.0-prereg.md before any NYC split by frame
was looked at. The King County figures were seen before registration and are
recomputed here only as a reproducibility check.

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
"""
import argparse
import csv
import json
import math
import os
import statistics
import sys
import urllib.parse
import urllib.request
from fractions import Fraction

VERSION = "0.1.0"
UA = "spice-lead-recalls sampling_frame %s (MV2 of Munim, Inc.; mv2@munimtech.com)" % VERSION

NYC_URL = "https://data.cityofnewyork.us/resource/da9u-wz3r.json"
NYC_WHERE = "product_type='Food-Spice' AND metal='Lead'"
NYC_FIELDS = ["row_id", "product_type", "product_name", "metal", "concentration", "units",
              "manufacturer", "made_in_country", "purchase_country", "collection_date",
              "investigation_type", "analysis_type"]

KC_URL = "https://data.kingcounty.gov/resource/i6sy-ckp7.json"
KC_WHERE = "product_type in('Seasoning','Food')"
KC_FIELDS = ["year_tested", "program", "data_source", "product_type", "product_name",
             "brand_name", "manufacturer", "made_in_country", "test_method", "qualifier",
             "lead_concentration_ppm"]
KC_FRAMES = {"case investigation": "case", "community product testing event": "community"}

LIMIT = 50000
THRESHOLD = 2.0
Z95 = 1.959963984540054


def fetch(url, where):
    query = urllib.parse.urlencode({"$where": where, "$limit": str(LIMIT), "$order": ":id"},
                                   quote_via=urllib.parse.quote, safe="$")
    req = urllib.request.Request(url + "?" + query, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as resp:
        records = json.loads(resp.read().decode("utf-8"))
    if len(records) >= LIMIT:
        raise RuntimeError("hit the %d-row page limit at %s; paginate" % (LIMIT, url))
    return records


def to_float(text):
    if text is None:
        return None
    text = str(text).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def nyc_rows(records):
    """Food-Spice lead results in ppm, laboratory only. -1 (and 0) mean not detected."""
    rows = []
    for rec in records:
        if (rec.get("product_type") or "").strip() != "Food-Spice":
            continue
        if (rec.get("metal") or "").strip().lower() != "lead":
            continue
        if (rec.get("units") or "").strip().lower() != "ppm":
            continue
        if "xrf" in (rec.get("analysis_type") or "").lower():
            continue
        value = to_float(rec.get("concentration"))
        if value is None:
            status = "missing"
        elif value <= 0:
            status, value = "nd", None
        else:
            status = "value"
        frame = (rec.get("investigation_type") or "").strip().upper() or "blank"
        year = (rec.get("collection_date") or "")[:4]
        rows.append({"frame": frame, "status": status, "value": value, "year": year,
                     "set": "Food-Spice"})
    return rows


def kc_rows(records):
    """Seasoning and Food lab results. A qualifier ('<', '<LOD') means below the limit."""
    rows = []
    for rec in records:
        ptype = (rec.get("product_type") or "").strip()
        if ptype not in ("Seasoning", "Food"):
            continue
        if (rec.get("test_method") or "").strip().lower() != "laboratory":
            continue
        source = (rec.get("data_source") or "").strip()
        frame = KC_FRAMES.get(source.lower(), source or "blank")
        value = to_float(rec.get("lead_concentration_ppm"))
        if (rec.get("qualifier") or "").strip():
            status, value = "nd", None
        elif value is None:
            status = "missing"
        elif value <= 0:
            status, value = "nd", None
        else:
            status = "value"
        rows.append({"frame": frame, "status": status, "value": value,
                     "year": (rec.get("year_tested") or "").strip(), "set": ptype})
    return rows


def wilson(k, n):
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + Z95 ** 2 / n
    mid = (p + Z95 ** 2 / (2 * n)) / den
    half = Z95 * math.sqrt(p * (1 - p) / n + Z95 ** 2 / (4 * n * n)) / den
    return (max(0.0, mid - half), min(1.0, mid + half))


def fisher_two_sided(a, b, c, d):
    """Exact two-sided Fisher p for [[a, b], [c, d]]: sum of tables no more likely than observed."""
    r1, c1, n = a + b, a + c, a + b + c + d
    total = math.comb(n, r1)
    lo, hi = max(0, r1 - (n - c1)), min(r1, c1)
    probs = {x: Fraction(math.comb(c1, x) * math.comb(n - c1, r1 - x), total)
             for x in range(lo, hi + 1)}
    p_obs = probs[a]
    return sum(p for p in probs.values() if p <= p_obs)


def summarize(rows, city, product_set, frame):
    n_rows = len(rows)
    n_missing = sum(1 for r in rows if r["status"] == "missing")
    n_nd = sum(1 for r in rows if r["status"] == "nd")
    values = [r["value"] for r in rows if r["status"] == "value"]
    n_result = n_nd + len(values)
    n_ge2 = sum(1 for v in values if v >= THRESHOLD)
    lo, hi = wilson(n_ge2, n_result)
    years = sorted(r["year"] for r in rows if r["year"])
    return {
        "city": city, "product_set": product_set, "frame": frame,
        "n_rows": n_rows, "n_missing": n_missing, "n_result": n_result, "n_nd": n_nd,
        "n_ge2": n_ge2,
        "share_ge2": round(n_ge2 / n_result, 4) if n_result else None,
        "wilson_lo": round(lo, 4) if lo is not None else None,
        "wilson_hi": round(hi, 4) if hi is not None else None,
        "n_ge10": sum(1 for v in values if v >= 10),
        "n_ge50": sum(1 for v in values if v >= 50),
        "median_detect": round(statistics.median(values), 4) if values else None,
        "max_value": max(values) if values else None,
        "year_min": years[0] if years else None,
        "year_max": years[-1] if years else None,
    }


def table(rows, city, product_set):
    frames = sorted({r["frame"] for r in rows})
    out = [summarize([r for r in rows if r["frame"] == f], city, product_set, f) for f in frames]
    out.append(summarize(rows, city, product_set, "all"))
    return out


def find(stats, city, product_set, frame):
    for s in stats:
        if (s["city"], s["product_set"], s["frame"]) == (city, product_set, frame):
            return s
    return None


def compare(stats, city, product_set, f1, f2):
    s1, s2 = find(stats, city, product_set, f1), find(stats, city, product_set, f2)
    if not s1 or not s2:
        return None
    a, b = s1["n_ge2"], s1["n_result"] - s1["n_ge2"]
    c, d = s2["n_ge2"], s2["n_result"] - s2["n_ge2"]
    p = fisher_two_sided(a, b, c, d)
    return {"city": city, "product_set": product_set, "frames": [f1, f2],
            "table": [[a, b], [c, d]], "fisher_two_sided_p": float(p)}


def grade(stats, tests):
    """The five pre-registered NYC predictions (docs/sampling-frame-0.1.0-prereg.md)."""
    c = find(stats, "NYC", "Food-Spice", "C")
    s = find(stats, "NYC", "Food-Spice", "S")
    allf = find(stats, "NYC", "Food-Spice", "all")
    sc, ss = c["share_ge2"], s["share_ge2"]
    cs = next(t for t in tests if t["city"] == "NYC" and t["frames"] == ["C", "S"])
    if ss == 0:
        p1 = sc > 0
    else:
        p1 = sc >= 2 * ss
    grades = {
        "P1_case_share_at_least_2x_survey": {"C": sc, "S": ss, "met": bool(p1)},
        "P2_survey_share_at_most_0.15": {"S": ss, "met": ss <= 0.15},
        "P3_case_share_in_0.20_to_0.50": {"C": sc, "met": 0.20 <= sc <= 0.50},
        "P4_survey_at_most_10pct_of_ge50": {
            "S_ge50": s["n_ge50"], "all_ge50": allf["n_ge50"],
            "met": allf["n_ge50"] >= 1 and s["n_ge50"] <= 0.10 * allf["n_ge50"]},
        "P5_fisher_C_vs_S_below_0.001": {
            "p": cs["fisher_two_sided_p"], "met": cs["fisher_two_sided_p"] < 0.001 and sc > ss},
    }
    grades["n_met"] = sum(1 for g in grades.values() if isinstance(g, dict) and g["met"])
    return grades


def write_snapshot(path, records, fields):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for rec in records:
            w.writerow({f: rec.get(f, "") for f in fields})


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)

    nyc_raw = fetch(NYC_URL, NYC_WHERE)
    kc_raw = fetch(KC_URL, KC_WHERE)
    write_snapshot(os.path.join(args.out_dir, "nyc_spice_lead_snapshot.csv"), nyc_raw, NYC_FIELDS)
    write_snapshot(os.path.join(args.out_dir, "kc_seasoning_food_snapshot.csv"), kc_raw, KC_FIELDS)

    nyc = nyc_rows(nyc_raw)
    kc = kc_rows(kc_raw)
    stats = table(nyc, "NYC", "Food-Spice")
    stats += table([r for r in kc if r["set"] == "Seasoning"], "King County", "Seasoning")
    stats += table(kc, "King County", "Seasoning+Food")

    tests = [t for t in (
        compare(stats, "NYC", "Food-Spice", "C", "S"),
        compare(stats, "NYC", "Food-Spice", "A", "S"),
        compare(stats, "NYC", "Food-Spice", "C", "A"),
        compare(stats, "King County", "Seasoning", "case", "community"),
        compare(stats, "King County", "Seasoning+Food", "case", "community"),
    ) if t]

    fields = list(stats[0].keys())
    with open(os.path.join(args.out_dir, "frame_yield.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(stats)
    grades = grade(stats, tests)
    with open(os.path.join(args.out_dir, "tests.json"), "w", encoding="utf-8") as fh:
        json.dump(tests, fh, indent=2)
    with open(os.path.join(args.out_dir, "grades.json"), "w", encoding="utf-8") as fh:
        json.dump(grades, fh, indent=2)
    summary = {"version": VERSION, "nyc_records": len(nyc_raw), "nyc_rows_used": len(nyc),
               "kc_records": len(kc_raw), "kc_rows_used": len(kc),
               "predictions_met": grades["n_met"], "stats": stats, "tests": tests}
    with open(os.path.join(args.out_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps({"predictions_met": grades["n_met"], "tests": tests}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
