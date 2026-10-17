#!/usr/bin/env python3
"""ota_spices 0.1.0: which declared origins carry the Canadian retail spices that would fail the EU's
ochratoxin A limits?

Grades docs/ota-spices-0.1.0-prereg.md, which was written and committed before any row of the data
file was read.

The Canadian Food Inspection Agency (CFIA) tested 8,384 retail foods for ochratoxin A (OTA) in
2012-2018 and 2019-2022, 778 of them spices, with a maximum of 1,770 ppb in a paprika. Canada has no
OTA limit for spices; the EU allows 20 ug/kg in Capsicum spices and 15 in pepper, nutmeg, ginger,
turmeric and spice mixtures. CFIA's report gives no breakdown by country. This reads the open
per-sample file (Open Government Licence - Canada), published 2026-10-06:

  - "Food Safety Action Plan Targeted Survey - Ochratoxin A in Selected Foods - 2012-2018 and
    2019-2022", open.canada.ca dataset 37300d06-0887-4353-bc9b-4f030f1089a2.

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
      "Chrome/126.0 Safari/537.36 ota_spices/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % VERSION)
DATASET = "https://open.canada.ca/data/en/dataset/37300d06-0887-4353-bc9b-4f030f1089a2"
URL = ("https://open.canada.ca/data/dataset/37300d06-0887-4353-bc9b-4f030f1089a2/resource/"
       "ebc03414-5782-48e7-9294-30b37213479e/download/"
       "chem_ts_2012-2018__2019-22_ochratoxin_a_in_selected_foods.csv")
FILE = "cfia_ota_selected_foods_2012-2022.csv"

UNKNOWN = "UNKNOWN"
IMPORTED = "IMPORTED (NO COUNTRY)"
ORIGIN_ALIASES = {"": UNKNOWN, "UNKNOWN": UNKNOWN, "INCONNU": UNKNOWN, "UNSPECIFIED": UNKNOWN,
                  "NOT SPECIFIED": UNKNOWN, "NOT STATED": UNKNOWN, "UNKNOWN OR NOT STATED": UNKNOWN,
                  "N/A": UNKNOWN, "NA": UNKNOWN, "IMPORT": IMPORTED, "IMPORTED": IMPORTED,
                  "USA": "UNITED STATES", "U.S.A.": "UNITED STATES", "US": "UNITED STATES",
                  "U.S.": "UNITED STATES", "UNITED STATES OF AMERICA": "UNITED STATES",
                  "TURKIYE": "TURKEY", "TÜRKIYE": "TURKEY", "VIET NAM": "VIETNAM",
                  "COTE D'IVOIRE": "IVORY COAST", "CÔTE D'IVOIRE": "IVORY COAST"}
NO_COUNTRY = (UNKNOWN, IMPORTED)
# Spice types, applied in this order to the English product text (lower case). EU Regulation
# 2023/915 OTA limits in ug/kg (= ppb); None = no EU limit for that spice.
SPICE_TYPES = (
    ("paprika", 20.0, (r"paprika", r"piment[oó]n")),
    ("chili", 20.0, (r"chil+i", r"\bchile", r"cayenne", r"red pepper", r"hot pepper", r"crushed pepper",
                     r"pepper flake", r"capsicum", r"chipotle", r"\bancho\b", r"jalape")),
    ("nutmeg", 15.0, (r"nutmeg", r"\bmace\b")),
    ("ginger", 15.0, (r"ginger",)),
    ("turmeric", 15.0, (r"turmeric",)),
    ("mixture", 15.0, (r"curry(?! lea)", r"masala", r"\bmix", r"blend", r"seasoning", r"five spice",
                       r"5 spice", r"ras el hanout", r"berbere", r"\bjerk", r"cajun", r"baharat",
                       r"tandoori", r"tikka", r"sambar", r"rasam", r"chaat", r"panch phoron")),
    ("pepper", 15.0, (r"\bpeppers?\b", r"peppercorn")),
)
OTHER_SPICE = (r"anise", r"cinnamon", r"cumin", r"fennel", r"fenugreek", r"methi", r"kaffir", r"marjoram",
               r"onion", r"savou?ry", r"vanilla", r"coriander", r"garlic", r"mustard", r"celery seed",
               r"curry lea", r"clove", r"cardamom", r"allspice", r"caraway", r"oregano", r"thyme",
               r"saffron", r"sumac", r"spice")
# Used only when the file has no product-type column, to keep baked goods etc. out of "spices".
NOT_A_SPICE = (r"bread", r"cookie", r"biscuit", r"cracker", r"cereal", r"\bbar\b", r"cake", r"muffin",
               r"\btea\b", r"candy", r"chocolate", r"cocoa", r"coffee", r"sauce", r"soup", r"\bbun",
               r"bagel", r"granola", r"loaf", r"scone", r"waffle", r"pasta", r"noodle", r"\brice\b",
               r"flour", r"\boats?\b", r"oatmeal", r"wheat", r"barley", r"\brye\b", r"\bcorn\b",
               r"(?<!vanilla )\bbeans?\b",
               r"lentil", r"\bpeas?\b", r"chickpea", r"\bsoy", r"tofu", r"\bnuts?\b", r"butter", r"almond",
               r"raisin", r"\bfigs?\b", r"\bdates?\b", r"apricot", r"licorice", r"liquorice", r"formula",
               r"juice", r"drink", r"beverage", r"pickle", r"candied", r"crystallized")
VINE_FRUIT = (r"raisin", r"sultana", r"currant")
NOT_VINE = (r"bran", r"bread", r"cereal", r"cookie", r"muffin", r"\bbun", r"granola", r"\bbar\b", r"bagel",
            r"cake", r"biscuit", r"\boats?\b", r"loaf", r"scone", r"\bmix", r"black currant", r"blackcurrant")
TO_PPB = {"ppb": 1.0, "µg/kg": 1.0, "μg/kg": 1.0, "ug/kg": 1.0, "ng/g": 1.0,
          "ppm": 1000.0, "mg/kg": 1000.0, "µg/g": 1000.0, "μg/g": 1000.0, "ug/g": 1000.0,
          "ppt": 0.001, "ng/kg": 0.001}
MIN_SAMPLES = 8000
SPICE_RANGE = (700, 860)
MAX_RANGE = (1700.0, 1850.0)
P3_SHARE = (0.05, 0.15)
VINE_LIMIT = 10.0


def decode(raw):
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            pass
    return raw.decode("latin-1"), "latin-1"


def _norm(c):
    return re.sub(r"\s+", " ", (c or "").replace("﻿", "")).strip().lower()


def find_columns(header):
    h = [_norm(c) for c in header]

    def first(test):
        for i, c in enumerate(h):
            if test(c):
                return i
        return None

    cols = {
        "sample": first(lambda c: c.startswith("sample")),
        "origin": first(lambda c: c == "origin" or c.startswith("origin ") or c.startswith("country")),
        "product": first(lambda c: c == "product" or c.startswith("product -") or c.startswith("product name")
                         or c.startswith("product description")),
        "type": first(lambda c: (c.startswith("commodity") or c.startswith("product type")
                                 or c.startswith("product category") or c.startswith("food type")
                                 or c.startswith("food group") or c.startswith("category"))),
        "component": first(lambda c: c == "component" or c.startswith("component -")
                           or c.startswith("analyte")),
        "result": first(lambda c: (c.startswith("result") or c.startswith("amount")) and "unit" not in c),
        "unit": first(lambda c: re.search(r"\bunits?\b", c) is not None or "unité" in c),
    }
    if cols["product"] is None:
        cols["product"] = first(lambda c: c.startswith("product") and "type" not in c and "categ" not in c)
    missing = [k for k in ("sample", "origin", "product", "result") if cols[k] is None]
    if missing:
        raise ValueError("missing columns %s in header %r" % (missing, header))
    return cols


def origin_of(value):
    o = re.sub(r"\s+", " ", value or "").strip().upper()
    return ORIGIN_ALIASES.get(o, o)


def base_id(sid):
    """'2014OTA0123D' (a duplicate) -> '2014OTA0123'."""
    return re.sub(r"(?<=\d)D$", "", sid)


def ppb(value, unit):
    """(ppb, ok). '<LOD', 'ND' and blanks read as 0; an unknown unit or text is not ok."""
    s = (value or "").strip().replace(",", ".")
    if not s or s.startswith("<") or s.lower() in ("nd", "n.d.", "not detected", "non détecté", "0"):
        return 0.0, True
    try:
        v = float(s)
    except ValueError:
        return None, False
    u = _norm(unit)
    if not u:
        return v, True                  # CFIA's report gives every OTA result in ppb
    if u not in TO_PPB:
        return None, False
    return v * TO_PPB[u], True


def _any(patterns, text):
    return any(re.search(p, text) for p in patterns)


def spice_type(product):
    """-> (type, EU limit in ppb or None)."""
    text = _norm(product)
    for name, limit, patterns in SPICE_TYPES:
        if _any(patterns, text):
            return name, limit
    return "other", None


def is_spice(kind, product, have_type):
    if have_type:
        k = _norm(kind)
        return "spice" in k or "épice" in k or "epice" in k
    text = _norm(product)
    if _any(NOT_A_SPICE, text):
        return False
    return spice_type(product)[0] != "other" or _any(OTHER_SPICE, text)


def is_vine_fruit(kind, product, have_type):
    text = _norm(product)
    if not _any(VINE_FRUIT, text) or _any(NOT_VINE, text):
        return False
    return "fruit" in _norm(kind) if have_type else True


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

    # Use the product-type column only if it names spices; otherwise fall back to product-name rules.
    have_type = cols["type"] is not None and any(
        "spice" in _norm(cell(r, "type")) or "épice" in _norm(cell(r, "type")) for r in table[1:])

    samples, order = {}, []
    components, units, types = {}, {}, {}
    bad_numbers = other_components = 0
    for row in table[1:]:
        sid = cell(row, "sample").upper()
        if not sid:
            continue
        comp = _norm(cell(row, "component"))
        components[comp] = components.get(comp, 0) + 1
        if cols["component"] is not None and "ochratoxin" not in comp and comp not in ("ota", "ota "):
            other_components += 1
            continue
        product, kind = cell(row, "product"), cell(row, "type")
        key = (base_id(sid), _norm(product))
        unit = cell(row, "unit")
        units[_norm(unit)] = units.get(_norm(unit), 0) + 1
        v, ok = ppb(cell(row, "result"), unit)
        if key not in samples:
            types[_norm(kind)] = types.get(_norm(kind), 0) + 1
            spice = is_spice(kind, product, have_type)
            st, limit = spice_type(product) if spice else (None, None)
            samples[key] = {"sample": base_id(sid), "origin": origin_of(cell(row, "origin")),
                            "type": kind, "product": product, "spice": spice, "spice_type": st,
                            "eu_limit": limit, "vine_fruit": is_vine_fruit(kind, product, have_type),
                            "ppb": 0.0, "results": 0}
            order.append(key)
        s = samples[key]
        if not ok:
            bad_numbers += 1
            continue
        s["ppb"] = max(s["ppb"], v)
        s["results"] += 1
    rows = [samples[k] for k in order]
    for s in rows:
        s["over_eu"] = s["eu_limit"] is not None and s["ppb"] > s["eu_limit"]
    check = {"encoding": enc, "header": header, "have_type_column": have_type,
             "data_rows": len(table) - 1, "samples": len(rows), "components": components,
             "units": units, "types": types, "bad_numbers": bad_numbers,
             "other_component_rows": other_components}
    return rows, check


def _status(gradable, met):
    if not gradable:
        return "not gradable"
    return "met" if met else "not met"


def _counts(items):
    out = {}
    for x in items:
        out[x] = out.get(x, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def _strict_top(counts, name):
    """True if `name` has strictly the highest count (a tie is not met)."""
    if not counts:
        return False
    best = max(counts.values())
    return counts.get(name, 0) == best and sum(1 for v in counts.values() if v == best) == 1


def grade(rows, check):
    n = len(rows)
    spices = [s for s in rows if s["spice"]]
    ok = n >= MIN_SAMPLES and SPICE_RANGE[0] <= len(spices) <= SPICE_RANGE[1]
    top = max(spices, key=lambda s: s["ppb"]) if spices else None
    consistent = (ok and top is not None and MAX_RANGE[0] <= top["ppb"] <= MAX_RANGE[1]
                  and top["spice_type"] == "paprika")
    over = [s for s in spices if s["over_eu"]]
    share = len(over) / len(spices) if spices else 0.0
    over_countries = _counts(s["origin"] for s in over if s["origin"] not in NO_COUNTRY)
    dom = [s for s in spices if s["origin"] == "CANADA"]
    foreign = [s for s in spices if s["origin"] not in NO_COUNTRY and s["origin"] != "CANADA"]
    dom_share = sum(s["over_eu"] for s in dom) / len(dom) if dom else 0.0
    for_share = sum(s["over_eu"] for s in foreign) / len(foreign) if foreign else 0.0
    vine_high = [s for s in rows if s["vine_fruit"] and s["ppb"] > VINE_LIMIT]
    vine_known = [s for s in vine_high if s["origin"] not in NO_COUNTRY]
    nut_over = _counts(s["origin"] for s in over if s["spice_type"] == "nutmeg" and s["origin"] not in NO_COUNTRY)
    p = {
        "P1": {"prediction": "at least %d samples parse and %d-%d of them are spices" % (
                   MIN_SAMPLES, SPICE_RANGE[0], SPICE_RANGE[1]),
               "value": "%d samples, %d spices" % (n, len(spices)), "status": "met" if ok else "not met"},
        "P2": {"prediction": "the highest spice result is %g-%g ppb in a paprika (CFIA's report; a consistency check)"
                             % MAX_RANGE,
               "value": "%s ppb, %s" % (top["ppb"], top["spice_type"]) if top else None,
               "status": _status(ok, consistent)},
        "P3": {"prediction": "%d-%d%% of spice samples exceed the EU limit for their type" % (
                   round(P3_SHARE[0] * 100), round(P3_SHARE[1] * 100)),
               "value": "%d of %d (%.1f%%)" % (len(over), len(spices), 100 * share),
               "status": _status(ok, P3_SHARE[0] <= share < P3_SHARE[1])},
        "P4": {"prediction": "the highest-OTA paprika declares Spain or Hungary",
               "value": top["origin"] if top else None,
               "status": _status(consistent, bool(top) and top["origin"] in ("SPAIN", "HUNGARY"))},
        "P5": {"prediction": "India is strictly the most frequent declared country among spices over the EU limit",
               "value": dict(list(over_countries.items())[:5]),
               "status": _status(ok and sum(over_countries.values()) >= 5, _strict_top(over_countries, "INDIA"))},
        "P6": {"prediction": "Canada-declared spices exceed EU limits less often than foreign-declared spices",
               "value": "Canada %d/%d, foreign %d/%d" % (sum(s["over_eu"] for s in dom), len(dom),
                                                       sum(s["over_eu"] for s in foreign), len(foreign)),
               "status": _status(ok and len(dom) >= 10 and len(foreign) >= 10, dom_share < for_share)},
        "P7": {"prediction": "no raisin/sultana/currant sample above %g ppb declares the United States" % VINE_LIMIT,
               "value": _counts(s["origin"] for s in vine_high),
               "status": _status(ok and bool(vine_known),
                                 all(s["origin"] != "UNITED STATES" for s in vine_known))},
        "P8": {"prediction": "Indonesia is strictly the most frequent declared country among nutmeg over 15 ppb",
               "value": nut_over,
               "status": _status(ok and sum(nut_over.values()) >= 3, _strict_top(nut_over, "INDONESIA"))},
    }
    return {"version": VERSION, "samples": n, "spices": len(spices), "gradable_parse": ok,
            "predictions": p,
            "met": sum(1 for v in p.values() if v["status"] == "met"),
            "gradable": sum(1 for v in p.values() if v["status"] != "not gradable")}


def describe(rows):
    spices = [s for s in rows if s["spice"]]
    by_type, by_origin = {}, {}
    for s in spices:
        t = by_type.setdefault(s["spice_type"], {"n": 0, "positive": 0, "over_eu": 0, "max_ppb": 0.0,
                                                 "eu_limit": s["eu_limit"], "origins": {}})
        t["n"] += 1
        t["positive"] += 1 if s["ppb"] > 0 else 0
        t["over_eu"] += 1 if s["over_eu"] else 0
        t["max_ppb"] = max(t["max_ppb"], s["ppb"])
        t["origins"][s["origin"]] = t["origins"].get(s["origin"], 0) + 1
        o = by_origin.setdefault(s["origin"], {"n": 0, "with_eu_limit": 0, "over_eu": 0, "max_ppb": 0.0})
        o["n"] += 1
        o["with_eu_limit"] += 1 if s["eu_limit"] is not None else 0
        o["over_eu"] += 1 if s["over_eu"] else 0
        o["max_ppb"] = max(o["max_ppb"], s["ppb"])
    for t in by_type.values():
        t["origins"] = dict(sorted(t["origins"].items(), key=lambda kv: (-kv[1], kv[0])))
    top = sorted(spices, key=lambda s: -s["ppb"])[:25]
    vine = sorted((s for s in rows if s["vine_fruit"] and s["ppb"] > VINE_LIMIT), key=lambda s: -s["ppb"])
    keep = ("sample", "spice_type", "product", "origin", "ppb", "eu_limit")
    return {"spices_by_type": by_type,
            "spices_by_origin": dict(sorted(by_origin.items(), key=lambda kv: (-kv[1]["n"], kv[0]))),
            "top_25_spices": [{k: s[k] for k in keep} for s in top],
            "vine_fruit_over_10_ppb": [{k: s[k] for k in ("sample", "product", "origin", "ppb")} for s in vine]}


FIELDS = ["sample", "type", "product", "origin", "spice", "spice_type", "eu_limit_ppb", "ota_ppb",
          "over_eu", "vine_fruit", "results"]


def write_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        for s in rows:
            w.writerow([s["sample"], s["type"], s["product"], s["origin"], int(s["spice"]),
                        s["spice_type"] or "", "" if s["eu_limit"] is None else s["eu_limit"], s["ppb"],
                        int(s["over_eu"]), int(s["vine_fruit"]), s["results"]])


def summary_md(result):
    g, d, c = result["grade"], result["descriptive"], result["check"]
    lines = ["# ota_spices %s" % VERSION, "",
             "- %s (Open Government Licence - Canada), sha256 %s. %d data rows, %d samples (%d spices); "
             "bad numbers %d; non-OTA component rows %d; type column %s." % (
                 DATASET, c.get("sha256", ""), c["data_rows"], c["samples"], g["spices"], c["bad_numbers"],
                 c["other_component_rows"], c["have_type_column"]),
             "", "## Pre-registered predictions (%d met of %d gradable)" % (g["met"], g["gradable"]),
             "", "| | prediction | value | status |", "|---|---|---|---|"]
    for k, v in g["predictions"].items():
        lines.append("| %s | %s | %s | %s |" % (k, v["prediction"], json.dumps(v["value"], ensure_ascii=False),
                                               v["status"]))
    lines += ["", "## Spices by type (EU limit in ppb; keyword rules, see prereg)", "",
              "| type | EU limit | n | positive | over EU limit | max ppb | top origins |",
              "|---|---|---|---|---|---|---|"]
    for name, t in sorted(d["spices_by_type"].items(), key=lambda kv: -kv[1]["n"]):
        top = ", ".join("%s %d" % (o, k) for o, k in list(t["origins"].items())[:5])
        lines.append("| %s | %s | %d | %d | %d | %g | %s |" % (name, t["eu_limit"], t["n"], t["positive"],
                                                              t["over_eu"], t["max_ppb"], top))
    lines += ["", "## Spices by declared origin", "",
              "| origin | n | with an EU limit | over EU limit | max ppb |", "|---|---|---|---|---|"]
    for o, t in d["spices_by_origin"].items():
        lines.append("| %s | %d | %d | %d | %g |" % (o, t["n"], t["with_eu_limit"], t["over_eu"], t["max_ppb"]))
    lines += ["", "## 25 highest spice results", ""]
    lines += ["- %s" % json.dumps(x, ensure_ascii=False) for x in d["top_25_spices"]] or ["- none"]
    lines += ["", "## Raisins, sultanas and currants above 10 ppb", ""]
    lines += ["- %s" % json.dumps(x, ensure_ascii=False) for x in d["vine_fruit_over_10_ppb"]] or ["- none"]
    lines += ["", "Header: %s" % c["header"], "Units: %s" % c["units"],
              "Product types: %s" % dict(list(c["types"].items())[:40]),
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
    ap.add_argument("--data", default=None, help="a local copy of the 2012-2022 CSV")
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
    write_rows(os.path.join(a.out_dir, "ota_samples.csv"), rows)
    with open(os.path.join(a.out_dir, "grades.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, ensure_ascii=False)
    with open(os.path.join(a.out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write(summary_md(result))
    g = result["grade"]
    print("ota_spices %s: %d samples, %d spices, %d of %d gradable predictions met"
          % (VERSION, g["samples"], g["spices"], g["met"], g["gradable"]))
    return 0 if g["gradable_parse"] else 1


if __name__ == "__main__":
    sys.exit(main())
