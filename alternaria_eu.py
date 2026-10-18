#!/usr/bin/env python3
"""alternaria_eu 0.1.0: how often do foods sold in Canada sit above the EU's indicative levels for the
Alternaria toxins alternariol (AOH) and alternariol monomethyl ether (AME)?

Grades docs/alternaria-eu-0.1.0-prereg.md, which was written and committed before any row of the data file
was read.

The Canadian Food Inspection Agency (CFIA) tested 2,597 retail foods for AOH and AME in 2014-2018 and
2019-2022. Its report gives AOH + AME combined, by product type, and compares with no level, because no
country sets a limit. The EU's Commission Recommendation (EU) 2022/553 sets indicative levels: values above
which the EU asks for investigation of causes. They are not food safety levels. The per-sample file is open
(Open Government Licence - Canada), dataset 8888649b-c059-4f76-ae0f-30ab6c1159c5.

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
      "Chrome/126.0 Safari/537.36 alternaria_eu/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % VERSION)
DATASET = "8888649b-c059-4f76-ae0f-30ab6c1159c5"
URL = ("https://open.canada.ca/data/dataset/8888649b-c059-4f76-ae0f-30ab6c1159c5/resource/"
       "c93db5ad-283a-45e1-8995-f1dc33c9392c/download/"
       "fsap-chem-ts-alternaria-in-selected-foods-2014-2018-and-2019-2022_paaspa-chem-ec-alternaria-dans.csv")

# Commission Recommendation (EU) 2022/553, Annex: indicative levels in ug/kg as (AOH, AME). Paprika powder,
# tree nuts and dried figs have a tenuazonic acid level only, which CFIA did not measure, so they are not
# graded.
EU_LEVELS = {"processed tomato": (10.0, 5.0), "sesame seeds": (30.0, 30.0), "sunflower seeds": (30.0, 30.0),
             "sunflower oil": (10.0, 10.0), "infant cereal": (2.0, 2.0)}

UNKNOWN = "UNKNOWN"
IMPORTED = "IMPORTED (NO COUNTRY)"
ORIGIN_ALIASES = {"": UNKNOWN, "UNKNOWN": UNKNOWN, "INCONNU": UNKNOWN, "UNSPECIFIED": UNKNOWN,
                  "NOT SPECIFIED": UNKNOWN, "NOT STATED": UNKNOWN, "UNKNOWN OR NOT STATED": UNKNOWN,
                  "N/A": UNKNOWN, "NA": UNKNOWN, "IMPORT": IMPORTED, "IMPORTED": IMPORTED, "IMPORTÉ": IMPORTED,
                  "DOMESTIC": "CANADA", "DOMESTIQUE": "CANADA",
                  "USA": "UNITED STATES", "U.S.A.": "UNITED STATES", "US": "UNITED STATES",
                  "U.S.": "UNITED STATES", "UNITED STATES OF AMERICA": "UNITED STATES",
                  "VIET NAM": "VIETNAM", "PEOPLE'S REPUBLIC OF CHINA": "CHINA", "TURKIYE": "TURKEY",
                  "TÜRKIYE": "TURKEY", "IRAN, ISLAMIC REPUBLIC OF": "IRAN"}
NO_COUNTRY = (UNKNOWN, IMPORTED)

INFANT = r"infant|baby|babies|b[ée]b[ée]|toddler|nourrisson|junior|teething|dentition|tout-petit"
CEREAL = (r"cereal|c[ée]r[ée]ale|\boat|avoine|\brice\b|\briz\b|barley|\borge\b|wheat|\bbl[ée]\b|grain|biscuit"
          r"|cracker|puff|rusk|pasta|p[âa]tes")
TOMATO = r"tomat"
FRESH = r"\bfresh\b|\bfrais\b|\bfra[iî]che\b"
OIL = r"\boil\b|huile"
SESAME = r"s[ée]same"
SUNFLOWER = r"sunflower|tournesol"
SEED_NOT = r"butter|beurre"
POMEGRANATE = r"pomegranate|\bgrenade\b"
ND = ("nd", "n.d.", "not detected", "non détecté", "0")
MULT = {"ppb": 1.0, "µg/kg": 1.0, "μg/kg": 1.0, "ug/kg": 1.0, "ng/g": 1.0,
        "ppm": 1000.0, "mg/kg": 1000.0, "µg/g": 1000.0, "μg/g": 1000.0, "ug/g": 1000.0}

N_SAMPLES = (2500, 2700)
TOP_TOTAL = (860.0, 890.0)
TOMATO_ABOVE = (2, 4)
OIL_ABOVE = (1, 5)
INFANT_PCT = 20
MIN_CAT = 10
POM_FROM = 100.0


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
    """'2019ALT0123D' (a duplicate) -> '2019ALT0123'."""
    return re.sub(r"(?<=\d)D$", "", sid)


def number(value, unit):
    """(value in ug/kg = ppb, ok). '<LOD', 'ND' and blanks read as 0; an unknown unit or text is not ok."""
    s = (value or "").strip().replace(",", ".")
    if not s or s.startswith("<") or s.lower() in ND:
        return 0.0, True
    try:
        v = float(s)
    except ValueError:
        return None, False
    u = _norm(unit)
    if not u:
        return v, True                  # CFIA's report gives Alternaria toxins in ppb
    if u not in MULT:
        return None, False
    return v * MULT[u], True


def component_of(comp):
    c = _norm(comp)
    if re.search(r"\btotal|somme|\bsum\b", c):
        return "TOTAL"
    if re.search(r"mono\s*-?\s*m[ée]thyl|\bame\b", c):
        return "AME"
    if re.search(r"alternariol|\baoh\b", c):
        return "AOH"
    return ""


def category(kind, product):
    """The EU 2022/553 food a sample falls under, or '' if none with an AOH/AME level."""
    text = _norm(kind) + " | " + _norm(product)
    if re.search(INFANT, text):
        return "infant cereal" if re.search(CEREAL, text) else ""
    if re.search(TOMATO, text) and not re.search(FRESH, text):
        return "processed tomato"
    if re.search(SESAME, text):
        return "" if re.search(OIL, text) else "sesame seeds"
    if re.search(SUNFLOWER, text):
        if re.search(OIL, text):
            return "sunflower oil"
        return "" if re.search(SEED_NOT, text) else "sunflower seeds"
    return ""


def is_pomegranate(kind, product):
    return re.search(POMEGRANATE, _norm(kind) + " | " + _norm(product)) is not None


def state(s):
    """above / within / undetermined against the EU level of the sample's food ('' if it has none). With AOH
    and AME separate the test is exact. With only a reported total: above if the total exceeds the sum of the
    two levels (then at least one toxin must exceed its own), within if it is no more than the smaller one."""
    lv = EU_LEVELS.get(s["category"])
    if lv is None:
        return ""
    la, lm = lv
    aoh, ame, tot = s["aoh"], s["ame"], s["total_reported"]
    if aoh is not None and ame is not None:
        return "above" if aoh > la or ame > lm else "within"
    if (aoh is not None and aoh > la) or (ame is not None and ame > lm):
        return "above"
    if aoh is None and ame is None and tot is not None:
        if tot > la + lm:
            return "above"
        if tot <= min(la, lm):
            return "within"
    return "undetermined"


def _mean(xs):
    return sum(xs) / len(xs) if xs else None


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
    components, units, types = {}, {}, {}
    bad_numbers = other_components = 0
    for row in table[1:]:
        sid = cell(row, "sample").upper()
        if not sid:
            continue
        raw_comp = cell(row, "component")
        components[_norm(raw_comp)] = components.get(_norm(raw_comp), 0) + 1
        comp = component_of(raw_comp) if cols["component"] is not None else "TOTAL"
        if not comp:
            other_components += 1
            continue
        product, kind = cell(row, "product"), cell(row, "type")
        key = (base_id(sid), _norm(product))
        unit = cell(row, "unit")
        units[_norm(unit)] = units.get(_norm(unit), 0) + 1
        v, ok = number(cell(row, "result"), unit)
        if key not in samples:
            types[_norm(kind)] = types.get(_norm(kind), 0) + 1
            samples[key] = {"sample": base_id(sid), "origin": origin_of(cell(row, "origin")), "type": kind,
                            "product": product, "category": category(kind, product),
                            "pomegranate": is_pomegranate(kind, product),
                            "vals": {"AOH": [], "AME": [], "TOTAL": []}}
            order.append(key)
        if not ok:
            bad_numbers += 1
            continue
        samples[key]["vals"][comp].append(v)
    rows = []
    for k in order:
        s = samples[k]
        vals = s.pop("vals")
        s["results"] = sum(len(v) for v in vals.values())
        s["aoh"], s["ame"], s["total_reported"] = _mean(vals["AOH"]), _mean(vals["AME"]), _mean(vals["TOTAL"])
        if s["aoh"] is not None and s["ame"] is not None:
            s["total"] = s["aoh"] + s["ame"]
        else:
            s["total"] = s["total_reported"] if s["aoh"] is None and s["ame"] is None else None
        s["state"] = state(s)
        rows.append(s)
    check = {"encoding": enc, "header": header, "data_rows": len(table) - 1, "samples": len(rows),
             "with_components": sum(1 for s in rows if s["aoh"] is not None and s["ame"] is not None),
             "components": components, "units": units, "types": types, "bad_numbers": bad_numbers,
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


def bounded(xs, test):
    """Grade test(k, n) on the number k of samples above their level. Undetermined samples may be either, so
    the status is met (or not met) only if it holds (or fails) for every k they allow."""
    lo = sum(1 for s in xs if s["state"] == "above")
    und = sum(1 for s in xs if s["state"] == "undetermined")
    outcomes = {test(k, len(xs)) for k in range(lo, lo + und + 1)}
    status = "not gradable" if len(outcomes) > 1 else "met" if outcomes.pop() else "not met"
    return status, "%d above of %d (%d undetermined)" % (lo, len(xs), und)


def _in(cats, rows):
    return [s for s in rows if s["category"] in cats]


def grade(rows):
    n = len(rows)
    ok = N_SAMPLES[0] <= n <= N_SAMPLES[1]
    with_total = [s for s in rows if s["total"] is not None]
    top = max(with_total, key=lambda s: s["total"]) if with_total else None
    p = {"P1": {"prediction": "%d-%d samples parse (parse gate)" % N_SAMPLES, "value": "%d samples" % n,
                "status": "met" if ok else "not met"},
         "P2": {"prediction": "the highest AOH + AME total is %g-%g ppb and is a processed tomato product "
                              "(CFIA's report; a consistency check)" % TOP_TOTAL,
                "value": "%g ppb (%s; %s)" % (top["total"], top["product"], top["category"] or "-") if top else None,
                "status": _status(ok, top is not None and TOP_TOTAL[0] <= top["total"] <= TOP_TOTAL[1]
                                  and top["category"] == "processed tomato")}}

    def against(key, prediction, cats, test):
        xs = _in(cats, rows)
        status, value = bounded(xs, test)
        p[key] = {"prediction": prediction, "value": value,
                  "status": status if ok and len(xs) >= MIN_CAT else "not gradable"}

    against("P3", "%d-%d processed tomato samples are above an EU indicative level (AOH 10 or AME 5 ug/kg)"
            % TOMATO_ABOVE, ("processed tomato",), lambda k, n: TOMATO_ABOVE[0] <= k <= TOMATO_ABOVE[1])
    against("P4", "no sesame or sunflower seed sample is above an EU indicative level (AOH 30, AME 30)",
            ("sesame seeds", "sunflower seeds"), lambda k, n: k == 0)
    against("P5", "%d-%d sunflower oil samples are above an EU indicative level (AOH 10, AME 10)" % OIL_ABOVE,
            ("sunflower oil",), lambda k, n: OIL_ABOVE[0] <= k <= OIL_ABOVE[1])
    against("P6", "at least %d%% of cereal-based infant foods are above an EU indicative level (AOH 2, AME 2)"
            % INFANT_PCT, ("infant cereal",), lambda k, n: 100 * k >= INFANT_PCT * n)

    pom = [s for s in rows if s["pomegranate"] and s["total"] is not None]
    high = _counts(s["origin"] for s in pom if s["total"] >= POM_FROM and s["origin"] not in NO_COUNTRY)
    p["P7"] = {"prediction": "Turkey is strictly the most frequent declared country among pomegranate products "
                             "with AOH + AME of %g ppb or more" % POM_FROM,
               "value": high, "status": _status(ok and sum(high.values()) >= 5, _strict_top(high, "TURKEY"))}
    foreign = [s["total"] for s in pom if s["origin"] not in NO_COUNTRY + ("CANADA",)]
    canada = [s["total"] for s in pom if s["origin"] == "CANADA"]
    med_f = statistics.median(foreign) if foreign else None
    med_c = statistics.median(canada) if canada else None
    p["P8"] = {"prediction": "pomegranate products declaring a foreign country have a higher median AOH + AME "
                             "than those declaring Canada",
               "value": {"foreign_median": med_f, "canada_median": med_c, "n_foreign": len(foreign),
                         "n_canada": len(canada)},
               "status": _status(ok and len(foreign) >= 5 and len(canada) >= 5,
                                 med_f is not None and med_c is not None and med_f > med_c)}
    above = [s for s in rows if s["state"] == "above" and s["origin"] not in NO_COUNTRY]
    abroad = sum(1 for s in above if s["origin"] != "CANADA")
    p["P9"] = {"prediction": "more than half of the above-level samples that declare a country declare one "
                             "other than Canada",
               "value": "%d of %d" % (abroad, len(above)), "status": _status(ok and len(above) >= 3,
                                                                           2 * abroad > len(above))}
    return {"version": VERSION, "samples": n, "gradable_parse": ok, "predictions": p,
            "met": sum(1 for v in p.values() if v["status"] == "met"),
            "gradable": sum(1 for v in p.values() if v["status"] != "not gradable")}


def _max(xs):
    xs = [x for x in xs if x is not None]
    return max(xs) if xs else None


def _group(origin):
    return "NO COUNTRY" if origin in NO_COUNTRY else "CANADA" if origin == "CANADA" else "FOREIGN"


def describe(rows):
    keep = ("sample", "type", "product", "origin", "category", "aoh", "ame", "total", "state")
    cats = {}
    for c in EU_LEVELS:
        xs = _in((c,), rows)
        groups = {}
        for s in xs:
            g = groups.setdefault(_group(s["origin"]), {"n": 0, "above": 0})
            g["n"] += 1
            g["above"] += s["state"] == "above"
        cats[c] = {"levels_aoh_ame": list(EU_LEVELS[c]), "n": len(xs),
                   "above": sum(1 for s in xs if s["state"] == "above"),
                   "within": sum(1 for s in xs if s["state"] == "within"),
                   "undetermined": sum(1 for s in xs if s["state"] == "undetermined"),
                   "max_aoh": _max(s["aoh"] for s in xs), "max_ame": _max(s["ame"] for s in xs),
                   "max_total": _max(s["total"] for s in xs), "by_origin": groups}
    by_type = {}
    for s in rows:
        t = by_type.setdefault(s["type"] or "(none)", {"n": 0, "detected": 0, "max_total": None})
        t["n"] += 1
        t["detected"] += (s["total"] or 0) > 0
        t["max_total"] = _max([t["max_total"], s["total"]])
    pom = {}
    for s in rows:
        if s["pomegranate"] and s["total"] is not None:
            pom.setdefault(s["origin"], []).append(s["total"])
    both = [s for s in rows if s["aoh"] is not None and s["ame"] is not None and s["total"] > 0]
    return {"categories": cats,
            "by_type": dict(sorted(by_type.items(), key=lambda kv: (-kv[1]["n"], kv[0]))),
            "pomegranate_by_origin": {o: {"n": len(v), "median": statistics.median(v), "max": max(v)}
                                      for o, v in sorted(pom.items(), key=lambda kv: (-len(kv[1]), kv[0]))},
            "above": [{k: s[k] for k in keep} for s in rows if s["state"] == "above"],
            "undetermined": [{k: s[k] for k in keep} for s in rows if s["state"] == "undetermined"],
            "top_15": [{k: s[k] for k in keep}
                       for s in sorted((s for s in rows if s["total"] is not None),
                                       key=lambda s: -s["total"])[:15]],
            "ame_over_aoh": {"n": len(both), "ame_greater": sum(1 for s in both if s["ame"] > s["aoh"])}}


FIELDS = ["sample", "type", "product", "origin", "category", "pomegranate", "aoh_ppb", "ame_ppb",
          "total_reported_ppb", "total_ppb", "state", "results"]


def _cell(x):
    return "" if x is None else x


def write_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        for s in rows:
            w.writerow([s["sample"], s["type"], s["product"], s["origin"], s["category"], int(s["pomegranate"]),
                        _cell(s["aoh"]), _cell(s["ame"]), _cell(s["total_reported"]), _cell(s["total"]),
                        s["state"], s["results"]])


def summary_md(result):
    g, d, c = result["grade"], result["descriptive"], result["check"]
    lines = ["# alternaria_eu %s" % VERSION, "",
             "- File sha256 %s; %d data rows, %d samples (%d with AOH and AME separate); bad numbers %d; "
             "other-component rows %d." % (c.get("sha256", ""), c["data_rows"], c["samples"], c["with_components"],
                                           c["bad_numbers"], c["other_component_rows"]),
             "", "## Pre-registered predictions (%d met of %d gradable)" % (g["met"], g["gradable"]),
             "", "| | prediction | value | status |", "|---|---|---|---|"]
    for k, v in g["predictions"].items():
        lines.append("| %s | %s | %s | %s |" % (k, v["prediction"], json.dumps(v["value"], ensure_ascii=False),
                                               v["status"]))
    lines += ["", "## EU 2022/553 foods (indicative levels are not food safety levels)", "",
              "| food | AOH/AME level ug/kg | n | above | within | undetermined | max AOH | max AME | max total | "
              "by origin (n, above) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for k, t in d["categories"].items():
        lines.append("| %s | %g/%g | %d | %d | %d | %d | %s | %s | %s | %s |" % (
            k, t["levels_aoh_ame"][0], t["levels_aoh_ame"][1], t["n"], t["above"], t["within"], t["undetermined"],
            t["max_aoh"], t["max_ame"], t["max_total"],
            "; ".join("%s %d, %d" % (o, x["n"], x["above"]) for o, x in sorted(t["by_origin"].items()))))
    lines += ["", "AME greater than AOH in %d of %d detected samples with both." % (
        d["ame_over_aoh"]["ame_greater"], d["ame_over_aoh"]["n"])]
    for key in ("above", "undetermined", "top_15"):
        lines += ["", "### %s" % key, ""]
        lines += ["- %s" % json.dumps(x, ensure_ascii=False) for x in d[key]] or ["- none"]
    lines += ["", "## Pomegranate products by declared origin", "", "| origin | n | median ppb | max ppb |",
              "|---|---|---|---|"]
    lines += ["| %s | %d | %g | %g |" % (o, t["n"], t["median"], t["max"]) for o, t in d["pomegranate_by_origin"].items()]
    lines += ["", "## By product type", "", "| type | n | detected | max total ppb |", "|---|---|---|---|"]
    lines += ["| %s | %d | %d | %s |" % (k, t["n"], t["detected"], t["max_total"]) for k, t in d["by_type"].items()]
    lines += ["", "Header: %s" % c["header"], "Units: %s" % c["units"],
              "Components: %s" % dict(list(c["components"].items())[:10]),
              "Types: %s" % dict(list(c["types"].items())[:40]),
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
    ap.add_argument("--data-dir", default=None, help="a folder holding a local copy named alternaria.csv")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    if a.data_dir:
        with open(os.path.join(a.data_dir, "alternaria.csv"), "rb") as f:
            raw = f.read()
    else:
        raw = fetch(URL)
        with open(os.path.join(a.out_dir, "cfia_alternaria.csv"), "wb") as f:
            f.write(raw)
    rows, check = parse(raw)
    check.update(dataset=DATASET, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    result = {"grade": grade(rows), "descriptive": describe(rows), "check": check}
    write_rows(os.path.join(a.out_dir, "alternaria_samples.csv"), rows)
    with open(os.path.join(a.out_dir, "grades.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, ensure_ascii=False)
    with open(os.path.join(a.out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write(summary_md(result))
    g = result["grade"]
    print("alternaria_eu %s: %d samples, %d of %d gradable predictions met"
          % (VERSION, g["samples"], g["met"], g["gradable"]))
    return 0 if g["gradable_parse"] else 1


if __name__ == "__main__":
    sys.exit(main())
