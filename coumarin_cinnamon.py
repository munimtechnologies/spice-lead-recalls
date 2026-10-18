#!/usr/bin/env python3
"""coumarin_cinnamon 0.1.0: does cinnamon sold in Canada as "Ceylon", or declared from Sri Lanka, carry
the coumarin of true cinnamon or of cassia?

Grades docs/coumarin-cinnamon-0.1.0-prereg.md, which was written and committed before any row of the
three primary data files was read.

True (Ceylon) cinnamon, Cinnamomum verum, carries only traces of coumarin; cassia cinnamons (Chinese,
Indonesian, Vietnamese/Saigon) carry thousands of ppm. Coumarin therefore tells the two apart. The
Canadian Food Inspection Agency (CFIA) tested retail cinnamon for coumarin in 2011-2016 and reports
ranges only; its open per-sample files (Open Government Licence - Canada) carry each product name and
declared origin:

  - 2011-12 Coumarin in cinnamon and cinnamon-containing products, dataset 327a6726-a515-4cf6-b106-0cdb13dd94ba
    (replication only: its header and one row were seen before this was written)
  - 2012-13 Coumarin in cinnamon and cinnamon-containing foods, dataset ca2411af-18da-44be-ada1-1592dd7b94b5
  - 2014-15 Coumarin in cinnamon-containing foods and vanilla extracts, dataset ecb615ff-504c-4e38-899e-3aeab317fadf
  - 2015-16 Coumarin in cinnamon, cinnamon-containing foods and licorice flavoured foods,
    dataset afa33f86-435b-490c-b7c1-31b7ed66c569

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
      "Chrome/126.0 Safari/537.36 coumarin_cinnamon/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % VERSION)
_BASE = "https://open.canada.ca/data/dataset/"
FILES = (
    ("2011-12", "replication", "327a6726-a515-4cf6-b106-0cdb13dd94ba",
     _BASE + "327a6726-a515-4cf6-b106-0cdb13dd94ba/resource/796ade00-c0cc-4cc6-b05d-cd440ca32dad/download/"
     "cfia_acia-1335_fsap_chem_ts_-_2011-12_coumarin_in_cinnamon_and_cinnamon-containing_products_-_ts.csv"),
    ("2012-13", "primary", "ca2411af-18da-44be-ada1-1592dd7b94b5",
     _BASE + "ca2411af-18da-44be-ada1-1592dd7b94b5/resource/51630c7f-f1e0-4aff-8f13-f673b64a7888/download/"
     "cfia_acia-1336-v1-cfia_acia_-_18926108_-_fsap_chem_ts_-_2012-13_coumarin_in_cinnamon_and_cinnamo.csv"),
    ("2014-15", "primary", "ecb615ff-504c-4e38-899e-3aeab317fadf",
     _BASE + "ecb615ff-504c-4e38-899e-3aeab317fadf/resource/85372927-17ac-4958-a66f-fdd278f13f26/download/"
     "cfia_acia-1337-v1-cfia_acia_-_18926143_-_fsap_chem_ts_-_2014-15_coumarin_in_cinnamon-containing_.csv"),
    ("2015-16", "primary", "afa33f86-435b-490c-b7c1-31b7ed66c569",
     _BASE + "afa33f86-435b-490c-b7c1-31b7ed66c569/resource/3a9481c9-cf6e-4dd0-8b25-29dd8975aa5e/download/"
     "cfia_acia-1338-v1-cfia_acia_-_18926158_-_fsap_chem_ts_-_2015-16_coumarin_cinnamon__cinnamon-cont.csv"),
)
PRIMARY = tuple(f[0] for f in FILES if f[1] == "primary")

UNKNOWN = "UNKNOWN"
IMPORTED = "IMPORTED (NO COUNTRY)"
ORIGIN_ALIASES = {"": UNKNOWN, "UNKNOWN": UNKNOWN, "INCONNU": UNKNOWN, "UNSPECIFIED": UNKNOWN,
                  "NOT SPECIFIED": UNKNOWN, "NOT STATED": UNKNOWN, "UNKNOWN OR NOT STATED": UNKNOWN,
                  "N/A": UNKNOWN, "NA": UNKNOWN, "IMPORT": IMPORTED, "IMPORTED": IMPORTED,
                  "USA": "UNITED STATES", "U.S.A.": "UNITED STATES", "US": "UNITED STATES",
                  "U.S.": "UNITED STATES", "UNITED STATES OF AMERICA": "UNITED STATES",
                  "VIET NAM": "VIETNAM", "VIET-NAM": "VIETNAM", "SRILANKA": "SRI LANKA", "CEYLON": "SRI LANKA",
                  "PEOPLE'S REPUBLIC OF CHINA": "CHINA", "CHINA, PEOPLE'S REPUBLIC OF": "CHINA",
                  "P.R. CHINA": "CHINA", "TURKIYE": "TURKEY", "TÜRKIYE": "TURKEY"}
NO_COUNTRY = (UNKNOWN, IMPORTED)
CASSIA_COUNTRIES = ("INDONESIA", "CHINA", "VIETNAM")

CINNAMON_WORD = r"cinn?amm?on|cannelle|canela|cassia"      # CFIA's 2015-16 report spells it "cinamon"
# A product name with any of these is a food or a blend that contains cinnamon, not cinnamon itself.
NOT_PURE = (r"\bmix", r"blend", r"\bpie\b", r"pumpkin", r"apple", r"chai", r"masala", r"garam", r"five spice",
            r"5 spice", r"seasoning", r"\brub\b", r"curry", r"sugar", r"\btea\b", r"tisane", r"infusion",
            r"\boil\b", r"huile", r"extract", r"essence", r"flavou?r", r"bread", r"\bbuns?\b", r"\brolls?\b",
            r"cereal", r"\boat", r"granola", r"cookie", r"biscuit", r"cake", r"muffin", r"\bbars?\b", r"toast",
            r"waffle", r"pancake", r"candy", r"\bgum\b", r"sauce", r"drink", r"beverage", r"coffee", r"latte",
            r"cocoa", r"chocolate", r"honey", r"butter", r"spread", r"raisin", r"bagel", r"cracker", r"pastry",
            r"danish", r"donut", r"doughnut", r"pudding", r"yog", r"cream", r"syrup", r"\bjam\b", r"allspice",
            r"clove", r"nutmeg", r"ginger", r"cardamom", r"vanill", r"licorice", r"liquorice", r"anise",
            r"\band\b", r"&", r"\bwith\b", r"\bavec\b", r"\bet\b", r"m[ée]lange", r"[ée]pices", r"baby",
            r"infant")
TYPE_NOT_PURE = (r"tea|thé|bak|bread|cereal|beverage|drink|sauce|oil|huile|extract|vanill|licorice|mix|m[ée]lange"
                 r"|baby|infant|oat|contain")
STICK = r"stick|quill|bark|whole|entera|entier|b[âa]ton|rolled"
CEYLON_CLAIM = (r"ceylon", r"ceylan", r"true cinnamon", r"\bverum\b", r"zeylanicum", r"sri lanka")
CASSIA_CLAIM = (r"cassia", r"saigon", r"vietnam", r"korint[jy]", r"indonesia", r"chinese cinnamon", r"china",
                r"burmannii", r"loureir", r"aromaticum")
VANILLA_FORM = r"extract|essence|flavou?r|imitation|artificial|paste|pure|ar[ôo]me|extrait"
NOT_VANILLA = r"\btea\b|chai|cinn?amm?on|cannelle|sugar|yog|ice cream|cookie|wafer|cake|\bmix|sauce|drink|beverage|coffee|latte"
TYPE_NOT_VANILLA = r"tea|thé|mix|sauce|beverage|bak"
DIVISOR = {"ppm": 1.0, "mg/kg": 1.0, "µg/g": 1.0, "μg/g": 1.0, "ug/g": 1.0,
           "ppb": 1000.0, "µg/kg": 1000.0, "μg/kg": 1000.0, "ug/kg": 1000.0, "ng/g": 1000.0}
# Pre-registered unit rule: CFIA's 2015-16 HTML report prints ppb for cinnamon values (6.8-5,040) that only
# make sense as ppm (published cassia levels are thousands of ppm). If a
# file labels results ppb (or ug/kg) but its pure-cinnamon results then all fall under 50 ppm while the
# largest raw number lies in the cassia range, the numbers are read as ppm and the file is flagged.
OVERRIDE_BELOW = 50.0
OVERRIDE_RAW = (1000.0, 20000.0)
VERUM_BELOW = 300.0
CASSIA_FROM = 1000.0
MIN_PRIMARY = 50
N_1516 = (26, 32)
MAX_1213 = 7621.0
MAX_1516 = 5040.0
P3_SHARE = 0.80
P4_SHARE = 0.10


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
    """'2012CUM0123D' (a duplicate) -> '2012CUM0123'."""
    return re.sub(r"(?<=\d)D$", "", sid)


def number(value, unit):
    """(value, divisor to ppm, ok). '<LOD', 'ND' and blanks read as 0; an unknown unit or text is not ok."""
    s = (value or "").strip().replace(",", ".")
    if not s or s.startswith("<") or s.lower() in ("nd", "n.d.", "not detected", "non détecté", "0"):
        return 0.0, 1.0, True
    try:
        v = float(s)
    except ValueError:
        return None, None, False
    u = _norm(unit)
    if not u:
        return v, 1.0, True             # CFIA's reports give coumarin in ppm
    if u not in DIVISOR:
        return None, None, False
    return v, DIVISOR[u], True


def _any(patterns, text):
    return any(re.search(p, text) for p in patterns)


def is_cinnamon(kind, product):
    """Cinnamon itself (ground, sticks, bark), not a food or blend that contains it. The cinnamon word may
    be in the product name or in a product-type column (a brand-only name)."""
    text, k = _norm(product), _norm(kind)
    if not (re.search(CINNAMON_WORD, text) or re.search(CINNAMON_WORD, k)) or _any(NOT_PURE, text):
        return False
    return not (k and re.search(TYPE_NOT_PURE, k))


def form_of(product):
    return "stick" if re.search(STICK, _norm(product)) else "ground"


def claim_of(product):
    """What the product name says about the kind of cinnamon: ceylon, cassia, both or none."""
    text = _norm(product)
    ceylon, cassia = _any(CEYLON_CLAIM, text), _any(CASSIA_CLAIM, text)
    if ceylon and cassia:
        return "both"
    return "ceylon" if ceylon else "cassia" if cassia else "none"


def is_vanilla(kind, product):
    text, k = _norm(product), _norm(kind)
    if "vanill" not in text or re.search(NOT_VANILLA, text):
        return False
    if not (re.search(VANILLA_FORM, text) or re.search(VANILLA_FORM + r"|\boil", k)):
        return False
    return not (k and re.search(TYPE_NOT_VANILLA, k))


def klass(ppm):
    if ppm < VERUM_BELOW:
        return "verum-type"
    return "intermediate" if ppm < CASSIA_FROM else "cassia-type"


def parse(raw, label=""):
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
    components, units, types = {}, {}, {}
    bad_numbers = other_components = 0
    for row in table[1:]:
        sid = cell(row, "sample").upper()
        if not sid:
            continue
        comp = _norm(cell(row, "component"))
        components[comp] = components.get(comp, 0) + 1
        if cols["component"] is not None and "coumarin" not in comp:
            other_components += 1
            continue
        product, kind = cell(row, "product"), cell(row, "type")
        key = (base_id(sid), _norm(product))
        unit = cell(row, "unit")
        units[_norm(unit)] = units.get(_norm(unit), 0) + 1
        v, div, ok = number(cell(row, "result"), unit)
        if key not in samples:
            types[_norm(kind)] = types.get(_norm(kind), 0) + 1
            samples[key] = {"file": label, "sample": base_id(sid), "origin": origin_of(cell(row, "origin")),
                            "type": kind, "product": product, "cinnamon": is_cinnamon(kind, product),
                            "form": form_of(product), "claim": claim_of(product),
                            "vanilla": is_vanilla(kind, product), "vals": []}
            order.append(key)
        if not ok:
            bad_numbers += 1
            continue
        samples[key]["vals"].append((v, div))
    rows = [samples[k] for k in order]
    cin = [s for s in rows if s["cinnamon"] and s["vals"]]
    raw_max = max((v for s in cin for v, _ in s["vals"]), default=0.0)
    conv_max = max((v / d for s in cin for v, d in s["vals"]), default=0.0)
    override = (any(d != 1.0 for s in cin for _, d in s["vals"]) and conv_max < OVERRIDE_BELOW
                and OVERRIDE_RAW[0] <= raw_max <= OVERRIDE_RAW[1])
    for s in rows:
        vals = [v if override else v / d for v, d in s.pop("vals")]
        s["results"] = len(vals)
        s["ppm"] = sum(vals) / len(vals) if vals else None
        s["class"] = klass(s["ppm"]) if s["cinnamon"] and vals else ""
    check = {"file": label, "encoding": enc, "header": header, "data_rows": len(table) - 1,
             "samples": len(rows), "cinnamon": len(cin), "vanilla": sum(1 for s in rows if s["vanilla"]),
             "components": components, "units": units, "types": types, "bad_numbers": bad_numbers,
             "other_component_rows": other_components, "unit_override": override}
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


def _cinnamon(rows, files):
    return [s for s in rows if s["file"] in files and s["cinnamon"] and s["ppm"] is not None]


def _pct(k, n):
    return "%d of %d (%.1f%%)" % (k, n, 100.0 * k / n if n else 0.0)


def grade(rows):
    cin = _cinnamon(rows, PRIMARY)
    n = len(cin)
    n1516 = sum(1 for s in cin if s["file"] == "2015-16")
    ok = n >= MIN_PRIMARY and N_1516[0] <= n1516 <= N_1516[1]
    top = max(cin, key=lambda s: s["ppm"]) if cin else None
    max1516 = max((s["ppm"] for s in cin if s["file"] == "2015-16"), default=None)
    consistent = (top is not None and top["file"] == "2012-13" and abs(top["ppm"] - MAX_1213) <= 1.0
                  and max1516 is not None and abs(max1516 - MAX_1516) <= 1.0)
    cassia = sum(1 for s in cin if s["class"] == "cassia-type")
    middle = sum(1 for s in cin if s["class"] == "intermediate")
    ceylon = [s for s in cin if s["claim"] == "ceylon"]
    cassia_claim = [s for s in cin if s["claim"] == "cassia"]
    from_cassia = [s for s in cin if s["origin"] in CASSIA_COUNTRIES]
    from_lanka = [s for s in cin if s["origin"] == "SRI LANKA"]
    vanilla = [s for s in rows if s["file"] == "2014-15" and s["vanilla"] and (s["ppm"] or 0) > 0]
    van_countries = _counts(s["origin"] for s in vanilla if s["origin"] not in NO_COUNTRY)
    p = {
        "P1": {"prediction": "at least %d cinnamon samples in the primary files, %d-%d of them in 2015-16" % (
                   MIN_PRIMARY, N_1516[0], N_1516[1]),
               "value": "%d primary, %d in 2015-16" % (n, n1516), "status": "met" if ok else "not met"},
        "P2": {"prediction": "the highest primary cinnamon result is %g ppm in 2012-13 and the 2015-16 maximum is "
                             "%g ppm (CFIA's reports; a consistency check)" % (MAX_1213, MAX_1516),
               "value": "%s ppm in %s; 2015-16 max %s" % (top["ppm"], top["file"], max1516) if top else None,
               "status": _status(ok, consistent)},
        "P3": {"prediction": "at least %d%% of primary cinnamon samples are cassia-type (>= %g ppm)" % (
                   round(P3_SHARE * 100), CASSIA_FROM),
               "value": _pct(cassia, n), "status": _status(ok, cassia >= P3_SHARE * n)},
        "P4": {"prediction": "fewer than %d%% of primary cinnamon samples are intermediate (%g-%g ppm)" % (
                   round(P4_SHARE * 100), VERUM_BELOW, CASSIA_FROM),
               "value": _pct(middle, n), "status": _status(ok, middle < P4_SHARE * n)},
        "P5": {"prediction": "no cinnamon sample whose name claims Ceylon is cassia-type",
               "value": [{"file": s["file"], "product": s["product"], "origin": s["origin"], "ppm": s["ppm"]}
                         for s in ceylon],
               "status": _status(ok and len(ceylon) >= 2, all(s["class"] != "cassia-type" for s in ceylon))},
        "P6": {"prediction": "every cinnamon sample whose name claims cassia, Saigon, Vietnam, Korintje, Indonesia "
                             "or China is cassia-type",
               "value": _counts(s["class"] for s in cassia_claim),
               "status": _status(ok and len(cassia_claim) >= 2,
                                 all(s["class"] == "cassia-type" for s in cassia_claim))},
        "P7": {"prediction": "no cinnamon sample declaring Indonesia, China or Vietnam is verum-type",
               "value": _counts(s["class"] for s in from_cassia),
               "status": _status(ok and len(from_cassia) >= 5,
                                 all(s["class"] != "verum-type" for s in from_cassia))},
        "P8": {"prediction": "more than half of the cinnamon samples declaring Sri Lanka are verum-type",
               "value": _counts(s["class"] for s in from_lanka),
               "status": _status(ok and len(from_lanka) >= 3,
                                 2 * sum(1 for s in from_lanka if s["class"] == "verum-type") > len(from_lanka))},
        "P9": {"prediction": "Mexico is strictly the most frequent declared country among 2014-15 vanilla "
                             "products with coumarin detected",
               "value": van_countries,
               "status": _status(sum(van_countries.values()) >= 3, _strict_top(van_countries, "MEXICO"))},
    }
    return {"version": VERSION, "primary_cinnamon": n, "gradable_parse": ok, "predictions": p,
            "met": sum(1 for v in p.values() if v["status"] == "met"),
            "gradable": sum(1 for v in p.values() if v["status"] != "not gradable")}


def _table(cin, key):
    out = {}
    for s in cin:
        t = out.setdefault(s[key], {"n": 0, "verum-type": 0, "intermediate": 0, "cassia-type": 0, "max_ppm": 0.0})
        t["n"] += 1
        t[s["class"]] += 1
        t["max_ppm"] = max(t["max_ppm"], s["ppm"])
    return dict(sorted(out.items(), key=lambda kv: (-kv[1]["n"], kv[0])))


def describe(rows):
    keep = ("file", "sample", "product", "origin", "form", "claim", "ppm", "class")
    out = {}
    for name, files in (("primary", PRIMARY), ("replication_2011_12", ("2011-12",))):
        cin = _cinnamon(rows, files)
        out[name] = {"n": len(cin), "by_file": _table(cin, "file"), "by_form": _table(cin, "form"),
                     "by_claim": _table(cin, "claim"), "by_origin": _table(cin, "origin"),
                     "claimed_or_sri_lanka": [{k: s[k] for k in keep} for s in cin
                                              if s["claim"] != "none" or s["origin"] == "SRI LANKA"],
                     "intermediate": [{k: s[k] for k in keep} for s in cin if s["class"] == "intermediate"],
                     "lowest_10": [{k: s[k] for k in keep} for s in sorted(cin, key=lambda s: s["ppm"])[:10]]}
    van = [s for s in rows if s["vanilla"] and s["ppm"] is not None]
    out["vanilla"] = {"n": len(van), "detected": [{k: s[k] for k in ("file", "sample", "product", "origin", "ppm")}
                                                  for s in van if s["ppm"] > 0],
                      "by_origin": _counts(s["origin"] for s in van)}
    return out


FIELDS = ["file", "sample", "type", "product", "origin", "cinnamon", "form", "claim", "vanilla", "coumarin_ppm",
          "class", "results"]


def write_rows(path, rows):
    """Cinnamon and vanilla samples only."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        for s in rows:
            if s["cinnamon"] or s["vanilla"]:
                w.writerow([s["file"], s["sample"], s["type"], s["product"], s["origin"], int(s["cinnamon"]),
                            s["form"] if s["cinnamon"] else "", s["claim"] if s["cinnamon"] else "",
                            int(s["vanilla"]), "" if s["ppm"] is None else s["ppm"], s["class"], s["results"]])


