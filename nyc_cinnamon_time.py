# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
"""nyc_cinnamon_time 0.1.0: cinnamon in NYC's lead case investigations, by level and date.

Grades docs/nyc-cinnamon-time-0.1.0-prereg.md, which was committed (v0.4.33) before any
case-frame cinnamon row was read. The rows are the sampling_frame.nyc_rows filter
(Food-Spice, lead, ppm, laboratory, XRF excluded) on the committed snapshot
data/nyc_spice_lead_snapshot_2026-10-17.csv, kept with their name, date and purchase country.
Frames: C = case investigation (main), S = store survey (check); any other code goes on its
own line. Levels: ASTA V3 bark 2.0 ug/g (strictly above) and gross 50 ppm (at or above).
Standard library only.
"""
import argparse
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT = os.path.join(HERE, "data", "nyc_spice_lead_snapshot_2026-10-17.csv")

BARK_LEVEL = 2.0
GROSS = 50.0
ABROAD_GROSS_RATE = 0.110  # 147 of 1,332 spices bought abroad, case frame (where-you-look)

CINNAMON = ("cinnamon", "cassia", "canela", "dalchini", "darchini", "darchin", "kaneel", "qirfa",
            "qerfa", "tarçın", "tarcin", "kayu manis", "quế")
BLEND = ("masala", "curry", "five-spice", "five spice", "mixed", "mix", "seasoning", "blend", "sugar",
         "tea")

# (label, first date, last date, length in years or None for open-ended periods)
PERIODS = (
    ("before-2019", "0000-01-01", "2018-12-31", None),
    ("2019-2022", "2019-01-01", "2022-12-31", 4.0),
    ("2023-to-oct", "2023-01-01", "2023-10-31", 10 / 12),
    ("post-recall", "2023-11-01", "2024-12-31", 14 / 12),
    ("2025-on", "2025-01-01", "9999-12-31", None),
)
NO_DATE = "no-date"
UNKNOWN_COUNTRY = {"", "UNKNOWN OR NOT STATED", "UNITED STATES MINOR OUTLYING ISLANDS"}


def norm(text):
    # casefold + dotless i, so "TARÇIN" and "tarçın" compare equal
    return (text or "").casefold().replace("ı", "i")


CINNAMON_RE = re.compile(r"\b(?:%s)\b" % "|".join(re.escape(norm(t)) for t in CINNAMON))
# blend words match at a word start, so "Mixed" and "Five Spices" are caught too
BLEND_RE = re.compile(r"\b(?:%s)" % "|".join(re.escape(norm(t)) for t in BLEND))


def kind(name):
    """'cinnamon', 'blend' (cinnamon-named blend) or None."""
    n = norm(name)
    if not CINNAMON_RE.search(n):
        return None
    return "blend" if BLEND_RE.search(n) else "cinnamon"


def period_of(date):
    d = (date or "").strip()[:10]
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
        return NO_DATE
    for label, lo, hi, _ in PERIODS:
        if lo <= d <= hi:
            return label
    return NO_DATE


def purchase_group(country):
    value = (country or "").strip().upper()
    if value == "UNITED STATES":
        return "US"
    if value in UNKNOWN_COUNTRY:
        return "unknown"
    return "abroad"


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


def read_snapshot(path=SNAPSHOT):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def cinnamon_rows(records):
    """Every cinnamon-named row of the nyc_rows filter, with frame, status, date and group."""
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
        k = kind(rec.get("product_name"))
        if k is None:
            continue
        value = to_float(rec.get("concentration"))
        if value is None:
            status = "missing"
        elif value <= 0:
            status, value = "nd", None
        else:
            status = "value"
        frame = (rec.get("investigation_type") or "").strip().upper() or "blank"
        date = (rec.get("collection_date") or "").strip()[:10]
        rows.append({"row_id": (rec.get("row_id") or "").strip(), "product_name": rec.get("product_name"),
                     "kind": k, "frame": frame, "status": status, "value": value, "date": date,
                     "period": period_of(date), "group": purchase_group(rec.get("purchase_country"))})
    return rows


def counts(rows):
    counted = [r for r in rows if r["status"] != "missing"]
    detected = [r for r in counted if r["status"] == "value"]
    over = [r for r in detected if r["value"] > BARK_LEVEL]
    gross = [r for r in detected if r["value"] >= GROSS]
    return {"rows": len(counted), "detected": len(detected), "over_2": len(over), "ge_50": len(gross),
            "missing": len(rows) - len(counted)}


def rate(k, n):
    return round(k / n, 4) if n else None


