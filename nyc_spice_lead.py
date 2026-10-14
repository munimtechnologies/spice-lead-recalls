#!/usr/bin/env python3
"""nyc_spice_lead: lead and chromium in spices tested by the NYC Health Department.

Reads NYC DOHMH's open dataset "Metal Content of Consumer Products Tested by
the NYC Health Department" (NYC Open Data da9u-wz3r: lab results for products
collected in lead-poisoning investigations and store surveys, 2011 on) and asks
two questions:

1. How many spices carried enough lead for a Raman screen to see lead chromate
   at all (about 3,206 ppm lead = 0.5% w/w PbCrO4, Erasmus et al. 2021), split
   by how the sample was obtained (the dataset's investigation_type code)?
2. Where the same spice was also tested for chromium, is the lead-to-chromium
   molar ratio near 1:1, the signature of lead chromate pigment (Forsyth et al.
   2019, 2024)?

Outputs: nyc_spice_lead.csv, nyc_spice_pb_cr_pairs.csv, nyc_summary.json,
nyc_summary.md. Every row keeps NYC's row_id, so each number can be checked
against the source.

Made by MV2 of Munim, Inc. with AI agents working in his name. Apache-2.0.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import urllib.request

__version__ = "0.2.0"

DATA_URL = "https://data.cityofnewyork.us/resource/da9u-wz3r.json?$limit=50000&$order=row_id"
SOURCE_PAGE = "https://data.cityofnewyork.us/d/da9u-wz3r"
CACHE_NAME = "nyc-da9u-wz3r.json"
USER_AGENT = "spice-lead-recalls (MV2 of Munim, Inc.; munimversion2@gmail.com)"

PB = 207.2
CR = 51.996
# Pb mass fraction of PbCrO4: 207.2 / (207.2 + 51.996 + 4 * 15.999) = 0.6411.
PB_IN_PBCRO4 = PB / (PB + CR + 4 * 15.999)
# 0.5% w/w lead chromate (Erasmus et al. 2021) expressed as ug/g lead.
RAMAN_LIMIT_PPM = round(0.005 * PB_IN_PBCRO4 * 1e6)

# Pb:Cr molar ratios read as lead chromate pigment. PbCrO4 is 1.0; chrome
# yellows mixed with lead sulfate (up to PbCrO4.PbSO4) carry more lead, and
# Forsyth et al. 2019 measured 1.3 on average in Bangladeshi turmeric pigments.
CHROMATE_BAND = (0.7, 2.0)
# Below this much lead, natural chromium in the plant can dominate the ratio
# (Forsyth et al. 2024 read ratios only above 18 ug/g lead).
PAIR_MIN_PB = 18.0

THRESHOLDS = [2, 10, 100, 1000, RAMAN_LIMIT_PPM]

# Georgian spice blends and their ingredients, as NYC staff spelled them.
GEORGIAN = ["georgia", "suneli", "sunely", "sunele", "zaprana", "yellow flower", "yellow flour", "svan",
            "marili", "ajika", "ajeeka", "adjika", "adjike", "kharcho", "xarcho", "hviteli", "kviteli",
            "khmeli", "hmely", "dzira", "utskho", "uckho"]


def _get(r, key):
    return " ".join(str(r.get(key, "") or "").split())


def to_float(text):
    try:
        return float(str(text).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _row_id(r):
    v = to_float(_get(r, "row_id"))
    return int(v) if v is not None else 0


def georgian_style(name, made_in="", bought_in=""):
    """True for a Georgian spice blend, by its name or its country."""
    n = (name or "").lower()
    return any(w in n for w in GEORGIAN) or "GEORGIA" in (made_in.upper(), bought_in.upper())


def lead_rows(records):
    """Spice lead results in ppm. NYC codes results below the reporting limit
    as -1; those (and zeros) are kept as not detected, lead_ppm 0."""
    out = []
    for r in records:
        if _get(r, "product_type") != "Food-Spice" or _get(r, "metal") != "Lead" or _get(r, "units") != "ppm":
            continue
        c = to_float(_get(r, "concentration"))
        if c is None:
            continue
        detected = c > 0
        ppm = c if detected else 0.0
        name = _get(r, "product_name")
        made, bought = _get(r, "made_in_country"), _get(r, "purchase_country")
        date = _get(r, "collection_date")[:10]
        out.append({
            "row_id": _row_id(r),
            "collection_date": date,
            "year": date[:4],
            "investigation_type": _get(r, "investigation_type"),
            "analysis_type": _get(r, "analysis_type"),
            "product_name": name,
            "manufacturer": _get(r, "manufacturer"),
            "made_in_country": made,
            "purchase_country": bought,
            "lead_ppm": ppm,
            "detected": detected,
            "georgian_style": georgian_style(name, made, bought),
            "at_or_above_raman_limit": ppm >= RAMAN_LIMIT_PPM,
        })
    out.sort(key=lambda x: x["row_id"])
    return out


def molar_ratio(pb_ppm, cr_ppm):
    if pb_ppm <= 0 or cr_ppm <= 0:
        return None
    return (pb_ppm / PB) / (cr_ppm / CR)


def verdict(pb_ppm, cr_ppm):
    if pb_ppm < PAIR_MIN_PB:
        return "too little lead to judge"
    if cr_ppm <= 0:
        return "no chromium detected"
    r = molar_ratio(pb_ppm, cr_ppm)
    lo, hi = CHROMATE_BAND
    if lo <= r <= hi:
        return "chromate-like"
    return "more lead than chromate" if r > hi else "more chromium than lead"


def _key(r):
    return (_get(r, "product_type"), _get(r, "product_name").lower(), _get(r, "collection_date")[:10],
            _get(r, "investigation_type"), _get(r, "purchase_country"))


def pair_pb_cr(records, product_types=("Food-Spice",)):
    """Pair each chromium result with the lead result for the same product:
    same type, name, collection date, investigation type and purchase
    country; the nearest row_id wins when a group holds several."""
    groups = {}
    for r in records:
        if _get(r, "product_type") not in product_types or _get(r, "units") != "ppm":
            continue
        metal = _get(r, "metal")
        if metal not in ("Lead", "Chromium"):
            continue
        c = to_float(_get(r, "concentration"))
        if c is None:
            continue
        g = groups.setdefault(_key(r), {"Lead": [], "Chromium": []})
        g[metal].append((_row_id(r), max(c, 0.0), r))
    pairs = []
    for g in groups.values():
        free = sorted(g["Lead"], key=lambda t: t[0])
        for cr_id, cr, _ in sorted(g["Chromium"], key=lambda t: t[0]):
            if not free:
                break
            j = min(range(len(free)), key=lambda i: abs(free[i][0] - cr_id))
            pb_id, pb, rec = free.pop(j)
            ratio = molar_ratio(pb, cr)
            name = _get(rec, "product_name")
            made, bought = _get(rec, "made_in_country"), _get(rec, "purchase_country")
            date = _get(rec, "collection_date")[:10]
            pairs.append({
                "lead_row_id": pb_id,
                "chromium_row_id": cr_id,
                "collection_date": date,
                "year": date[:4],
                "investigation_type": _get(rec, "investigation_type"),
                "product_name": name,
                "made_in_country": made,
                "purchase_country": bought,
                "lead_ppm": pb,
                "chromium_ppm": cr,
                "mass_ratio_pb_cr": round(pb / cr, 3) if pb > 0 and cr > 0 else "",
                "molar_ratio_pb_cr": round(ratio, 3) if ratio is not None else "",
                "verdict": verdict(pb, cr),
                "georgian_style": georgian_style(name, made, bought),
            })
    pairs.sort(key=lambda p: (-p["lead_ppm"], p["lead_row_id"]))
    return pairs


def _label(t):
    return ">=%g" % t


def _count(items, key):
    out = {}
    for it in items:
        k = key(it)
        out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], str(kv[0]))))


def median(v):
    v = sorted(v)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0


def channel_table(rows, key):
    out = {}
    for k in sorted({key(r) for r in rows}):
        sub = [r for r in rows if key(r) == k]
        d = {"samples": len(sub), "detected": sum(r["detected"] for r in sub)}
        for t in THRESHOLDS:
            d[_label(t)] = sum(r["lead_ppm"] >= t for r in sub)
        d["max_ppm"] = max(r["lead_ppm"] for r in sub)
        out[k] = d
    return out


def summarize(rows, pairs, meta):
    above = [r for r in rows if r["at_or_above_raman_limit"]]
    judged = [p for p in pairs if p["verdict"] != "too little lead to judge"]
    chromate = [p for p in judged if p["verdict"] == "chromate-like"]
    ratios = [p["molar_ratio_pb_cr"] for p in chromate]
    by_country = channel_table(rows, lambda r: r["purchase_country"] or "(blank)")
    top = sorted(by_country.items(), key=lambda kv: -kv[1]["samples"])[:20]
    us = [r for r in rows if r["purchase_country"] == "UNITED STATES"]
    dates = sorted(r["collection_date"] for r in rows if r["collection_date"])
    return {
        "version": __version__,
        "source": SOURCE_PAGE, "api": DATA_URL, "sha256": meta.get("sha256", ""),
        "rows_read": meta.get("rows", 0),
        "spice_lead_results": len(rows),
        "detected": sum(r["detected"] for r in rows),
        "first_collected": dates[0] if dates else "", "last_collected": dates[-1] if dates else "",
        "raman_limit_ppm_pb": RAMAN_LIMIT_PPM,
        "by_investigation_type": channel_table(rows, lambda r: r["investigation_type"] or "(blank)"),
        "by_purchase_country_top20": dict(top),
        "bought_in_us": {"samples": len(us), _label(RAMAN_LIMIT_PPM): sum(r["at_or_above_raman_limit"] for r in us)},
        "at_or_above_raman_limit": len(above),
        "at_or_above_raman_limit_georgian_style": sum(r["georgian_style"] for r in above),
        "above_limit_rows": [{k: r[k] for k in ("row_id", "collection_date", "investigation_type", "product_name",
                                                "made_in_country", "purchase_country", "lead_ppm", "georgian_style")}
                             for r in sorted(above, key=lambda x: -x["lead_ppm"])],
        "chromate_band_molar": list(CHROMATE_BAND),
        "pair_min_pb_ppm": PAIR_MIN_PB,
        "pb_cr_pairs": len(pairs),
        "pb_cr_pairs_judged": len(judged),
        "pb_cr_verdicts": _count(pairs, lambda p: p["verdict"]),
        "chromate_like": len(chromate),
        "chromate_like_molar_min": min(ratios) if ratios else None,
        "chromate_like_molar_median": median(ratios),
        "chromate_like_molar_max": max(ratios) if ratios else None,
        "chromate_like_by_purchase_country": _count(chromate, lambda p: p["purchase_country"] or "(blank)"),
        "chromate_like_store_survey": sum(p["investigation_type"] == "S" for p in chromate),
        "judged_pairs": [{k: p[k] for k in ("lead_row_id", "chromium_row_id", "collection_date", "investigation_type",
                                            "product_name", "purchase_country", "lead_ppm", "chromium_ppm",
                                            "molar_ratio_pb_cr", "verdict")} for p in judged],
    }


def write_markdown(s, path):
    labels = [_label(t) for t in THRESHOLDS]
    lines = ["# Lead and chromium in spices tested by the NYC Health Department", "",
             "nyc_spice_lead %s. Source: %s (sha256 %s), %d rows read; %d spice lead results in ppm, "
             "collected %s to %s." % (s["version"], s["source"], s["sha256"][:12], s["rows_read"],
                                      s["spice_lead_results"], s["first_collected"], s["last_collected"]),
             "", "- Lead detected: %d." % s["detected"],
             "- At or above about %s ppm lead (0.5%% w/w lead chromate, the reported Raman limit): %d, of which "
             "Georgian-style blends: %d." % (format(s["raman_limit_ppm_pb"], ","), s["at_or_above_raman_limit"],
                                             s["at_or_above_raman_limit_georgian_style"]),
             "- Bought in the United States: %d samples, %d at or above the Raman limit." % (
                 s["bought_in_us"]["samples"], s["bought_in_us"][_label(s["raman_limit_ppm_pb"])]),
             "- Lead/chromium pairs: %d; judged (lead >= %g ppm): %d; chromate-like (molar Pb:Cr %g-%g): %d, "
             "median ratio %s." % (s["pb_cr_pairs"], s["pair_min_pb_ppm"], s["pb_cr_pairs_judged"],
                                    s["chromate_band_molar"][0], s["chromate_band_molar"][1], s["chromate_like"],
                                    None if s["chromate_like_molar_median"] is None
                                    else round(s["chromate_like_molar_median"], 3)), ""]

    def channel(d, head):
        out = ["| %s | samples | detected | %s | max ppm |" % (head, " | ".join(labels)),
               "|---|---|---|%s---|" % ("---|" * len(labels))]
        for k, v in d.items():
            out.append("| %s | %d | %d | %s | %g |" % (k, v["samples"], v["detected"],
                                                     " | ".join(str(v[lb]) for lb in labels), v["max_ppm"]))
        return out

    lines += ["## By investigation type (how the sample was obtained)", ""]
    lines += channel(s["by_investigation_type"], "type") + [""]
    lines += ["## By purchase country (top 20 by samples)", ""]
    lines += channel(s["by_purchase_country_top20"], "bought in") + [""]
    lines += ["## Pb:Cr verdicts", "", "| verdict | pairs |", "|---|---|"]
    lines += ["| %s | %d |" % (k, v) for k, v in s["pb_cr_verdicts"].items()] + [""]
    lines += ["## Judged pairs", "", "| Pb row | Cr row | collected | type | product | bought in | Pb ppm | Cr ppm | "
              "molar Pb:Cr | verdict |", "|---|---|---|---|---|---|---|---|---|---|"]
    for p in s["judged_pairs"]:
        lines.append("| %s | %s | %s | %s | %s | %s | %g | %g | %s | %s |" % (
            p["lead_row_id"], p["chromium_row_id"], p["collection_date"], p["investigation_type"],
            p["product_name"].replace("|", "/"), p["purchase_country"], p["lead_ppm"], p["chromium_ppm"],
            p["molar_ratio_pb_cr"], p["verdict"]))
    lines += ["", "## Spices at or above the Raman limit", "",
              "| row | collected | type | product | made in | bought in | Pb ppm | Georgian-style |",
              "|---|---|---|---|---|---|---|---|"]
    for r in s["above_limit_rows"]:
        lines.append("| %s | %s | %s | %s | %s | %s | %g | %s |" % (
            r["row_id"], r["collection_date"], r["investigation_type"], r["product_name"].replace("|", "/"),
            r["made_in_country"], r["purchase_country"], r["lead_ppm"], "yes" if r["georgian_style"] else ""))
    lines += ["", "Not detected (-1 in the source) counts as 0 ppm. Chromium was tested on few samples, mostly "
              "ones already suspected; the ratio speaks for each pair, not for all spices."]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


LEAD_FIELDS = ["row_id", "collection_date", "year", "investigation_type", "analysis_type", "product_name",
               "manufacturer", "made_in_country", "purchase_country", "lead_ppm", "detected", "georgian_style",
               "at_or_above_raman_limit"]
PAIR_FIELDS = ["lead_row_id", "chromium_row_id", "collection_date", "year", "investigation_type", "product_name",
               "made_in_country", "purchase_country", "lead_ppm", "chromium_ppm", "mass_ratio_pb_cr",
               "molar_ratio_pb_cr", "verdict", "georgian_style"]


def write_csv(rows, fields, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def load_records(data_dir):
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, CACHE_NAME)
    if not os.path.exists(path):
        req = urllib.request.Request(DATA_URL, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as resp, open(path + ".part", "wb") as fh:
            fh.write(resp.read())
        os.replace(path + ".part", path)
    with open(path, "rb") as fh:
        blob = fh.read()
    records = json.loads(blob.decode("utf-8"))
    if len(records) >= 50000:
        print("warning: the API limit was reached; raise $limit", file=sys.stderr)
    return records, {"sha256": hashlib.sha256(blob).hexdigest(), "rows": len(records)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    records, meta = load_records(args.data_dir)
    rows = lead_rows(records)
    pairs = pair_pb_cr(records)
    write_csv(rows, LEAD_FIELDS, os.path.join(args.out_dir, "nyc_spice_lead.csv"))
    write_csv(pairs, PAIR_FIELDS, os.path.join(args.out_dir, "nyc_spice_pb_cr_pairs.csv"))
    s = summarize(rows, pairs, meta)
    with open(os.path.join(args.out_dir, "nyc_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)
    write_markdown(s, os.path.join(args.out_dir, "nyc_summary.md"))
    print(json.dumps({k: s[k] for k in ("rows_read", "spice_lead_results", "detected", "at_or_above_raman_limit",
                                        "at_or_above_raman_limit_georgian_style", "pb_cr_pairs",
                                        "pb_cr_pairs_judged", "chromate_like", "chromate_like_molar_median")}))
    print("by type:", json.dumps(s["by_investigation_type"]))
    print("verdicts:", json.dumps(s["pb_cr_verdicts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