def summary_md(result):
    g, d = result["grade"], result["descriptive"]
    lines = ["# coumarin_cinnamon %s" % VERSION, ""]
    for c in result["checks"]:
        lines.append("- %s: sha256 %s; %d data rows, %d samples, %d cinnamon, %d vanilla; bad numbers %d; "
                     "non-coumarin rows %d; unit override %s." % (
                         c["file"], c.get("sha256", ""), c["data_rows"], c["samples"], c["cinnamon"], c["vanilla"],
                         c["bad_numbers"], c["other_component_rows"], c["unit_override"]))
    lines += ["", "## Pre-registered predictions (%d met of %d gradable)" % (g["met"], g["gradable"]),
              "", "| | prediction | value | status |", "|---|---|---|---|"]
    for k, v in g["predictions"].items():
        lines.append("| %s | %s | %s | %s |" % (k, v["prediction"], json.dumps(v["value"], ensure_ascii=False),
                                               v["status"]))
    for name in ("primary", "replication_2011_12"):
        part = d[name]
        lines += ["", "## %s cinnamon (n = %d); classes: verum-type < %g ppm, cassia-type >= %g" % (
            name, part["n"], VERUM_BELOW, CASSIA_FROM)]
        for key in ("by_file", "by_form", "by_claim", "by_origin"):
            lines += ["", "| %s | n | verum-type | intermediate | cassia-type | max ppm |" % key[3:],
                      "|---|---|---|---|---|---|"]
            for k, t in part[key].items():
                lines.append("| %s | %d | %d | %d | %d | %g |" % (k, t["n"], t["verum-type"], t["intermediate"],
                                                                 t["cassia-type"], t["max_ppm"]))
        for key in ("claimed_or_sri_lanka", "intermediate", "lowest_10"):
            lines += ["", "### %s" % key, ""]
            lines += ["- %s" % json.dumps(x, ensure_ascii=False) for x in part[key]] or ["- none"]
    lines += ["", "## Vanilla products (n = %d)" % d["vanilla"]["n"], "",
              "By origin: %s" % json.dumps(d["vanilla"]["by_origin"], ensure_ascii=False), ""]
    lines += ["- %s" % json.dumps(x, ensure_ascii=False) for x in d["vanilla"]["detected"]] or ["- none detected"]
    for c in result["checks"]:
        lines += ["", "%s header: %s" % (c["file"], c["header"]), "Units: %s" % c["units"],
                  "Components: %s" % dict(list(c["components"].items())[:10]),
                  "Types: %s" % dict(list(c["types"].items())[:40])]
    lines += ["", "Made by MV2 of Munim, Inc. with AI agents. Code Apache-2.0; derived data CC BY 4.0.",
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
    ap.add_argument("--data-dir", default=None, help="a folder holding local copies named <label>.csv")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    rows, checks = [], []
    for label, role, dataset, url in FILES:
        if a.data_dir:
            with open(os.path.join(a.data_dir, "%s.csv" % label), "rb") as f:
                raw = f.read()
        else:
            raw = fetch(url)
            with open(os.path.join(a.out_dir, "cfia_coumarin_%s.csv" % label), "wb") as f:
                f.write(raw)
        r, check = parse(raw, label)
        check.update(role=role, dataset=dataset, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        rows += r
        checks.append(check)
    result = {"grade": grade(rows), "descriptive": describe(rows), "checks": checks}
    write_rows(os.path.join(a.out_dir, "coumarin_samples.csv"), rows)
    with open(os.path.join(a.out_dir, "grades.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, ensure_ascii=False)
    with open(os.path.join(a.out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write(summary_md(result))
    g = result["grade"]
    print("coumarin_cinnamon %s: %d primary cinnamon samples, %d of %d gradable predictions met"
          % (VERSION, g["primary_cinnamon"], g["met"], g["gradable"]))
    return 0 if g["gradable_parse"] else 1


if __name__ == "__main__":
    sys.exit(main())
