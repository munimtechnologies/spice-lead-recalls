#!/usr/bin/env python3
"""sudan_spices 0.1.0: which red spices did Canada's Sudan-dye survey sample, and from where?

Grades docs/sudan-spices-0.1.0-prereg.md, which was written and committed before any row
of the data file was read.

The Canadian Food Inspection Agency (CFIA) bought red spices (paprika, sumac, chili
powder, cayenne) at retail in 2019-20 and tested each for the industrial Sudan dyes I-IV.
CFIA's headline is that none of 63 samples had a detectable amount. It publishes no
breakdown by declared origin. This reads the open per-sample file, one row per sample
and colour (Open Government Licence - Canada):

  - "2019-2020 Non-Permitted Colours in Spices Data", open.canada.ca dataset
    c2003a7b-9ca8-46cd-ba83-ecafd1c8569c.

It is the spice counterpart of red_palm_dyes.py: the same CFIA programme found Sudan IV in
red palm oil declared from Nigeria. The question is whether the spice frame sampled the
origins where Sudan dyes have turned up.

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.request

VERSION = "0.1.0"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36 sudan_spices/%s (MV2 of Munim, Inc.; mv2@munimtech.com)"
      % VERSION)
DATASET = "https://open.canada.ca/data/en/dataset/c2003a7b-9ca8-46cd-ba83-ecafd1c8569c"
URL = ("https://open.canada.ca/data/dataset/c2003a7b-9ca8-46cd-ba83-ecafd1c8569c/resource/"
       "281a285f-04fe-438d-8fc4-fdc2c1138c94/download/"
       "cfia_acia-1265-2019-2020_non-permitted_colours_in_spices_open_data.csv")
FILE = "cfia_sudan_spices_2019-2020.csv"

WEST_CENTRAL_AFRICA = ("NIGERIA", "GHANA", "SENEGAL", "TOGO", "IVORY COAST", "CAMEROON",
                       "BENIN", "BURKINA FASO", "MALI", "SIERRA LEONE", "GUINEA", "LIBERIA",
                       "GAMBIA", "NIGER", "CONGO", "GABON")
UNKNOWN = "UNKNOWN"
ORIGIN_ALIASES = {"COTE D'IVOIRE": "IVORY COAST", "CÔTE D'IVOIRE": "IVORY COAST",
                  "UNKNOWN OR NOT STATED": UNKNOWN, "NOT STATED": UNKNOWN,
                  "UNSPECIFIED": UNKNOWN, "": UNKNOWN}
MIN_SAMPLES = 55
P4_MAX_SHARE = 0.10
P6_MIN_SHARE = 0.25


def decode(raw):
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            pass
    return raw.decode("latin-1"), "latin-1"


def find_columns(header):
    h = [re.sub(r"\s+", " ", (c or "").replace("﻿", "")).strip().lower() for c in header]

    def first(test):
        for i, c in enumerate(h):
            if test(c):
                return i
        return None

    cols = {
        "sample": first(lambda c: c.startswith("sample")),
        "origin": first(lambda c: c == "origin" or c.startswith("country of origin")),
        "product": first(lambda c: c == "product"),
        "function": first(lambda c: c == "function"),
        "component": first(lambda c: c == "component"),
        "amount": first(lambda c: c == "amount"),
    }
    missing = [k for k in ("sample", "origin", "component", "amount") if cols[k] is None]
    if missing:
        raise ValueError("missing columns %s in header %r" % (missing, header))
    return cols


def origin_of(value):
    o = re.sub(r"\s+", " ", value or "").strip().upper()
    return ORIGIN_ALIASES.get(o, o)


def base_id(sid):
    """'C2019NPC00019D' (a duplicate) -> 'C2019NPC00019'."""
    return re.sub(r"(?<=\d)D$", "", sid)


def number(value):
    s = (value or "").strip().replace(",", ".")
    if s.startswith("<"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return None


def parse(raw):
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
    components = {}
    bad_numbers = conflicts = 0
    for row in table[1:]:
        sid = cell(row, "sample").upper()
        if not sid:
            continue
        base = base_id(sid)
        origin = origin_of(cell(row, "origin"))
        if base not in samples:
            samples[base] = {"sample": base, "origin": origin, "product": cell(row, "product"),
                             "function": cell(row, "function"), "amounts": {}}
            order.append(base)
        s = samples[base]
        if origin != s["origin"]:
            conflicts += 1
        comp = re.sub(r"\s+", " ", cell(row, "component")).strip().lower()
        components[comp] = components.get(comp, 0) + 1
        v = number(cell(row, "amount"))
        if v is None:
            bad_numbers += 1
            continue
        s["amounts"][comp] = max(v, s["amounts"].get(comp, v))
    rows = [samples[k] for k in order]
    for s in rows:
        s["positive"] = sorted(c for c, v in s["amounts"].items() if v > 0)
        s["sudan_positive"] = any(c.startswith("sudan") for c in s["positive"])
    check = {"encoding": enc, "header": header, "data_rows": len(table) - 1,
             "samples": len(rows), "components": components, "bad_numbers": bad_numbers,
             "origin_conflicts": conflicts}
    return rows, check


def _status(gradable, met):
    if not gradable:
        return "not gradable"
    return "met" if met else "not met"


def grade(rows, check):
    n = len(rows)
    ok = n >= MIN_SAMPLES and any(c.startswith("sudan") for c in check["components"])
    origins = {}
    for s in rows:
        origins[s["origin"]] = origins.get(s["origin"], 0) + 1
    known = {o: k for o, k in origins.items() if o != UNKNOWN}
    top = max(known.values()) if known else 0
    pos = [s for s in rows if s["sudan_positive"]]
    wca = sum(k for o, k in origins.items() if o in WEST_CENTRAL_AFRICA)
    unknown = origins.get(UNKNOWN, 0)
    p = {
        "P1": {"prediction": "at least %d samples parse and the file reports Sudan dyes" % MIN_SAMPLES,
               "value": n, "status": "met" if ok else "not met"},
        "P2": {"prediction": "no sample carries a Sudan dye (CFIA's headline; a consistency check)",
               "value": len(pos), "status": _status(ok, not pos)},
        "P3": {"prediction": "India is the single most common declared origin",
               "value": sorted(o for o, k in known.items() if k == top),
               "status": _status(ok and bool(known), known.get("INDIA", 0) == top)},
        "P4": {"prediction": "under 10% of samples declare a West or Central African origin",
               "value": "%d of %d" % (wca, n), "status": _status(ok, wca < P4_MAX_SHARE * n)},
        "P5": {"prediction": "no sample declares Georgia (the country)",
               "value": origins.get("GEORGIA", 0), "status": _status(ok, not origins.get("GEORGIA"))},
        "P6": {"prediction": "at least 25% of samples have no declared country of origin",
               "value": "%d of %d" % (unknown, n), "status": _status(ok, unknown >= P6_MIN_SHARE * n)},
    }
    return {"version": VERSION, "samples": n, "gradable_parse": ok, "predictions": p,
            "met": sum(1 for v in p.values() if v["status"] == "met"),
            "gradable": sum(1 for v in p.values() if v["status"] != "not gradable"),
            "origins": dict(sorted(origins.items(), key=lambda kv: (-kv[1], kv[0])))}


def describe(rows):
    by_product, any_colour = {}, []
    for s in rows:
        t = by_product.setdefault(s["product"] or "?", {"n": 0, "origins": {}})
        t["n"] += 1
        t["origins"][s["origin"]] = t["origins"].get(s["origin"], 0) + 1
        if s["positive"]:
            any_colour.append({"sample": s["sample"], "origin": s["origin"], "product": s["product"],
                               "nonzero": {c: s["amounts"][c] for c in s["positive"]}})
    return {"by_product": by_product, "any_nonzero_colour": any_colour}


FIELDS = ["sample", "product", "origin", "function", "sudan_positive", "positive",
          "components_tested"]


def write_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        for s in rows:
            w.writerow([s["sample"], s["product"], s["origin"], s["function"],
                        int(s["sudan_positive"]), ";".join(s["positive"]), len(s["amounts"])])


def summary_md(result):
    g, d, c = result["grade"], result["descriptive"], result["check"]
    lines = ["# sudan_spices %s" % VERSION, "",
             "- %s (Open Government Licence - Canada), sha256 %s. %d data rows, %d samples; "
             "bad numbers %d; origin conflicts %d; components %s." % (
                 DATASET, c.get("sha256", ""), c["data_rows"], c["samples"], c["bad_numbers"],
                 c["origin_conflicts"], c["components"]),
             "", "## Pre-registered predictions (%d met of %d gradable)" % (g["met"], g["gradable"]),
             "", "| | prediction | value | status |", "|---|---|---|---|"]
    for k, v in g["predictions"].items():
        lines.append("| %s | %s | %s | %s |" % (k, v["prediction"], v["value"], v["status"]))
    lines += ["", "## Declared origin (all samples)", "", "| origin | n |", "|---|---|"]
    lines += ["| %s | %d |" % (o, k) for o, k in g["origins"].items()]
    lines += ["", "## By product (descriptive)", ""]
    for prod, t in sorted(d["by_product"].items()):
        lines.append("- %s: %d (%s)" % (prod, t["n"], t["origins"]))
    lines += ["", "Samples with any non-zero colour: %s" % (d["any_nonzero_colour"] or "none"),
              "", "Made by MV2 of Munim, Inc. with AI agents. Code Apache-2.0; derived data CC BY 4.0.",
              "Contains information licensed under the Open Government Licence - Canada.", ""]
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
    ap.add_argument("--data", default=None, help="a local copy of the 2019-20 CSV")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    if a.data:
        with open(a.data, "rb") as f:
            raw = f.read()
    else:
        raw = fetch(URL)
        with open(os.path.join(a.out_dir, FILE), "wb") as f:
            f.write(raw)
    rows, check = parse(raw)
    check.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    result = {"grade": grade(rows, check), "descriptive": describe(rows), "check": check}
    write_rows(os.path.join(a.out_dir, "sudan_spices_samples.csv"), rows)
    with open(os.path.join(a.out_dir, "grades.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, ensure_ascii=False)
    with open(os.path.join(a.out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write(summary_md(result))
    g = result["grade"]
    print("sudan_spices %s: %d samples, %d of %d gradable predictions met"
          % (VERSION, g["samples"], g["met"], g["gradable"]))
    return 0 if g["gradable_parse"] else 1


if __name__ == "__main__":
    sys.exit(main())