def main_rows(rows, frame):
    return [r for r in rows if r["kind"] == "cinnamon" and r["frame"] == frame]


def is_jan_2024(r):
    return r["date"][:7] == "2024-01"


def score(rows):
    c = main_rows(rows, "C")
    s = main_rows(rows, "S")
    other = [r for r in rows if r["kind"] == "cinnamon" and r["frame"] not in ("C", "S")]
    tc = counts(c)
    out = {"case": tc, "store": counts(s), "other_frames": counts(other),
           "blends": {f: counts([r for r in rows if r["kind"] == "blend" and r["frame"] == f])
                      for f in sorted({r["frame"] for r in rows})},
           "case_by_period": {}, "store_by_period": {}, "case_by_group": {}}
    labels = [p[0] for p in PERIODS] + [NO_DATE]
    for label in labels:
        out["case_by_period"][label] = counts([r for r in c if r["period"] == label])
        out["store_by_period"][label] = counts([r for r in s if r["period"] == label])
    for g in ("US", "abroad", "unknown"):
        out["case_by_group"][g] = counts([r for r in c if r["group"] == g])

    over_rate = rate(tc["over_2"], tc["detected"])
    gross_rate = rate(tc["ge_50"], tc["rows"])
    out["case_over_2_rate_detected"] = over_rate
    out["case_ge_50_rate_all"] = gross_rate
    powered = tc["rows"] >= 15

    p = {"P1_rows_45_in_15_120": 15 <= tc["rows"] <= 120}
    if powered and over_rate is not None:
        p["P2_over2_40pct_in_15_65"] = 0.15 <= over_rate <= 0.65
    else:
        p["P2_over2_40pct_in_15_65"] = "not scorable"
    p["P3_ge50_4pct_in_0_12"] = (0.0 <= gross_rate <= 0.12) if powered and gross_rate is not None \
        else "not scorable"
    early = out["case_by_period"]["2019-2022"]["rows"] / 4.0
    post = out["case_by_period"]["post-recall"]["rows"] / (14 / 12)
    ratio = round(post / early, 4) if early else None
    out["P4_ratio"] = ratio
    if powered and ratio is not None:
        p["P4_ratio_ge_2"] = ratio >= 2.0
        p["P4_ratio_in_0.8_5"] = 0.8 <= ratio <= 5.0
    else:
        p["P4_ratio_ge_2"] = p["P4_ratio_in_0.8_5"] = "not scorable"

    h = {}
    h["H1_gross_below_11pct"] = (gross_rate < ABROAD_GROSS_RATE) if gross_rate is not None else "not scorable"
    outside = counts([r for r in s if not is_jan_2024(r)])
    store_rate = rate(outside["over_2"], outside["detected"])
    out["store_outside_jan2024"] = outside
    out["store_outside_jan2024_rate"] = store_rate
    if tc["detected"] >= 10 and store_rate is not None:
        h["H2_case_rate_ge_store_outside_jan2024"] = over_rate >= store_rate
    else:
        h["H2_case_rate_ge_store_outside_jan2024"] = "not scorable"
    post_over = out["case_by_period"]["post-recall"]["over_2"]
    h["H3_post_recall_not_majority"] = (2 * post_over <= tc["over_2"]) if tc["over_2"] else "not scorable"
    out["predictions"] = p
    out["hypotheses"] = h
    out["underpowered"] = not powered
    return out


def write_rows(rows, path):
    fields = ["row_id", "frame", "kind", "date", "period", "group", "status", "value", "product_name"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["frame"], r["date"], r["row_id"])):
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--snapshot", default=SNAPSHOT)
    ap.add_argument("--out-dir", default=os.path.join(HERE, "data"))
    args = ap.parse_args()
    rows = cinnamon_rows(read_snapshot(args.snapshot))
    os.makedirs(args.out_dir, exist_ok=True)
    write_rows(rows, os.path.join(args.out_dir, "nyc_cinnamon_time.csv"))
    s = score(rows)
    with open(os.path.join(args.out_dir, "nyc_cinnamon_time.json"), "w", encoding="utf-8") as fh:
        json.dump(s, fh, indent=1, sort_keys=True)
    for r in sorted(rows, key=lambda r: (r["kind"], r["frame"], r["date"])):
        print("%-8s %-5s %-10s %-7s %-8s %s" % (r["kind"], r["frame"], r["date"] or "-", r["status"],
                                                r["value"] if r["value"] is not None else "-",
                                                r["product_name"]))
    print(json.dumps({k: s[k] for k in ("case", "store", "predictions", "hypotheses", "underpowered")},
                     indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
