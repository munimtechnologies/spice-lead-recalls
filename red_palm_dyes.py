#!/usr/bin/env python3
"""red_palm_dyes 0.1.0: banned Sudan dyes in red palm oil sold in Canada, by declared origin.

Grades docs/red-palm-dyes-0.1.0-prereg.md, which was written and committed before any
AMOUNT value in the 2019-20 data file was read.

The Canadian Food Inspection Agency (CFIA) bought imported red palm oil at retail and
tested each sample for 18 colours that are not permitted in food, among them the
industrial Sudan dyes that some producers add to make poor oil look redder. Two years are
open, one row per sample and colour, amounts in ug/g (= ppm), a bare 0 where nothing was
found (Open Government Licence - Canada):

  - "2019-2020 Non-Permitted Food Colours in Red Palm Oil Data", open.canada.ca dataset
    f0aa9c6f-984f-4cc8-a7d7-b679c6e64e10 (the blind, primary file);
  - "2020-2021 Non-Permitted Food Colours in Red Palm Oil Data", open.canada.ca dataset
    5841c1a3-055e-489a-8766-1781a908903f (its headline was seen before registering).

Sudan dyes are the second target of this repository's screen (spice-screen's dye mode),
and the producing country's regulator (FDA Ghana) publishes its own market trend. This
grades where the dyed oil that reached Canadian shelves was declared to come from.

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
      "Chrome/126.0 Safari/537.36 red_palm_dyes/%s (MV2 of Munim, Inc.; mv2@munimtech.com)"
      % VERSION)
FILES = {
    "2019-20": {
        "dataset": "https://open.canada.ca/data/en/dataset/f0aa9c6f-984f-4cc8-a7d7-b679c6e64e10",
        "url": ("https://open.canada.ca/data/dataset/f0aa9c6f-984f-4cc8-a7d7-b679c6e64e10/resource/"
                "be73ef42-6be8-430d-b663-d5888a774c9f/download/"
                "cfia-acia-1260_non-permitted_colours_in_red_palm_oil_colorants_alimentaires_"
                "non_autorises_2019-2.csv"),
        "file": "cfia_red_palm_oil_colours_2019-2020.csv",
    },
    "2020-21": {
        "dataset": "https://open.canada.ca/data/en/dataset/5841c1a3-055e-489a-8766-1781a908903f",
        "url": ("https://open.canada.ca/data/dataset/5841c1a3-055e-489a-8766-1781a908903f/resource/"
                "333b304a-8e85-4c7f-a0cf-083eb9de7904/download/"
                "cfia_acia-1262-2020-2021_non-permitted_colours_in_red_palm_oil_open_data.csv"),
        "file": "cfia_red_palm_oil_colours_2020-2021.csv",
    },
}
PRIMARY = "2019-20"

SUDAN = ("sudan i", "sudan ii", "sudan iii", "sudan iv", "sudan black b", "sudan blue ii",
         "sudan orange g", "sudan red 7b", "sudan red g")
OTHER_DYES = ("citrus red 2", "metanil yellow", "methyl yellow", "orange ii", "para red",
              "rhodamine b", "solvent blue 59", "toluidine red")
# Reported, never graded: chlorophyllin is a green plant-derived colour, not an industrial dye.
DESCRIPTIVE_ONLY = ("chlorophylline",)
KNOWN = SUDAN + OTHER_DYES + DESCRIPTIVE_ONLY

AFRICA = ("GHANA", "NIGERIA", "SENEGAL", "TOGO", "IVORY COAST", "CAMEROON")
UNKNOWN = "UNKNOWN"
ORIGIN_ALIASES = {"COTE D'IVOIRE": "IVORY COAST", "CÔTE D'IVOIRE": "IVORY COAST",
                  "UNKNOWN OR NOT STATED": UNKNOWN, "": UNKNOWN}
P2_MAX_SHARE = 0.10
MIN_SAMPLES = 60


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
        "region": first(lambda c: c.startswith("region")),
        "origin": first(lambda c: c == "origin"),
        "date": first(lambda c: c.startswith("date")),
        "component": first(lambda c: c == "component"),
        "amount": first(lambda c: c == "amount"),
        "unit": first(lambda c: c.startswith("report unit")),
    }
    missing = [k for k in ("sample", "origin", "component", "amount") if cols[k] is None]
    if missing:
        raise ValueError("missing columns %s in header %r" % (missing, header))
    return cols


def component_of(value):
    return re.sub(r"\s+", " ", value or "").strip().lower()


def origin_of(value):
    o = re.sub(r"\s+", " ", value or "").strip().upper()
    return ORIGIN_ALIASES.get(o, o)


def base_id(sid):
    """'C2019FFPO00019D' (a duplicate) -> 'C2019FFPO00019'."""
    return re.sub(r"(?<=\d)D$", "", sid)


def number(value):
    s = (value or "").strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def parse(raw, year):
    """Samples (one dict per base sample number, duplicates merged) and a parse check."""
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

    samples, order, seen = {}, [], set()
    components, units = {}, {}
    bad_numbers = repeats = unknown = conflicts = 0
    for row in table[1:]:
        sid = cell(row, "sample").upper()
        if not sid:
            continue
        base = base_id(sid)
        origin = origin_of(cell(row, "origin"))
        if base not in samples:
            samples[base] = {"year": year, "sample": base, "ids": [], "region": cell(row, "region"),
                             "origin": origin, "date": cell(row, "date"), "amounts": {},
                             "id_sudan": {}}
            order.append(base)
        s = samples[base]
        if origin != s["origin"]:
            conflicts += 1
        if sid not in s["id_sudan"]:
            s["ids"].append(sid)
            s["id_sudan"][sid] = False
        comp = component_of(cell(row, "component"))
        components[comp] = components.get(comp, 0) + 1
        if comp not in KNOWN:
            unknown += 1
            continue
        unit = cell(row, "unit")
        units[unit] = units.get(unit, 0) + 1
        v = number(cell(row, "amount"))
        if v is None:
            bad_numbers += 1
            continue
        if (sid, comp) in seen:
            repeats += 1
        seen.add((sid, comp))
        s["amounts"][comp] = max(v, s["amounts"].get(comp, v))
        if comp in SUDAN and v > 0:
            s["id_sudan"][sid] = True
    rows = [samples[k] for k in order]
    for s in rows:
        a = s["amounts"]
        s["sudan_dyes"] = [c for c in SUDAN if a.get(c, 0) > 0]
        s["other_dyes"] = [c for c in OTHER_DYES if a.get(c, 0) > 0]
        s["sudan_positive"] = bool(s["sudan_dyes"])
        s["sudan_max"] = max(a.get(c, 0.0) for c in SUDAN)
        s["chlorophylline"] = a.get("chlorophylline")
        s["components_tested"] = len(a)
    origins = {}
    for s in rows:
        origins[s["origin"]] = origins.get(s["origin"], 0) + 1
    check = {"year": year, "encoding": enc, "header": header, "data_rows": len(table) - 1,
             "ids": sum(len(s["ids"]) for s in rows), "samples": len(rows),
             "duplicate_ids": sum(1 for s in rows for i in s["ids"] if i != s["sample"]),
             "components": components, "units": units, "origins": origins,
             "bad_numbers": bad_numbers, "repeats": repeats, "unknown_components": unknown,
             "origin_conflicts": conflicts,
             "incomplete_samples": sum(1 for s in rows if s["components_tested"] < len(KNOWN))}
    return rows, check


def _status(gradable, met):
    if not gradable:
        return "not gradable"
    return "met" if met else "not met"


def grade(primary, pooled, check):
    """primary: the 2019-20 samples; pooled: every year that parsed (primary included)."""
    n = len(primary)
    ok = n >= MIN_SAMPLES and "sudan iv" in check["components"]
    pos = [s for s in primary if s["sudan_positive"]]
    ppos = [s for s in pooled if s["sudan_positive"]]
    outside = [s for s in ppos if s["origin"] not in AFRICA + (UNKNOWN,)]
    dye_counts = {c: sum(1 for s in ppos if c in s["sudan_dyes"]) for c in SUDAN}
    origin_pos = {}
    for s in ppos:
        if s["origin"] != UNKNOWN:
            origin_pos[s["origin"]] = origin_pos.get(s["origin"], 0) + 1
    known = sum(origin_pos.values())
    other = [s for s in pooled if s["other_dyes"]]
    p = {
        "P1": {"prediction": "in 2019-20, at least one sample carries a Sudan dye",
               "value": len(pos), "status": _status(ok, len(pos) >= 1)},
        "P2": {"prediction": "in 2019-20, at most 10% of samples carry a Sudan dye",
               "value": "%d of %d" % (len(pos), n),
               "status": _status(ok, len(pos) <= P2_MAX_SHARE * n)},
        "P3": {"prediction": "every Sudan-positive sample (both years) declares a West or Central "
                             "African origin, or none",
               "value": "%d of %d outside" % (len(outside), len(ppos)),
               "status": _status(ok and bool(ppos), not outside)},
        "P4": {"prediction": "Sudan IV is found in at least as many positive samples as any other "
                             "Sudan dye (both years)",
               "value": {c: k for c, k in dye_counts.items() if k},
               "status": _status(ok and len(ppos) >= 2,
                                 dye_counts["sudan iv"] == max(dye_counts.values()))},
        "P5": {"prediction": "Ghana is the declared origin of at least as many Sudan-positive "
                             "samples as any other single origin (both years)",
               "value": origin_pos,
               "status": _status(ok and known >= 2, bool(origin_pos) and
                                 origin_pos.get("GHANA", 0) == max(origin_pos.values()))},
        "P6": {"prediction": "no non-Sudan non-permitted colour is found in any sample of either "
                             "year",
               "value": len(other), "status": _status(ok, not other)},
    }
    return {"version": VERSION, "samples": n, "pooled_samples": len(pooled),
            "pooled_years": sorted({s["year"] for s in pooled}), "gradable_parse": ok,
            "predictions": p, "met": sum(1 for v in p.values() if v["status"] == "met"),
            "gradable": sum(1 for v in p.values() if v["status"] != "not gradable")}


def describe(by_year):
    out = {"by_year_origin": {}, "component_positives": {}, "positive_rows": [],
           "duplicate_agreement": [], "chlorophylline_nonzero": {}}
    for year, rows in sorted(by_year.items()):
        table = {}
        for s in rows:
            t = table.setdefault(s["origin"], {"n": 0, "sudan_positive": 0, "sudan_max": 0.0,
                                               "other_positive": 0})
            t["n"] += 1
            t["sudan_positive"] += int(s["sudan_positive"])
            t["sudan_max"] = max(t["sudan_max"], s["sudan_max"])
            t["other_positive"] += int(bool(s["other_dyes"]))
        out["by_year_origin"][year] = dict(sorted(table.items()))
        out["component_positives"][year] = {
            c: sum(1 for s in rows if (s["amounts"].get(c) or 0) > 0) for c in KNOWN}
        out["chlorophylline_nonzero"][year] = sum(1 for s in rows if (s["chlorophylline"] or 0) > 0)
        out["positive_rows"] += [_public(s) for s in rows if s["sudan_positive"] or s["other_dyes"]]
        out["duplicate_agreement"] += [{"year": year, "sample": s["sample"], "ids": s["id_sudan"]}
                                       for s in rows if len(s["ids"]) > 1]
    return out


FIELDS = ["year", "sample", "ids", "region", "origin", "date", "sudan_positive", "sudan_dyes",
          "sudan_max", "other_dyes", "chlorophylline", "components_tested"]


def _public(s):
    out = {k: s[k] for k in FIELDS}
    for k in ("ids", "sudan_dyes", "other_dyes"):
        out[k] = ";".join(out[k])
    out["amounts_nonzero"] = {c: v for c, v in s["amounts"].items() if v > 0}
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
    g, d = result["grade"], result["descriptive"]
    lines = ["# red_palm_dyes %s" % VERSION, ""]
    for year, c in sorted(result["checks"].items()):
        lines.append("- %s: %s (Open Government Licence - Canada), sha256 %s. %d data rows, %d ids, "
                     "%d samples, %d duplicate ids; units %s; bad numbers %d; repeats %d; unknown "
                     "components %d; origin conflicts %d; incomplete samples %d." % (
                         year, FILES[year]["dataset"], c.get("sha256", ""), c["data_rows"], c["ids"],
                         c["samples"], c["duplicate_ids"], c["units"], c["bad_numbers"],
                         c["repeats"], c["unknown_components"], c["origin_conflicts"],
                         c["incomplete_samples"]))
    lines += ["", "## Pre-registered predictions (%d met of %d gradable)" % (g["met"], g["gradable"]),
              "", "| | prediction | value | status |", "|---|---|---|---|"]
    for k, v in g["predictions"].items():
        lines.append("| %s | %s | %s | %s |" % (k, v["prediction"], v["value"], v["status"]))
    lines += ["", "## By year and declared origin (descriptive)", "",
              "| year | origin | n | Sudan-positive | highest Sudan ug/g | other dye positive |",
              "|---|---|---|---|---|---|"]
    for year, table in d["by_year_origin"].items():
        for origin, t in table.items():
            lines.append("| %s | %s | %d | %d | %s | %d |" % (
                year, origin, t["n"], t["sudan_positive"], t["sudan_max"], t["other_positive"]))
    lines += ["", "## Samples with any non-permitted colour", ""]
    for s in d["positive_rows"] or [None]:
        lines.append("- none" if s is None else "- %s %s (%s, %s, %s): %s" % (
            s["year"], s["sample"], s["origin"], s["region"], s["date"], s["amounts_nonzero"]))
    lines += ["", "Duplicates (Sudan-positive per id): %s" % d["duplicate_agreement"],
              "Chlorophyllin found (descriptive): %s" % d["chlorophylline_nonzero"],
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
    ap.add_argument("--data-2019", default=None, help="a local copy of the 2019-20 CSV")
    ap.add_argument("--data-2020", default=None, help="a local copy of the 2020-21 CSV")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    local = {"2019-20": a.data_2019, "2020-21": a.data_2020}
    by_year, checks = {}, {}
    for year, meta in FILES.items():
        try:
            if local[year]:
                with open(local[year], "rb") as f:
                    raw = f.read()
                src = local[year]
            else:
                raw = fetch(meta["url"])
                src = meta["url"]
                with open(os.path.join(a.out_dir, meta["file"]), "wb") as f:
                    f.write(raw)
        except Exception as e:  # noqa: BLE001 - the secondary year may be missing
            if year == PRIMARY:
                raise
            print("could not read %s: %s" % (year, e))
            continue
        rows, check = parse(raw, year)
        check.update(source=src, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        by_year[year], checks[year] = rows, check
    pooled = [s for year in sorted(by_year) for s in by_year[year]]
    result = {"grade": grade(by_year[PRIMARY], pooled, checks[PRIMARY]),
              "descriptive": describe(by_year), "checks": checks,
              "sudan": list(SUDAN), "other_dyes": list(OTHER_DYES), "africa": list(AFRICA)}
    write_rows(os.path.join(a.out_dir, "red_palm_dyes_samples.csv"), pooled)
    with open(os.path.join(a.out_dir, "grades.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, ensure_ascii=False)
    with open(os.path.join(a.out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write(summary_md(result))
    g = result["grade"]
    print("red_palm_dyes %s: %d primary samples, %d pooled, %d of %d gradable predictions met"
          % (VERSION, g["samples"], g["pooled_samples"], g["met"], g["gradable"]))
    return 0 if g["gradable_parse"] else 1


if __name__ == "__main__":
    sys.exit(main())
