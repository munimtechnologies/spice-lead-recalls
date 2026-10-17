#!/usr/bin/env python3
"""cfia_chromate_2018 0.1.0: does the Pb:Cr chromate screen stay quiet on spices a regulator called clean?

Grades docs/cfia-chromate-2018-0.1.0-prereg.md, which was written and committed before
any lead, chromium or chromate value in the data file was read.

The Canadian Food Inspection Agency (CFIA) bought 131 yellow and red retail spices in six
Canadian cities in 2018-19 and measured lead, total chromium and a colorimetric chromate
spot test on each ("2018-2019 Lead Chromates in Spices Data", open.canada.ca dataset
06033736-6095-4b85-8760-95dd8c209576, Open Government Licence - Canada). CFIA's own
report found no sample adulterated with lead chromate. That makes the file a labelled
negative set for two published parts of this repository:

  - nyc_spice_lead.py calls a lead/chromium pair "chromate-like" when lead is at least
    18 ppm and the molar Pb:Cr ratio lies in 0.7-2.0 (PbCrO4 = 1);
  - cr_baseline.py calls a chromate-like pair "robust" when its chromium is above every
    published natural-chromium ceiling for that spice (data/natural_cr_ceilings.csv).

If clean retail spices often carry more chromium than those ceilings, the ceilings are too
low and the "robust" verdicts are weaker than claimed. If clean spices often fall in the
molar band, the band is not specific without its lead floor.

The file is long: one row per sample and component (Lead/Plomb, Chromium/Chrome,
Chromates), metal amounts in ug/g (= ppm), a bare 0 where nothing was detected.

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import re
import statistics
import sys
import time
import urllib.request

VERSION = "0.1.0"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36 cfia_chromate_2018/%s (MV2 of Munim, Inc.; mv2@munimtech.com)"
      % VERSION)
DATASET = "https://open.canada.ca/data/en/dataset/06033736-6095-4b85-8760-95dd8c209576"
URL = ("https://open.canada.ca/data/dataset/06033736-6095-4b85-8760-95dd8c209576/resource/"
       "e21700b3-408d-4ce8-a82b-8bc3023e7242/download/"
       "cfia-acia-1261_lead_chromates_in_spices__chromates_de_plomb_dans_les_epices_2018-2019.csv")
FILE_NAME = "cfia_lead_chromates_2018-2019.csv"

PB = 207.2
CR = 51.996
# Same band and lead floor as nyc_spice_lead.py.
CHROMATE_BAND = (0.7, 2.0)
PAIR_MIN_PB = 18.0

# Highest ceiling per matrix, any method, in data/natural_cr_ceilings.csv on main when this
# analysis was registered (natural_cr_ceilings 0.1.2). Frozen here so the grade cannot move.
CEILINGS = {
    "turmeric": 2.88,       # Lopez et al. 2022, ICP-MS
    "cinnamon": 4.0,        # J Environ Expo Assess 2025, ICP-MS
    "chili/paprika": 3.17,  # Ghuniem et al. 2025, ICP-MS
    "cumin": 8.59,          # Ghuniem et al. 2025, ICP-MS
    "coriander": 18.93,     # Tefera & Teklewold 2021, FAAS
    "generic": 8.59,        # highest single ICP-MS spice value (cumin)
}
# Descriptive only: coriander's highest ICP-MS ceiling (Voica et al. 2021).
CORIANDER_ICPMS = 0.912
MATRICES = (
    ("turmeric", ("turmeric", "curcuma")),
    ("cinnamon", ("cinnamon", "cannelle")),
    ("chili/paprika", ("cayenne", "chili", "chilli", "paprika")),
    ("cumin", ("cumin",)),
    ("coriander", ("coriander", "coriandre")),
)
P1_MAX_SHARE = 0.05
P2_MAX_COUNT = 2
P2_CR_PPM = 8.59
P5_STORE_SHARE = 0.083  # NYC store-survey results >= 2 ppm, 2016-2025 (purchase-place 0.1.0)
MIN_PAIRS = 120


def decode(raw):
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            pass
    return raw.decode("latin-1"), "latin-1"


def english(value):
    """'Turmeric/Curcuma' -> 'Turmeric'; 'Import/importé' -> 'Import'."""
    return (value or "").split("/")[0].strip()


def find_columns(header):
    h = [re.sub(r"\s+", " ", (c or "").replace("﻿", "")).strip().lower() for c in header]

    def first(test):
        for i, c in enumerate(h):
            if test(c):
                return i
        return None

    cols = {
        "sample": first(lambda c: c.startswith("sample")),
        "region": first(lambda c: c.startswith("region")),
        "function": first(lambda c: c == "function"),
        "origin": first(lambda c: c == "origin"),
        "product": first(lambda c: c == "product"),
        "date": first(lambda c: c.startswith("date")),
        "component": first(lambda c: c == "component"),
        "amount": first(lambda c: c == "amount"),
        "unit": first(lambda c: c.startswith("report unit")),
    }
    missing = [k for k in ("sample", "product", "component", "amount") if cols[k] is None]
    if missing:
        raise ValueError("missing columns %s in header %r" % (missing, header))
    return cols


def component_of(value):
    v = (value or "").strip().lower()
    if v.startswith("lead") or v.startswith("plomb"):
        return "pb"
    if v.startswith("chromium") or v.startswith("chrome"):
        return "cr"
    if v.startswith("chromate"):
        return "spot"
    return None


def number(value):
    s = (value or "").strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def matrix_of(product):
    p = (product or "").lower()
    for name, words in MATRICES:
        if any(w in p for w in words):
            return name
    return "generic"


def molar_ratio(pb, cr):
    if pb is None or cr is None or pb <= 0 or cr <= 0:
        return None
    return (pb / PB) / (cr / CR)


def in_band(r):
    return r is not None and CHROMATE_BAND[0] <= r <= CHROMATE_BAND[1]


def nyc_verdict(pb, cr):
    """nyc_spice_lead.verdict, copied so the screen is graded exactly as published."""
    if pb < PAIR_MIN_PB:
        return "too little lead to judge"
    if cr <= 0:
        return "no chromium detected"
    r = molar_ratio(pb, cr)
    if in_band(r):
        return "chromate-like"
    return "more lead than chromate" if r > CHROMATE_BAND[1] else "more chromium than lead"


def parse(raw):
    """Samples (one dict per sample number) and a parse check."""
    text, enc = decode(raw)
    table = [r for r in csv.reader(io.StringIO(text)) if any((c or "").strip() for c in r)]
    if not table:
        raise ValueError("empty file")
    header = table[0]
    cols = find_columns(header)

    def cell(row, key):
        i = cols[key]
        if i is None or i >= len(row):
            return ""
        return (row[i] or "").strip()

    samples, order = {}, []
    components, units, bad_numbers, duplicates, unknown = {}, {}, 0, 0, 0
    for row in table[1:]:
        sid = cell(row, "sample")
        if not sid:
            continue
        if sid not in samples:
            samples[sid] = {"sample": sid, "region": english(cell(row, "region")),
                            "function": english(cell(row, "function")),
                            "origin": english(cell(row, "origin")),
                            "product": english(cell(row, "product")),
                            "date": cell(row, "date"), "pb": None, "cr": None, "spot": ""}
            order.append(sid)
        s = samples[sid]
        comp_raw = cell(row, "component")
        components[comp_raw] = components.get(comp_raw, 0) + 1
        comp = component_of(comp_raw)
        if comp is None:
            unknown += 1
            continue
        amount = cell(row, "amount")
        if comp == "spot":
            if s["spot"]:
                duplicates += 1
            else:
                s["spot"] = amount
            continue
        unit = cell(row, "unit")
        units[unit] = units.get(unit, 0) + 1
        v = number(amount)
        if v is None:
            bad_numbers += 1
            continue
        if s[comp] is not None:
            duplicates += 1
            continue
        s[comp] = v
    rows = [samples[k] for k in order]
    for s in rows:
        s["matrix"] = matrix_of(s["product"])
        s["ceiling_ppm"] = CEILINGS[s["matrix"]]
        s["molar_ratio_pb_cr"] = molar_ratio(s["pb"], s["cr"])
        s["band"] = in_band(s["molar_ratio_pb_cr"])
        s["over_ceiling"] = s["cr"] is not None and s["cr"] > s["ceiling_ppm"]
        s["nyc_verdict"] = (nyc_verdict(s["pb"], s["cr"])
                            if s["pb"] is not None and s["cr"] is not None else "")
    check = {"encoding": enc, "header": header, "data_rows": len(table) - 1,
             "samples": len(rows), "components": components, "units": units,
             "bad_numbers": bad_numbers, "duplicates": duplicates, "unknown_components": unknown,
             "pairs": sum(1 for s in rows if s["pb"] is not None and s["cr"] is not None),
             "pb_zero": sum(1 for s in rows if s["pb"] == 0),
             "cr_zero": sum(1 for s in rows if s["cr"] == 0)}
    return rows, check


def _status(gradable, met):
    if not gradable:
        return "not gradable"
    return "met" if met else "not met"


def grade(rows, check):
    pairs = [s for s in rows if s["pb"] is not None and s["cr"] is not None]
    ok = check["pairs"] >= MIN_PAIRS
    own = [s for s in pairs if s["matrix"] != "generic"]
    over = [s for s in own if s["over_ceiling"]]
    hi_cr = [s for s in pairs if s["cr"] > P2_CR_PPM]
    band = [s for s in pairs if s["band"]]
    flagged = [s for s in pairs if s["nyc_verdict"] == "chromate-like"]
    pb2 = [s for s in pairs if s["pb"] >= 2.0]
    n = len(pairs)
    p = {
        "P1": {"prediction": "at most 5% of samples of a spice with its own ceiling carry more "
                             "chromium than that spice's highest published natural ceiling",
               "value": "%d of %d" % (len(over), len(own)),
               "status": _status(ok and bool(own), len(over) <= P1_MAX_SHARE * len(own))},
        "P2": {"prediction": "at most 2 samples carry more than 8.59 ppm chromium",
               "value": len(hi_cr), "status": _status(ok, len(hi_cr) <= P2_MAX_COUNT)},
        "P3": {"prediction": "with no lead floor, no sample's molar Pb:Cr lies in 0.7-2.0",
               "value": len(band), "status": _status(ok, len(band) == 0)},
        "P4": {"prediction": "the published screen (lead >= 18 ppm and molar Pb:Cr 0.7-2.0) "
                             "flags no sample (agreement with CFIA's 'none adulterated')",
               "value": len(flagged), "status": _status(ok, len(flagged) == 0)},
        "P5": {"prediction": "fewer than 8.3% of samples (NYC's store-survey rate) carry lead "
                             ">= 2 ppm",
               "value": "%d of %d" % (len(pb2), n),
               "status": _status(ok and n > 0, n > 0 and len(pb2) < P5_STORE_SHARE * n)},
    }
    return {"version": VERSION, "samples": len(rows), "pairs": n, "gradable_parse": ok,
            "predictions": p, "met": sum(1 for v in p.values() if v["status"] == "met"),
            "gradable": sum(1 for v in p.values() if v["status"] != "not gradable")}


def _median(xs):
    return round(statistics.median(xs), 4) if xs else None


def _tally(rows, key):
    out = {}
    for s in rows:
        if s["pb"] is None or s["cr"] is None:
            continue
        out.setdefault(key(s), []).append(s)
    table = {}
    for k, g in sorted(out.items()):
        pb = [s["pb"] for s in g]
        cr = [s["cr"] for s in g]
        table[k] = {"n": len(g), "pb_median": _median(pb), "pb_max": max(pb),
                    "cr_median": _median(cr), "cr_max": max(cr),
                    "pb_ge_1": sum(1 for x in pb if x >= 1), "pb_ge_2": sum(1 for x in pb if x >= 2),
                    "over_ceiling": sum(1 for s in g if s["over_ceiling"]),
                    "band": sum(1 for s in g if s["band"])}
    return table


def describe(rows):
    pairs = [s for s in rows if s["pb"] is not None and s["cr"] is not None]
    ratios = [s["molar_ratio_pb_cr"] for s in pairs if s["molar_ratio_pb_cr"] is not None]
    spots = {}
    for s in rows:
        spots[s["spot"]] = spots.get(s["spot"], 0) + 1
    cor = [s for s in pairs if s["matrix"] == "coriander"]
    return {
        "by_product": _tally(rows, lambda s: s["product"]),
        "by_matrix": _tally(rows, lambda s: s["matrix"]),
        "by_function": _tally(rows, lambda s: s["function"]),
        "by_origin": _tally(rows, lambda s: s["origin"]),
        "spot_test_values": spots,
        "molar_ratio_max": round(max(ratios), 4) if ratios else None,
        "molar_ratio_n": len(ratios),
        "pb_over_cr_mass": sum(1 for s in pairs if s["pb"] > s["cr"]),
        "coriander_over_icpms_ceiling": "%d of %d" % (
            sum(1 for s in cor if s["cr"] > CORIANDER_ICPMS), len(cor)),
        "over_ceiling_rows": [_public(s) for s in pairs if s["over_ceiling"]],
        "band_rows": [_public(s) for s in pairs if s["band"]],
        "top_lead_rows": [_public(s) for s in sorted(pairs, key=lambda s: -s["pb"])[:10]],
    }


FIELDS = ["sample", "region", "function", "origin", "product", "date", "matrix", "pb", "cr",
          "spot", "molar_ratio_pb_cr", "band", "ceiling_ppm", "over_ceiling", "nyc_verdict"]


def _public(s):
    out = {k: s[k] for k in FIELDS}
    if out["molar_ratio_pb_cr"] is not None:
        out["molar_ratio_pb_cr"] = round(out["molar_ratio_pb_cr"], 4)
    return out


def write_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        for s in rows:
            p = _public(s)
            w.writerow([int(p[k]) if isinstance(p[k], bool) else ("" if p[k] is None else p[k])
                        for k in FIELDS])


def summary_md(result):
    g, d, c = result["grade"], result["descriptive"], result["check"]
    lines = ["# cfia_chromate_2018 %s" % VERSION, "",
             "Source: CFIA, 2018-2019 Lead Chromates in Spices Data, %s (Open Government "
             "Licence - Canada). sha256 %s." % (DATASET, c.get("sha256", "")), "",
             "Parse check: %d data rows, %d samples, %d with both lead and chromium; components %s; "
             "units %s; bad numbers %d; duplicates %d." % (
                 c["data_rows"], c["samples"], c["pairs"], c["components"], c["units"],
                 c["bad_numbers"], c["duplicates"]), "",
             "## Pre-registered predictions (%d met of %d gradable)" % (g["met"], g["gradable"]), "",
             "| | prediction | value | status |", "|---|---|---|---|"]
    for k, v in g["predictions"].items():
        lines.append("| %s | %s | %s | %s |" % (k, v["prediction"], v["value"], v["status"]))
    for title, key in (("By product", "by_product"), ("By ceiling matrix", "by_matrix"),
                       ("By function", "by_function"), ("By declared origin", "by_origin")):
        lines += ["", "## %s (descriptive)" % title, "",
                  "| | n | Pb median | Pb max | Cr median | Cr max | Pb>=1 | Pb>=2 | Cr over ceiling | in band |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for k, t in d[key].items():
            lines.append("| %s | %d | %s | %s | %s | %s | %d | %d | %d | %d |" % (
                k, t["n"], t["pb_median"], t["pb_max"], t["cr_median"], t["cr_max"],
                t["pb_ge_1"], t["pb_ge_2"], t["over_ceiling"], t["band"]))
    lines += ["", "Chromate spot test values: %s" % d["spot_test_values"],
              "Largest molar Pb:Cr: %s (of %d defined)." % (d["molar_ratio_max"], d["molar_ratio_n"]),
              "Coriander over its highest ICP-MS ceiling (0.912 ppm): %s." % d["coriander_over_icpms_ceiling"],
              "", "## Samples over their ceiling", ""]
    for s in d["over_ceiling_rows"] or [None]:
        lines.append("- none" if s is None else "- %s %s (%s, %s): Pb %s, Cr %s, ceiling %s" % (
            s["sample"], s["product"], s["origin"], s["function"], s["pb"], s["cr"], s["ceiling_ppm"]))
    lines += ["", "## Samples in the molar band", ""]
    for s in d["band_rows"] or [None]:
        lines.append("- none" if s is None else "- %s %s (%s): Pb %s, Cr %s, ratio %s, spot %s" % (
            s["sample"], s["product"], s["origin"], s["pb"], s["cr"], s["molar_ratio_pb_cr"], s["spot"]))
    lines += ["", "Made by MV2 of Munim, Inc. with AI agents. Code Apache-2.0; derived data CC BY 4.0.", ""]
    return "\n".join(lines)


def fetch(url, tries=4, pause=10):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read()
        except Exception as e:  # noqa: BLE001 - retried, then raised
            last = e
            time.sleep(pause * (k + 1))
    raise last


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", default=None, help="a local copy of the CFIA CSV (else download)")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    if a.data:
        with open(a.data, "rb") as f:
            raw = f.read()
        src = a.data
    else:
        raw = fetch(URL)
        src = URL
        with open(os.path.join(a.out_dir, FILE_NAME), "wb") as f:
            f.write(raw)
    rows, check = parse(raw)
    check.update(source=src, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    result = {"grade": grade(rows, check), "descriptive": describe(rows), "check": check,
              "ceilings": CEILINGS, "band": list(CHROMATE_BAND), "pair_min_pb": PAIR_MIN_PB}
    write_rows(os.path.join(a.out_dir, "cfia_chromate_2018_samples.csv"), rows)
    with open(os.path.join(a.out_dir, "grades.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, ensure_ascii=False)
    with open(os.path.join(a.out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write(summary_md(result))
    g = result["grade"]
    print("cfia_chromate_2018 %s: %d samples, %d pairs, %d of %d gradable predictions met"
          % (VERSION, g["samples"], g["pairs"], g["met"], g["gradable"]))
    return 0 if g["gradable_parse"] else 1


if __name__ == "__main__":
    sys.exit(main())
