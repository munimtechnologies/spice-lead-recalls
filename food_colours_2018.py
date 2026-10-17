#!/usr/bin/env python3
"""food_colours_2018 0.1.0: which product carried the one non-permitted colour in Canada's
2018-19 food colours survey?

Grades docs/food-colours-2018-0.1.0-prereg.md, which was written and committed before any
row of the data file was read.

The Canadian Food Inspection Agency (CFIA) bought 399 essences/flavourings, oils, sweets and
processed vegetables at retail in 2018-19 and tested them for up to 43 food colours. Its
report says one sample held a non-permitted colour (Table 3: Rhodamine B, 10.8 ppm) but does
not say which product or origin. This reads the open per-sample file, one row per sample and
colour (Open Government Licence - Canada):

  - "Food Colours in Essences/flavourings, oils, sweets and processed vegetables - April 1,
    2018 to March 31, 2019", open.canada.ca dataset 1b0c4141-7a22-4c93-8679-63eb49f7be24.

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
      "Chrome/126.0 Safari/537.36 food_colours_2018/%s (MV2 of Munim, Inc.; mv2@munimtech.com)"
      % VERSION)
DATASET = "https://open.canada.ca/data/en/dataset/1b0c4141-7a22-4c93-8679-63eb49f7be24"
URL = ("https://open.canada.ca/data/dataset/1b0c4141-7a22-4c93-8679-63eb49f7be24/resource/"
       "3006ff94-fa7a-4cc4-8b58-a2164ce6a937/download/"
       "cfia_acia-1133_2018-19_food_colours_in_selected_foods_-2018-2019_"
       "colorants-alimentaires-dans-les.csv")
FILE = "cfia_food_colours_2018-19.csv"

UNKNOWN = "UNKNOWN"
UNCLASSIFIED = "unclassified"
ORIGIN_ALIASES = {"COTE D'IVOIRE": "IVORY COAST", "CÔTE D'IVOIRE": "IVORY COAST",
                  "UNKNOWN OR NOT STATED": UNKNOWN, "NOT STATED": UNKNOWN, "NOT SPECIFIED": UNKNOWN,
                  "UNSPECIFIED": UNKNOWN, "": UNKNOWN}
WEST_CENTRAL_AFRICA = ("NIGERIA", "GHANA", "SENEGAL", "TOGO", "IVORY COAST", "CAMEROON",
                       "BENIN", "BURKINA FASO", "MALI", "SIERRA LEONE", "GUINEA", "LIBERIA",
                       "GAMBIA", "NIGER", "CONGO", "GABON")
ASIA = ("INDIA", "PAKISTAN", "BANGLADESH", "SRI LANKA", "NEPAL", "CHINA", "HONG KONG", "TAIWAN",
        "VIETNAM", "VIET NAM", "THAILAND", "PHILIPPINES", "INDONESIA", "MALAYSIA", "SINGAPORE",
        "KOREA", "SOUTH KOREA", "REPUBLIC OF KOREA", "JAPAN", "IRAN", "TURKEY", "TURKIYE",
        "TÜRKIYE", "AFGHANISTAN", "MYANMAR", "CAMBODIA", "LAOS", "LEBANON", "SYRIA", "IRAQ",
        "ISRAEL", "JORDAN", "SAUDI ARABIA", "UNITED ARAB EMIRATES", "YEMEN", "UZBEKISTAN",
        "KAZAKHSTAN", "MONGOLIA", "BHUTAN", "MALDIVES")
# CFIA Appendix A, the 10 permitted water-soluble colours. "Erythrosin Yellowish" is NOT permitted.
PERMITTED = ("tartrazine", "amaranth", "indigo carmine", "indigotine", "sunset yellow", "allura red",
             "ponceau sx", "fast green", "brilliant blue", "erythrosin", "chlorophyllin")
# Category rules, applied in this order to "Commodity Product" text (lower case).
CATEGORY_RULES = (
    ("oils", (r"\boils?\b", r"\bhuiles?\b")),
    ("processed vegetables", (r"pickle", r"vegetable", r"chutney", r"relish", r"kimchi", r"achar",
                              r"sauerkraut", r"\bolives?\b", r"l[ée]gume", r"marin[ée]", r"\bpeppers?\b",
                              r"\bcorn\b", r"\bbeans?\b", r"\bbeets?\b", r"cucumber", r"cabbage", r"turnip",
                              r"radish", r"carrot", r"mushroom", r"\bonions?\b", r"garlic", r"chil+i",
                              r"jalape", r"capsicum", r"tomato", r"pimiento")),
    ("sweets", (r"sweet", r"cand(y|ies)", r"confection", r"\bgum", r"jell", r"lollipop", r"marshmallow",
                r"chocolate", r"toffee", r"licorice", r"liquorice", r"halwa", r"mithai", r"sprinkle",
                r"icing", r"frosting", r"marzipan", r"bonbon", r"lozenge", r"\bmints?\b", r"nougat",
                r"fudge", r"caramel", r"dessert", r"sucrerie", r"friandise")),
    ("essences/flavourings", (r"essence", r"flavou?r", r"extract", r"aroma", r"colou?r", r"ar[ôo]me")),
)
MIN_SAMPLES = 380
P6_MAX_SHARE = 0.05
HIGH_PPM = 300.0


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
        "commodity": first(lambda c: c.startswith("commodity")),
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
    """'C2018FC00019D' (a duplicate) -> 'C2018FC00019'."""
    return re.sub(r"(?<=\d)D$", "", sid)


def number(value):
    s = (value or "").strip().replace(",", ".")
    if s.startswith("<"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return None


def classify(commodity, product):
    text = re.sub(r"\s+", " ", "%s %s" % (commodity or "", product or "")).strip().lower()
    for cat, patterns in CATEGORY_RULES:
        for pat in patterns:
            if re.search(pat, text):
                return cat
    return UNCLASSIFIED


def is_permitted(component):
    c = re.sub(r"\s+", " ", component or "").strip().lower()
    if "yellowish" in c:
        return False
    return any(p in c for p in PERMITTED)


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
            commodity, product = cell(row, "commodity"), cell(row, "product")
            samples[base] = {"sample": base, "origin": origin, "commodity": commodity,
                             "product": product, "category": classify(commodity, product),
                             "amounts": {}}
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
        s["non_permitted"] = [c for c in s["positive"] if not is_permitted(c)]
        permitted = [s["amounts"][c] for c in s["positive"] if is_permitted(c)]
        s["max_permitted_ppm"] = max(permitted) if permitted else 0.0
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
    ok = n >= MIN_SAMPLES and any("rhodamine" in c for c in check["components"])
    rho = [s for s in rows if any("rhodamine" in c for c in s["positive"])]
    one = ok and len(rho) == 1
    r = rho[0] if one else None
    o2 = [s for s in rows if any(c.startswith("orange ii") for c in s["positive"])]
    o2_classified = bool(o2) and all(s["category"] != UNCLASSIFIED for s in o2)
    oils = [s for s in rows if s["category"] == "oils"]
    oils_wca = [s for s in oils if s["origin"] in WEST_CENTRAL_AFRICA]
    categories = {}
    for s in rows:
        categories[s["category"]] = categories.get(s["category"], 0) + 1
    p = {
        "P1": {"prediction": "at least %d samples parse and the file reports Rhodamine B" % MIN_SAMPLES,
               "value": n, "status": "met" if ok else "not met"},
        "P2": {"prediction": "exactly one sample carries Rhodamine B above zero (CFIA's Table 3; a consistency check)",
               "value": len(rho), "status": _status(ok, len(rho) == 1)},
        "P3": {"prediction": "the Rhodamine B sample is a sweet",
               "value": r["category"] if r else None,
               "status": _status(one and r["category"] != UNCLASSIFIED, bool(r) and r["category"] == "sweets")},
        "P4": {"prediction": "the Rhodamine B sample declares an Asian origin",
               "value": r["origin"] if r else None,
               "status": _status(one, bool(r) and r["origin"] in ASIA)},
        "P5": {"prediction": "every sample with Orange II above zero is a sweet",
               "value": [s["category"] for s in o2],
               "status": _status(ok and o2_classified, o2_classified and all(s["category"] == "sweets" for s in o2))},
        "P6": {"prediction": "under 5% of oil samples declare a West or Central African origin",
               "value": "%d of %d" % (len(oils_wca), len(oils)),
               "status": _status(ok and bool(oils), len(oils_wca) < P6_MAX_SHARE * len(oils))},
    }
    return {"version": VERSION, "samples": n, "gradable_parse": ok, "predictions": p,
            "met": sum(1 for v in p.values() if v["status"] == "met"),
            "gradable": sum(1 for v in p.values() if v["status"] != "not gradable"),
            "categories": dict(sorted(categories.items(), key=lambda kv: (-kv[1], kv[0])))}


def describe(rows):
    by_cat, non_permitted, high = {}, [], []
    for s in rows:
        t = by_cat.setdefault(s["category"], {"n": 0, "with_colour": 0, "origins": {}})
        t["n"] += 1
        t["with_colour"] += 1 if s["positive"] else 0
        t["origins"][s["origin"]] = t["origins"].get(s["origin"], 0) + 1
        if s["non_permitted"]:
            non_permitted.append({"sample": s["sample"], "category": s["category"], "origin": s["origin"],
                                  "commodity": s["commodity"], "product": s["product"],
                                  "amounts": {c: s["amounts"][c] for c in s["non_permitted"]}})
        if s["max_permitted_ppm"] > HIGH_PPM:
            high.append({"sample": s["sample"], "category": s["category"], "origin": s["origin"],
                         "product": s["product"], "max_permitted_ppm": s["max_permitted_ppm"],
                         "amounts": {c: s["amounts"][c] for c in s["positive"]}})
    for t in by_cat.values():
        t["origins"] = dict(sorted(t["origins"].items(), key=lambda kv: (-kv[1], kv[0])))
    return {"by_category": by_cat, "non_permitted_samples": non_permitted,
            "permitted_colour_above_%d_ppm" % int(HIGH_PPM): high}


FIELDS = ["sample", "category", "commodity", "product", "origin", "positive", "non_permitted",
          "max_permitted_ppm", "components_tested"]


def write_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        for s in rows:
            w.writerow([s["sample"], s["category"], s["commodity"], s["product"], s["origin"],
                        ";".join(s["positive"]), ";".join(s["non_permitted"]),
                        s["max_permitted_ppm"], len(s["amounts"])])


def summary_md(result):
    g, d, c = result["grade"], result["descriptive"], result["check"]
    lines = ["# food_colours_2018 %s" % VERSION, "",
             "- %s (Open Government Licence - Canada), sha256 %s. %d data rows, %d samples; "
             "bad numbers %d; origin conflicts %d; %d components." % (
                 DATASET, c.get("sha256", ""), c["data_rows"], c["samples"], c["bad_numbers"],
                 c["origin_conflicts"], len(c["components"])),
             "", "## Pre-registered predictions (%d met of %d gradable)" % (g["met"], g["gradable"]),
             "", "| | prediction | value | status |", "|---|---|---|---|"]
    for k, v in g["predictions"].items():
        lines.append("| %s | %s | %s | %s |" % (k, v["prediction"], v["value"], v["status"]))
    lines += ["", "## By category (keyword rules; see prereg)", "",
              "| category | n | with any colour | top origins |", "|---|---|---|---|"]
    for cat, t in sorted(d["by_category"].items()):
        top = ", ".join("%s %d" % (o, k) for o, k in list(t["origins"].items())[:5])
        lines.append("| %s | %d | %d | %s |" % (cat, t["n"], t["with_colour"], top))
    lines += ["", "## Samples with a non-permitted colour", ""]
    lines += ["- %s" % json.dumps(x, ensure_ascii=False) for x in d["non_permitted_samples"]] or ["- none"]
    lines += ["", "## Samples with a permitted colour above %d ppm (descriptive, not graded)" % int(HIGH_PPM), ""]
    lines += ["- %s" % json.dumps(x, ensure_ascii=False)
              for x in d["permitted_colour_above_%d_ppm" % int(HIGH_PPM)]] or ["- none"]
    lines += ["", "Components in file: %s" % sorted(c["components"]),
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
    ap.add_argument("--data", default=None, help="a local copy of the 2018-19 CSV")
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
    write_rows(os.path.join(a.out_dir, "food_colours_2018_samples.csv"), rows)
    with open(os.path.join(a.out_dir, "grades.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, ensure_ascii=False)
    with open(os.path.join(a.out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write(summary_md(result))
    g = result["grade"]
    print("food_colours_2018 %s: %d samples, %d of %d gradable predictions met"
          % (VERSION, g["samples"], g["met"], g["gradable"]))
    return 0 if g["gradable_parse"] else 1


if __name__ == "__main__":
    sys.exit(main())
