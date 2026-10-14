#!/usr/bin/env python3
"""lod_curve: how low must a lead chromate screen reach to catch lead-laced spices?

For each candidate detection limit, expressed as % w/w lead chromate (PbCrO4)
and converted to ug/g lead, counts how many high-lead spice samples in two open
public-health lab datasets a screen with that limit would have caught:

- NYC Health Department, "Metal Content of Consumer Products" (NYC Open Data
  da9u-wz3r), Food-Spice lead results in ppm, split by investigation type.
- Public Health - Seattle & King County, "Lead Content of Consumer Products
  tested in King County, Washington" (data.kingcounty.gov i6sy-ckp7):
  product type Seasoning, plus Food rows named as spices.

The curve assumes all the lead is lead chromate, an upper bound on what a
chromate-band screen can see (34 of 39 NYC lead/chromium pairs had a
chromate-like molar ratio; see nyc_spice_lead.py). Lopez et al. (ES&T 2022)
compared one limit (about 3,200 mg/kg lead) with a global turmeric maximum;
this script gives the whole curve on case and survey lab data.

Outputs: lod_curve.json, lod_curve.md, lod_curve.csv.

Made by MV2 of Munim, Inc. with AI agents working in his name. Apache-2.0.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sys
import urllib.parse
import urllib.request

__version__ = "0.1.0"

USER_AGENT = "spice-lead-recalls (MV2 of Munim, Inc.; munimversion2@gmail.com)"
NYC_URL = ("https://data.cityofnewyork.us/resource/da9u-wz3r.json?" + urllib.parse.urlencode({
    "$where": "product_type='Food-Spice' AND metal='Lead' AND units='ppm'",
    "$limit": "50000", "$order": "row_id"}))
KC_URL = "https://data.kingcounty.gov/resource/i6sy-ckp7.json?" + urllib.parse.urlencode({"$limit": "50000"})

PB = 207.2
CR = 51.996
PB_IN_PBCRO4 = PB / (PB + CR + 4 * 15.999)

# Candidate limits, % w/w PbCrO4. 0.5% is the bench powder Raman limit
# (Erasmus et al. 2021: 0.5% PLSR, 0.6% single band).
LIMITS_PCT = [1.0, 0.5, 0.25, 0.1, 0.05, 0.025, 0.01, 0.005]
# Which samples count as "lead-laced": Forsyth et al. 2024 read Pb:Cr ratios
# above 18 ug/g; 100 ug/g is 50 times the 2 ug/g level King County uses for spices.
BASES_PPM = [18, 100]

# Spice words for King County's "Food" rows (its Seasoning rows are all kept).
SPICE_WORDS = ["spice", "masala", "curry", "cinnamon", "turmeric", "chili", "chilli", "pepper", "paprika",
               "cumin", "coriander", "oregano", "tomillo", "thyme", "berbere", "ginger", "clove", "cardamom",
               "saffron", "sumac", "zaatar", "za'atar", "suneli", "khmeli", "hing", "asafoetida", "fenugreek",
               "mustard", "seasoning", "podi", "sambar", "garam"]
# Food rows that carry a spice word but are not spices ("Ginger Honey Crystals").
NOT_SPICE_WORDS = ["honey", "candy", "crystal", "tea"]


def limit_ppm(pct):
    """% w/w lead chromate -> ug/g lead, rounded (0.5% -> 3206)."""
    return int(round(pct / 100.0 * PB_IN_PBCRO4 * 1e6))


def to_float(text):
    try:
        return float(str(text).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _get(r, key):
    return " ".join(str(r.get(key, "") or "").split())


def nyc_samples(records):
    """(channel, lead_ppm) for NYC spice lead results; -1 (not detected) -> 0."""
    out = []
    for r in records:
        if _get(r, "product_type") != "Food-Spice" or _get(r, "metal") != "Lead" or _get(r, "units") != "ppm":
            continue
        c = to_float(_get(r, "concentration"))
        if c is None:
            continue
        out.append(("NYC " + (_get(r, "investigation_type") or "(blank)"), max(c, 0.0)))
    return out


def kc_is_spice(r):
    t = _get(r, "product_type")
    if t == "Seasoning":
        return True
    name = _get(r, "product_name").lower()
    return (t == "Food" and any(w in name for w in SPICE_WORDS)
            and not any(w in name.split() or w + "s" in name.split() for w in NOT_SPICE_WORDS))


def kc_samples(records):
    """(channel, lead_ppm) for King County spices; '<' or '<LOD' -> 0. Rows
    with neither a value nor a qualifier carry no result and are skipped."""
    out = []
    for r in records:
        if not kc_is_spice(r):
            continue
        q = _get(r, "qualifier")
        c = to_float(_get(r, "lead_concentration_ppm"))
        if c is None and not q:
            continue
        ppm = 0.0 if (q.startswith("<") or c is None) else c
        out.append(("King County " + (_get(r, "data_source") or "(blank)"), ppm))
    return out


def curve(values, base):
    """For lead values >= base: how many each limit catches, and the share."""
    hot = [v for v in values if v >= base]
    rows = []
    for pct in LIMITS_PCT:
        lim = limit_ppm(pct)
        caught = sum(v >= max(lim, base) for v in hot)
        rows.append({"limit_pct_pbcro4": pct, "limit_ppm_pb": lim, "caught": caught,
                     "share": round(caught / len(hot), 3) if hot else None})
    return {"base_ppm": base, "samples_at_or_above_base": len(hot), "rows": rows}


def needed_for(values, base, share):
    """Lead level (ug/g) a screen must see to catch `share` of the samples
    >= base, with its % w/w PbCrO4. None if there are none."""
    hot = sorted((v for v in values if v >= base), reverse=True)
    if not hot:
        return None
    k = max(1, math.ceil(share * len(hot) - 1e-9))
    ppm = hot[k - 1]
    return {"share": share, "samples": len(hot), "must_see_ppm_pb": ppm,
            "pct_pbcro4": round(ppm / (PB_IN_PBCRO4 * 1e4), 4)}


def summarize(samples, meta):
    groups = {}
    for ch, v in samples:
        groups.setdefault(ch, []).append(v)
    groups["NYC all"] = [v for ch, v in samples if ch.startswith("NYC ")]
    groups["King County all"] = [v for ch, v in samples if ch.startswith("King County ")]
    out = {"version": __version__, "sources": meta, "pb_in_pbcro4": round(PB_IN_PBCRO4, 4),
           "limits_pct_pbcro4": LIMITS_PCT, "channels": {}}
    for ch in sorted(groups):
        vals = groups[ch]
        out["channels"][ch] = {
            "samples": len(vals),
            "detected": sum(v > 0 for v in vals),
            "max_ppm": max(vals) if vals else None,
            "curves": [curve(vals, b) for b in BASES_PPM],
            "needed_for_90pct": [needed_for(vals, b, 0.9) for b in BASES_PPM],
        }
    return out


def write_markdown(s, path):
    lines = ["# How low must a lead chromate screen reach?", "",
             "lod_curve %s. Each cell: samples caught / samples at or above the base lead level, if all the lead "
             "were lead chromate. Lead chromate is %.1f%% lead by mass." % (s["version"], 100 * s["pb_in_pbcro4"]), ""]
    head = " | ".join("%g%% (%s ppm)" % (p, format(limit_ppm(p), ",")) for p in s["limits_pct_pbcro4"])
    for b_i, base in enumerate(BASES_PPM):
        lines += ["## Samples with at least %g ppm lead" % base, "",
                  "| channel | n | max ppm | %s | 90%% needs |" % head,
                  "|---|---|---|%s---|" % ("---|" * len(s["limits_pct_pbcro4"]))]
        for ch, d in s["channels"].items():
            c = d["curves"][b_i]
            n = c["samples_at_or_above_base"]
            cells = " | ".join("%d" % r["caught"] for r in c["rows"])
            need = d["needed_for_90pct"][b_i]
            lines.append("| %s | %d | %g | %s | %s |" % (
                ch, n, d["max_ppm"] or 0, cells,
                "%s ppm (%g%%)" % (format(need["must_see_ppm_pb"], "g"), need["pct_pbcro4"]) if need else "-"))
        lines.append("")
    lines += ["'90% needs' is the lead level the screen must see to catch 9 in 10 of those samples. "
              "Not detected counts as 0 ppm. Case samples are chosen because a child or adult was poisoned, so "
              "they over-represent heavy adulteration; store and community samples show the shelf."]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_csv(s, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["channel", "base_ppm", "samples_at_or_above_base", "limit_pct_pbcro4", "limit_ppm_pb",
                    "caught", "share"])
        for ch, d in s["channels"].items():
            for c in d["curves"]:
                for r in c["rows"]:
                    w.writerow([ch, c["base_ppm"], c["samples_at_or_above_base"], r["limit_pct_pbcro4"],
                                r["limit_ppm_pb"], r["caught"], r["share"]])


def fetch(url, data_dir, name):
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, name)
    if not os.path.exists(path):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as resp, open(path + ".part", "wb") as fh:
            fh.write(resp.read())
        os.replace(path + ".part", path)
    with open(path, "rb") as fh:
        blob = fh.read()
    records = json.loads(blob.decode("utf-8"))
    if len(records) >= 50000:
        print("warning: the API limit was reached for %s" % name, file=sys.stderr)
    return records, {"url": url, "rows": len(records), "sha256": hashlib.sha256(blob).hexdigest()}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    nyc, nyc_meta = fetch(NYC_URL, args.data_dir, "nyc-da9u-wz3r-spice-lead.json")
    kc, kc_meta = fetch(KC_URL, args.data_dir, "kc-i6sy-ckp7.json")
    s = summarize(nyc_samples(nyc) + kc_samples(kc), {"nyc": nyc_meta, "king_county": kc_meta})
    with open(os.path.join(args.out_dir, "lod_curve.json"), "w", encoding="utf-8") as fh:
        json.dump(s, fh, indent=1)
    write_markdown(s, os.path.join(args.out_dir, "lod_curve.md"))
    write_csv(s, os.path.join(args.out_dir, "lod_curve.csv"))
    for ch, d in s["channels"].items():
        print(ch, d["samples"], d["max_ppm"], [r["caught"] for r in d["curves"][1]["rows"]],
              d["needed_for_90pct"][1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
